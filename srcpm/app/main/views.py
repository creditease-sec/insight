#-*- coding:utf-8 -*-
from flask import render_template
from . import main
import chartkick
from .. import db
from ..admin.models import VulType, Asset
from ..src.models import VulReport
from datetime import datetime
import json

@main.route('/')
def index():
    #-----------------漏洞类型数量统计-------------------
    query = db.session.query( db.func.count(VulReport.related_vul_type), VulReport.related_vul_type ).group_by( VulReport.related_vul_type )
    print query
    list_count_vul_type = query.all()
    data_vul_type = {}
    #data = {'王昊': 150, '万杰': 200, '潘烁宇': 100}
    for i in list_count_vul_type:
        data_vul_type[i[1]] = int(i[0])
    data_vul_type = sorted(data_vul_type.iteritems(), key=lambda d:d[1], reverse = True)
    
    #-----------------漏洞状态统计------------------------
    query = db.session.query( db.func.count(VulReport.vul_status), VulReport.vul_status ).group_by( VulReport.vul_status )
    list_count_vul_status = query.all()
    data_vul_status = {}
    #data = {'王昊': 150, '万杰': 200, '潘烁宇': 100}
    for i in list_count_vul_status:
        data_vul_status[i[1]] = int(i[0])

    #-----------------资产漏洞数量统计-------------------
    query = db.session.query( db.func.count(VulReport.related_asset), VulReport.related_asset ).group_by( VulReport.related_asset )
    list_count_related_asset = query.all()
    data_related_asset = {}
    #data = {'王昊': 150, '万杰': 200, '潘烁宇': 100}
    for i in list_count_related_asset:
        data_related_asset[i[1]] = int(i[0])
    data_related_asset = sorted(data_related_asset.iteritems(), key=lambda d:d[1], reverse = True)

    #---------------部门漏洞数量--------------------
    query = db.session.query( db.func.count(Asset.department), Asset.department ).filter(VulReport.related_asset == Asset.domain).group_by( Asset.department )
    #query = query.query( db.func.count(Asset.department), Asset.department ).group_by( Asset.department )
    list_count_department_vul = query.order_by(-db.func.count(Asset.department)).all()
    data_department_vul = {}
    for i in list_count_department_vul:
        data_department_vul[i[1]] = int(i[0])
    data_department_vul = sorted(data_department_vul.iteritems(), key=lambda d:d[1], reverse = True)


    #-------------------剩余风险变化趋势---------------------
    

    #-----------------部门剩余风险值------------------

    return render_template('index.html', data_vul_type=json.dumps(data_vul_type, encoding='utf-8', indent=4),
                            data_vul_status = json.dumps(data_vul_status, encoding='utf-8', indent=4),
                            data_related_asset = json.dumps(data_related_asset, encoding='utf-8', indent=4),
                            count_asset = len(list_count_related_asset),
                            data_department_vul = json.dumps(data_department_vul, encoding='utf-8', indent=4),
                        )


