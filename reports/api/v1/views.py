from rest_framework.viewsets import generics

from reports.models import Report
from .serializers import ReportSerializer


class ReportsView(generics.CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def perform_create(self, serializer):
        reported_by = self.request.user
        serializer.save(reported_by=reported_by)
