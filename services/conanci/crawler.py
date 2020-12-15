from conanci import database
from conanci.config import connect_to_database, logger
from conanci.worker import Worker
from sqlalchemy.orm import sessionmaker
import asyncio
import git
import os.path
import re
import shutil

data_dir = os.environ.get("VCS_DATA_DIR", "/data")


class RepoController(object):
    def __init__(self, repo_dir):
        self.repo_dir = repo_dir

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

    def create_new_clone(self, url):
        shutil.rmtree(self.repo_dir, ignore_errors=True)
        git.Repo.clone_from(url=url, to_path=self.repo_dir)

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


class Crawler(Worker):
    def __init__(self, scheduler):
        super().__init__()
        connect_to_database()
        self.__scheduler = scheduler

    async def work(self):
        logger.info("Start crawling")
        loop = asyncio.get_running_loop()

        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            logger.info("Created directory '%s'", data_dir)

        new_commits = False
        with database.session_scope() as session:
            repos = session.query(database.Repo).all()
            channels = session.query(database.Channel).all()
            for repo in repos:
                try:
                    repo_dir = os.path.join(data_dir, str(repo.id))
                    controller = RepoController(repo_dir)
                    if not controller.is_clone_of(repo.url):
                        logger.info("Clone URL '%s' to '%s'", repo.url, repo_dir)
                        await loop.run_in_executor(None, controller.create_new_clone, repo.url)
                    else:
                        logger.info("Fetch existing repo '%s' for URL '%s'",
                                    repo_dir, repo.url)
                        await loop.run_in_executor(None, controller.fetch)

                    branches = controller.get_remote_branches()
                    for channel in channels:
                        if channel.branch in branches:
                            logger.info("Checkout branch '%s'", channel.branch)
                            controller.checkout(channel.branch)
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
