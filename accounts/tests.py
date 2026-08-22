from django.contrib.auth import get_user_model
from django.test import TestCase

class UserManagerTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            email='viewer@example.com',
            password='testpassword'
        )
        self.assertEqual(user.email, 'viewer@example.com')
        self.assertEqual(user.role, User.Role.VIEWER)
        self.assertTrue(user.check_password('testpassword'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_requires_email(self):
        User = get_user_model()

        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",
                password="testpassword",
            )

    def test_create_superuser(self):
            User = get_user_model()
    

            user =User.objects.create_superuser(
                    email="admin@example.com",
                    password="testpassword",
                )

            self.assertEqual(user.role, User.Role.ADMIN)
            self.assertTrue(user.is_staff)
            self.assertTrue(user.is_superuser)
            self.assertTrue(user.check_password("testpassword"))


        