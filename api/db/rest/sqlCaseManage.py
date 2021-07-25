import os
from io import BytesIO
import xlrd
import xlwt
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http.response import JsonResponse, HttpResponse
from django.utils.encoding import escape_uri_path
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import SqlCaseManage, DataStructureManage
from api.db.serializers.sqlCaseMangeSer import SqlCaseManageListSer, SqlCaseManageAddSer, ClearResultSer, \
    UpdateEnabledSer
from api.db.serializers.dataStructureManageSer import UpdateDdlCount, UpdateDmlCount
from api.db.serializers.dataStructureManageSer import DataStructureManageAddSer
import logging

logger = logging.getLogger('default')

class SqlCaseManageList(APIView):

    def get(self, request, *args, **kwargs):
        """SQL测试用例列表"""
        parent = request.GET.get('parent', '')  # 父id也是结构的id
        ddlDmlType = request.GET.get('type', "")  # ddl还是dml
        filterInputValue = request.GET.get("filterInputValue", "")  # 搜索条件
        version = request.GET.get("version", "")  # 版本
        dic = {
            "parent": parent,
            "ddlDmlType": ddlDmlType
        }
        obj = SqlCaseManage.objects.filter(**dic)
        if version:
            obj = obj.filter(version__contains=version)
        if filterInputValue:
            obj = obj.filter(executeSql__icontains=filterInputValue)
        serializer = SqlCaseManageListSer(obj, many=True)
        pageindex = request.GET.get('page', 1)  # 页数
        pagesize = request.GET.get("limit", 10)  # 每页显示数量
        pageInator = Paginator(serializer.data, pagesize)
        # 分页
        contacts = pageInator.page(pageindex)
        res = []
        for contact in contacts:
            res.append(contact)
        return Response(data={"code": 0, "msg": "SQL用例列表", "count": len(serializer.data), "data": res})

    def put(self, request, *args, **kwargs):
        """编辑SQL测试用例"""
        data = request.data
        obj = SqlCaseManage.objects.filter(id=data['id']).first()
        if len(data) == 2:
            serializer = UpdateEnabledSer(obj, data=data)
        else:
            serializer = SqlCaseManageAddSer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 1000, "data": "编辑测试用例成功"})
        else:
            return Response({"code": 1001, "data": "编辑测试用例失败"})

    def post(self, request, *args, **kwargs):
        """
            创建SQL测试用例
            级联更新结构表ddl/dml的数量
        """
        data = request.data
        ddlDmlType = data['ddlDmlType']
        parent = data['parent']
        try:
            serializer = SqlCaseManageAddSer(data=data)
            if serializer.is_valid():
                serializer.save()
                # 更新结构表DDL、DML的数量
                counts = SqlCaseManage.objects.filter(Q(parent=parent) & Q(ddlDmlType=ddlDmlType)).count()
                obj = DataStructureManage.objects.filter(id=parent).first()
                if ddlDmlType == 'ddl':
                    ser = UpdateDdlCount(obj, data={'ddlCount': counts})
                else:
                    ser = UpdateDmlCount(obj, data={'dmlCount': counts})
                if ser.is_valid():
                    ser.save()
                    return Response({"code": 1000, "data": "新建" + ddlDmlType + "测试用例成功"})
            else:
                return Response({"code": 1001, "data": "参数有误"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})

    def delete(self, request, *args, **kwargs):
        """
            删除SQL测试用例
            级联更新结构表ddl/dml的数量
        """
        id = request.GET.get("id", "")
        ddlDmlType = request.GET.get("ddlDmlType", "")
        parent = request.GET.get("parent", "")
        try:
            SqlCaseManage.objects.filter(id=id).delete()
            counts = SqlCaseManage.objects.filter(Q(parent=parent) & Q(ddlDmlType=ddlDmlType)).count()
            obj = DataStructureManage.objects.filter(id=parent).first()
            if ddlDmlType == 'ddl':
                ser = UpdateDdlCount(obj, data={'ddlCount': counts})
            else:
                ser = UpdateDmlCount(obj, data={'dmlCount': counts})
            if ser.is_valid():
                ser.save()
                return Response({"code": 1000, "data": "删除测试用例成功"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})


class UploadSqlCase(APIView):

    def post(self, request, *args, **kwargs):
        datas = request.data
        f = request.FILES.get('file')
        excel_type = f.name.split('.')
        if "ddl" not in excel_type[0].lower() and "dml" not in excel_type[0].lower():
            return JsonResponse({"code": 1001, "data": "文件名必须包含ddl或者dml"})
        else:
            ddlDmlType = "ddl" if "ddl" in excel_type[0].lower() else "dml"
        if excel_type[1] in ['xlsx', 'xls']:
            # 开始解析上传的excel表格
            wb = xlrd.open_workbook(filename=None, file_contents=f.read())
            # 遍历sheets，先按照每个sheetName在数据库创建对应的结构名称
            flag = 0
            for sheetName in wb.sheet_names():
                # 判断当前sheetName在数据库中是否存在，存在则跳过
                if not DataStructureManage.objects.filter(
                        Q(dbTypeName=datas["dbTypeName"]) & Q(structureName=sheetName) & Q(
                            stockAddType=datas["stockAddType"])):
                    # 创建结构名称"dbTypeName","structureName","stockAddType"
                    data = {
                        "dbTypeName": datas["dbTypeName"],
                        "structureName": sheetName,
                        "stockAddType": datas["stockAddType"]
                    }
                    serializer = DataStructureManageAddSer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        # 如果创建成功，在此结构下创建对应的DDL测试用例
                        structureLastObj = DataStructureManage.objects.filter().last()
                else:
                    structureLastObj = DataStructureManage.objects.filter(
                        Q(dbTypeName=datas["dbTypeName"]) & Q(structureName=sheetName) & Q(
                            stockAddType=datas["stockAddType"])).first()
                table = wb.sheets()[flag]
                rows = table.nrows  # 总行数
                try:
                    with transaction.atomic():  # 控制数据库事务交易
                        for i in range(1, rows):
                            rowVlaues = table.row_values(i)
                            executeSql = rowVlaues[1]
                            validationSql = rowVlaues[2]
                            version = rowVlaues[3]
                            # 如果数据库不存在则新建
                            if not SqlCaseManage.objects.filter(
                                    Q(executeSql=executeSql) & Q(parent=structureLastObj.id)):
                                addSqlCaseData = {
                                    "executeSql": executeSql,
                                    "validationSql": validationSql,
                                    "parent": structureLastObj.id,
                                    "ddlDmlType": ddlDmlType,
                                    'version': version
                                }
                                ser = SqlCaseManageAddSer(data=addSqlCaseData)
                                if ser.is_valid():
                                    ser.save()
                            # 数据库存在则跳过
                            else:
                                pass
                except Exception as e:
                    logger.error("导入用例出错，错误原因：%s" % e)
                flag += 1
                # 级联更新结构表统计ddl或dml的数量,related_name='structure_sql'
                # counts = structureLastObj.structure_sql.count()  #无法对ddl与dml做区分
                counts = SqlCaseManage.objects.filter(Q(parent=structureLastObj.id) & Q(ddlDmlType=ddlDmlType)).count()
                if ddlDmlType == 'ddl':
                    ser = UpdateDdlCount(structureLastObj, data={'ddlCount': counts})
                else:
                    ser = UpdateDmlCount(structureLastObj, data={'dmlCount': counts})
                if ser.is_valid():
                    ser.save()
                logger.info(sheetName + ":导入完成")
        else:
            return JsonResponse({"code": 1001, "data": "文件格式不允许"})
        return JsonResponse({"code": 1000, "data": "导入成功"})


class DownloadSqlCase(APIView):

    def post(self, request, *args, **kwargs):
        """下载用例"""
        data = request.data
        ddlDmlType = data.get("ddlDmlType", "")
        dbTypeName = data.get("dbTypeName", "")
        stockAddType = data.get("stockAddType", "")

        workbook = xlwt.Workbook(encoding='utf-8')
        # 样式设置(可选)
        style = xlwt.XFStyle()  # 初始化样式
        font = xlwt.Font()  # 为样式创建字体
        font.name = "Times New Roman"
        font.bold = True  # 加粗
        font.underline = True  # 下划线
        font.italic = True  # 斜体字
        style.font = font  # 设定样式

        # 背景颜色设置
        pattern = xlwt.Pattern()  # Create the Pattern
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
        pattern.pattern_fore_colour = 3  # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray, the list goes on...
        style = xlwt.XFStyle()  # Create the Pattern
        style.pattern = pattern  # Add Pattern to Style

        structureObjs = DataStructureManage.objects.filter(Q(dbTypeName=dbTypeName) & Q(stockAddType=stockAddType))
        for structureObj in structureObjs:
            # 创建一个工作表(worksheet)
            w = workbook.add_sheet(structureObj.structureName)
            # 设置宽度
            w.col(0).width = 8000
            w.col(1).width = 18000
            w.col(2).width = 18000
            list_obj = SqlCaseManage.objects.filter(Q(parent=structureObj.id) & Q(ddlDmlType=ddlDmlType))
            if list_obj:
                # 创建工作薄
                w.write(0, 0, u'用例名称', style)
                w.write(0, 1, u'执行用例', style)
                w.write(0, 2, u'验证用例', style)
                w.write(0, 3, u'支持版本', style)
                # 写入数据
                excel_row = 1
                for obj in list_obj:
                    w.write(excel_row, 0, '字段已移除')
                    w.write(excel_row, 1, obj.executeSql)
                    w.write(excel_row, 2, obj.validationSql)
                    w.write(excel_row, 3, obj.version)
                    excel_row += 1
                    # 检测文件是否存在
                    # 方框中代码是保存本地文件使用，如不需要请删除该代码
        title = 'stock' if stockAddType == '存量' else "incremental"
        # 文件保存到项目目录下，不想保存可以注释
        # exist_file = os.path.exists('api/export/'+title+"-DDL.xlsx")
        # if exist_file:
        #     os.remove('api/export/'+title+"-DDL.xlsx")
        # workbook.save('api/export/'+title+"-DDL.xlsx")
        ############################
        sio = BytesIO()
        workbook.save(sio)
        # 设置文件读取的偏移量，0表示从头读起
        sio.seek(0)
        response = HttpResponse(sio.getvalue(), content_type='application/octet-stream')
        # 字符串替换成下载文件,escape_uri_path解决返回的文件名乱码问题
        response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(
            escape_uri_path(title) + '-' + ddlDmlType + '.xlsx')
        response.write(sio.getvalue())
        return response


class ClearAllResult(APIView):

    def post(self, request, *args, **kwargs):
        """清空结果"""
        data = request.data
        ddlDmlType = data['ddlDmlType']
        parent = data['parent']
        version = data['version']
        filterInputValue = data['filterInputValue']
        dic = {
            "parent": parent,
            "ddlDmlType": ddlDmlType
        }
        objs = SqlCaseManage.objects.filter(**dic)
        if version:
            objs = objs.filter(version__contains=version)
        if filterInputValue:
            objs = objs.filter(executeSql__icontains=filterInputValue)
        clearData = {
            "sourceStock": None,
            "targetStock": None,
            "validationResult": None,
            "executeResult": None
        }
        for obj in objs:
            # 只要源库存量结果或目标库存量结果中有一个存在，则更新三个结果字段的值为NULL
            if obj.sourceStock or obj.targetStock or obj.sourceStock == 0 or obj.targetStock == 0:
                ser = ClearResultSer(obj, data=clearData)
                if ser.is_valid():
                    ser.save()
                else:
                    return Response({"code": 1001, "data": "清除结果失败"})
        structureName = DataStructureManage.objects.filter(id=parent).first().structureName
        return Response({"code": 1000, "data": "清除<" + structureName + "-" + ddlDmlType + ">结果成功"})
