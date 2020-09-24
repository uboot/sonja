from conans.client.conan_api import ConanAPIV1

class Conan(object):
    def __init__(self):
        self.api = ConanAPIV1()

    def remotes(self):
        return self.api.remote_list()