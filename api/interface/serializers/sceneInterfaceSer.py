from api.models import SceneCase, SceneInterface
from rest_framework import serializers


class SceneCaseSer(serializers.ModelSerializer):
    class Meta:
        model = SceneCase
        fields = "__all__"


class PlanModuleSceneCaseSer(serializers.ModelSerializer):
    label = serializers.CharField(source='name')
    value = serializers.CharField(source='id')

    class Meta:
        model = SceneCase
        fields = ("label", "value")


class SceneInterfaceSer(serializers.ModelSerializer):
    class Meta:
        model = SceneInterface
        fields = "__all__"


class SceneSortNumberSer(serializers.ModelSerializer):
    class Meta:
        model = SceneInterface
        fields = ("sortNumber",)


class SceneInterfaceResultSer(serializers.ModelSerializer):
    """更新单一接口的结果"""

    class Meta:
        model = SceneInterface
        fields = ("result",)


class excludeResultSer(serializers.ModelSerializer):
    """返回的结果渲染的是编辑界面，不需要返回结果的值"""

    class Meta:
        model = SceneInterface
        exclude = ("result",)
