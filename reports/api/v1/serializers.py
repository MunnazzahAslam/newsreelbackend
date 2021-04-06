from rest_framework import serializers

from reports.models import Report


class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Report
        fields = ('id', 'user', 'post', 'reply', 'review')
        read_only_fields = ('id', )
