import os
import shutil
import unittest
import tempfile

from sonja.crawler import RepoController


known_hosts = ("Z2l0aHViLmNvbSwxNDAuODIuMTIxLjQgc3NoLXJzYSBBQUFBQjNOemFDMXljMkVBQUFBQkl3QUFBUUVBcTJBN"
               "2hSR21kbm05dFVEYk85SURTd0JLNlRiUWErUFhZUENQeTZyYlRyVHR3N1BIa2NjS3JwcDB5VmhwNUhkRUljS3"
               "I2cExsVkRCZk9MWDlRVXN5Q09WMHd6ZmpJSk5sR0VZc2RsTEppekhoYm4ybVVqdlNBSFFxWkVUWVA4MWVGekx"
               "RTm5QSHQ0RVZWVWg3VmZERVNVODRLZXptRDVRbFdwWExtdlUzMS95TWYrU2U4eGhIVHZLU0NaSUZJbVd3b0c2"
               "bWJVb1dmOW56cElvYVNqQit3ZXFxVVVtcGFhYXNYVmFsNzJKK1VYMkIrMlJQVzNSY1QwZU96UWdxbEpMM1JLc"
               "lRKdmRzakUzSkVBdkdxM2xHSFNaWHkyOEczc2t1YTJTbVZpL3c0eUNFNmdiT0RxblRXbGc3K3dDNjA0eWRHWE"
               "E4VkppUzVhcDQzSlhpVUZGQWFRPT0K")

class TestRepoController(unittest.TestCase):
    def setUp(self):
        self.work_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.work_dir)

    def test_checkout_master(self):
        controller = RepoController(self.work_dir)
        controller.create_new_repo("git@github.com:uboot/sonja-backend.git")
        controller.setup_ssh(os.environ.get("SSH_KEY", ""), known_hosts)
        controller.fetch()
        controller.checkout("master")
        self.assertTrue(os.path.exists(os.path.join(self.work_dir, "repo", "chart")))

    def test_setup_ssh(self):
        controller = RepoController(self.work_dir)
        controller.create_new_repo("git@github.com:uboot/sonja-backend.git")
        controller.setup_ssh(os.environ.get("SSH_KEY", ""), known_hosts)
        self.assertTrue(os.path.exists(os.path.join(self.work_dir, "id_rsa")))
        self.assertTrue(os.path.exists(os.path.join(self.work_dir, "known_hosts")))