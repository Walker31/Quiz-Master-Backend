from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, LoginView, LogoutView, MeView, BatchViewSet, AdminUserViewSet

router = DefaultRouter()
router.register(r'batches', BatchViewSet, basename='batch')
router.register(r'users', AdminUserViewSet, basename='admin-user')

urlpatterns = [
    # Auth endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/me/', MeView.as_view(), name='me'),
    # Admin management
    path('admin/', include(router.urls)),
]
