from api.models import ModuleTree, InterfaceMange
from rest_framework import serializers


class ModuleTreeSer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ModuleTree
        fields = ("id", "parent", "name", "pid", "children")

    def get_children(self, obj):
        queryset = obj.module_interface.all()
        data = [{"name": row.interfaceName, "id": row.id} for row in queryset]
        return data


class InterfaceMangeListSer(serializers.ModelSerializer):
    class Meta:
        model = InterfaceMange
        fields = "__all__"

class UpdateTreeNodeSer(serializers.ModelSerializer):
    class Meta:
        model = InterfaceMange
        fields = ("parent",)
