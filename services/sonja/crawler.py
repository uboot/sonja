import gitdb.exc

from sonja.config import connect_to_database, logger
from sonja.credential_helper import build_credential_helper
from sonja.database import Session, session_scope, get_current_configuration
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
ALL_REPOS = "all_repos"


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

    def checkout_sha(self, sha: str) -> bool:
        logger.info("Checkout '%s'", sha)
        repo = git.Repo(self.repo_dir)
        try:
            commit = git.Commit.new(repo, sha)
            repo.head.reset(commit, working_tree=True)
            return True
        except gitdb.exc.BadName:
            return False

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
        try:
            past_commit = repo.commit(commit_sha)
        except gitdb.exc.BadName:
            logger.debug("Commit '%s' can not be found, assume a diff", commit_sha)
            return True

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
                normalized_ref = f"heads/{ref.name.removeprefix('origin/')}"
            elif isinstance(ref, git.TagReference):
                normalized_ref = f"tags/{ref.name}"
            else:
                continue

            if not re.fullmatch(ref_pattern, normalized_ref):
                continue

            logger.info("Checkout '%s'", ref)
            repo.head.reset(ref, working_tree=True)
            yield normalized_ref


class RepoUpdate:
    def __init__(self, repo_id: str = "", sha: str = "", ref: str = ""):
        self.repo_id = repo_id
        self.sha = sha
        self.ref = ref


class Crawler(Worker):
    def __init__(self, scheduler, periodic: bool = True):
        super().__init__()
        connect_to_database()

        self.__data_dir = tempfile.mkdtemp()
        logger.info("Created data directory '%s'", self.__data_dir)

        self.__scheduler = scheduler
        self.__repos = SimpleQueue()
        self.__periodic = periodic

    def process_repo(self, repo_id: str = "", sha: str = "", ref: str = ""):
        self.__repos.put(RepoUpdate(repo_id, sha, ref))

    async def work(self, payload):
        try:
            if payload == ALL_REPOS or self.__periodic:
                self.__periodic = False
                await self.__process_all_repos()
                self.reschedule_internally(CRAWLER_PERIOD_SECONDS, ALL_REPOS)

            else:
                for repo in self.__get_repos():
                    await self.__process_update(repo)
        except Exception as e:
            logger.error("Processing repos failed: %s", e)
            logger.info("Retry in %i seconds", TIMEOUT)
            time.sleep(TIMEOUT)

    def cleanup(self):
        shutil.rmtree(self.__data_dir)
        logger.info("Removed data directory '%s'", self.__data_dir)

    async def __process_all_repos(self):
        logger.info("Start crawling all repos")

        with session_scope() as session:
            for repo in session.query(Repo).all():
                await self.__process_repo(session, repo, "", "")

        logger.info("Finish crawling all repos")

    async def __process_update(self, update: RepoUpdate):
        logger.info("Start crawling")

        with session_scope() as session:
            logger.info("Crawl manually triggered repos")
            repo = session.query(Repo).filter_by(id=update.repo_id).first()
            await self.__process_repo(session, repo, update.sha, update.ref)

        logger.info("Finish crawling")

    def __get_repos(self):
        try:
            while True:
                yield self.__repos.get_nowait()
        except Empty:
            pass

    async def __process_repo(self, session: Session, repo: Repo, sha: str, ref: str):        
        loop = asyncio.get_running_loop()
        new_commits = False
        try:
            work_dir = os.path.join(self.__data_dir, str(repo.id))
            controller = RepoController(work_dir)
            if not controller.is_clone_of(repo.url):
                logger.info("Create repo for URL '%s' in '%s'", repo.url, work_dir)
                await loop.run_in_executor(None, controller.create_new_repo, repo.url)
            configuration = get_current_configuration(session)
            logger.info("Setup SSH in '%s'", work_dir)
            await loop.run_in_executor(None, controller.setup_ssh, configuration.ssh_key,
                                        configuration.known_hosts)
            logger.info("Setup HTTP credentials in '%s'", work_dir)
            credentials = [
                {
                    "url": c.url,
                    "username": c.username,
                    "password": c.password
                } for c in configuration.git_credentials
            ]
            await loop.run_in_executor(None, controller.setup_http, credentials)
            logger.info("Fetch repo '%s' for URL '%s'", work_dir, repo.url)
            await loop.run_in_executor(None, controller.fetch)

            for channel in session.query(Channel).all():
                if sha and ref:
                    if re.fullmatch(channel.ref_pattern, ref):
                        logger.info("Ref '%s' matches '%s'", ref, channel.ref_pattern)
                        if not controller.checkout_sha(sha):
                            logger.info("Can not checkout commit '%s'", sha)
                            continue
                        if self.__process_commit(session, controller, repo, channel):
                            new_commits = True
                else:
                    for ref in controller.checkout_matching_refs(channel.ref_pattern):
                        logger.info("Ref '%s' matches '%s'", ref, channel.ref_pattern)
                        if self.__process_commit(session, controller, repo, channel):
                            new_commits = True

        except git.exc.GitError as e:
            logger.error("Failed to process repo '%s' with message '%s'", repo.url, e)

        if new_commits:
            logger.info("Finish crawling '%s'", repo.name)
            session.commit()
            logger.info('Trigger scheduler: process commits')
            if not self.__scheduler.process_commits():
                logger.error("Failed to trigger scheduler")
    
    def __process_commit(self, session: Session, controller: RepoController, repo: Repo, channel: Channel):
        sha = controller.get_sha()

        commits = session.query(Commit).filter_by(repo=repo,
                                                  sha=sha, channel=channel)

        # continue if this commit has already been stored
        if list(commits):
            logger.info("Commit '%s' exists", sha[:7])
            return False

        old_commits = session.query(Commit).filter(
            Commit.repo == repo,
            Commit.channel == channel,
            Commit.sha != sha,
            Commit.status != CommitStatus.old
        )

        if repo.path and any(old_commits):
            if not any([controller.has_diff(commit.sha, repo.path) for commit in old_commits]):
                logger.info("Path '%s' was not changed since previous commits", repo.path)
                return False

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

        for c in old_commits:
            logger.info("Set status of '%s' to 'old'", c.sha[:7])
            c.status = CommitStatus.old

        return True
