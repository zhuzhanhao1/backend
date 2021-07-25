from rest_framework.views import APIView
from rest_framework.response import Response
from api.common.connectMysql import ConnectMysql
from api.common.connectOracle import ConnectOracle
from api.common.connectSqlServer import ConnectSqlServer
from api.models import SqlCaseManage, DataSourceConfig
from api.db.serializers.sqlCaseMangeSer import UpdateSourceStock, UpdateTargetStock
import logging
logger = logging.getLogger('default')

class ExecuteSql(APIView):
    """
        执行SQL用例
        1.行按钮请求==勾选一个CheckBox的请求
        2.勾选多个CheckBox的请求
        3.不够选CheckBox的请求，默认为执行当前结构下的所有用例
    """

    def getConnObj(self, dataSourceInfo):
        """获取数据库连接对象"""
        conn_obj = None
        if dataSourceInfo["dbType"] == 'SQL SERVER':
            conn_obj = ConnectSqlServer(dataSourceInfo['username'], dataSourceInfo['password'], dataSourceInfo['host'],
                                        dataSourceInfo['dbName'], dataSourceInfo['port'])
        elif dataSourceInfo["dbType"] == "MYSQL":
            conn_obj = ConnectMysql(dataSourceInfo['host'], dataSourceInfo['username'], dataSourceInfo['password'],
                                    dataSourceInfo['dbName'], dataSourceInfo['port'])
        elif dataSourceInfo["dbType"] == 'ORACLE':
            conn_obj = ConnectOracle(dataSourceInfo['username'], dataSourceInfo['password'],
                                     dataSourceInfo['host'] + ":" + str(dataSourceInfo['port']) + "/" + dataSourceInfo[
                                         'serviceName'])
        return conn_obj

    def getDatabaseInfo(self, host):
        """获取连接数据库的详细信息"""
        params = host.split(',')
        dic = {
            "dbType": params[0],
            "host": params[1],
            "username": params[2],
            "dbName": params[3],
            "serviceName": params[4]
        }
        # if not params[-1]:
        #     obj = DataSourceConfig.objects.filter(Q(dbType=params[0]) & Q(host=params[1]) & Q(dbName=params[2])).first()
        # else:
        #     obj = DataSourceConfig.objects.filter(
        #         Q(dbType=params[0]) & Q(host=params[1]) & Q(serviceName=params[-1])).first()
        obj = DataSourceConfig.objects.filter(**dic).first()
        return {
            "dbType": obj.dbType,
            "host": obj.host,
            "username": obj.username,
            "dbName": obj.dbName,
            "serviceName": obj.serviceName,
            "password": obj.password,
            "port": obj.port,
        }

    def executeSqlCase(self, dataSourceInfo, content):
        """执行SQL用例"""
        connObj = self.getConnObj(dataSourceInfo)
        if not connObj.cursor:
            return {"code": 1001, "data": connObj.connect}
        for item in content:
            if item["enabled"]:
                executeResult = connObj.executeSql(item['executeSql'])
                validationResult = connObj.validationSql(item['validationSql'])
                sourceStock = validationResult[0] if isinstance(validationResult, tuple) else validationResult
                # 更新该条记录的源库存量结果
                obj = SqlCaseManage.objects.filter(id=item['id']).first()
                serializer = UpdateSourceStock(obj, data={"sourceStock": sourceStock, "executeResult": executeResult[0:200]})
                if serializer.is_valid():
                    serializer.save()
                else:
                    logger.error(item['executeSql']+"，保存执行结果失败")
            else:
                pass
            # 失败重连
            # if executeResult != True:
            #     connObj.closeConn()
            #     connObj = self.getConnObj(dataSourceInfo)
        connObj.closeConn()
        return {"code": 1000, "data": "SQL用例执行完成"}

    def post(self, request, *args, **kwargs):
        """后台处理SQL用例与验证SQL用例"""
        data = request.data
        databaseInfo = self.getDatabaseInfo(data['host'])
        # 全选执行
        if len(data) == 5:
            parent = data.get('parentId', '')  # 父id也是结构的id
            ddlDmlType = data.get('ddlDmlType', "")  # ddl还是dml
            filterInputValue = data.get("filterInputValue", "")  # 搜索条件
            version = data.get("version", "")  # 版本
            dic = {
                "parent": parent,
                "ddlDmlType": ddlDmlType
            }
            obj = SqlCaseManage.objects.filter(**dic)
            if version:
                obj = obj.filter(version__contains=version)
            if filterInputValue:
                obj = obj.filter(executeSql__icontains=filterInputValue)
            content = obj.values("id", "executeSql", "validationSql", "enabled")
        # 勾选执行
        else:
            content = data["content"]
        res = self.executeSqlCase(databaseInfo, content)
        return Response(res)


class ValidationSql(ExecuteSql):

    def executeSqlCase(self, dataTargetInfo, content):
        """验证目标库存量结果和源库是否匹配"""
        connObj = self.getConnObj(dataTargetInfo)
        if not connObj.cursor:
            return {"code": 1001, "data": connObj.connect}
        for item in content:
            targetStock = connObj.validationSql(item['validationSql'])
            targetStock = targetStock[0] if isinstance(targetStock, tuple) else targetStock
            # 更新该条记录的目标库存量结果
            obj = SqlCaseManage.objects.filter(id=item['id']).first()
            validationResult = '相同' if obj.sourceStock == targetStock else "不相同"
            serializer = UpdateTargetStock(obj,
                                           data={"targetStock": targetStock, 'validationResult': validationResult})
            if serializer.is_valid():
                serializer.save()
        connObj.closeConn()
        return {"code": 1000, "data": "SQL用例验证完成"}


class RefreshSourceStock(ExecuteSql):

    def executeSqlCase(self, dataTargetInfo, content):
        """刷新源库存量"""
        connObj = self.getConnObj(dataTargetInfo)
        if not connObj.cursor:
            return {"code": 1001, "data": connObj.connect}
        for item in content:
            if item["enabled"]:
                sourceStock = connObj.validationSql(item['validationSql'])
                sourceStock = sourceStock[0] if isinstance(sourceStock, tuple) else sourceStock
                # 更新该条记录的目标库存量结果
                obj = SqlCaseManage.objects.filter(id=item['id']).first()
                serializer = UpdateSourceStock(obj, data={"sourceStock": sourceStock})
                if serializer.is_valid():
                    serializer.save()
            else:
                pass
        connObj.closeConn()
        return {"code": 1000, "data": "刷新源库存量完成"}
