
from django.urls import path
from .views import LoginView, RegisterView

app_name = 'accounts'

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
]
