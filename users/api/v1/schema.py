from rest_framework import serializers


class AuthSchema(serializers.Serializer):
    id = serializers.IntegerField()
    refresh = serializers.CharField()
    access = serializers.CharField()
