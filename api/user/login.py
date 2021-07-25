from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib import auth
from api.user.jwtAuth import getToken


class UserLogin(APIView):
    """用户登录"""
    # 取消校验登录
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        # Django自带user校验登录信息
        obj = auth.authenticate(username=username, password=password)
        if not obj:
            return Response({"code": 1001, "data": "账号或密码错误", "message": "用户登录失败"})
        token = getToken({"user_id": obj.id, "username": username})
        return Response({"code": 1000, "data": {"token": token, "username": username}, "message": "用户登录成功"})


class UserLoginStatus(APIView):
    """
        查看用户登录状态
        用户权限
    """

    def get(self, request, *args, **kwargs):
        # token = request.query_params.get("token")
        return Response({"code": 1000, "data": {"name": "admin", "avatar": ""}})


class UserLogout(APIView):
    """用户登出"""

    def post(self, request, *args, **kwargs):
        return Response({"code": 1000, "data": "登出成功！"})
