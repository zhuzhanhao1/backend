FROM python:3.7
ENV PYTHONUNBUFFERED 1
# 镜像作者
MAINTAINER zhuzh 971567069@qq.com

RUN mkdir /code
WORKDIR /code
COPY pip.conf /root/.pip/pip.conf
ADD . /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -U --force-reinstall --no-binary :all: gevent

#服务器部署
CMD ["gunicorn", "backend.wsgi:application","-c","./gunicorn.conf"]



