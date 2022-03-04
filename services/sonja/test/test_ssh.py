import unittest

from sonja import auth, ssh


class TestSsh(unittest.TestCase):
    def test_generate_rsa_key(self):
        private, public = ssh.generate_rsa_key()
        self.assertTrue(private.startswith("-----BEGIN RSA PRIVATE KEY-----"))
        self.assertTrue(public.startswith("ssh-rsa"))

    def test_encode(self):
        self.assertEqual("aGVsbG8=", ssh.encode("hello"))

    def test_encode_none(self):
        self.assertEqual("", ssh.encode(None))

    def test_decode(self):
        self.assertEqual("hello", ssh.decode("aGVsbG8="))

    def test_decode_none(self):
        self.assertEqual("", ssh.decode(None))

    def test_hash_password(self):
        self.assertEqual("$2b$12$", auth.hash_password("password")[:7])

    def test_test_password(self):
        hashed = auth.hash_password("password")
        self.assertTrue(auth.test_password("password", hashed))
