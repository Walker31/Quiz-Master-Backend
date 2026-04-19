"""URL configuration for quizMaster project."""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── API v1 (new architecture) ─────────────────────────────────────────────
    path('api/v1/', include('apps.accounts.urls')),
    path('api/v1/content/', include('apps.content.urls')),

    # ── Legacy API (kept until frontend is migrated) ──────────────────────────
    path('api/auth/', include('users.urls')),
    path('api/quizzes/', include('quizzes.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
