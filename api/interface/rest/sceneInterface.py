import json
import re
import jsonpath
from django.core.paginator import Paginator
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from api.common.requestInterface import RequestInterface
from django.db.models import Max, Q
from api.interface.rest.singleInterface import RunSingleInterfaceCase
from api.models import SceneCase, SceneInterface, InterfaceMange
from api.interface.serializers.sceneInterfaceSer import SceneCaseSer, SceneInterfaceSer, excludeResultSer, \
    SceneInterfaceResultSer, SceneSortNumberSer, PlanModuleSceneCaseSer
from django_redis import get_redis_connection
import logging
import uuid

logger = logging.getLogger('log')


class SceneCaseTree(APIView):

    def get(self, request, *args, **kwargs):
        """
            1.项目不存在返回[]
            2.项目存在返回项目下所有的节点
        """
        parent = request.GET.get("id", "")
        planCase = request.GET.get("planCase", "")
        if not parent:
            return Response([])
        elif planCase:
            obj = SceneCase.objects.filter(parent=parent)
            data = PlanModuleSceneCaseSer(obj, many=True).data
        else:
            obj = SceneCase.objects.filter(parent=parent)
            data = SceneCaseSer(obj, many=True).data
        return Response(data)

    def post(self, request, *args, **kwargs):
        """
            创建场景用例
        """
        data = request.data
        if SceneCase.objects.filter(name=data['name']):
            return Response({"code": 1001, "data": "场景用例已存在"})
        try:
            serializer = SceneCaseSer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"code": 1000, "data": "新建场景用例成功"})
            else:
                return Response({"code": 1001, "data": "参数有误"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})

    def put(self, request, *args, **kwargs):
        """
            编辑场景接口
        """
        data = request.data
        obj = SceneCase.objects.filter(id=data['id']).first()
        serializer = SceneCaseSer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 1000, "data": "编辑场景接口成功"})
        else:
            return Response({"code": 1001, "data": "编辑场景接口失败"})

    def delete(self, request, *args, **kwargs):
        """
            删除场景用例
        """
        id = request.GET.get("id", "")
        try:
            obj = SceneCase.objects.filter(id=id)
            obj.delete()
            return Response({"code": 1000, "data": "删除场景接口成功"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})


class SceneInterfaceList(APIView):

    def get(self, request, *args, **kwargs):
        """
            场景接口用例列表
        """
        parent = request.GET.get("id", "")
        caseId = request.GET.get("caseId", "")
        filterInputValue = request.GET.get("filterInputValue", "")
        if parent:
            obj = SceneInterface.objects.filter(parent=parent).order_by("sortNumber")
            if filterInputValue:
                obj = obj.filter(Q(url__contains=filterInputValue) | Q(interfaceName__contains=filterInputValue))
            serializer = SceneInterfaceSer(obj, many=True)
            pageindex = request.GET.get('page', 1)  # 页数
            pagesize = request.GET.get("limit", 10)  # 每页显示数量
            pageInator = Paginator(serializer.data, pagesize)
            # 分页
            contacts = pageInator.page(pageindex)
            res = []
            for contact in contacts:
                res.append(contact)
            return Response(data={"code": 1000, "msg": "场景接口用例列表", "count": len(serializer.data), "data": res})
        elif caseId:
            obj = SceneInterface.objects.filter(id=caseId)
            if not obj:
                return Response({"code": 1001, "data": "该id的接口用例不存在"})
            serializer = excludeResultSer(obj, many=True).data
            return Response({"code": 1000, "data": serializer[0]})

    def post(self, request, *args, **kwargs):
        """
            创建场景接口
        """
        data = request.data
        id = data.get("id", "")
        parent = data.get("parent", "")
        # 通过id查找interfacemanage的接口
        obj = InterfaceMange.objects.filter(id=id).first()
        if SceneInterface.objects.filter(parent=parent).exists():
            sortNumber = SceneInterface.objects.filter(parent=parent).aggregate(Max('sortNumber'))[
                             "sortNumber__max"] + 1
        else:
            sortNumber = 0
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
            "bodyType": obj.bodyType,
            "jsonExtract": [],
            "sortNumber": sortNumber,
            "frontMap": []
        }
        try:
            serializer = SceneInterfaceSer(data=data)
            if serializer.is_valid():
                serializer.save()
                data = {
                    "message": "新建场景接口成功",
                    "id": SceneInterface.objects.filter().last().id
                }
                return Response({"code": 1000, "data": data})
            else:
                return Response({"code": 1001, "data": "参数有误"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})

    def put(self, request, *args, **kwargs):
        """
            编辑接口用例
        """
        data = request.data
        obj = SceneInterface.objects.filter(id=data['id']).first()
        serializer = SceneInterfaceSer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 1000, "data": "编辑场景接口用例成功"})
        else:
            return Response({"code": 1001, "data": "编辑场景接口用例失败"})

    def delete(self, request, *args, **kwargs):
        """
            删除场景接口
        """
        id = request.GET.get("id", "")
        try:
            obj = SceneInterface.objects.filter(id=id)
            obj.delete()
            return Response({"code": 1000, "data": "删除场景接口用例成功"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})


class SceneInterfaceSort(APIView):

    def post(self, request, *args, **kwargs):
        # 前端传过来的是排序后的[num1,num2]
        data = request.data
        for index, id in enumerate(data["newList"]):
            obj = SceneInterface.objects.filter(id=id).first()
            serializer = SceneSortNumberSer(obj, data={"sortNumber": index})
            if serializer.is_valid():
                serializer.save()
            else:
                return Response({"code": 1001, "data": "排序失败"})
        return Response({"code": 1000, "data": "排序成功"})


class RunSceneInterface(RunSingleInterfaceCase):
    """
        1.重写post
        2.继承RunSingleInterface中的方法
        3.增加参数提取方法
        3.增加局部变量替换方法
    """

    def strReplacement(self, prefix, value, frontMap={}, urlMap=False):
        """
            请求参数中存在${xxx}字样的内容，替换为Redis中存储的参数值
        """
        # 正则查询包含'${xxx}',返回["","",.....]
        VarList = re.findall('\$\{\w+\}', value)
        # 去重，当长度大于0，则说明请求中有需要替换的内容
        VarList = list(set(VarList))
        if len(VarList) > 0:
            for var in VarList:
                redisConnect = get_redis_connection('default')
                # key = 项目id + 场景id + 变量名保证唯一性
                redisValue = redisConnect.get(prefix + var[2:-1])
                if redisValue:
                    replaceValue = json.loads(redisValue.decode()).get("value", "")
                    # 当依赖值为字符串可以选用str替换的下面两种方法
                    if type(replaceValue) == str:
                        # 1.py字符串替换value
                        # value = value.replace(var, replaceValue)
                        # 2.py-re正则字符串替换
                        value = json.dumps(value) if type(value) != str else value
                        value = re.sub('(\$\{' + var[2:-1] + '\})', replaceValue, value)
                    # 当依赖值为int且需要修改的URL时
                    elif type(replaceValue) == int and urlMap:
                        value = json.dumps(value) if type(value) != str else value
                        value = re.sub('(\$\{' + var[2:-1] + '\})', str(replaceValue), value)
                    # body映射替换
                    else:
                        # 替换映射 ${xxx} --> [0][xxx]
                        # 如果映射内容存在
                        if len(frontMap) > 0:
                            # 将列表包含对象的方式改为dict
                            if type(frontMap) == list:
                                frontMap = {item["key"]: item["value"] for item in frontMap}
                            # 如果请求中的变量在映射dict中，则需要转换
                            if var in frontMap:
                                # 校验前置value的正确性
                                if not frontMap[var].startswith("[") or not frontMap[var].endswith("]"):
                                    return {"code": 1001, "data": "前置映射的值不合法"}
                                # dict修改需要先转为dict类型
                                value = json.loads(value) if type(value) == str else value
                                try:
                                    # 构造赋值表达式
                                    execStr = "value" + frontMap[var] + "= %s" % replaceValue
                                    # 执行字符串表达式
                                    exec(execStr)
                                except Exception as e:
                                    return {"code": 1001, "data": "前置映射的值替换失败，失败原因：%s" % e}
                            else:
                                return {"code": 1001, "data": "请求中的变量%s不在前置映射中存在" % var}
                else:
                    return {"code": 1001, "data": "%s在redis缓存中未找到，请查看前置接口是否已经提取成功" % var}
        return value

    def extractReplacement(self, projectId, *args):
        """
            1.查询url和bodyJson中是否存在局部变量
            2.replace将局部变量替换为JSON提取后的值
        """
        # 正则查询以及字符串替换的前提都是处理字符串，将内容转换为JSON字符串
        url = args[0][3]
        sceneId = args[0][6]
        frontMap = args[0][8]
        # body是json对象转为json字符串
        bodyJson = json.dumps(args[0][4])
        # key前缀
        prefix = str(projectId) + '_' + str(sceneId) + '_'
        # 替换内容返回请求参数需要的数据格式
        url = self.strReplacement(prefix, url, urlMap=True)
        logger.info("url信息：" + str(url))
        if type(url) == dict:
            return url
        bodyJson = self.strReplacement(prefix, bodyJson, frontMap)
        logger.info("body信息：" + str(bodyJson))
        if type(bodyJson) == dict and bodyJson.get("code", "") == 1001:
            return bodyJson
        # 返回元祖对象
        return (args[0][0], args[0][1], args[0][2], url, bodyJson, args[0][5], args[0][6], args[0][7], args[0][8])

    def storageExtractResult(self, jsonExtracts, response_body, projectId, parent):
        """
            参数提取支持JSONPATH、正则提取
            返回接口返回结果内满足参数提取的内容
        """
        jsonExtractResult = []
        if jsonExtracts != []:
            for jsonExtract in jsonExtracts:
                # 构造提取结果集对象
                dic = {
                    "extractResult": "成功",
                    "expression": jsonExtract["expression"],
                    "extractValueType": "<class 'str'>"
                }
                # JSONPATH提取
                if jsonExtract["type"] == "JSONPATH":
                    dic["type"] = "JSONPATH"
                    value = jsonpath.jsonpath(response_body, jsonExtract["expression"])
                    # 提取内容提取失败
                    if not value:
                        dic["extractResult"] = "失败"
                        dic["extractValue"] = "表达式：" + jsonExtract["expression"] + "提取错误"
                    else:
                        # key值格式：项目id_场景id_提取变量名
                        key = str(projectId) + '_' + str(parent) + '_' + jsonExtract["variableName"]
                        redisConnect = get_redis_connection('default')
                        # JSONPATH提取成功返回的是[].需提取索引为0的项
                        redisValue = {"value": value[0]}
                        # 存储的为JSON的字符串
                        redisConnect.set(key, json.dumps(redisValue))
                        dic["extractValue"] = value[0]
                        dic["extractValueType"] = str(type(value[0]))
                        # 设置局部变量的存活时间为1小时
                        redisConnect.expire(key, 3600)
                if jsonExtract["type"] == "正则":
                    pass
                jsonExtractResult.append(dic)
        return jsonExtractResult

    def runCase(self, projectId, host, *args):
        """
            元祖顺序：headers,method，url，bodyJson，resultAsserts, parent, jsonExtracts
        """
        headers = args[0][1]
        method = args[0][2]
        url = host + args[0][3]
        bodyJson = args[0][4]
        resultAsserts = args[0][5]
        jsonExtracts = args[0][7]
        parent = args[0][6]
        # 转换headers中的公共参数值
        headers = self.headersReplacement(headers, projectId)
        logger.info("请求头信息：" + str(headers))
        # 执行请求
        response = RequestInterface(method, url, headers, bodyJson).main()
        # 响应异常返回post方法处理
        if type(response) == dict:
            return response
        response_headers, response_body, duration, status_code, body = response[0], response[1], response[2], response[
            3], response[4]
        # 提取参数存储Redis
        jsonExtractResult = self.storageExtractResult(jsonExtracts, response_body, projectId, parent)
        # 执行断言
        assertList, assertConclusion = self.doAssert(resultAsserts, response_body, status_code)
        # 构造返回结果
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
            "status_code": status_code,
            "extract": jsonExtractResult
        }
        return result

    def post(self, request, *args, **kwargs):
        """运行接口，保存结果"""
        data = request.data
        projectId = data.get("projectId", "")
        host = data.get("host", "")
        parentId = data.get("parentId", "")
        idList = data.get("idList", "")
        # 当前节点下的所有接口用例全部运行
        if parentId:
            objs = SceneInterface.objects.filter(parent=parentId).values_list(
                "id", "headers", "method", "url", "bodyJson", "resultAsserts", "parent", "jsonExtract",
                "frontMap").order_by("sortNumber")
        # 勾选的用例执行
        elif idList:
            objs = SceneInterface.objects.filter(id__in=idList).values_list(
                "id", "headers", "method", "url", "bodyJson", "resultAsserts", "parent", "jsonExtract",
                "frontMap").order_by("sortNumber")
        else:
            # 行内按钮执行，构造[()]对象
            parent = data.get("parent", "")
            id = data.get("id", "")
            headers = data.get("headers", "")
            method = data.get("method", "")
            url = data.get("url", "")
            bodyJson = data.get("bodyJson", "")
            resultAsserts = data.get("resultAsserts", "")
            jsonExtract = data.get("jsonExtract", "")
            frontMap = data.get("frontMap", "")
            objs = [(id, headers, method, url, bodyJson, resultAsserts, parent, jsonExtract, frontMap)]
        res = {}
        for obj in objs:
            # 前置结果取值替换
            newObj = self.extractReplacement(projectId, obj)
            if type(newObj) == dict:
                logger.warning("前置结果取值替换出错")
                return Response(newObj)
            result = self.runCase(projectId, host, newObj)
            # 如果异常存在，则返回，停止继续执行
            if result.get("code", ""):
                logger.warning("接口执行异常")
                return Response(result)
            # 将运行结果持久化数据库
            sceneObj = SceneInterface.objects.filter(id=obj[0]).first()
            serializer = SceneInterfaceResultSer(sceneObj, data={"result": result})
            if serializer.is_valid():
                serializer.save()
            res["result"] = result
            logger.info(str(obj[0]) + '*' * 100)
        return Response({"code": 1000, "message": "运行结束，双击行查看详情", "data": res})


class LocalParams(APIView):
    def get(self, request, *args, **kwargs):
        """
            获取Redis中公共参数的值
        """
        projectId = request.GET.get("projectId", "")
        sceneId = request.GET.get("sceneId", "")
        prefix = str(projectId) + '_' + str(sceneId) + '_'
        try:
            redisConnect = get_redis_connection('default')
            keyLists = redisConnect.keys(prefix + '*')
            data = []
            for key in keyLists:
                if key:
                    dic = {}
                    key = key.decode()  # 字节转为字符串
                    value = redisConnect.get(key)
                    dic["key"] = key
                    value = json.loads(value.decode())["value"]
                    value = json.dumps(value) if type(value) != str else value
                    dic["value"] = value
                    data.append(dic)
            pageindex = request.GET.get('page', 1)  # 页数
            pagesize = request.GET.get("limit", 10)  # 每页显示数量
            pageInator = Paginator(data, pagesize)
            # 分页
            contacts = pageInator.page(pageindex)
            res = []
            for contact in contacts:
                res.append(contact)
            return Response(data={"code": 1000, "count": len(keyLists), "data": res})
        except ConnectionError as e:
            return Response({"code": 1001, "data": "redis连接超时 %s" % e})
        except Exception as e:
            return Response({"code": 1001, "data": "获取局部参数失败 %s" % e})


class SceneInterfaceImport(APIView):

    def post(self, request, *args, **kwargs):
        url = request.META.get("PATH_INFO", "")
        f = request.data.get('file')
        if url:
            parent = url.split("/")[-1]
            host = SceneCase.objects.filter(id=parent).first().parent.host
        else:
            return JsonResponse({"code": 1001, "data": "项目ID不存在"})
        if f.name.split('.')[-1] != 'json':
            return JsonResponse({"code": 1001, "data": "导入的文件必须是.json文件"})
        fileDcit = f.read().decode("utf-8")
        res = self.handleJsonData(fileDcit, parent, host)
        return JsonResponse(res)

    def handleJsonData(self, fileDcit, parent, host):
        res = {"code": 1000, "data": "导入成功"}
        dic = {
            "parent": parent,
            "formDatas": [],
            "resultAsserts": [],
            "bodyType": 'raw',
            "jsonExtract": [],
            "frontMap": [],
        }
        allDicts = json.loads(fileDcit)
        for oneDict in allDicts.values():  # 只有一个层级
            for one in oneDict.values():  # 循环次数代表有多少条数据
                # 域名必须和当前项目域名相同，不相同则导入失败
                if host not in one["url"]:
                    return {"code": 1001, "data": "导入数据有误,域名必须和当前项目域名相同"}
                dic["url"] = "/"+"/".join(one["url"].split("/")[3::])
                dic["method"] = one["method"]
                dic["interfaceName"] = str(uuid.uuid4())
                dic["headers"] = self.dicKeyReplace(one["headers"])
                dic["bodyJson"] = json.loads(one.get("body", "")[0]) if one.get("body", "") else {}
                dic["sortNumber"] = self.sortNumber(parent)
                dic["params"] = self.urlToParams(one["url"])
                # 持久化数据
                res = self.save(dic, res)
        return res

    def dicKeyReplace(self, value):
        try:
            for val in value:
                val["key"] = val.pop("name")
        except Exception as e:
            return value
        return value

    def sortNumber(self, parent):
        if SceneInterface.objects.filter(parent=parent).exists():
            sortNumber = SceneInterface.objects.filter(parent=parent).aggregate(Max('sortNumber'))[
                             "sortNumber__max"] + 1
        else:
            sortNumber = 0
        return sortNumber

    def urlToParams(self, url):
        data = []
        urlList = url.split("?")
        if len(urlList) > 1:
            paramsList = urlList[1].split("&")
            if len(paramsList) > 0:
                for params in paramsList:
                    dic = {}
                    dic["key"] = params.split("=")[0]
                    dic["value"] = params.split("=")[1]
                    data.append(dic)
        return data

    def save(self, data, res):
        try:
            serializer = SceneInterfaceSer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                res = {"code": 1001, "data": "导入数据有误,保持数据库失败"}
        except Exception as e:
            res = {"code": 1001, "data": "序列化失败，失败原因：%s" % e}
        return res
