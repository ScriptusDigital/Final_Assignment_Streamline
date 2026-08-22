from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import login as django_login, logout as django_logout

from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect


from .serializers import LoginSerializer, LoginSerializer, RegistrationSerializer, UserSerializer, UserSerializer

""" csrf_protect decorator ensures that the view is protected against Cross-Site Request Forgery (CSRF) attacks."""
@method_decorator(ensure_csrf_cookie, name='dispatch')
class CsrfView(APIView):
    """View to provide a CSRF token."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        """Return a CSRF token in the response."""
        get_token(request)
        return Response({"detail": "CSRF token provided."}, status=status.HTTP_200_OK)

@method_decorator(csrf_protect, name='dispatch')

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
            django_login(request, user)

            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

""" login view and csrf protect """
@method_decorator(csrf_protect, name='dispatch')


class LoginView(APIView):
    """Authenticate a user and return an authentication token."""
    authentication_classes = [SessionAuthentication]
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

     

class CurrentUserView(APIView):
    """Retrieve the currently authenticated user."""
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
       return Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        django_logout(request)

        return Response(
            {"detail": "Logged out."},
            status=status.HTTP_200_OK
        )


