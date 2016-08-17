#-*- coding:utf-8 -*-
from flask import render_template
from . import main
import chartkick
from .. import db
from ..admin.models import VulType
from ..src.models import VulReport
from datetime import datetime
import json

@main.route('/')
def index():
    #-----------------漏洞类型数量统计-------------------
    query = db.session.query( db.func.count(VulReport.related_vul_type), VulReport.related_vul_type ).group_by( VulReport.related_vul_type )
    list_count_vul_type = query.all()
    data_vul_type = {}
    #data = {'王昊': 150, '万杰': 200, '潘烁宇': 100}
    for i in list_count_vul_type:
        data_vul_type[i[1]] = int(i[0])
    
    #-----------------漏洞状态统计------------------------
    query = db.session.query( db.func.count(VulReport.vul_status), VulReport.vul_status ).group_by( VulReport.vul_status )
    list_count_vul_status = query.all()
    data_vul_status = {}
    #data = {'王昊': 150, '万杰': 200, '潘烁宇': 100}
    for i in list_count_vul_status:
        data_vul_status[i[1]] = int(i[0])
    return render_template('index.html', data_vul_type=json.dumps(data_vul_type, encoding='utf-8', indent=4),
                            data_vul_status = json.dumps(data_vul_status, encoding='utf-8', indent=4),
                        )


