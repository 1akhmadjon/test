from django.urls import path

from main.views import RegisterView, LoginView, Profile

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('register', RegisterView.as_view(), name='register'),
    path('profile', Profile.as_view(), name='profile')
]