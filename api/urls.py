from django.conf.urls import url
from api.db.rest.dataSourceConfig import DataSourceConfigList, DataSourceHosts, TestConnect, DownloadDataSource
from api.db.rest.dataStructureManage import DataStructureManageList
from api.db.rest.sqlCaseManage import SqlCaseManageList, UploadSqlCase, DownloadSqlCase, ClearAllResult
from api.db.rest.sqlExecOrValidate import ExecuteSql, ValidationSql, RefreshSourceStock
from api.db.rest.sqlQuery import SqlTableQuery, SqlTableDataQuery
from api.systemManage.rest.operationLog import OperationLog
from api.interface.rest.projectManage import ProjectManageList
from api.interface.rest.interfaceManage import ModuleCaseTree, InterfaceManageList, InterfaceDebug, \
    InterfaceSearch
from api.interface.rest.singleInterface import SingleInterfaceCaseList, PublicParams, \
    RunSingleInterfaceCase
from api.interface.rest.sceneInterface import SceneCaseTree, SceneInterfaceList, RunSceneInterface, \
    SceneInterfaceSort, LocalParams, SceneInterfaceImport
from api.interface.rest.executePlan import ExecutePlanList, RunExecutePlan, TestReport, TestCharts
from api.systemManage.rest.mailConfig import MailConfigList, MailTestSend
from api.user.login import UserLogin, UserLoginStatus, UserLogout

urlpatterns = [
    # 登录
    url(r'user/login$', UserLogin.as_view()),
    url(r'user/info$', UserLoginStatus.as_view()),
    url(r'user/logout$', UserLogout.as_view()),
    # 数据源配置模块
    url(r'dataSourceConfig$', DataSourceConfigList.as_view()),
    url(r'dataSourceConfig/getHosts$', DataSourceHosts.as_view()),
    url(r'dataSourceConfig/testConnect$', TestConnect.as_view()),
    url(r'dataSourceConfig/download$', DownloadDataSource.as_view()),
    # 数据结构分类管理
    url(r'dataStructureManage$', DataStructureManageList.as_view()),
    # SQL用例管理模块
    url(r'sqlCaseManage$', SqlCaseManageList.as_view()),
    url(r'sqlCaseManage/clear$', ClearAllResult.as_view()),
    url(r'sqlCaseManage/upload$', UploadSqlCase.as_view()),
    url(r'sqlCaseManage/download$', DownloadSqlCase.as_view()),
    url(r'sqlCaseManage/executeSql$', ExecuteSql.as_view()),
    url(r'sqlCaseManage/ValidationSql$', ValidationSql.as_view()),
    url(r'sqlCaseManage/refreshSourceStock$', RefreshSourceStock.as_view()),
    # SQL查询模块
    url(r'sqlQuery/allTables$', SqlTableQuery.as_view()),
    url(r'sqlQuery/allColumns$', SqlTableQuery.as_view()),
    url(r'sqlQuery/allDatas$', SqlTableDataQuery.as_view()),
    # 接口项目管理
    url(r'projectManage$', ProjectManageList.as_view()),
    url(r'moduleTree$', ModuleCaseTree.as_view()),
    # 接口管理
    url(r'interfaceManage$', InterfaceManageList.as_view()),
    url(r'interfaceDebug$', InterfaceDebug.as_view()),
    url(r'interfaceSearch$', InterfaceSearch.as_view()),
    # 单一接口
    url(r'singleInterfaceCase$', SingleInterfaceCaseList.as_view()),
    url(r'singleInterfaceCase/run$', RunSingleInterfaceCase.as_view()),
    # 参数
    url(r'publicParams$', PublicParams.as_view()),
    url(r'localParams$', LocalParams.as_view()),
    # 场景接口
    url(r'sceneCaseTree$', SceneCaseTree.as_view()),
    url(r'sceneInterface$', SceneInterfaceList.as_view()),
    url(r'sceneInterface/run$', RunSceneInterface.as_view()),
    url(r'sceneInterface/sort$', SceneInterfaceSort.as_view()),
    url(r'sceneInterface/upload', SceneInterfaceImport.as_view()),
    # 执行计划模块
    url(r'executePlan$', ExecutePlanList.as_view()),
    url(r'executePlan/run$', RunExecutePlan.as_view()),
    url(r'testReprot$', TestReport.as_view()),
    url(r'testCharts$', TestCharts.as_view()),
    # 邮箱配置列表
    url(r'mailConfig$', MailConfigList.as_view()),
    url(r'mailTestSend$', MailTestSend.as_view()),
    # 操作日志模块
    url(r'operationLog$', OperationLog.as_view()),
]
