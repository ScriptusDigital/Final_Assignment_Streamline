
from django.urls import path
from .views import CurrentUserView, LoginView, RegisterView

app_name = 'accounts'

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/me/", CurrentUserView.as_view(), name="me"),
]
