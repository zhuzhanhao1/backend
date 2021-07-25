import datetime
import json
import re
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from api.common.requestInterface import RequestInterface
from api.interface.rest.interfaceManage import InterfaceDebug
from api.models import SingleInterfaceCase, InterfaceMange
from api.interface.serializers.singleInterfaceSer import SingleInterfaceCaseSer, excludeResultSer, \
    SingleInterfaceCaseResultSer
from django_redis import get_redis_connection
import logging

logger = logging.getLogger('log')


class SingleInterfaceCaseList(APIView):

    def get(self, request, *args, **kwargs):
        """单接口用例列表"""
        parent = request.GET.get("id", "")
        caseId = request.GET.get("caseId", "")
        filterInputValue = request.GET.get("filterInputValue", "")
        if parent:
            objs = SingleInterfaceCase.objects.filter(parent=parent)
            if filterInputValue:
                objs = objs.filter(Q(url__contains=filterInputValue) | Q(interfaceName__contains=filterInputValue))
            # 点击接口没有用例则初始化一条
            if objs.count() == 0:
                # copy用例管理的用例到当前
                obj = InterfaceMange.objects.filter(id=parent).first()
                data = {
                    "parent": parent,
                    "interfaceName": obj.interfaceName,
                    "url": obj.url,
                    "method": obj.method,
                    "headers": obj.headers,
                    "params": obj.params,
                    "formDatas": obj.formDatas,
                    "bodyJson": obj.bodyJson,
                    "resultAsserts": obj.resultAsserts,
                    "bodyType": obj.bodyType
                }
                try:
                    serializer = SingleInterfaceCaseSer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response({"code": 1001, "data": "参数有误"})
                except Exception as e:
                    return Response({"code": 1001, "data": str(e)})
            serializer = SingleInterfaceCaseSer(objs, many=True)
            pageindex = request.GET.get('page', 1)  # 页数
            pagesize = request.GET.get("limit", 10)  # 每页显示数量
            pageInator = Paginator(serializer.data, pagesize)
            # 分页
            contacts = pageInator.page(pageindex)
            res = []
            for contact in contacts:
                res.append(contact)
            return Response(data={"code": 1000, "msg": "单接口用例列表", "count": len(serializer.data), "data": res})
        # 获取结果详情
        elif caseId:
            obj = SingleInterfaceCase.objects.filter(id=caseId)
            if not obj:
                return Response({"code": 1001, "data": "该id的接口用例不存在"})
            serializer = excludeResultSer(obj, many=True).data
            return Response({"code": 1000, "data": serializer[0]})

    def post(self, request, *args, **kwargs):
        """复制接口"""
        data = request.data
        id = data.get("id", "")
        parent = data.get("parent", "")
        # 通过id查找interfacemanage的接口
        obj = SingleInterfaceCase.objects.filter(id=id).first()
        data = {
            "parent": parent,
            "interfaceName": obj.interfaceName,
            "url": obj.url,
            "method": obj.method,
            "headers": obj.headers,
            "params": obj.params,
            "formDatas": obj.formDatas,
            "bodyJson": obj.bodyJson,
            "resultAsserts": obj.resultAsserts,
            "bodyType": obj.bodyType
        }
        try:
            serializer = SingleInterfaceCaseSer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"code": 1000, "data": "新建单接口成功"})
            else:
                return Response({"code": 1001, "data": "参数有误"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})

    def put(self, request, *args, **kwargs):
        """编辑接口用例"""
        data = request.data
        obj = SingleInterfaceCase.objects.filter(id=data['id']).first()
        serializer = excludeResultSer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 1000, "data": "编辑单接口用例成功"})
        else:
            return Response({"code": 1001, "data": "编辑单接口用例失败"})

    def delete(self, request, *args, **kwargs):
        """删除单接口"""
        id = request.GET.get("id", "")
        try:
            obj = SingleInterfaceCase.objects.filter(id=id)
            obj.delete()
            return Response({"code": 1000, "data": "删除单接口用例成功"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})


class PublicParams(APIView):

    def post(self, request, *args, **kwargs):
        """
            将公共参数的值存储到Redis
        """
        data = request.data
        # 超时时间、key、value
        timeout = int(data["outTime"])
        updateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data["updateTime"] = updateTime
        data["variableName"] = "${" + data["variableName"] + "}"

        key = "publicParams" + str(data.get("projectId", ""))
        data = json.dumps(data)
        # 建立Redis连接
        redisConnect = get_redis_connection('default')
        # 将key-value存入Redis-db1，set存储是字符串
        redisConnect.set(key, data)
        # 设置超时时间
        redisConnect.expire(key, timeout)
        return Response({"code": 1000, "data": "公共参数设置成功"})

    def get(self, request, *args, **kwargs):
        """
            获取Redis中公共参数的值
        """
        projectId = request.GET.get("projectId", "")
        key = "publicParams" + str(projectId)
        redisConnect = get_redis_connection('default')
        try:
            value = redisConnect.get(key)
            print("剩余时间", redisConnect.ttl(key))
            if value:
                # btyes -> str,字节转换为字符在转换为JSON对象
                value = json.loads(value.decode())
                value["variableName"] = value["variableName"][2:-1]
                value["ttl"] = redisConnect.ttl(key)
                return Response({"code": 1000, "data": value})
            else:
                return Response({"code": 1001, "data": "公共参数到期被移除，请重新创建"})
        except ConnectionError as e:
            return Response({"code": 1001, "data": "redis连接超时 %s" % e})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})


class RunSingleInterfaceCase(InterfaceDebug):
    """
        1.重写post
        2.集成InterfaceDebug
    """

    def getRedisPublicParams(self, projectId):
        """
            获取Redis中的公共参数（必须是本项目的）
        """
        redisConnect = get_redis_connection('default')
        try:
            key = "publicParams" + str(projectId)
            publicParamsValue = redisConnect.get(key)
            if publicParamsValue:
                value = json.loads(publicParamsValue.decode())
                paramsValue = value.get("paramsValue", "")
                variableName = value.get("variableName", "")
                return variableName, paramsValue
        except TimeoutError as e:
            logger.warning("TimeoutError：" + str(e))
        except ConnectionError as e:
            logger.warning("redis连接超时 %s" % e)
        return "", ""

    def headersReplacement(self, headers, projectId):
        """
            headers中存在Redis中存储的公共参数则需要替换
        """
        headersDict = {}
        # 查询Redis中是否存在当前模块的publicParams
        VarList = re.findall('\$\{\w+\}', json.dumps(headers))
        logger.info("headers中存在的变量:" + str(VarList))
        variableName, paramsValue = '', ''
        if len(VarList) > 0:
            variableName, paramsValue = self.getRedisPublicParams(projectId)
            logger.info("公共参数变量名称为：" + variableName)
            logger.info("公共参数变量对应的值为：" + paramsValue)
        for item in headers:
            headersDict[item["key"]] = item["value"]
            # 如果请求头中的value值与公共参数的变量值相同，则替换为公共参数的value值
            if item["value"] == variableName:
                headersDict[item["key"]] = paramsValue
        return headersDict

    def doAssert(self, resultAsserts, response_body, status_code):
        """
            遍历断言请求列表，依次执行断言，将断言结果加入结果集内
            返回断言结果集，断言结论
        """
        assertList = []
        assertConclusion = "成功"
        if resultAsserts != []:
            for item in resultAsserts:
                # 断言校验 ，校验方法
                assertResult = self.interfaceAssert(item, response_body, status_code)
                assertList.append(assertResult)
                if assertResult["assertRes"] == "失败":
                    assertConclusion = "失败"
        assertConclusion = "未断言" if assertList == [] else assertConclusion
        return assertList, assertConclusion

    def runCase(self, projectId, host, *args):
        """
            元祖顺序：headers,method，url，bodyJson，resultAsserts
        """
        headers = args[0][1]
        method = args[0][2]
        url = host + args[0][3]
        bodyJson = args[0][4]
        resultAsserts = args[0][5]
        # 转换headers中的公共参数值
        headers = self.headersReplacement(headers, projectId)

        logger.info("请求头信息：" + str(headers))
        # 执行请求
        response = RequestInterface(method, url, headers, bodyJson).main()
        # 响应异常返回post方法处理
        if type(response) == dict:
            return response
        response_headers, response_body, duration, status_code = response[0], response[1], response[2], response[3]
        # 执行断言
        assertList, assertConclusion = self.doAssert(resultAsserts, response_body, status_code)
        result = {
            "request": {
                "method": method,
                "url": url,
                "headers": headers,
                "body": bodyJson
            },
            "response": {
                "headers": json.loads(json.dumps(dict(response_headers))),
                "body": response_body
            },
            "assert": assertList,
            "conclusion": assertConclusion,
            "duration": duration,
            "status_code": status_code
        }
        return result

    def post(self, request, *args, **kwargs):
        """运行接口，保存结果"""
        data = request.data
        projectId = data.get("projectId", "")
        host = data.get("host", "")
        parent = data.get("parent", "")
        idList = data.get("idList", "")
        # 当前节点下的所有接口用例全部运行
        if parent:
            objs = SingleInterfaceCase.objects.filter(parent=parent).values_list("id", "headers", "method", "url",
                                                                                 "bodyJson", "resultAsserts")
        # 勾选的用例执行
        elif idList:
            objs = SingleInterfaceCase.objects.filter(id__in=idList).values_list("id", "headers", "method", "url",
                                                                                 "bodyJson", "resultAsserts")
        else:
            # 行内按钮执行，构造[()]对象
            id = data.get("id", "")
            headers = data.get("headers", "")
            method = data.get("method", "")
            url = data.get("url", "")
            bodyJson = data.get("bodyJson", "")
            resultAsserts = data.get("resultAsserts", "")
            objs = [(id, headers, method, url, bodyJson, resultAsserts)]
        # 循环用例集合
        res = {}
        for obj in objs:
            result = self.runCase(projectId, host, obj)
            # 如果异常存在，则返回，停止继续执行
            if result.get("code", ""):
                return Response(result)
            # 将运行结果持久化数据库
            obj = SingleInterfaceCase.objects.filter(id=obj[0]).first()
            serializer = SingleInterfaceCaseResultSer(obj, data={"result": result})
            if serializer.is_valid():
                serializer.save()
            res["result"] = result
        return Response({"code": 1000, "data": res, "message": "运行结束，双击行查看详情"})
