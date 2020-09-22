from swagger_server.config import app
from swagger_server import database
import git
import os.path
import re
import shutil

data_dir = os.environ.get("CRAWLER_REPO_DIR", "/data")
logger = app.app.logger


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
        repo = git.Repo.clone_from(url=url, to_path=self.repo_dir)

    def fetch(self):
        repo = git.Repo(self.repo_dir)
        repo.git.fetch()

    def get_remote_branches(self):
        repo = git.Repo(self.repo_dir)
        branches = [b.strip() for b in repo.git.branch('-r').split()]
        pattern = 'origin/([/\-\\w]+)'
        matches = [re.match(pattern, b) for b in branches]
        return list(set(m.group(1) for m in matches if m and m.group(1) != 'HEAD'))

    def checkout_and_update(self, branch):
        repo = git.Repo(self.repo_dir)
        repo.git.checkout(branch)
        repo.git.pull()

def trigger():
    logger.info("start crawling")

    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        logger.info("created directory '%s'", data_dir)

    repos = database.Repo.query.all()
    channels = database.Channel.query.all()
    for repo in repos:
        repo_dir = os.path.join(data_dir, str(repo.id))
        controller = RepoController(repo_dir)
        if not controller.is_clone_of(repo.url):
            controller.create_new_clone(repo.url)
            logger.info("cloned URL '%s' to '%s'", repo.url, repo_dir)
        else:
            controller.fetch()
            logger.info("fetch existing repo '%s' for URL '%s'",
                         repo_dir, repo.url)

        branches = controller.get_remote_branches()
        for channel in channels:
            if channel.branch in branches:
                controller.checkout_and_update(channel.branch)
                logger.info("checkout and update branch '%s'", channel.branch)

