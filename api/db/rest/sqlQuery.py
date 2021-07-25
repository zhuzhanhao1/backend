from django.core.paginator import Paginator
from rest_framework.response import Response
from api.db.rest.sqlExecOrValidate import ExecuteSql


class SqlTableQuery(ExecuteSql):

    def get(self, request, *args, **kwargs):
        """查询改数据源下所有的tables"""
        host = request.GET.get("host", "")
        tableName = request.GET.get("tableName", "")
        columns = request.GET.get("columns", "")
        dataSourceDict = self.getDatabaseInfo(host)
        connObj = self.getConnObj(dataSourceDict)
        if not connObj.cursor:
            return Response({"code": 1001, "data": "连接数据库失败"})
        # 查询所有的表，返回list
        if host and not tableName:
            res = connObj.getAllTables()
            return Response({"code": 1000, "data": res})
        # 查询创表语句，返回str
        elif host and tableName and not columns:
            res = connObj.describeTable(tableName)
            return Response({"code": 1000, "data": res})
        # 查询所有的列，返回list
        elif host and tableName and columns:
            columns, result = connObj.getAllColumns(tableName, dataSourceDict['dbName'])
            pageindex = request.GET.get('page', 1)  # 页数
            pagesize = request.GET.get("limit", 10)  # 每页显示数量
            pageInator = Paginator(result, pagesize)
            # 分页
            contacts = pageInator.page(pageindex)
            res = []
            for contact in contacts:
                res.append(contact)
            return Response(data={"code": 1000, "msg": "数据列表", "count": len(result), "data": [columns, res]})


class SqlTableDataQuery(ExecuteSql):

    def get(self, request, *args, **kwargs):
        """表内所有数据"""
        host = request.GET.get("host", "")
        tableName = request.GET.get("tableName", "")
        dataSourceDict = self.getDatabaseInfo(host)
        connObj = self.getConnObj(dataSourceDict)
        if not connObj.cursor:
            return Response({"code": 1001, "data": "连接数据库失败"})
        columns, result = connObj.getTableDatas(tableName)
        pageindex = request.GET.get('page', 1)  # 页数
        pagesize = request.GET.get("limit", 10)  # 每页显示数量
        pageInator = Paginator(result, pagesize)
        # 分页
        contacts = pageInator.page(pageindex)
        res = []
        for contact in contacts:
            res.append(contact)
        return Response(data={"code": 1000, "msg": "数据列表", "count": len(result), "data": [columns, res]})
