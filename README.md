# 简介
Django+restFrameWork+jwt

## 启动(以下是在windows下开发操作步骤)

### django后端
定位到backend文件夹

安装依赖包 `pip install -r requirements.txt`

同步数据库 `python manage.py makemigrations`

同步数据库 `python manage.py migrate`

创建超级管理员 `python manage.py createsuperuser`\
            `username:admin`\
            `password:admin123456`

运行服务 `python manage.py runserver 8000` 
