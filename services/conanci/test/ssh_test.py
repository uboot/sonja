import unittest

from conanci import ssh


class SshTest(unittest.TestCase):
    def test_generate_rsa_key(self):
        private, public = ssh.generate_rsa_key()
        self.assertTrue(private.startswith("-----BEGIN RSA PRIVATE KEY-----"))
        self.assertTrue(public.startswith("ssh-rsa"))

    def test_encode(self):
        self.assertEqual("aGVsbG8=", ssh.encode("hello"))

    def test_decode(self):
        self.assertEqual("hello", ssh.decode("aGVsbG8="))
