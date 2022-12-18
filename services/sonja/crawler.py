from sonja.config import connect_to_database, logger
from sonja.credential_helper import build_credential_helper
from sonja.database import session_scope
from sonja.model import CommitStatus, Commit, Channel, Repo
from sonja.ssh import decode
from sonja.worker import Worker
from queue import Empty, SimpleQueue
import asyncio
import datetime
import git
import os.path
import re
import shutil
import stat
import tempfile
import time


CRAWLER_PERIOD_SECONDS = 300
TIMEOUT = 10


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
        shutil.rmtree(self.repo_dir, ignore_errors=True)
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
        with repo.config_writer() as config:
            config.set_value("core", "sshCommand", "ssh -i {0} -o UserKnownHostsFile={1}".format(ssh_key_path,
                                                                                                 known_hosts_path))

    def setup_http(self, git_credentials):
        credential_helper = build_credential_helper(git_credentials)
        credential_helper_path = os.path.abspath(os.path.join(self.work_dir, "credential_helper.sh"))
        with open(credential_helper_path, "w") as f:
            f.write(credential_helper)
        os.chmod(credential_helper_path, stat.S_IRWXU)
        repo = git.Repo(self.repo_dir)
        with repo.config_writer() as config:
            config.set_value("credential", "helper", "{0}".format(credential_helper_path))

    def fetch(self):
        repo = git.Repo(self.repo_dir)
        repo.remotes.origin.fetch()

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

    def has_diff(self, commit_sha: str, path: str):
        repo = git.Repo(self.repo_dir)
        this_commit = repo.head.commit
        past_commit = repo.commit(commit_sha)
        diffs = this_commit.diff(past_commit)
        for d in diffs:
            if os.path.commonprefix((d.a_path, path)) == path:
                return True
            if os.path.commonprefix((d.b_path, path)) == path:
                return True

        return False

    def checkout_matching_refs(self, ref_pattern):
        repo = git.Repo(self.repo_dir)
        for ref in repo.refs:
            if isinstance(ref, git.RemoteReference):
                normalized_ref = f"heads/{ref.name.lstrip('origin/')}"
            elif isinstance(ref, git.TagReference):
                normalized_ref = f"tags/{ref.name}"
            else:
                continue

            if not re.fullmatch(ref_pattern, normalized_ref):
                continue

            repo.head.reset(ref, working_tree=True)
            yield normalized_ref





class Crawler(Worker):
    def __init__(self, scheduler):
        super().__init__()
        connect_to_database()
        self.__data_dir = tempfile.mkdtemp()
        self.__scheduler = scheduler
        self.__repos = SimpleQueue()
        self.__next_crawl = datetime.datetime.now()
        logger.info("Created data directory '%s'", self.__data_dir)

    def process_repo(self, repo_id: str, sha: str = "", ref: str = ""):
        self.__repos.put(repo_id)

    async def work(self):
        try:
            await self.__process_repos()
        except Exception as e:
            logger.error("Processing repos failed: %s", e)
            logger.info("Retry in %i seconds", TIMEOUT)
            time.sleep(TIMEOUT)

    def cleanup(self):
        shutil.rmtree(self.__data_dir)
        logger.info("Removed data directory '%s'", self.__data_dir)

    async def __process_repos(self):
        logger.info("Start crawling")
        loop = asyncio.get_running_loop()

        with session_scope() as session:
            if datetime.datetime.now() >= self.__next_crawl:
                logger.info("Crawl all repos")
                repos = session.query(Repo).all()
                self.__next_crawl = datetime.datetime.now() + datetime.timedelta(seconds=CRAWLER_PERIOD_SECONDS)
                self.reschedule_internally(CRAWLER_PERIOD_SECONDS)
            else:
                logger.info("Crawl manually triggered repos")
                repo_ids = [repo for repo in self.__get_repos()]
                repos = session.query(Repo).filter(Repo.id.in_(repo_ids)).all()
            channels = session.query(Channel).all()
            for repo in repos:
                new_commits = False
                try:
                    work_dir = os.path.join(self.__data_dir, str(repo.id))
                    controller = RepoController(work_dir)
                    if not controller.is_clone_of(repo.url):
                        logger.info("Create repo for URL '%s' in '%s'", repo.url, work_dir)
                        await loop.run_in_executor(None, controller.create_new_repo, repo.url)
                    logger.info("Setup SSH in '%s'", work_dir)
                    await loop.run_in_executor(None, controller.setup_ssh, repo.ecosystem.ssh_key,
                                               repo.ecosystem.known_hosts)
                    logger.info("Setup HTTP credentials in '%s'", work_dir)
                    credentials = [
                        {
                            "url": c.url,
                            "username": c.username,
                            "password": c.password
                        } for c in repo.ecosystem.git_credentials
                    ]
                    await loop.run_in_executor(None, controller.setup_http, credentials)
                    logger.info("Fetch repo '%s' for URL '%s'", work_dir, repo.url)
                    await loop.run_in_executor(None, controller.fetch)

                    for channel in channels:
                        for ref in controller.checkout_matching_refs(channel.ref_pattern):
                            logger.info("Ref '%s' matches '%s'", ref, channel.ref_pattern)
                            sha = controller.get_sha()

                            commits = session.query(Commit).filter_by(repo=repo,
                                                                      sha=sha, channel=channel)

                            # continue if this commit has already been stored
                            if list(commits):
                                logger.info("Commit '%s' exists", sha[:7])
                                continue

                            old_commits = session.query(Commit).filter(
                                Commit.repo == repo,
                                Commit.channel == channel,
                                Commit.sha != sha,
                                Commit.status != CommitStatus.old
                            )

                            if repo.path and any(old_commits):
                                if not any([controller.has_diff(commit.sha, repo.path) for commit in old_commits]):
                                    logger.info("Path '%s' was not changed since previous commits", repo.path)
                                    continue

                            logger.info("Add commit '%s'", sha[:7])
                            commit = Commit()
                            commit.sha = sha
                            commit.message = controller.get_message()
                            commit.user_name = controller.get_user_name()
                            commit.user_email = controller.get_user_email()
                            commit.repo = repo
                            commit.channel = channel
                            commit.status = CommitStatus.new
                            session.add(commit)
                            new_commits = True

                            for c in old_commits:
                                logger.info("Set status of '%s' to 'old'", c.sha[:7])
                                c.status = CommitStatus.old
                except git.exc.GitError as e:
                    logger.error("Failed to process repo '%s' with message '%s'", repo.url, e)

                if new_commits:
                    logger.info("Finish crawling '%s'", repo.name)
                    session.commit()
                    logger.info('Trigger scheduler: process commits')
                    if not self.__scheduler.process_commits():
                        logger.error("Failed to trigger scheduler")

        logger.info("Finish crawling")

    def __get_repos(self):
        try:
            while True:
                yield self.__repos.get_nowait()
        except Empty:
            pass