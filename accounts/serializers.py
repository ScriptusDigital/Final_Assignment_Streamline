from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

# Serializer for the User model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role')
        read_only_fields = fields

#Registration serializer for creating new users

class RegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        max_length=150,
        allow_blank=False,
        )

    last_name = serializers.CharField(
        max_length=150,
        allow_blank=False,
        )

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={'input_type': 'password'},
    )

    role = serializers.ChoiceField(
        choices=User.Role.choices,
        read_only=True,
    )

# Meta class for the RegistrationSerializer

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'role')

        read_only_fields = ('id', 'role',)

    def validate_email(self, value):
        email = User.objects.normalize_email(value).strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Email is already in use.")

        return email

    def validate(self, attrs):
        candidate = User(
            email=attrs.get('email',""),
            first_name=attrs.get('first_name',""),
            last_name=attrs.get('last_name',""),
        )

        validate_password(
            attrs["password"],
            user=candidate
        )

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')

        return User.objects.create_user(
            password=password,
            **validated_data,    
        )

# Login serializer for authenticating users

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={'input_type': 'password'},
    )

    def validate(self, attrs):
        email = attrs['email'].strip().lower()
        password = attrs['password']

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
   )
        if user is None:
            raise serializers.ValidationError(
                "Cannot log in with provided credentials.",
            )

        attrs['email'] = email
        attrs['user'] = user
        return attrs
