from api.models import ProjectManage
from rest_framework import serializers


class ProjectManageListSer(serializers.ModelSerializer):
    class Meta:
        model = ProjectManage
        fields = "__all__"
