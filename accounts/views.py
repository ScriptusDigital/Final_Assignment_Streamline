from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login as django_login


from .serializers import LoginSerializer, LoginSerializer, RegistrationSerializer, UserSerializer, UserSerializer

class RegisterView(APIView):
    """Create a new Viewer user account."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

""" Login view for user authentication. """
class LoginView(APIView):
    """Authenticate a user and return an authentication token."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, 
        context={'request': request})

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        django_login(request, user)

        return Response(
                UserSerializer(user).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )