from django.contrib.auth import get_user_model
from django.test import TestCase

class UserManagerTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )
        self.assertEqual(user.email, 'viewer@example.com')
        self.assertEqual(user.role, User.Role.VIEWER)
        self.assertTrue(user.check_password('testpassword'))
        self.assertFalse(user.is_staff),
        self.assertFalse(user.is_superuser)