from django.contrib import admin
from api.models import DataSourceConfig


@admin.register(DataSourceConfig)
class DataSourceConfigAdmin(admin.ModelAdmin):
    list_display = ('dbType', 'version', 'host', 'port', 'username', "password", "dbName", "serviceName")  # 在后台列表下显示的字段
    search_fields = ('dbType',)
