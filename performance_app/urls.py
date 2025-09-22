# performance_app/urls.py
from django.urls import path
from .views import (
    LoginView, LogoutView, ReviewCreateView, ReviewSubmitView, ReviewDetailView,
    EmployeeReviewsView, PerformanceTrendView, EmployeeGoalsView, DepartmentSummaryView,
    BulkImportReviewsView
)

urlpatterns = [
    path('auth/login', LoginView.as_view(), name='login'),
    path('auth/logout', LogoutView.as_view(), name='logout'),
    path('reviews', ReviewCreateView.as_view(), name='create-review'),
    path('reviews/bulk-import', BulkImportReviewsView.as_view(), name='bulk-import'),
    path('reviews/<int:pk>', ReviewDetailView.as_view(), name='review-detail'),
    path('reviews/<int:pk>/submit', ReviewSubmitView.as_view(), name='review-submit'),
    path('employees/<int:id>/reviews', EmployeeReviewsView.as_view(), name='employee-reviews'),
    path('employees/<int:id>/performance-trend', PerformanceTrendView.as_view(), name='performance-trend'),
    path('employees/<int:id>/goals', EmployeeGoalsView.as_view(), name='employee-goals'),
    path('departments/<str:dept>/summary', DepartmentSummaryView.as_view(), name='dept-summary'),
]
