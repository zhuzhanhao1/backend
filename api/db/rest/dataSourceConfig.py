import json
from io import BytesIO
import xlwt
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from django.utils.encoding import escape_uri_path
from rest_framework.views import APIView
from rest_framework.response import Response
from api.db.rest.sqlExecOrValidate import ExecuteSql
from api.models import DataSourceConfig
from api.db.serializers.dataSourceConfigSer import DataSourceConfigListSer


# from rest_framework.pagination import PageNumberPagination

# class DrfPaginate(PageNumberPagination):
#     # 用来控制每页显示多少条数据（全局参数名为PAGE_SIZE）；
#     page_size = 10
#     # 用来提供直接访问某页的数据；
#     page_query_param = 'page'
#     # 控制page_size_query_param参数能调整的最大条数
#     max_page_size = 50
#     # 临时调整当前显示多少条数据
#     page_size_query_param = 'size'

# from rest_framework.pagination import CursorPagination

# 看源码，是通过sql查询，大于id和小于id
# class  Pager(APIView):
#     def get(self,request,*args,**kwargs):
#
#         obj = DataSourceConfig.objects.filter()
#         pagination_class = DrfPaginate()
#         paginate_list = pagination_class.paginate_queryset(obj, request, self)
#         res = DataSourceConfigListSer(instance=paginate_list, many=True).data
#         return Response(data={"code": 0, "msg": "数据源列表", "count": len(res), "data": res})

class DataSourceConfigList(APIView):

    def get(self, request, *args, **kwargs):
        '''
            数据源列表
        '''

        filterInputValue = request.GET.get("filterInputValue", "")
        filterDbType = request.GET.get("filterDbType[]", "")
        filterDbType = json.loads(filterDbType) if len(filterDbType) > 2 else None
        obj = DataSourceConfig.objects.filter()
        if filterInputValue:
            obj = obj.filter(host__contains=filterInputValue)
        if filterDbType:
            obj = obj.filter(dbType__in=filterDbType)
        serializer = DataSourceConfigListSer(obj, many=True)
        pageindex = request.GET.get('page', 1)  # 页数
        pagesize = request.GET.get("limit", 10)  # 每页显示数量
        pageInator = Paginator(serializer.data, pagesize)
        # 分页
        contacts = pageInator.page(pageindex)
        res = []
        for contact in contacts:
            res.append(contact)
        return Response(data={"code": 1000, "msg": "数据源列表", "count": len(serializer.data), "data": res})

    def put(self, request, *args, **kwargs):
        '''
            编辑数据源
        '''
        data = request.data
        # 数据校验
        if DataSourceConfig.objects.filter((Q(host=data['host']) & Q(dbName=data['dbName'])) | (
                Q(host=data['host']) & Q(dbName=data['serviceName']))).count() > 1:
            return Response({"code": 1001, "data": "数据源已存在"})
        obj = DataSourceConfig.objects.filter(id=data['id']).first()
        serializer = DataSourceConfigListSer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 1000, "data": "编辑数据源成功"})
        else:
            return Response({"code": 1001, "data": "编辑数据源失败"})

    def post(self, request, *args, **kwargs):
        '''
            创建数据源
        '''
        data = request.data
        # 数据校验
        if DataSourceConfig.objects.filter(
                (Q(host=data['host']) & Q(dbName=data['dbName']) & Q(version=data['version'])) & (
                        Q(host=data['host']) & Q(dbName=data['serviceName']) & Q(version=data['version']))):
            return Response({"code": 1001, "data": "数据源已存在"})
        try:
            serializer = DataSourceConfigListSer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"code": 1000, "data": "新建数据源成功"})
            else:
                return Response({"code": 1001, "data": "参数有误"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})

    def delete(self, request, *args, **kwargs):
        '''
            删除数据源
        '''
        id = request.GET.get("id", "")
        try:
            obj = DataSourceConfig.objects.filter(id=id)
            obj.delete()
            return Response({"code": 1000, "data": "删除数据源成功"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})


class DataSourceHosts(APIView):

    def get(self, request, *args, **kwargs):
        '''
            返回所有的主机列表集
        '''
        # 按照数据库种类分组
        dbTypeGroups = DataSourceConfig.objects.filter().values("dbType").annotate(c=Count("dbType"))
        data = []
        for group in dbTypeGroups:
            dic = {}
            dic["label"] = group["dbType"]
            dic["options"] = DataSourceConfig.objects.filter(dbType=group["dbType"]).values("host", "dbType", "dbName",
                                                                                            "serviceName", "username")
            data.append(dic)
        return Response(data)


class TestConnect(ExecuteSql):

    def post(self, request, *args, **kwargs):
        '''
            测试连接状态
        '''
        data = request.data
        res = self.getConnObj(data)
        if res.cursor:
            response = {"code": 1000, "data": "连接成功"}
        else:
            response = {"code": 1001, "data": res.connect}
        return Response(response)


class DownloadDataSource(APIView):

    def post(self, request, *args, **kwargs):

        # 结构ID
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
        dbTypes = DataSourceConfig.objects.filter().values_list("dbType").distinct()
        for dbType in dbTypes:
            # 创建一个工作表(worksheet)
            w = workbook.add_sheet(dbType[0])
            # 设置宽度
            w.col(0).width = 6000
            w.col(1).width = 6000
            w.col(2).width = 6000
            w.col(3).width = 6000
            w.col(4).width = 6000
            w.col(5).width = 6000
            w.col(6).width = 6000
            w.col(7).width = 6000
            list_obj = DataSourceConfig.objects.filter(dbType=dbType[0])
            if list_obj:
                # 创建工作薄
                w.write(0, 0, u'数据库类型', style)
                w.write(0, 1, u'版本号', style)
                w.write(0, 2, u'主机', style)
                w.write(0, 3, u'端口', style)
                w.write(0, 4, u'用户名', style)
                w.write(0, 5, u'密码', style)
                w.write(0, 6, u'数据库名', style)
                w.write(0, 7, u'实例名', style)
                # 写入数据
                excel_row = 1
                for obj in list_obj:
                    w.write(excel_row, 0, obj.dbType)
                    w.write(excel_row, 1, obj.version)
                    w.write(excel_row, 2, obj.host)
                    w.write(excel_row, 3, obj.port)
                    w.write(excel_row, 4, obj.username)
                    w.write(excel_row, 5, obj.password)
                    w.write(excel_row, 6, obj.dbName)
                    w.write(excel_row, 7, obj.serviceName)
                    excel_row += 1
                    # 方框中代码是保存本地文件使用，如不需要请删除该代码
        # 文件保存到项目目录下，不想保存可以注释
        # exist_file = os.path.exists('api/export/'+title+"-DDL.xlsx")
        # if exist_file:
        #     os.remove('api/export/'+title+"-DDL.xlsx")
        # workbook.save("xxx.xlsx")
        ############################
        sio = BytesIO()
        workbook.save(sio)
        # 设置文件读取的偏移量，0表示从头读起
        sio.seek(0)
        response = HttpResponse(sio.getvalue(), content_type='application/octet-stream')
        # 字符串替换成下载文件,escape_uri_path解决返回的文件名乱码问题
        response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path("数据源信息") + '.xlsx')
        response.write(sio.getvalue())
        return response
