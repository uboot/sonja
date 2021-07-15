from conanci import database
from conanci.config import connect_to_database, logger
from conanci.ssh import decode
from conanci.worker import Worker
from queue import Empty, SimpleQueue
import asyncio
import datetime
import git
import os.path
import re
import shutil
import stat


data_dir = os.environ.get("VCS_DATA_DIR", "/data")
CRAWLER_PERIOD_SECONDS = 300


class RepoController(object):
    def __init__(self, work_dir):
        self.work_dir = work_dir
        self.repo_dir = os.path.join(work_dir, "repo")

    def is_clone_of(self, url):
        try:
            repo = git.Repo(self.repo_dir)
        except git.exc.NoSuchPathError:
            return False

        if len(repo.remotes) == 0:
            return False

        for remote_url in repo.remotes[0].urls:
            if remote_url == url:
                return True
        return False

    def create_new_repo(self, url):
        shutil.rmtree(self.work_dir, ignore_errors=True)
        repo = git.Repo.init(self.repo_dir)
        repo.create_remote('origin', url=url)

    def setup_ssh(self, ssh_key, known_hosts):
        ssh_key_path = os.path.abspath(os.path.join(self.work_dir, "id_rsa"))
        with open(ssh_key_path, "w") as f:
            f.write(decode(ssh_key))
        os.chmod(ssh_key_path, stat.S_IRUSR | stat.S_IWUSR)
        known_hosts_path = os.path.abspath(os.path.join(self.work_dir, "known_hosts"))
        with open(known_hosts_path, "w") as f:
            f.write(decode(known_hosts))
        repo = git.Repo(self.repo_dir)
        config = repo.config_writer()
        config.set_value("core", "sshCommand", "ssh -i {0} -o UserKnownHostsFile={1}".format(ssh_key_path,
                                                                                             known_hosts_path))

    def fetch(self):
        repo = git.Repo(self.repo_dir)
        repo.git.fetch()

    def get_remote_branches(self):
        repo = git.Repo(self.repo_dir)
        branches = [b.strip() for b in repo.git.branch('-r').split()]
        pattern = 'origin/([/\\-\\w]+)'
        matches = [re.match(pattern, b) for b in branches]
        return list(set(m.group(1) for m in matches
                    if m and m.group(1) != 'HEAD'))

    def checkout(self, branch):
        repo = git.Repo(self.repo_dir)
        repo.git.reset('--hard', 'origin/{}'.format(branch))

    def get_sha(self):
        repo = git.Repo(self.repo_dir)
        return repo.head.commit.hexsha

    def get_message(self):
        repo = git.Repo(self.repo_dir)
        message = repo.head.commit.message
        if not len(message):
            return ''

        first_line = message.splitlines()[0]
        return first_line[:255] if len(first_line) > 255 else first_line

    def get_user_name(self):
        repo = git.Repo(self.repo_dir)
        name = repo.head.commit.author.name
        if not len(name):
            return ''
        return name[:255] if len(name) > 255 else name

    def get_user_email(self):
        repo = git.Repo(self.repo_dir)
        email = repo.head.commit.author.email
        if not len(email):
            return ''
        return email[:255] if len(email) > 255 else email


class Crawler(Worker):
    def __init__(self, scheduler):
        super().__init__()
        connect_to_database()
        self.__scheduler = scheduler
        self.__repos = SimpleQueue()
        self.__next_crawl = datetime.datetime.now()

    def post_repo(self, repo_id):
        self.__repos.put(repo_id)

    async def work(self):
        try:
            await self.__process_repos()
        except Exception as e:
            logger.error("Processing repos failed: %s", e)

    async def __process_repos(self):
        logger.info("Start crawling")
        loop = asyncio.get_running_loop()

        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            logger.info("Created directory '%s'", data_dir)

        new_commits = False
        with database.session_scope() as session:
            if datetime.datetime.now() >= self.__next_crawl:
                logger.info("Crawl all repos")
                repos = session.query(database.Repo).all()
                self.__next_crawl = datetime.datetime.now() + datetime.timedelta(seconds=CRAWLER_PERIOD_SECONDS)
                self.reschedule_internally(CRAWLER_PERIOD_SECONDS)
            else:
                logger.info("Crawl manually triggered repos")
                repo_ids = [repo for repo in self.__get_repos()]
                repos = session.query(database.Repo).filter(database.Repo.id.in_(repo_ids)).all()
            channels = session.query(database.Channel).all()
            for repo in repos:
                try:
                    work_dir = os.path.join(data_dir, str(repo.id))
                    controller = RepoController(work_dir)
                    if not controller.is_clone_of(repo.url):
                        logger.info("Create repo for URL '%s' in '%s'", repo.url, work_dir)
                        await loop.run_in_executor(None, controller.create_new_repo, repo.url)
                    logger.info("Setup SSH for in '%s'", work_dir)
                    await loop.run_in_executor(None, controller.setup_ssh, repo.ecosystem.ssh_key,
                                               repo.ecosystem.known_hosts)
                    logger.info("Fetch repo '%s' for URL '%s'", work_dir, repo.url)
                    await loop.run_in_executor(None, controller.fetch)

                    branches = controller.get_remote_branches()
                    for channel in channels:
                        for branch in branches:
                            if not re.fullmatch(channel.branch, branch):
                                continue

                            logger.info("Branch '%s' matches '%s'", branch, channel.branch)
                            logger.info("Checkout branch '%s'", branch)
                            controller.checkout(branch)
                            sha = controller.get_sha()

                            commits = session.query(database.Commit).filter_by(repo=repo,
                                sha=sha, channel=channel)

                            # continue if this commit has already been stored
                            if list(commits):
                                logger.info("Commit '%s' exists", sha[:7])
                                continue

                            logger.info("Add commit '%s'", sha[:7])
                            commit = database.Commit()
                            commit.sha = sha
                            commit.message = controller.get_message()
                            commit.user_name = controller.get_user_name()
                            commit.user_email = controller.get_user_email()
                            commit.repo = repo
                            commit.channel = channel
                            commit.status = database.CommitStatus.new
                            session.add(commit)
                            new_commits = True

                            old_commits = session.query(database.Commit).filter(
                                database.Commit.repo == repo,
                                database.Commit.channel == channel,
                                database.Commit.sha != sha,
                                database.Commit.status != database.CommitStatus.old
                            )
                            for c in old_commits:
                                logger.info("Set status of '%s' to 'old'", c.sha[:7])
                                c.status = database.CommitStatus.old
                except git.exc.GitError as e:
                    logger.error("Failed to process repo '%s' with message '%s'", repo.url, e)

        if new_commits:
            logger.info("Finish crawling with *new* commits")
            logger.info('Trigger scheduler: process commits')
            self.__scheduler.process_commits()
        else:
            logger.info("Finish crawling with *no* new commits")

    def __get_repos(self):
        try:
            while True:
                yield self.__repos.get_nowait()
        except Empty:
            pass