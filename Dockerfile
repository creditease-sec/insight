# Version: 0.0.1
FROM centos
MAINTAINER Pyshen "pyshen@example.com"
ENV REFRESHED_AT 2016-07-17
RUN yum -y update
RUN yum -y install wget
RUN wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate
RUN python get-pip.py
ENV REFRESHED_AT 2016-07-19-08-40
RUN yum -y update
RUN yum install -y python-devel
RUN yum install -y mysql-devel
RUN yum install -y gcc
RUN mkdir -p /opt/webapp/
ENV REFRESHED_REQ_AT 2016-08-18-1
ADD srcpm/requirement.txt /opt/webapp/requirement.txt
WORKDIR /opt/webapp/
RUN pip install -r requirement.txt
COPY srcpm/venv_srcpm/lib/python2.7/site-packages/flask_bootstrap/__init__.py /lib/python2.7/site-packages/flask_bootstrap/__init__.py
EXPOSE 5000


