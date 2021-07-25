from api.models import DataSourceConfig
from rest_framework import serializers

class DataSourceConfigListSer(serializers.ModelSerializer):

    class Meta:
        model = DataSourceConfig
        fields = "__all__"
