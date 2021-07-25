import time
import uuid
from django.core.paginator import Paginator
from django.db.models import Max
from rest_framework.views import APIView
from rest_framework.response import Response
from api.common.notification import EmailSender
from api.interface.rest.sceneInterface import RunSceneInterface
from api.interface.serializers.sceneInterfaceSer import PlanModuleSceneCaseSer
from api.models import ExecutePlan, ProjectManage, SceneCase, InterfaceTestReport, SceneInterface, MailConfig
from api.interface.serializers.executePlanSer import ExecutePlanListSer, PlanNotificationSer, PlanExecuteTypeSer, \
    InterfaceTestReportSer, PlanExecuteStatusSer, ExecutePlanAddSer
from apscheduler.schedulers.background import BackgroundScheduler  # 非阻塞
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from collections import Counter
import logging

logger = logging.getLogger('log')


class ExecutePlanList(APIView):

    def get(self, request, *args, **kwargs):
        """执行计划列表"""
        projectId = request.GET.get("projectId", "")
        filterInputValue = request.GET.get("filterInputValue", "")
        obj = ExecutePlan.objects.filter(parent=projectId)
        if filterInputValue:
            obj = ExecutePlan.objects.filter(planName__contains=filterInputValue)
        serializer = ExecutePlanListSer(obj, many=True)
        pageindex = request.GET.get('page', 1)  # 页数
        pagesize = request.GET.get("limit", 999)  # 每页显示数量
        pageInator = Paginator(serializer.data, pagesize)
        # 分页
        contacts = pageInator.page(pageindex)
        res = []
        for contact in contacts:
            res.append(contact)
        return Response(data={"code": 1000, "msg": "执行计划列表", "count": len(serializer.data), "data": res})

    def put(self, request, *args, **kwargs):
        """编辑执行计划"""
        data = request.data
        obj = ExecutePlan.objects.filter(id=data['id']).first()
        if len(data) == 2:
            serializer = PlanNotificationSer(obj, data=data)
        elif len(data) == 3:
            serializer = PlanExecuteTypeSer(obj, data=data)
        else:
            serializer = ExecutePlanAddSer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 1000, "data": "编辑执行计划成功"})
        else:
            return Response({"code": 1001, "data": "编辑执行计划失败"})

    def post(self, request, *args, **kwargs):
        """创建执行计划"""
        data = request.data
        # 数据校验
        if ExecutePlan.objects.filter(planName=data['planName']):
            return Response({"code": 1001, "data": "执行计划已存在"})
        try:
            serializer = ExecutePlanAddSer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"code": 1000, "data": "新建执行计划成功"})
            else:
                return Response({"code": 1001, "data": "参数有误"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})

    def delete(self, request, *args, **kwargs):
        """删除执行计划"""
        id = request.GET.get("id", "")
        try:
            obj = ExecutePlan.objects.filter(id=id)
            obj.delete()
            return Response({"code": 1000, "data": "删除执行计划成功"})
        except Exception as e:
            return Response({"code": 1001, "data": str(e)})


class RunExecutePlan(RunSceneInterface):

    def getRunNumber(self, planId):
        """
            返回运行次数，运行过的取最大值+1，没有运行过的取1
        """
        reportObject = InterfaceTestReport.objects.filter(parent=planId)
        if reportObject:
            runNumber = reportObject.aggregate(Max('runNumber'))["runNumber__max"] + 1
        else:
            runNumber = 1
        return runNumber

    def updateStatus(self, planId, status):
        data = {
            "executeStatus": status
        }
        planoOj = ExecutePlan.objects.filter(id=planId).first()
        serializer = PlanExecuteStatusSer(planoOj, data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            logger.warning("执行计划%s更新状态%s失败" % planId, status)
        return

    def determine_ploy(self, ploy):
        '''
            校验ploy参数是否符合cron格式要求
            year (int|str) – 4-digit year
            month (int|str) – month (1-12)
            day (int|str) – day of the (1-31)
            week (int|str) – ISO week (1-53)
            day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
            hour (int|str) – hour (0-23)
            minute (int|str) – minute (0-59)
            second (int|str) – second (0-59)
            start_date (datetime|str) – earliest possible date/time to trigger on (inclusive)
            end_date (datetime|str) – latest possible date/time to trigger on (inclusive)
            timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone)
        '''
        ploy_list = ploy.split(" ")
        if len(ploy_list) == 7:
            return ploy_list
        return False

    def post(self, request, *args, **kwargs):
        """运行执行计划"""
        data = request.data
        # 公共参数
        planName = data.get("planName", "")
        sceneCaseIds = data.get("sceneCaseIds", "")
        projectId = data.get("parent", "")
        host = ProjectManage.objects.filter(id=projectId).first().host
        planId = data.get("id", "")
        notification = data.get("notification", "")
        executeType = data.get("executeType", "")
        # 创建调速器对象
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(20),
            'processpool': ProcessPoolExecutor(10)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
        uid = str(uuid.uuid4())
        # 运行一次
        if executeType == True:
            # 将时间戳转化为时间数组
            timeArray = time.localtime(time.time() + 5)
            # 将时间数组转化为北京时间格式
            beiJingTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            # 运行时间特意加了五秒，要求在五秒内，加入任务job
            scheduler.add_job(self.schedulerFun, 'date', id=uid, run_date=beiJingTime,
                              args=(sceneCaseIds, scheduler, uid, projectId, planId, host, planName, notification))
        # 定时运行
        else:
            ploy = data.get("ploy", "")
            startTime = data.get("startTime", "")
            endTime = data.get("endTime", "")
            cron = self.determine_ploy(ploy)
            # 验证ploy策略是否合法
            if not cron:
                return Response({"code": 1001, "data": "请输入合法的ploy"})

            scheduler.add_job(self.schedulerFun, 'cron', year=cron[0], month=cron[1], day=cron[2],  # week='*',
                              day_of_week=cron[3], hour=cron[4], minute=cron[5], second=cron[6], id=uid,
                              start_date=startTime, end_date=endTime,
                              args=(sceneCaseIds, scheduler, uid, projectId, planId, host, planName, notification))
        scheduler.add_listener(self.listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        scheduler.start()  # paused=False
        job = str(scheduler.get_job(uid))
        logger.info(job)
        # 获取下次运行的时间节点
        taskNotification = job.split(",")[-1][1:-1]
        # 更新执行任务状态为进行中
        self.updateStatus(planId, "2")
        return Response({"code": 1000, "data": "Task<{0}>:已启动，开启消息通知将会收到消息提醒,%s".format(planName) % taskNotification})

    def schedulerFun(self, *args):
        sceneCaseIds, scheduler, uid, projectId, planId, host, planName, notification = \
            args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7]
        logger.info("{0}任务已开始.........".format(planName))
        # 获取最大的运行次数
        runNumber = self.getRunNumber(planId)
        for sceneCaseId in sceneCaseIds:
            objs = SceneInterface.objects.filter(parent=sceneCaseId).values_list(
                "id", "headers", "method", "url", "bodyJson", "resultAsserts", "parent", "jsonExtract",
                "frontMap", "interfaceName").order_by("sortNumber")
            for obj in objs:
                # 查询接口参数中是否存在需要替换的内容，存在则替换返回新的元祖
                newObj = self.extractReplacement(projectId, obj)
                if type(newObj) == dict:
                    # 参数替换异常则将执行状态改为异常
                    self.updateStatus(planId, "4")
                    # 移除任务，关闭调度器
                    self.closeScheduler(scheduler, uid)
                result = self.runCase(projectId, host, newObj)
                if result.get("code", ""):
                    # 参数替换异常则将执行状态改为异常
                    self.updateStatus(planId, "4")
                    # 移除任务，关闭调度器
                    self.closeScheduler(scheduler, uid)
                # 构造请求的数据
                result["request_data"] = {"interfaceName": obj[9], "method": obj[2], "url": obj[3]}
                # 构造测试报告数据
                data = {"parent": planId, "runNumber": runNumber, "result": result, "relatedId": sceneCaseId}
                # 保存测试结果
                serializer = InterfaceTestReportSer(data=data)
                if serializer.is_valid():
                    serializer.save()
        taskInfo = scheduler.get_job(uid)
        if taskInfo:
            # 下一次的运行时间
            nexttime = str(taskInfo).split(",")[-1][1:-1]
        else:
            nexttime = "已结束任务，不再运行"
            # 任务完成无异常，更新状态为已完成
            self.updateStatus(planId, "3")
        # 消息通知
        if notification:
            mailDict, subject = self.getMailInfo()
            EmailSender(**mailDict).sendMail(subject,
                                             "Task<{0}>：此次运行已完成，请前往系统查看测试报告,%s".format(planName) % nexttime)
        return

    def getMailInfo(self):
        subject = "接口测试消息通知"
        mailDict = MailConfig.objects.filter().values("mailHost", "mailUser", "mailPassword", "sender", "receivers")[0]
        return mailDict, subject

    def closeScheduler(self, scheduler, uid):
        try:
            if scheduler.get_job(uid):
                scheduler.remove_job(uid)
                logger.info("移除任务成功")
            # 关闭调度器
            scheduler.shutdown(wait=False)
        except Exception as e:
            logger.error("调度器关闭异常，异常原因：%s" % e)
        return

    def listener(self, event):
        if event.exception:
            mailDict, subject = self.getMailInfo()
            EmailSender(**mailDict).sendMail(subject, '执行任务出错了,错误原因：%s' % event.exception)
            logger.error('任务出错了,%s' % event.exception)


class TestReport(APIView):

    def get(self, request, *args, **kwargs):
        """
            return:开始时间、结束时间、运行次数
        """
        id = request.GET.get("id", "")
        # 测试报告基本信息
        planObj = ExecutePlan.objects.filter(id=id).first()
        # 获取项目名称
        projectName = planObj.parent.projectName
        reportObject = InterfaceTestReport.objects.filter(parent=id)
        # 当前最新的一次运行次数号
        maxRunNumber = reportObject.aggregate(Max('runNumber'))["runNumber__max"]
        # 运行次数
        runNumberList = reportObject.values("runNumber").distinct()
        # 场景树
        sceneObj = SceneCase.objects.filter(id__in=planObj.sceneCaseIds)
        setTree = PlanModuleSceneCaseSer(sceneObj, many=True).data
        data = {
            "projectName": projectName,
            "startTime": planObj.startTime,
            "endTime": planObj.endTime,
            "executeStatus": planObj.get_executeStatus_display(),
            "runNumberList": runNumberList,
            "setTree": setTree,
            "maxRunNumber": maxRunNumber
        }
        return Response(data)

    def post(self, request, *args, **kwargs):
        """
        测试报告数据列表
        """
        data = request.data
        id = data.get("id", "")
        relatedId = data.get("relatedId", "")
        runNumberId = data.get("runNumberId", "")
        # 过滤条件
        dic = {
            "relatedId": relatedId,
            "parent": id,
            "runNumber": runNumberId
        }
        reportObject = InterfaceTestReport.objects.filter(**dic)
        serializer = InterfaceTestReportSer(reportObject, many=True)
        pageindex = request.GET.get('page', 1)  # 页数
        pagesize = request.GET.get("limit", 999)  # 每页显示数量
        pageInator = Paginator(serializer.data, pagesize)
        # 分页
        contacts = pageInator.page(pageindex)
        res = []
        for contact in contacts:
            res.append(contact)
        return Response(data={"code": 0, "msg": "执行计划列表", "count": len(serializer.data), "data": res})


class TestCharts(APIView):

    def get(self, request, *args, **kwargs):
        id = request.GET.get("id", "")
        relatedId = request.GET.get("relatedId", None)
        runNumberId = request.GET.get("runNumberId", None)
        # 过滤条件
        dic = {
            "relatedId": relatedId,
            "parent": id,
            "runNumber": runNumberId
        }
        reportObject = InterfaceTestReport.objects.filter(**dic).values_list("result")
        assertData = []
        codeData = []
        try:
            for obj in reportObject:
                assertData.append(obj[0]["conclusion"])
                codeData.append(obj[0]["status_code"])
        except Exception as e:
            logger.error("运行结果异常，图表无法取值：%s" % e)
            return Response({"assertChartList": [], "codeChartList": []})
        # 获取占比数据
        assertData = self.getChartList(assertData)
        codeData = self.getChartList(codeData)
        data = {
            "assertChartList": assertData,
            "codeChartList": codeData
        }
        return Response(data)

    def getChartList(self, data):
        """
            返回字符串在list中的占比
        """
        data = dict(Counter(data))
        result = []
        for key, value in data.items():
            list = []
            list.append(str(key))
            if len(data) == 1:
                list.append(100.0)
            else:
                list.append(round(value / len(data), 3) * 100)
            result.append(list)
        return result
