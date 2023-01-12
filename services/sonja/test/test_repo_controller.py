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

    def test_checkout_main(self):
        controller = RepoController(self.work_dir)
        controller.create_new_repo("git@github.com:uboot/sonja-backend.git")
        controller.setup_ssh(os.environ.get("SSH_KEY", ""), known_hosts)
        controller.fetch()
        for _ in controller.checkout_matching_refs("heads/main"):
            self.assertTrue(os.path.exists(os.path.join(self.work_dir, "repo", "services")))

    def test_checkout_sha(self):
        controller = RepoController(self.work_dir)
        controller.create_new_repo("git@github.com:uboot/conan-packages.git")
        controller.setup_ssh(os.environ.get("SSH_KEY", ""), known_hosts)
        controller.fetch()
        controller.checkout_sha("ef89f593ea439d8986aca1a52257e44e7b8fea29")

    def test_setup_ssh(self):
        controller = RepoController(self.work_dir)
        controller.create_new_repo("git@github.com:uboot/sonja-backend.git")
        controller.setup_ssh(os.environ.get("SSH_KEY", ""), known_hosts)
        self.assertTrue(os.path.exists(os.path.join(self.work_dir, "id_rsa")))
        self.assertTrue(os.path.exists(os.path.join(self.work_dir, "known_hosts")))

    def test_has_diff(self):
        controller = RepoController(self.work_dir)
        controller.create_new_repo("git@github.com:uboot/conan-packages.git")
        controller.setup_ssh(os.environ.get("SSH_KEY", ""), known_hosts)
        controller.fetch()
        matched_a_branch = False
        for _ in controller.checkout_matching_refs("heads/change_base_version"):
            matched_a_branch = True
            self.assertTrue(controller.has_diff("d4e6245faa52440bd4386ed431ab723993fdb1d6", "base/"))
            self.assertTrue(controller.has_diff("d4e6245faa52440bd4386ed431ab723993fdb1d6", "base"))
            self.assertFalse(controller.has_diff("d4e6245faa52440bd4386ed431ab723993fdb1d6", "app/"))
            self.assertFalse(controller.has_diff("d4e6245faa52440bd4386ed431ab723993fdb1d6", "app"))
        self.assertTrue(matched_a_branch)

    def test_has_diff_invalid_sha(self):
        controller = RepoController(self.work_dir)
        controller.create_new_repo("git@github.com:uboot/conan-packages.git")
        controller.setup_ssh(os.environ.get("SSH_KEY", ""), known_hosts)
        controller.fetch()
        matched_a_branch = False
        for _ in controller.checkout_matching_refs("heads/change_base_version"):
            matched_a_branch = True
            self.assertTrue(controller.has_diff("1234567890abcdef", "base"))
        self.assertTrue(matched_a_branch)

    def test_checkout_sha(self):
        controller = RepoController(self.work_dir)
        controller.create_new_repo("git@github.com:uboot/conan-packages.git")
        controller.setup_ssh(os.environ.get("SSH_KEY", ""), known_hosts)
        controller.fetch()
        self.assertTrue(controller.checkout_sha("d4e6245faa52440bd4386ed431ab723993fdb1d6"))

    def test_checkout_invalid_sha(self):
        controller = RepoController(self.work_dir)
        controller.create_new_repo("git@github.com:uboot/conan-packages.git")
        controller.setup_ssh(os.environ.get("SSH_KEY", ""), known_hosts)
        controller.fetch()
        self.assertFalse(controller.checkout_sha("1234567890abcdef"))
