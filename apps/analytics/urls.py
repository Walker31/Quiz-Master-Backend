from django.urls import path
from .views import AdminDashboardStatsView, LeaderboardView, StudentPerformanceView

urlpatterns = [
    path('dashboard-stats/', AdminDashboardStatsView.as_view(), name='admin-dashboard-stats'),
    path('leaderboard/<int:quiz_id>/', LeaderboardView.as_view(), name='leaderboard'),
    path('performance/', StudentPerformanceView.as_view(), name='student-performance'),
]
