from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'role')

        read_only_fields = ('id', 'role',)

    def validate(self, value):
        email = User.objects.normalize_email(value).strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({"email": "Email is already in use."})

        return email

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user