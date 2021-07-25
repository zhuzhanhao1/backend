from api.models import DataStructureManage
from rest_framework import serializers

class DataStructureManageListSer(serializers.ModelSerializer):

    class Meta:
        model = DataStructureManage
        fields = "__all__"

class DataStructureManageAddSer(serializers.ModelSerializer):

    class Meta:
        model = DataStructureManage
        fields = ("dbTypeName","structureName","stockAddType")

class UpdateDdlCount(serializers.ModelSerializer):

    class Meta:
        model = DataStructureManage
        fields = ("ddlCount",)

class UpdateDmlCount(serializers.ModelSerializer):

    class Meta:
        model = DataStructureManage
        fields = ("dmlCount",)