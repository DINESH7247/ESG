from django.urls import path

from .views import AuditLogView, RecordDetailView, RecordsView, UploadView

urlpatterns = [
    path("upload", UploadView.as_view()),
    path("records", RecordsView.as_view()),
    path("records/<str:pk>", RecordDetailView.as_view()),
    path("records/<str:pk>/review", RecordsView.as_view()),
    path("audit-logs/<str:record_id>", AuditLogView.as_view()),
]
