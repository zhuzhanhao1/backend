from api.models import SqlCaseManage
from rest_framework import serializers


class SqlCaseManageListSer(serializers.ModelSerializer):
    class Meta:
        model = SqlCaseManage
        fields = "__all__"


class SqlCaseManageAddSer(serializers.ModelSerializer):
    class Meta:
        model = SqlCaseManage
        fields = ("parent", "ddlDmlType", "executeSql", "validationSql", "version", "caseName")


class UpdateEnabledSer(serializers.ModelSerializer):
    class Meta:
        model = SqlCaseManage
        fields = ("enabled",)


class UpdateSourceStock(serializers.ModelSerializer):
    class Meta:
        model = SqlCaseManage
        fields = ("sourceStock", "executeResult")


class UpdateTargetStock(serializers.ModelSerializer):
    class Meta:
        model = SqlCaseManage
        fields = ("targetStock", "validationResult")


class ClearResultSer(serializers.ModelSerializer):
    class Meta:
        model = SqlCaseManage
        fields = ("sourceStock", "targetStock", "validationResult", "executeResult")
