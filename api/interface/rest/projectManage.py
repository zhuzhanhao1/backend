from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import ProjectManage
from api.interface.serializers.projentManageSer import ProjectManageListSer


class ProjectManageList(APIView):

    def get(self, request, *args, **kwargs):
        """项目列表"""
        obj = ProjectManage.objects.filter()
        serializer = ProjectManageListSer(obj, many=True)
        pageindex = request.GET.get('page', 1)  # 页数
        pagesize = request.GET.get("limit", 999)  # 每页显示数量
        pageInator = Paginator(serializer.data, pagesize)
        # 分页
        contacts = pageInator.page(pageindex)
        res = []
        for contact in contacts:
            res.append(contact)
        return Response(data={"code": 0, "msg": "项目列表", "count": len(serializer.data), "data": res})

    def put(self, request, *args, **kwargs):
        """编辑项目"""
        data = request.data
        obj = ProjectManage.objects.filter(id=data['id']).first()
        serializer = ProjectManageListSer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 1000, "data": "编辑项目成功"})
        else:
            return Response({"code": 1001, "data": "编辑项目失败"})

    def post(self, request, *args, **kwargs):
        """创建项目"""
        data = request.data
        print(data)
        # 数据校验
        if ProjectManage.objects.filter(projectName=data['projectName']):
            return Response({"code": 1001, "data": "项目已存在"})
        try:
            serializer = ProjectManageListSer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"code": 1000, "data": "新建项目成功"})
            else:
                return Response({"code": 1001, "data": "参数有误"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})

    def delete(self, request, *args, **kwargs):
        """删除项目"""
        id = request.GET.get("id", "")
        try:
            obj = ProjectManage.objects.filter(id=id)
            obj.delete()
            return Response({"code": 1000, "data": "删除项目成功"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})
