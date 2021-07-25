import jsonpath
from rest_framework.views import APIView
from rest_framework.response import Response
from api.common.requestInterface import RequestInterface
from api.interface.serializers.singleInterfaceSer import InterfaceSerachSer
from api.models import ModuleTree, InterfaceMange
from api.interface.serializers.interfaceManageSer import ModuleTreeSer, InterfaceMangeListSer, UpdateTreeNodeSer


class ModuleCaseTree(APIView):

    def get(self, request, *args, **kwargs):
        """模块列表"""
        parent = request.GET.get("id", "")
        if not parent:
            return Response([])
        obj = ModuleTree.objects.filter(parent=parent)
        data = ModuleTreeSer(obj, many=True).data
        return Response(data)

    def put(self, request, *args, **kwargs):
        """编辑模块"""
        data = request.data
        obj = ModuleTree.objects.filter(id=data['id']).first()
        serializer = ModuleTreeSer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 1000, "data": "编辑模块成功"})
        else:
            return Response({"code": 1001, "data": "编辑模块失败"})

    def post(self, request, *args, **kwargs):
        """创建模块"""
        data = request.data
        if ModuleTree.objects.filter(name=data['name']):
            return Response({"code": 1001, "data": "模块已存在"})
        try:
            serializer = ModuleTreeSer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"code": 1000, "data": "新建模块成功"})
            else:
                return Response({"code": 1001, "data": "参数有误"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})

    def delete(self, request, *args, **kwargs):
        """删除模块"""
        id = request.GET.get("id", "")
        try:
            obj = ModuleTree.objects.filter(id=id)
            obj.delete()
            return Response({"code": 1000, "data": "删除模块成功"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})


class InterfaceManageList(APIView):

    def post(self, request, *args, **kwargs):
        """新建接口"""
        data = request.data
        if InterfaceMange.objects.filter(interfaceName=data['interfaceName']):
            return Response({"code": 1001, "data": "接口已存在"})
        try:
            serializer = InterfaceMangeListSer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"code": 1000, "data": "新建接口成功"})
            else:
                return Response({"code": 1001, "data": "参数有误"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})

    def put(self, request, *args, **kwargs):
        """编辑接口"""
        data = request.data
        obj = InterfaceMange.objects.filter(id=data['id']).first()
        if len(data) == 2:
            parent = InterfaceMange.objects.filter(id=data['nodeId']).first().parent.id
            data = {
                "parent": parent
            }
            serializer = UpdateTreeNodeSer(obj, data=data)
        else:
            serializer = InterfaceMangeListSer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 1000, "data": "编辑接口成功"})
        else:
            return Response({"code": 1001, "data": "编辑接口失败"})

    def get(self, request, *args, **kwargs):
        """获取接口详情"""
        id = request.GET.get("id")
        obj = InterfaceMange.objects.filter(id=id)
        data = InterfaceMangeListSer(obj, many=True).data
        return Response(data[0])

    def delete(self, request, *args, **kwargs):
        """删除接口"""
        id = request.GET.get("id", "")
        try:
            obj = InterfaceMange.objects.filter(id=id)
            obj.delete()
            return Response({"code": 1000, "data": "删除接口成功"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})


class InterfaceDebug(APIView):

    def conversionExpectValue(self, expectType, expectValue):
        if expectType == "数值":
            expectValue = int(expectValue)
        elif expectType == "布尔值":
            expectValue = bool(expectValue)
        elif expectType == "对象":
            expectValue = eval(expectValue)
        return expectValue

    def assertResult(self, expectRelation, expectValue, res, dic):
        assertRes = ""
        if expectRelation == "等于":
            assertRes = res == expectValue
        elif expectRelation == "不等于":
            assertRes = res != expectValue
        elif expectRelation == "包含":
            assertRes = res in expectValue
        elif expectRelation == "不包含":
            assertRes = res not in expectValue
        elif expectRelation == "大于":
            assertRes = res > expectValue
        elif expectRelation == "大于等于":
            assertRes = res >= expectValue
        elif expectRelation == "小于":
            assertRes = res < expectValue
        elif expectRelation == "小于等于":
            assertRes = res <= expectValue
        assertRes = "成功" if assertRes else "失败"
        dic["assertRes"] = assertRes
        dic["extractValue"] = res
        return dic

    def interfaceAssert(self, obj, result, status_code):
        """断言"""
        extractType = obj["extractType"]
        extractExpress = obj["extractExpress"].strip()
        expectRelation = obj["expectRelation"]
        expectType = obj["expectType"]
        expectValue = obj["expectValue"]
        dic = {
            "assertRes": "失败",
            "extractValue": "",
            "expectRelation": expectRelation,
            "expectValue": expectValue,
            "extractExpress": extractExpress,
            "extractType": extractType
        }
        # jsonpath断言
        if extractType == "JSONPATH":
            if not all([value for key, value in obj.items()]):
                dic["extractValue"] = "断言中有参数不全，请检查！"
                return dic
            try:
                res = jsonpath.jsonpath(result, extractExpress)
                if res == False:
                    dic["extractValue"] = "JSONPATH提取表达式错误"
                    return dic
                expectValue = self.conversionExpectValue(expectType, expectValue)
                # 断言结果
                return self.assertResult(expectRelation, expectValue, res[0], dic)
            except Exception as e:
                dic["extractValue"] = str(e)
                return dic

        # 状态码断言
        elif extractType == "响应码":
            if expectRelation == "等于":
                if int(expectValue) == status_code:
                    dic["assertRes"] = "成功"
            elif expectRelation == "不等于":
                if int(expectValue) != status_code:
                    dic["assertRes"] = "成功"
            dic["extractValue"] = status_code
            return dic

        # 正则断言
        else:
            pass

    def post(self, request, *args, **kwargs):
        """调试接口"""
        data = request.data
        method = data.get("method", "")
        url = data.get("host", "") + data.get("url", "")
        headers = data.get("headers", "")
        bodyJson = data.get("bodyJson", "")
        resultAsserts = data.get("resultAsserts", "")
        headersDict = {}
        if headers != []:
            for item in headers:
                headersDict[item["key"]] = item["value"]
        # 执行请求
        response = RequestInterface(method, url, headersDict, bodyJson).main()
        if type(response) == dict:
            return Response(response)
        # 响应异常，则返回错误内容给前端
        response_headers, response_body, duration, status_code = response[0], response[1], response[2], response[3]
        assertList = []
        if resultAsserts != []:
            for item in resultAsserts:
                # 断言校验 ，校验方法
                assertResult = self.interfaceAssert(item, response_body, status_code)
                assertList.append(assertResult)
        # 构造返回结果
        # result = {
        #     "request_headers": headersDict,
        #     "response_headers": response_headers,
        #     "response_body": response_body,
        #     "duration": duration,
        #     "status_code": status_code,
        #     "assertResult": assertList
        # }
        result = {
            "request": {
                "method": method,
                "url": url,
                "headers": headersDict,
                "body": bodyJson
            },
            "response": {
                "headers": response_headers,
                "body": response_body
            },
            "assert": assertList,
            "duration": duration,
            "status_code": status_code
        }
        return Response({"code": 1000, "data": result})


class InterfaceSearch(APIView):

    def get(self, request, *args, **kwargs):
        """Cascader 级联选择器返回值"""
        parent = request.GET.get("id", "")
        if not parent:
            return Response([])
        obj = ModuleTree.objects.filter(parent=parent)
        data = InterfaceSerachSer(obj, many=True).data
        return Response(data)
