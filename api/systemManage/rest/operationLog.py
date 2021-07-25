from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response


class OperationLog(APIView):
    """
        操作日志
    """

    def get(self, request, *args, **kwargs):
        startNum = request.GET.get("startNum", "")
        endNum = request.GET.get("endNum", "")
        logLevel = request.GET.get("logLevel", "all")
        data = ''
        try:
            with open(r'logs/{0}-{1}.log'.format(logLevel, datetime.now().strftime('%Y-%m-%d')), 'r') as f:
                if int(startNum) < 2:
                    for line in f.readlines()[-int(endNum)::]:
                        data += line.strip(',')
                else:
                    for line in f.readlines()[-int(endNum):-int(startNum)]:
                        data += line.strip(',')
        except Exception as e:
            return Response({"code": 1001, "data": "日志文件获取失败，失败原因： %s" % e})
        return Response({"code": 1000, "data": data})
