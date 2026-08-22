from django.contrib.auth import get_user_model
from django.test import TestCase
from .serializers import LoginSerializer, RegistrationSerializer

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# Test cases for the User model and related serializers and views.

class UserManagerTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            email='viewer@example.com',
            password='Strong-Password_123'
        )
        self.assertEqual(user.email, 'viewer@example.com')
        self.assertEqual(user.role, User.Role.VIEWER)
        self.assertTrue(user.check_password('Strong-Password_123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_requires_email(self):
        User = get_user_model()

        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",
                password="Strong-Password_123",
            )

    def test_create_superuser(self):
            User = get_user_model()
    

            user =User.objects.create_superuser(
                    email="admin@example.com",
                    password="Strong-Password_123",
                )

            self.assertEqual(user.role, User.Role.ADMIN)
            self.assertTrue(user.is_staff)
            self.assertTrue(user.is_superuser)
            self.assertTrue(user.check_password("Strong-Password_123"))


# Test cases for the RegistrationSerializer and RegisterView.
class RegistrationSerializerTests(TestCase):
    password = "Strong-Password_123"

    def test_valid_registration_creates_viewer(self):
        User = get_user_model()

        serializer = RegistrationSerializer(data={
               "email": "new.user@example.com",
               "password": self.password,
               "first_name": "New",
               "last_name": "User",
               "role": User.Role.VIEWER,
          })

        self.assertTrue(
               serializer.is_valid(),
               serializer.errors
          )

        user = serializer.save()

        self.assertEqual(user.email, 'new.user@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.role, User.Role.VIEWER)
        self.assertTrue(user.check_password(self.password))
        self.assertNotEqual(user.password, self.password) 

    def test_duplicate_email_is_case_insensitive(self):
        User = get_user_model()

        User.objects.create_user(
            email="member@example.com",
            password=self.password,
        )

        serializer = RegistrationSerializer(data={
            "email": "member@example.com",
            "password": self.password,
            "first_name": "Another",
            "last_name": "Member",
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertEqual(User.objects.count(), 1)

    def test_registration_requires_names(self):
        serializer = RegistrationSerializer(data={
            "email": "nameless@example.com",
            "password": self.password,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("first_name", serializer.errors)
        self.assertIn("last_name", serializer.errors)

# Test cases for the RegisterView API endpoint.
class RegistrationViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('accounts:register')
        self.password = "Strong-Password_123"

    def test_register_creates_viewer_and_hides_password(self):
       User = get_user_model()

       response = self.client.post(
           self.url,
           {
               
               "email": "New.Api.User@Example.com",
                "password": self.password,
                "first_name": "New",
                "last_name": "User", 
                "role": User.Role.ADMIN,
           },
           format='json'
       )

       self.assertEqual(
           response.status_code, 
           status.HTTP_201_CREATED,
           response.data,
       )

       self.assertEqual(
           response.data['email'], 
           "new.api.user@example.com",
       )

       self.assertEqual(
           response.data['role'],
            User.Role.VIEWER,
       )

       self.assertNotIn('password', response.data)

       user = User.objects.get(
           email="new.api.user@example.com"
       )

       self.assertEqual(user.role, User.Role.VIEWER)
       self.assertTrue(user.check_password(self.password))

    def test_invalid_registration_returns_400(self):
        User = get_user_model()

        response = self.client.post(
            self.url,
            {
                "email": "incomplete@example.com",
                "password": self.password,
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)
        self.assertEqual(User.objects.count(), 0)


class LoginSerializerTests(TestCase):
    password = "Strong-Password_123"

    def setUp(self):
       User = get_user_model()
       self.user = User.objects.create_user(
           email="member@example.com",
           password=self.password,
       )

    def test_valid_credentials_returns_user(self):
        serializer = LoginSerializer(data={
            "email": "member@example.com",
            "password": self.password
        })
        self.assertTrue(serializer.is_valid(),
        serializer.errors,
        )

        
        self.assertEqual(serializer.validated_data['user'], self.user)

    def test_invalid_credentials_returns_error(self):
        serializer = LoginSerializer(data={
            "email": "member@example.com",
            "password": "wrongpassword"
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)