import unittest

from sonja import database


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        database.reset_database()

    def test_insert_first_user(self):
        database.insert_first_user("user", "password")
        with database.session_scope() as session:
            users = session.query(database.User).all()
            self.assertEqual(len(users), 1)

    def test_insert_first_user_twice(self):
        database.insert_first_user("user1", "password")
        database.insert_first_user("user2", "password")
        with database.session_scope() as session:
            users = session.query(database.User).all()
            self.assertEqual(len(users), 1)

    def test_remove_but_last_user_last_user(self):
        with database.session_scope() as session:
            user = database.User()
            user.user_name = "user"
            session.add(user)

        self.assertFalse(database.remove_but_last_user("1"))
        with database.session_scope() as session:
            user = session.query(database.User).filter_by(id="1").first()
            self.assertIsNotNone(user)

    def test_remove_but_last_user(self):
        with database.session_scope() as session:
            user1 = database.User()
            user2 = database.User()
            user1.user_name = "user1"
            user2.user_name = "user2"
            session.add(user1)
            session.add(user2)

        self.assertTrue(database.remove_but_last_user("1"))
        with database.session_scope() as session:
            users = session.query(database.User).count()
            self.assertEqual(users, 1)



