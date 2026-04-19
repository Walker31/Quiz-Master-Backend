from django.urls import path

from .views import MeView, SignInView, SignUpView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='user-signup'),
    path('signin/', SignInView.as_view(), name='user-signin'),
    path('me/', MeView.as_view(), name='user-me'),
]
