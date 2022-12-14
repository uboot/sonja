import os
from requests import get
from requests.exceptions import RequestException
from requests.status_codes import codes
from urllib.parse import urlencode


class ClientBase:
    def call_get(self, url, path) -> bool:
        host = f"http://{url}:8080"
        try:
            r = get(f"{host}/{path}", timeout=1)
        except RequestException:
            return False

        return r.status_code == codes.ok


class LinuxAgent(ClientBase):
    def process_builds(self) -> bool:
        url = os.environ.get('SONJA_LINUXAGENT_URL', '127.0.0.1')
        return self.call_get(url, "process_builds")


class WindowsAgent(ClientBase):
    def process_builds(self) -> bool:
        url = os.environ.get('SONJA_WINDOWSAGENT_URL', '127.0.0.1')
        return self.call_get(url, "process_builds")


class Scheduler(ClientBase):
    def process_commits(self) -> bool:
        url = os.environ.get('SONJA_SCHEDULER_URL', '127.0.0.1')
        return self.call_get(url, "process_commits")


class Crawler(ClientBase):
    def process_repo(self, repo_id: str, sha: str = "", ref: str = 22) -> bool:
        url = os.environ.get('SONJA_CRAWLER_URL', '127.0.0.1')
        params = {"sha": sha, "ref": ref}
        return self.call_get(url, f"process_repo/{repo_id}?{urlencode(params)}")
