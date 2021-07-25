from django.contrib import admin
from django.conf.urls import url, include
# from django.views.generic.base import TemplateView

urlpatterns = [
    # 后台管理页面
    url(r'^admin', admin.site.urls),
    # vue-dist，使用通用视图创建最简单的模板控制器，访问 『/』时直接返回 index.html
    # url(r'^$',TemplateView.as_view(template_name='index.html')),
    # django-restframework
    url(r'^api/(?P<version>\w+)/', include('api.urls')),
]
