from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import DataStructureManage
from api.db.serializers.dataStructureManageSer import DataStructureManageListSer, DataStructureManageAddSer


class DataStructureManageList(APIView):

    def get(self, request, *args, **kwargs):
        """数据源列表"""
        dbTypeName = request.GET.get("dbTypeName", "")
        stockAddType = request.GET.get("stockAddType", "")
        obj = DataStructureManage.objects.filter(Q(dbTypeName=dbTypeName) & Q(stockAddType=stockAddType))
        serializer = DataStructureManageListSer(obj, many=True)
        pageindex = request.GET.get('page', 1)  # 页数
        pagesize = request.GET.get("limit", 10)  # 每页显示数量
        pageInator = Paginator(serializer.data, pagesize)
        # 分页
        contacts = pageInator.page(pageindex)
        res = []
        for contact in contacts:
            res.append(contact)
        return Response(data={"code": 0, "msg": "数据结构列表", "count": len(serializer.data), "data": res})

    def put(self, request, *args, **kwargs):
        """编辑数据源"""
        data = request.data
        obj = DataStructureManage.objects.filter(id=data['id']).first()
        serializer = DataStructureManageAddSer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 1000, "data": "编辑数据结构成功"})
        else:
            return Response({"code": 1001, "data": "编辑数据结构失败"})

    def post(self, request, *args, **kwargs):
        """创建数据源"""
        data = request.data
        try:
            serializer = DataStructureManageAddSer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"code": 1000, "data": "新建数据结构成功"})
            else:
                return Response({"code": 1001, "data": "参数有误"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})

    def delete(self, request, *args, **kwargs):
        """删除数据源"""
        id = request.GET.get("id", "")
        try:
            obj = DataStructureManage.objects.filter(id=id)
            obj.delete()
            return Response({"code": 1000, "data": "删除数据结构成功"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})
