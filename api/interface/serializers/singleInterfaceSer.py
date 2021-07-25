from api.models import  SingleInterfaceCase, ModuleTree
from rest_framework import serializers


class SingleInterfaceCaseSer(serializers.ModelSerializer):

    class Meta:
        model = SingleInterfaceCase
        fields = "__all__"


class SingleInterfaceCaseResultSer(serializers.ModelSerializer):
    """更新单一接口的结果"""

    class Meta:
        model = SingleInterfaceCase
        fields = ("result",)

class excludeResultSer(serializers.ModelSerializer):
    """返回的结果渲染的是编辑界面，不需要返回结果的值"""
    class Meta:
        model = SingleInterfaceCase
        exclude = ("result",)

class InterfaceSerachSer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()
    label = serializers.CharField(source='name')
    value = serializers.CharField(source='id')

    class Meta:
        model = ModuleTree
        fields = ("value",  "label", "children")

    def get_children(self, obj):
        queryset = obj.module_interface.all()
        data = [{"label": row.interfaceName, "value": row.id} for row in queryset]
        return data