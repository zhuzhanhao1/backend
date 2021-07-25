from django.db import models
from django_mysql.models import JSONField


class DataSourceConfig(models.Model):
    """数据源管理"""
    dbType = models.CharField(max_length=50, verbose_name="数据库类型")
    version = models.CharField(max_length=50, verbose_name="版本号")
    host = models.CharField(max_length=50, verbose_name="服务器名")
    port = models.IntegerField(verbose_name="端口号")
    username = models.CharField(max_length=50, verbose_name="账户")
    password = models.CharField(max_length=50, verbose_name="密码")
    dbName = models.CharField(max_length=50, verbose_name="数据库名", null=True, blank=True)
    serviceName = models.CharField(max_length=50, verbose_name="oracle服务名", null=True, blank=True)

    class Meta:
        verbose_name_plural = '数据源管理'


class DataStructureManage(models.Model):
    """数据结构管理"""
    dbTypeName = models.CharField(max_length=50, verbose_name="数据库类型名称")
    stockAddType = models.CharField(max_length=20, verbose_name="存量或是增量")
    structureName = models.CharField(max_length=50, verbose_name="数据库结构名称")
    ddlCount = models.IntegerField(verbose_name="DDL数量", default=0)
    dmlCount = models.IntegerField(verbose_name="DML数量", default=0)
    updateTime = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    class Meta:
        verbose_name_plural = '数据结构管理'


class SqlCaseManage(models.Model):
    """SQL用例管理"""
    parent = models.ForeignKey(DataStructureManage, on_delete=models.CASCADE,
                               verbose_name='数据结构ID', related_name='structure_sql')
    ddlDmlType = models.CharField(max_length=20, verbose_name="DDL或DML")
    executeSql = models.TextField(null=True, verbose_name='执行SQL的语句')
    sourceStock = models.IntegerField(null=True, verbose_name="主库存量")
    validationSql = models.TextField(null=True, verbose_name='验证SQL的语句')
    targetStock = models.IntegerField(null=True, verbose_name='备库存量')
    validationResult = models.CharField(null=True, max_length=20, verbose_name="验证SQL结果")
    enabled = models.BooleanField(verbose_name="启用状态", default=True)
    version = JSONField()
    caseName = models.CharField(null=True, max_length=200, verbose_name="SQL用例名称")
    executeResult = models.TextField(null=True, verbose_name="执行SQL结果")
    updateTime = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    class Meta:
        verbose_name_plural = 'SQL用例管理'


class ProjectManage(models.Model):
    """接口测试项目管理"""
    projectName = models.CharField(max_length=50, verbose_name="项目名称")
    host = models.CharField(max_length=50, verbose_name="项目host")
    describe = models.CharField(max_length=150, verbose_name="项目描述", null=True, blank=True)
    head = models.CharField(max_length=50, verbose_name="负责人")

    class Meta:
        verbose_name_plural = '接口测试项目管理'


class ModuleTree(models.Model):
    """模块管理"""
    parent = models.ForeignKey(ProjectManage, on_delete=models.CASCADE,
                               verbose_name='项目id', related_name='project_module')
    name = models.CharField(max_length=50, verbose_name="模块名称")
    pid = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = '接口测试模块管理'


class InterfaceMange(models.Model):
    """接口管理"""
    parent = models.ForeignKey(ModuleTree, on_delete=models.CASCADE, related_name='module_interface')
    interfaceName = models.CharField(max_length=50, verbose_name="接口名称")
    url = models.CharField(max_length=500, verbose_name="接口地址")
    method = models.CharField(max_length=25, verbose_name="请求方式")
    headers = JSONField()  # 请求头
    params = JSONField()  # 请求参数
    formDatas = JSONField()  # 请求体参数
    bodyJson = JSONField()  # raw-json请求数据
    resultAsserts = JSONField()  # 断言
    bodyType = models.CharField(max_length=25, verbose_name="body请求类型")

    class Meta:
        verbose_name_plural = '接口测试接口管理'


class SingleInterfaceCase(models.Model):
    """单一接口用例"""
    parent = models.ForeignKey(InterfaceMange, on_delete=models.CASCADE, related_name='single_interface_case')
    interfaceName = models.CharField(max_length=50, verbose_name="接口名称")
    url = models.CharField(max_length=500, verbose_name="接口地址")
    method = models.CharField(max_length=25, verbose_name="请求方式")
    headers = JSONField()  # 请求头
    params = JSONField()  # 请求参数
    formDatas = JSONField()  # 请求体参数
    bodyJson = JSONField()  # raw-json请求数据
    resultAsserts = JSONField()  # 断言
    bodyType = models.CharField(max_length=25, verbose_name="body请求类型")
    result = JSONField()  # 执行结果
    updateTime = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    class Meta:
        verbose_name_plural = '接口测试单一接口用例'


class SceneCase(models.Model):
    """场景用例"""
    parent = models.ForeignKey(ProjectManage, on_delete=models.CASCADE,
                               verbose_name='项目id', related_name='project_scene_interface')
    name = models.CharField(max_length=50, verbose_name="场景用例名称")
    pid = models.SmallIntegerField(default=0)
    describe = models.CharField(max_length=250, verbose_name="用例描述", null=True, blank=True)

    class Meta:
        verbose_name_plural = '接口测试场景接口'


class SceneInterface(models.Model):
    """场景接口用例"""
    parent = models.ForeignKey(SceneCase, on_delete=models.CASCADE, related_name='scene_case_interface')
    interfaceName = models.CharField(max_length=50, verbose_name="接口名称")
    url = models.CharField(max_length=500, verbose_name="接口地址")
    method = models.CharField(max_length=25, verbose_name="请求方式")
    headers = JSONField()  # 请求头
    params = JSONField()  # 请求参数
    formDatas = JSONField()  # 请求体参数
    bodyJson = JSONField()  # raw-json请求数据
    resultAsserts = JSONField()  # 断言
    jsonExtract = JSONField()  # JSON提取器
    bodyType = models.CharField(max_length=25, verbose_name="body请求类型")
    result = JSONField()  # 执行结果
    updateTime = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    sortNumber = models.SmallIntegerField(verbose_name="排序号")
    frontMap = JSONField()  # 前置映射

    class Meta:
        verbose_name_plural = '接口测试场景接口用例'


class ExecutePlan(models.Model):
    """执行计划"""
    parent = models.ForeignKey(ProjectManage, on_delete=models.CASCADE,
                               verbose_name='项目id', related_name='project_execute_plan')
    planName = models.CharField(max_length=50, verbose_name="执行计划名称")
    ploy = models.CharField(max_length=50, verbose_name="策略", null=True, blank=True)
    describe = models.CharField(max_length=250, verbose_name="策略描述", null=True, blank=True)
    notification = models.BooleanField(verbose_name="消息通知")
    startTime = models.DateTimeField(verbose_name="开始时间", null=True, blank=True)
    endTime = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)
    sceneCaseIds = JSONField()
    executeType = models.BooleanField(verbose_name="执行方式，true代表直接运行一次，false代表按策略运行")
    statusChoices = (
        ('1', u'待启动'),
        ('2', u'进行中'),
        ('3', u'已完成'),
        ('4', u'异常'),
        ('5', u'停止'),
    )
    executeStatus = models.CharField(max_length=1, choices=statusChoices, default="1")

    class Meta:
        verbose_name_plural = '执行计划'


class InterfaceTestReport(models.Model):
    """接口测试报告"""
    parent = models.ForeignKey(ExecutePlan, on_delete=models.CASCADE,
                               verbose_name='执行计划ID', related_name='execute_plan_report')
    runNumber = models.IntegerField(verbose_name="运行次数")
    UpdateTime = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    result = JSONField()
    relatedId = models.IntegerField(verbose_name="关联场景接口用例的id，为了查询")

    class Meta:
        verbose_name_plural = '接口测试报告'


class MailConfig(models.Model):
    """{
        "mailHost": "smtp.qq.com",
        "mailUser": "971567069@qq.com",
        "mailPassword": "nbvgfdcukqjjbbaa",
        "sender": "971567069@qq.com",
        "receivers": ['971567069@qq.com']
    }"""
    mailHost = models.CharField(max_length=50, verbose_name="邮箱服务器")
    mailUser = models.EmailField(max_length=50, verbose_name="用户名")
    mailPassword = models.CharField(max_length=50, verbose_name="口令")
    sender = models.EmailField(max_length=50, verbose_name="发件人")
    receivers = JSONField()
