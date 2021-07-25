from api.models import ExecutePlan, InterfaceTestReport
from rest_framework import serializers


# .get_gender_display()
class ExecutePlanListSer(serializers.ModelSerializer):
    # 显示choices的值
    executeStatus = serializers.CharField(source="get_executeStatus_display")

    class Meta:
        model = ExecutePlan
        fields = "__all__"
        # fields = (
        # "parent", "id", "planName", "ploy", "describe", "notification", "startTime", "endTime", "sceneCaseIds",
        # "executeType", "executeStatus")

class ExecutePlanAddSer(serializers.ModelSerializer):

    class Meta:
        model = ExecutePlan
        exclude = ("executeStatus",)

class PlanNotificationSer(serializers.ModelSerializer):
    class Meta:
        model = ExecutePlan
        fields = ("id", "notification")


class PlanExecuteTypeSer(serializers.ModelSerializer):
    class Meta:
        model = ExecutePlan
        fields = ("id", "executeType")

class PlanExecuteStatusSer(serializers.ModelSerializer):
    class Meta:
        model = ExecutePlan
        fields = ("id", "executeStatus")

class InterfaceTestReportSer(serializers.ModelSerializer):
    class Meta:
        model = InterfaceTestReport
        fields = "__all__"
