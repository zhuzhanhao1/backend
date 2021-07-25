from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from api.common.notification import EmailSender
from api.models import MailConfig
from api.systemManage.serializers.mailConfigSer import MailConfigListSer


class MailConfigList(APIView):

    def get(self, request, *args, **kwargs):
        """邮箱配置列表"""
        obj = MailConfig.objects.all()
        serializer = MailConfigListSer(obj, many=True)
        pageindex = request.GET.get('page', 1)  # 页数
        pagesize = request.GET.get("limit", 10)  # 每页显示数量
        pageInator = Paginator(serializer.data, pagesize)
        # 分页
        contacts = pageInator.page(pageindex)
        res = []
        for contact in contacts:
            res.append(contact)
        return Response(data={"code": 0, "msg": "邮箱配置列表", "count": len(serializer.data), "data": res})

    def put(self, request, *args, **kwargs):
        """编辑邮箱配置"""
        data = request.data
        obj = MailConfig.objects.filter(id=data['id']).first()
        serializer = MailConfigListSer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 1000, "data": "编辑邮箱配置成功"})
        else:
            return Response({"code": 1001, "data": "编辑邮箱配置失败"})

    def post(self, request, *args, **kwargs):
        """创建邮箱配置"""
        data = request.data
        print(data)
        try:
            serializer = MailConfigListSer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"code": 1000, "data": "新建邮箱配置成功"})
            else:
                return Response({"code": 1001, "data": "参数有误,请注意邮箱格式"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})

    def delete(self, request, *args, **kwargs):
        """删除邮箱配置"""
        id = request.GET.get("id", "")
        try:
            obj = MailConfig.objects.filter(id=id)
            obj.delete()
            return Response({"code": 1000, "data": "删除邮箱配置成功"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})

class MailTestSend(APIView):
    """
        邮件发送测试
    """

    def post(self, request, *args, **kwargs):
        data = request.data
        result = EmailSender(**data).sendMail("测试主题区域", "测试邮箱内容区域")
        return Response(result)