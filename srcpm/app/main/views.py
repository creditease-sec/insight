#-*- coding:utf-8 -*-
from flask import render_template, current_app, request
from . import main
import chartkick
from .. import db
from ..admin.models import VulType, Asset, AssetScore
from ..src.models import VulReport, VulLog
#from datetime import datetime
#from datetime import date
import datetime
import json
from ..decorators import permission_required
from ..src.views import date_asset_sec_score
#from ..src.views import get_asset_code_score
#from ..src.views import get_asset_attack_score
import os
#from threading import Thread
#import time
import calendar
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


@main.route('/depart_risk_stat', methods=['GET','POST'])
@main.route('/depart_risk_stat/<start_date>/<end_date>', methods=['GET','POST'])
def depart_risk_stat(start_date='20170101',end_date=datetime.date.today):
    try:
        startDate = datetime.date(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:8]))
        endDate = datetime.date(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8]))
    except:
        startDate = datetime.date(2017,1,1)
        endDate = datetime.date.today()

    #---------------部门外网资产数量-------------------
    #部门外网资产：资产为‘外网’，且状态为‘线上’，且分配了‘安全官’
    depart_asset_stat = db.session.query( Asset.department, db.func.count(Asset.department) ).filter(
                                                                            Asset.in_or_out == u'外网',
                                                                            Asset.status == u'线上',
                                                                            Asset.sec_owner != '',
                                                                        ).group_by(
                                                                            Asset.department
                                                                            ).order_by(-db.func.count(Asset.department)).all()
    #print depart_asset_stat
    count_asset = 0
    for i in depart_asset_stat:
        count_asset += i[1]


    #---------------部门外网漏洞数量--------------------
    #部门外网漏洞数量：外网资产，且漏洞报告状态为‘线上’,指定时间段内新增加的漏洞报告
    data_department_vul = db.session.query( Asset.department, db.func.count(Asset.department)).filter(
                                                                            Asset.in_or_out == u'外网',
                                                                            Asset.status == u'线上',
                                                                            Asset.sec_owner != '',
                                                                            VulReport.related_asset == Asset.domain,
                                                                            VulReport.start_date >= startDate,
                                                                            VulReport.start_date <= endDate,
                                                                            VulReport.related_asset_status == u'线上',
                                                                            VulReport.related_vul_type != u'输出文档',
                                                                        ).group_by(
                                                                            Asset.department
                                                                        ).order_by(-db.func.count(Asset.department)).all()
    #count_vul = 0
    #for j in data_department_vul:
    #    count_vul += j[1]
    
    #在统计时间段之前发现，至今还没有修复的漏洞
    data_department_vul_unfinish = db.session.query( Asset.department, db.func.count(Asset.department)).filter(
                                                                            Asset.in_or_out == u'外网',
                                                                            Asset.status == u'线上',
                                                                            Asset.sec_owner != '',
                                                                            VulReport.related_asset == Asset.domain,
                                                                            VulReport.start_date < startDate,
                                                                            VulReport.fix_date == None,
                                                                            VulReport.related_asset_status == u'线上',
                                                                            VulReport.related_vul_type != u'输出文档',
                                                                        ).group_by(
                                                                            Asset.department
                                                                        ).order_by(-db.func.count(Asset.department)).all()

    #在统计时间段之前发现，至今已修复的漏洞（包括统计时间段内修复的，和统计时间段之后修复的）
    data_department_vul_finished = db.session.query( Asset.department, db.func.count(Asset.department)).filter(
                                                                            Asset.in_or_out == u'外网',
                                                                            Asset.status == u'线上',
                                                                            Asset.sec_owner != '',
                                                                            VulReport.related_asset == Asset.domain,
                                                                            VulReport.start_date < startDate,
                                                                            VulReport.fix_date >= startDate,
                                                                            #VulReport.fix_date <= endDate,
                                                                            VulReport.related_asset_status == u'线上',
                                                                            VulReport.related_vul_type != u'输出文档',
                                                                        ).group_by(
                                                                            Asset.department
                                                                        ).order_by(-db.func.count(Asset.department)).all()

    data_department_vul_count_all = {}
    for c in data_department_vul:
        #print c[0],c[1]
        if data_department_vul_count_all.has_key(c[0]):
            data_department_vul_count_all[c[0]] += int(c[1])
        else:
            data_department_vul_count_all.update({c[0]:c[1]})
    for c in data_department_vul_unfinish:
        #print c[0],c[1]
        if data_department_vul_count_all.has_key(c[0]):
            data_department_vul_count_all[c[0]] += int(c[1])
        else:
            data_department_vul_count_all.update({c[0]:c[1]})
    for c in data_department_vul_finished:
        #print c[0],c[1]
        if data_department_vul_count_all.has_key(c[0]):
            data_department_vul_count_all[c[0]] += int(c[1])
        else:
            data_department_vul_count_all.update({c[0]:c[1]})

    #-------------部门外网风险累计-------------------
    #部门外网资产漏洞报告风险*修复时长

    #统计时间段内新增加的漏洞
    data_department_vul_list = db.session.query( Asset.department, VulReport.id, VulReport.risk_score, VulReport.start_date, VulReport.fix_date).filter(
                                                                            Asset.in_or_out == u'外网',
                                                                            Asset.status == u'线上',
                                                                            Asset.sec_owner != '',
                                                                            VulReport.related_asset == Asset.domain,
                                                                            VulReport.start_date >= startDate,
                                                                            VulReport.start_date <= endDate,
                                                                            VulReport.related_asset_status == u'线上',
                                                                            VulReport.related_vul_type != u'输出文档',
                                                                        ).all()
    count_vul_new = len(data_department_vul_list)

    #统计时间段内新增加的漏洞,未完成修复的
    data_department_vul_list_unfinish = db.session.query( Asset.department, VulReport.id, VulReport.risk_score, VulReport.start_date, VulReport.fix_date).filter(
                                                                            Asset.in_or_out == u'外网',
                                                                            Asset.status == u'线上',
                                                                            Asset.sec_owner != '',
                                                                            VulReport.related_asset == Asset.domain,
                                                                            VulReport.start_date >= startDate,
                                                                            VulReport.start_date <= endDate,
                                                                            VulReport.fix_date == None,
                                                                            VulReport.related_asset_status == u'线上',
                                                                            VulReport.related_vul_type != u'输出文档',
                                                                        ).all()
    count_vul_new_unfinish = len(data_department_vul_list_unfinish)


    #统计时间段内新增加的漏洞,完成修复的
    data_department_vul_list_finished = db.session.query( Asset.department, VulReport.id, VulReport.risk_score, VulReport.start_date, VulReport.fix_date).filter(
                                                                            Asset.in_or_out == u'外网',
                                                                            Asset.status == u'线上',
                                                                            Asset.sec_owner != '',
                                                                            VulReport.related_asset == Asset.domain,
                                                                            VulReport.start_date >= startDate,
                                                                            VulReport.start_date <= endDate,
                                                                            VulReport.fix_date != None,
                                                                            VulReport.related_asset_status == u'线上',
                                                                            VulReport.related_vul_type != u'输出文档',
                                                                        ).all()
    count_vul_new_finished = len(data_department_vul_list_finished)


    #统计时间段之前发现的漏洞，至今还没有修复的
    data_department_vul_list_2 = db.session.query( Asset.department, VulReport.id, VulReport.risk_score, VulReport.start_date, VulReport.fix_date).filter(
                                                                            Asset.in_or_out == u'外网',
                                                                            Asset.status == u'线上',
                                                                            Asset.sec_owner != '',
                                                                            VulReport.related_asset == Asset.domain,
                                                                            VulReport.start_date < startDate,
                                                                            VulReport.fix_date == None,
                                                                            VulReport.related_asset_status == u'线上',
                                                                            VulReport.related_vul_type != u'输出文档',
                                                                        ).all()
    count_vul_old_unfinish = len(data_department_vul_list_2)
    #print count_vul_old_unfinish,u'个之前未修复漏洞'

    #统计时间段之前发现的漏洞，至今已修复的漏洞（包括在统计时间段内修复的，和统计时间段之后修复的）
    data_department_vul_list_3 = db.session.query( Asset.department, VulReport.id, VulReport.risk_score, VulReport.start_date, VulReport.fix_date).filter(
                                                                            Asset.in_or_out == u'外网',
                                                                            Asset.status == u'线上',
                                                                            Asset.sec_owner != '',
                                                                            VulReport.related_asset == Asset.domain,
                                                                            VulReport.start_date < startDate,
                                                                            VulReport.fix_date >= startDate,
                                                                            #VulReport.fix_date <= endDate,
                                                                            VulReport.related_asset_status == u'线上',
                                                                            VulReport.related_vul_type != u'输出文档',
                                                                        ).all()
    count_vul_old_finished = len(data_department_vul_list_3)
    #print count_vul_old_finished,u'个之前漏洞当月修复'

    #统计时间段内新增漏洞产生的风险值计算
    data_department_risk_new = {}
    risk_all_new = 0
    for vul in data_department_vul_list:
        if (vul[4] is not None) and (vul[4] <= endDate):
            days = ((vul[4]-vul[3]).days + 1)
        else:
            days = (endDate-vul[3]).days + 1
        risk = days * vul[2]
        risk_all_new += risk
        if data_department_risk_new.has_key(vul[0]):
            data_department_risk_new[vul[0]] += risk
        else:
            data_department_risk_new.update({vul[0]: risk})
    

    #统计时间段内产生的总风险值计算（包括统计时间段内新增漏洞产生的风险，统计时间段之前产生的漏洞至今未修复的，统计时间段之前产生的漏洞在统计开始日期后已修复的）
    data_department_risk_all = data_department_risk_new.copy()
    risk_all = risk_all_new
    #data_department_risk = {}
    #risk_all = 0
    #开始日期前通告的漏洞，到这个时间段才修复的，或者没有修复的
    data_department_vul_list_2_3 = data_department_vul_list_2 + data_department_vul_list_3
    for vul in data_department_vul_list_2_3:
        if (vul[4] is not None) and (startDate <= vul[4] <= endDate):
            #print u'================之前漏洞当月修复=============='
            #print vul[0]
            #print vul[1]
            days = ((vul[4]-startDate).days + 1)
            #print days,u'天'
        elif (vul[4] is None) or (vul[4] > endDate):
            #print u'======================之前漏洞未修复，和之前漏洞在统计时间段后修复的================='
            #print vul[0]
            #print vul[1]
            days = (endDate - startDate).days + 1
            #print days,u'天'
        else:
            continue
        risk = days * vul[2]
        #print risk,u'分'
        risk_all += risk
        if data_department_risk_all.has_key(vul[0]):
            data_department_risk_all[vul[0]] += risk
        else:
            data_department_risk_all.update({vul[0]: risk})


    data_department_risk_new = sorted(data_department_risk_new.iteritems(), key=lambda d:d[1], reverse = True)        
    data_department_risk_all = sorted(data_department_risk_all.iteritems(), key=lambda d:d[1], reverse = True)        
    data_department_vul_count_all = sorted(data_department_vul_count_all.iteritems(), key=lambda d:d[1], reverse = True)



    return render_template('depart_risk_stat.html',
                            startDate = startDate,
                            endDate = endDate,
                            count_asset = count_asset,
                            count_vul_new = count_vul_new,
                            count_vul_new_unfinish = count_vul_new_unfinish,
                            count_vul_new_finished = count_vul_new_finished,
                            count_vul_old_unfinish = count_vul_old_unfinish,
                            count_vul_old_finished = count_vul_old_finished,
                            risk_all_new = risk_all_new,
                            risk_all = risk_all,
                            data_department_vul = json.dumps(data_department_vul, encoding='utf-8', indent=4),
                            data_department_vul_count_all = json.dumps(data_department_vul_count_all, encoding='utf-8', indent=4),
                            depart_asset_stat = json.dumps(depart_asset_stat, encoding='utf-8', indent=4),
                            data_department_risk_new = json.dumps(data_department_risk_new, encoding='utf-8', indent=4),
                            data_department_risk_all = json.dumps(data_department_risk_all, encoding='utf-8', indent=4),
                        )



@main.route('/')
@main.route('/<start_date>/<end_date>')
def index(start_date=0, end_date=0):
    try:
        startDate = datetime.datetime.strptime(start_date, '%Y%m%d')
        endDate = datetime.datetime.strptime(end_date, '%Y%m%d')
    except:
        startDate = datetime.datetime(2015,1,1)
        endDate = datetime.datetime(2099,1,1)


    #-----------------漏洞类型数量统计-------------------
    #query = db.session.query( db.func.count(VulReport.related_vul_type), VulReport.related_vul_type ).group_by( VulReport.related_vul_type )
    query = db.session.query( db.func.count(VulReport.related_vul_type), VulReport.related_vul_type ).filter(
                                                    VulReport.start_date >= startDate,
                                                    VulReport.start_date <= endDate,
                                                    VulReport.related_vul_type != u'输出文档',
                                                ).group_by( VulReport.related_vul_type )
    print query
    list_count_vul_type = query.all()
    data_vul_type = {}
    #data = {'王昊': 150, '万杰': 200, '潘烁宇': 100}
    for i in list_count_vul_type:
        data_vul_type[i[1]] = int(i[0])
    data_vul_type = sorted(data_vul_type.iteritems(), key=lambda d:d[1], reverse = True)
    
    #-----------------漏洞状态统计------------------------
    #query = db.session.query( db.func.count(VulReport.vul_status), VulReport.vul_status ).group_by( VulReport.vul_status )
    query = db.session.query( db.func.count(VulReport.vul_status), VulReport.vul_status ).filter(
                                                    VulReport.start_date >= startDate,
                                                    VulReport.start_date <= endDate,
                                                    VulReport.related_vul_type != u'输出文档',
                                                ).group_by( VulReport.vul_status )
    list_count_vul_status = query.all()
    data_vul_status = {}
    #data = {'王昊': 150, '万杰': 200, '潘烁宇': 100}
    for i in list_count_vul_status:
        data_vul_status[i[1]] = int(i[0])

    count_vul = 0
    for i in list_count_vul_status:
        count_vul += int(i[0])


    #-----------------漏洞来源统计------------------------
    #query = db.session.query( db.func.count(VulReport.vul_status), VulReport.vul_status ).group_by( VulReport.vul_status )
    query = db.session.query( db.func.count(VulReport.vul_source), VulReport.vul_source ).filter(
                                                    VulReport.start_date >= startDate,
                                                    VulReport.start_date <= endDate,
                                                    VulReport.related_vul_type != u'输出文档',
                                                ).group_by( VulReport.vul_source )
    list_count_vul_source = query.all()
    data_vul_source = {}
    #data = {'王昊': 150, '万杰': 200, '潘烁宇': 100}
    for i in list_count_vul_source:
        data_vul_source[i[1]] = int(i[0])


    #-----------------资产漏洞数量统计-------------------
    #query = db.session.query( db.func.count(VulReport.related_asset), VulReport.related_asset ).group_by( VulReport.related_asset )
    query = db.session.query( db.func.count(VulReport.related_asset), VulReport.related_asset ).filter(
                                                    VulReport.start_date >= startDate,
                                                    VulReport.start_date <= endDate,
                                                    VulReport.related_vul_type != u'输出文档',
                                                ).group_by( VulReport.related_asset )
    list_count_related_asset = query.all()
    data_related_asset = {}
    #data = {'王昊': 150, '万杰': 200, '潘烁宇': 100}
    for i in list_count_related_asset:
        data_related_asset[i[1]] = int(i[0])
    data_related_asset = sorted(data_related_asset.iteritems(), key=lambda d:d[1], reverse = True)


    #-----------------资产逾期已修复漏洞数量统计-------------------
    #query = db.session.query( db.func.count(VulReport.related_asset), VulReport.related_asset ).group_by( VulReport.related_asset )
    query = db.session.query( db.func.count(VulReport.related_asset), VulReport.related_asset ).filter(
                                                    VulReport.start_date >= startDate,
                                                    VulReport.start_date <= endDate,
                                                    VulReport.vul_status == u'完成',
                                                    VulReport.fix_date > VulReport.end_date,
                                                    VulReport.related_vul_type != u'输出文档',
                                                ).group_by( VulReport.related_asset )
    list_count_related_asset_timeout = query.all()
    data_related_asset_timeout = {}
    #data = {'王昊': 150, '万杰': 200, '潘烁宇': 100}
    for i in list_count_related_asset_timeout:
        data_related_asset_timeout[i[1]] = int(i[0])
    data_related_asset_timeout = sorted(data_related_asset_timeout.iteritems(), key=lambda d:d[1], reverse = True)


    #-----------------资产逾期未修复漏洞数量统计-------------------
    #query = db.session.query( db.func.count(VulReport.related_asset), VulReport.related_asset ).group_by( VulReport.related_asset )
    query = db.session.query( db.func.count(VulReport.related_asset), VulReport.related_asset ).filter(
                                                    VulReport.start_date >= startDate,
                                                    VulReport.start_date <= endDate,
                                                    VulReport.vul_status != u'完成',
                                                    datetime.date.today() > VulReport.end_date,
                                                    VulReport.related_vul_type != u'输出文档',
                                                ).group_by( VulReport.related_asset )
    list_count_related_asset_timeout_unfinish = query.all()
    data_related_asset_timeout_unfinish = {}
    #data = {'王昊': 150, '万杰': 200, '潘烁宇': 100}
    for i in list_count_related_asset_timeout_unfinish:
        data_related_asset_timeout_unfinish[i[1]] = int(i[0])
    data_related_asset_timeout_unfinish = sorted(data_related_asset_timeout_unfinish.iteritems(), key=lambda d:d[1], reverse = True)


    #---------------部门漏洞数量--------------------
    #query = db.session.query( db.func.count(Asset.department), Asset.department ).filter(VulReport.related_asset == Asset.domain).group_by( Asset.department )
    query = db.session.query( db.func.count(Asset.department), Asset.department ).filter(
                                                                            VulReport.related_asset == Asset.domain,
                                                                            VulReport.start_date >= startDate,
                                                                            VulReport.start_date <= endDate,
                                                                            VulReport.related_vul_type != u'输出文档',
                                                                        ).group_by( Asset.department )
    
    list_count_department_vul = query.order_by(-db.func.count(Asset.department)).all()
    data_department_vul = {}
    for i in list_count_department_vul:
        data_department_vul[i[1]] = int(i[0])
    data_department_vul = sorted(data_department_vul.iteritems(), key=lambda d:d[1], reverse = True)


    #-------------------剩余风险变化趋势---------------------
    

    #-----------------部门有剩余风险的漏洞数量------------------
    #query = db.session.query( db.func.count(Asset.department), Asset.department ).filter(VulReport.related_asset == Asset.domain,
    #                        VulReport.residual_risk_score != 0).group_by( Asset.department)
    query = db.session.query( db.func.count(Asset.department), Asset.department ).filter(
                                                                        VulReport.related_asset == Asset.domain,
                                                                        VulReport.residual_risk_score != 0,
                                                                        VulReport.start_date >= startDate,
                                                                        VulReport.start_date <= endDate,
                                                                        VulReport.related_vul_type != u'输出文档',
                                                                ).group_by( Asset.department)
    list_count_department_risk_vul = query.order_by(-db.func.count(Asset.department)).all()
    data_department_risk_vul = {}
    for i in list_count_department_risk_vul:
        data_department_risk_vul[i[1]] = int(i[0])
    data_department_risk_vul = sorted(data_department_risk_vul.iteritems(), key=lambda d:d[1], reverse = True)

    #-----------------部门的剩余风险值---------------------
    #query = db.session.query( VulReport.residual_risk_score, Asset.department ).filter(VulReport.related_asset == Asset.domain,
    #                        VulReport.residual_risk_score != 0)
    query = db.session.query( VulReport.residual_risk_score, Asset.department ).filter(
                                                                        VulReport.related_asset == Asset.domain,
                                                                        VulReport.residual_risk_score != 0,
                                                                        VulReport.start_date >= startDate,
                                                                        VulReport.start_date <= endDate,
                                                                        VulReport.related_vul_type != u'输出文档',
                                                                    )
    data_department_residual_risk = {}
    for depart in list_count_department_risk_vul:
        depart_list = query.filter(Asset.department == depart[1]).all()
        residual_risk = float(0)
        for r in depart_list:
            residual_risk += float(r[0])
        data_department_residual_risk[depart[1]] = float(residual_risk)
    data_department_residual_risk = sorted(data_department_residual_risk.iteritems(), key=lambda d:d[1], reverse = True)    



    return render_template('index.html', data_vul_type=json.dumps(data_vul_type, encoding='utf-8', indent=4),
                            data_vul_status = json.dumps(data_vul_status, encoding='utf-8', indent=4),
                            count_vul = count_vul,
                            data_vul_source = json.dumps(data_vul_source, encoding='utf-8', indent=4),
                            data_related_asset = json.dumps(data_related_asset, encoding='utf-8', indent=4),
                            count_asset = len(list_count_related_asset),
                            data_related_asset_timeout = json.dumps(data_related_asset_timeout, encoding='utf-8', indent=4),
                            count_asset_timeout = len(list_count_related_asset_timeout),
                            data_related_asset_timeout_unfinish = json.dumps(data_related_asset_timeout_unfinish, encoding='utf-8', indent=4),
                            count_asset_timeout_unfinish = len(list_count_related_asset_timeout_unfinish),
                            data_department_vul = json.dumps(data_department_vul, encoding='utf-8', indent=4),
                            data_department_risk_vul = json.dumps(data_department_risk_vul, encoding='utf-8', indent=4),
                            data_department_residual_risk = json.dumps(data_department_residual_risk, encoding='utf-8', indent=4),
                        )




@main.route('/index_count/')
@main.route('/index_count/<start_date>/<end_date>')
@permission_required('main.index_count')
def index_count(start_date=0, end_date=0):
    try:
        startDate = datetime.datetime.strptime(start_date, '%Y%m%d')
        endDate = datetime.datetime.strptime(end_date, '%Y%m%d')
    except:
        startDate = datetime.datetime(2015,1,1)
        endDate = datetime.datetime(2099,1,1)


    query = db.session.query(VulReport, Asset).filter(VulReport.related_asset==Asset.domain,
                                                            #VulReport.related_asset_status!=u'上线前',
                                                            VulReport.related_vul_type!=u'输出文档',
                                                            VulReport.start_date >= startDate,
                                                            VulReport.start_date <= endDate,
                                                        )
    vul_report_list_result = query.order_by(-VulReport.start_date).all()


    list_asset = []
    list_department = []
    for vul_asset in vul_report_list_result:
        if vul_asset[0].fix_date:
            if vul_asset[0].fix_date > vul_asset[0].end_date:
                vul_asset[0].timeout = u'逾期'
        else:
            if datetime.date.today() > vul_asset[0].end_date:
                vul_asset[0].timeout = u'逾期'

        if vul_asset[1].domain not in list_asset:
            list_asset.append(vul_asset[1].domain)

        if vul_asset[1].department not in list_department:
            list_department.append(vul_asset[1].department)
    
    list_result_sort_asset = []
    for asset in list_asset:
        for vul_asset in vul_report_list_result:
            if vul_asset[1].domain == asset:
                list_result_sort_asset.append(vul_asset)

    list_result_sort_department = []
    for department in list_department:
        for vul_asset in list_result_sort_asset:
            if vul_asset[1].department == department:
                list_result_sort_department.append(vul_asset)


    return render_template('index_count.html', vul_report_list_result = list_result_sort_department)


@main.route('/index_stats_time/')
@main.route('/index_stats_time/<start_date>/<end_date>')
@permission_required('main.index_stats_time')
def index_stats_time(start_date='20171101', end_date='20990101'):
    try:
        startDate = datetime.datetime.strptime(start_date, '%Y%m%d')
        endDate = datetime.datetime.strptime(end_date, '%Y%m%d')
    except:
        startDate = datetime.datetime(2017,1,1)
        endDate = datetime.datetime(2099,1,1)

    #计算所有漏洞的已知悉时间
    query = db.session.query(VulReport, Asset).filter(VulReport.related_asset==Asset.domain,
                                                            #VulReport.related_asset_status!=u'上线前',
                                                            VulReport.related_vul_type!=u'输出文档',
                                                            VulReport.start_date >= startDate,
                                                            VulReport.start_date <= endDate,
                                                        )

    vul_report_list_result = query.order_by(-VulReport.start_date).all()

    #统计漏洞处理时间数据列表
    list_stats_time = []
    list_stats_retest_time = []
    #加入所有漏洞统计数据
    list_stats_time.append(compute_take_time('all', vul_report_list_result))
    list_stats_retest_time.append(compute_retest_time('all', vul_report_list_result))


    #统计漏洞作者姓名
    author_list = []
    for vulreport, asset in vul_report_list_result:
        if vulreport.author not in author_list:
            author_list.append(vulreport.author)

    #print author_list

    
    for author in author_list:
        query = db.session.query(VulReport, Asset).filter(VulReport.related_asset==Asset.domain,
                                                            #VulReport.related_asset_status!=u'上线前',
                                                            VulReport.related_vul_type!=u'输出文档',
                                                            VulReport.start_date >= startDate,
                                                            VulReport.start_date <= endDate,
                                                            VulReport.author == author,
                                                        )

        vul_report_list_result = query.order_by(-VulReport.start_date).all()
        
        list_stats_time.append(compute_take_time(author, vul_report_list_result))
        list_stats_retest_time.append(compute_retest_time(author, vul_report_list_result))



    return render_template('index_stats_time.html', 
                            list_stats_time = list_stats_time,
                            list_stats_retest_time = list_stats_retest_time,
                        )


def compute_take_time(author, vul_report_list_result):
    #print 'author: ', author
    vul_known_take_time_list = []
    for vulreport, asset in vul_report_list_result:
        #print vulreport.id
        #print asset.id
        vul_logs = VulLog.query.filter_by(related_vul_id = vulreport.id)
        if vul_logs.first():
            vul_known_take_time = 0
            vul_known_time_start = 0
            vul_known_time_end = 0
            for vul_log in vul_logs:
                if vul_log.action == u'发送新漏洞通告':
                    vul_known_time_start = vul_log.time
                if vul_log.action == u'已知悉':
                    vul_known_time_end = vul_log.time
            #print 'vul_log_related_vul_id: ', vul_log.related_vul_id
            #print 'vul_known_time_start: ', vul_known_time_start
            #print 'vul_known_time_end: ', vul_known_time_end
            if vul_known_time_start != 0 and vul_known_time_end !=0:
                #start_datetime = datetime.strptime(vul_known_time_start, "%Y-%m-%d %H:%M:%S")
                #end_datetime = datetime.strptime(vul_known_time_end, "%Y-%m-%d %H:%M:%S")
                vul_known_take_time = (vul_known_time_end - vul_known_time_start).seconds
                #print 'known_datetime: ', known_datetime
                vul_known_take_time_list.append(vul_known_take_time)

    count = len(vul_known_take_time_list)
    #print '统计已知悉漏洞数量: %d 个' %count
    if count != 0:
        max_time = round(max(vul_known_take_time_list) / 60.0 / 60.0, 2)
        min_time = round(min(vul_known_take_time_list) / 60.0 / 60.0, 2)
        #print '最大值: %s 小时' % str(max_time)
        #print '最小值: %s 小时' % str(min_time)

        time_sum = 0
        for take_time in vul_known_take_time_list:
            time_sum += take_time

        #print '总和: %d 秒' %time_sum
        averge_time = round((time_sum / count) / 60.0 / 60.0, 2)
        #print '平均值: %s 小时' % str(averge_time)
    else:
        max_time = 0
        min_time = 0
        averge_time = 0

    return author, count, max_time, min_time, averge_time



def compute_retest_time(author, vul_report_list_result):
    #print 'author: ', author
    vul_retest_time_list = []
    for vulreport, asset in vul_report_list_result:
        #print vulreport.id
        #print asset.id
        vul_logs = VulLog.query.filter_by(related_vul_id = vulreport.id)
        if vul_logs.first():
            vul_retest_time = 0
            vul_retest_time_start = 0
            vul_retest_time_end = 0
            for vul_log in vul_logs:
                if vul_log.action == u'申请复测':
                    vul_retest_time_start = vul_log.time
                if vul_log.action == u'复测结果提交':
                    vul_retest_time_end = vul_log.time
                    vul_retest_time = (vul_retest_time_end - vul_retest_time_start).seconds
                    # 如果超过14个小时，认为是下班后申请，减去晚上休息时间14个小时。
                    #if 223200 > vul_retest_time > 50400:
                    #    vul_retest_time -= 50400
                    # 如果超过2天，认为是周末，减去62个小时，24+24+14=62
                    #elif vul_retest_time >= 223200:
                    #    vul_retest_time -= 223200
                    vul_retest_time_list.append(vul_retest_time)

    count = len(vul_retest_time_list)
    #print '统计复测漏洞数量: %d 个' %count
    if count != 0:
        max_time = round(max(vul_retest_time_list) / 60.0 / 60.0, 2)
        min_time = round(min(vul_retest_time_list) / 60.0 / 60.0, 2)
        #print '最大值: %s 小时' % str(max_time)
        #print '最小值: %s 小时' % str(min_time)

        time_sum = 0
        for take_time in vul_retest_time_list:
            time_sum += take_time

        #print '总和: %d 秒' %time_sum
        averge_time = round((time_sum / count) / 60.0 / 60.0, 2)
        #print '平均值: %s 小时' % str(averge_time)
    else:
        max_time = 0
        min_time = 0
        averge_time = 0

    return author, count, max_time, min_time, averge_time


"""
@main.route('/asset_sec_score_stat', methods=['GET','POST'])
@main.route('/asset_sec_score_stat/<start_date>/<end_date>', methods=['GET','POST'])
@permission_required('main.asset_sec_score_stat')
def asset_sec_score_stat(start_date=0, end_date=0):
    #opt = request.args.get('opt','all')
    try:
        startDate = datetime.date(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:8]))
        endDate = datetime.date(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8]))
    except:
        startDate = datetime.date(2017,1,1)
        endDate = datetime.date.today()




    #后面计算每个应用的安全能力分使用
    date_one = getFirstDayOfMonth(endDate)


    asset_list = Asset.query.filter(
                                Asset.sec_owner!='',
                                Asset.business_cata!='',
                                Asset.create_date!='',
                                Asset.create_date<date_one,
                            ).all()

    #print '--------------------len(asset_list)-----------'
    asset_count = len(asset_list)
    #print len(asset_list)


    today = endDate
    list_date = []
    ing_date = getFirstDayOfMonth(today)
    list_date.append(ing_date.strftime('%Y%m%d'))


    for i in range(5):
        ing_date = getFirstDayOfLastMonth(ing_date)
        list_date.append(ing_date.strftime('%Y%m%d'))

    list_date.reverse()
    #print '----list_date------'
    #print list_date

    data_asset_count_all = []
    data_sec_score_all = []
    data_code_score_all = []
    data_ops_score_all = []
    data_attack_score_all = []

    data_sec_score_add_month = []

    last_month = ()
    for i_date in list_date:
        endDate = datetime.date(int(i_date[0:4]), int(i_date[4:6]), int(i_date[6:8]))
        file_exsit = os.path.isfile('tmp/all_'+endDate.strftime('%Y%m%d'))
        #print '-------file_exsit-------'
        if file_exsit:
            with open('tmp/all_'+endDate.strftime('%Y%m%d')) as f:
                list1 = f.read().split(',')
                (s,c,o,a,l) = (float(list1[0]),float(list1[1]),float(list1[2]),float(list1[3]),int(list1[4]))
                #print '-----s,c,o,a------'
                #print str(i_date[4:6])+u'月'
                #print s,c,o,a
            data_sec_score_all.append((str(i_date[4:6])+u'月',s))
            data_code_score_all.append((str(i_date[4:6])+u'月',c))
            data_ops_score_all.append((str(i_date[4:6])+u'月',o))
            data_attack_score_all.append((str(i_date[4:6])+u'月',a))
            data_asset_count_all.append((str(i_date[4:6])+u'月',l))

            now_month = (s,c,o,a,l)

            if len(last_month):
                year = int(i_date[0:4])
                month = 12 if int(i_date[4:6])==1 else int(i_date[4:6])-1
                days = calendar.monthrange(year,month)[1]
                full_score = 0.3*days
                data_sec_score_add_month.append((str(i_date[4:6])+u'月',round((now_month[0] - last_month[0])/full_score*100,2)))
            last_month = now_month

        else:
            '''
            app = current_app._get_current_object()
            thr = Thread(target=async_get_asset_score_all, args=[app,asset_list,startDate,endDate])
            thr.start()
            return u'计算中'
            '''
            asset_list = Asset.query.filter(
                                Asset.sec_owner!='',
                                Asset.business_cata!='',
                                Asset.create_date!='',
                                Asset.create_date<endDate,
                            ).all()
            get_asset_score_all(asset_list,startDate,endDate)
        #(s,c,o,a) = get_asset_score_all(asset_list,startDate,endDate)


    #print '--------------------'
    #print data_sec_score_all
    #print data_code_score_all
    #print data_ops_score_all
    #print data_attack_score_all
    #print data_sec_score_add_month




    #asset_code_score = get_asset_code_score(opt,startDate,endDate,u'代码层面')



    #-------------------计算每个应用的安全能力分排名 start----------------------
    data_score_lv_count = {
                            u'一级安全能力' : 0,
                            u'二级安全能力' : 0,
                            u'三级安全能力' : 0,
                            u'四级安全能力' : 0,
                            u'五级安全能力' : 0,
                        }

    data_domain_score = {}
    file_domain_date_one = os.path.isfile('tmp/domain_'+date_one.strftime('%Y%m%d'))
    if file_domain_date_one:
        with open('tmp/domain_'+date_one.strftime('%Y%m%d')) as f:
            list_domain_score = f.readlines()
        
        for domain_score in list_domain_score:
            #print domain_score
            domain = domain_score.split(',')[0]
            sec_score = domain_score.split(',')[1]
            data_domain_score.update({domain:float(sec_score)})


            if float(sec_score)<=25:
                data_score_lv_count[u'一级安全能力'] += 1
            elif 25<float(sec_score)<=50:
                data_score_lv_count[u'二级安全能力'] += 1
            elif 50<float(sec_score)<=75:
                data_score_lv_count[u'三级安全能力'] += 1
            elif 75<float(sec_score)<100:
                data_score_lv_count[u'四级安全能力'] += 1
            elif float(sec_score)>=100:
                data_score_lv_count[u'五级安全能力'] += 1


    data_domain_score = sorted(data_domain_score.iteritems(), key=lambda d:d[1], reverse = False)[:30]

#-------------------计算每个应用的安全能力分排名 end------------------------
    
    return render_template('asset_sec_score_stat.html',
                            asset_count = asset_count,
                            month = date_one.strftime('%Y%m%d'),
                            data_asset_count_all=json.dumps(data_asset_count_all),
                            data_sec_score_all=json.dumps(data_sec_score_all),
                            data_code_score_all=json.dumps(data_code_score_all),
                            data_ops_score_all=json.dumps(data_ops_score_all),
                            data_attack_score_all=json.dumps(data_attack_score_all),
                            data_domain_score=json.dumps(data_domain_score),
                            data_sec_score_add_month=json.dumps(data_sec_score_add_month),
                            data_score_lv_count=json.dumps(data_score_lv_count),
                            )
"""



"""
def get_asset_score_all(asset_list,startDate,endDate):
    asset_count = len(asset_list)
    asset_sec_score_all = 0
    asset_code_score_all = 0
    asset_ops_score_all = 0
    asset_attack_score_all = 0

    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    f_domain_score = open('tmp/domain_'+endDate.strftime('%Y%m%d'),'w')
    for asset in asset_list:
        f_domain_score.write(asset.domain)

        asset_sec_score = get_asset_sec_score(asset.domain,startDate,endDate)
        asset_sec_score_all += asset_sec_score
        f_domain_score.write(','+str(asset_sec_score))


        asset_code_score = get_asset_code_score(asset.domain,startDate,endDate,u'代码层面')
        asset_code_score_all += asset_code_score
        f_domain_score.write(','+str(asset_code_score))

        asset_ops_score = get_asset_code_score(asset.domain,startDate,endDate,u'运维层面')
        asset_ops_score_all += asset_ops_score
        f_domain_score.write(','+str(asset_ops_score))

        asset_attack_score = get_asset_attack_score(asset.domain,startDate,endDate)
        asset_attack_score_all += asset_attack_score
        f_domain_score.write(','+str(asset_attack_score)+'\n')
    f_domain_score.close()

    with open('tmp/all_'+endDate.strftime('%Y%m%d'),'w') as f:
        f.write(
                str(round(asset_sec_score_all/asset_count,2))
                +','+str(round(asset_code_score_all/asset_count,2))
                +','+str(round(asset_ops_score_all/asset_count,2))
                +','+str(round(asset_attack_score_all/asset_count,2))
                +','+str(asset_count)
            )
"""

"""
获取前一个月的第一天
def getFirstDayOfLastMonth(v_date):
    d = v_date
    #c = calendar.Calendar()
     
    year = d.year
    month = d.month
     
    if month == 1 :
        month = 12
        year -= 1
    else :
        month -= 1
    return datetime.datetime(year,month,1)


#获取当前月的第一天
def getFirstDayOfMonth(v_date):
    d = v_date
    #c = calendar.Calendar()
     
    year = d.year
    month = d.month

    return datetime.datetime(year,month,1)
"""

"""
@main.route('/month_every_asset_score', methods=['GET','POST'])
@main.route('/month_every_asset_score/<end_date>', methods=['GET','POST'])
@permission_required('main.month_every_asset_score')
def month_every_asset_score(end_date=0):
    #opt = request.args.get('opt','all')
    try:
        endDate = datetime.date(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8]))
    except:
        endDate = datetime.date.today()

    now_month = getFirstDayOfMonth(endDate)
    last_month = getFirstDayOfLastMonth(endDate)


    #-------------------计算每个应用的安全能力增长分排名 start----------------------
    data_month_domain_score = {}
    data_month_code_score = {}
    data_month_ops_score = {}
    data_month_attack_score = {}

    data_now_month_score = {}
    data_last_month_score  = {}
    file_domain_now_month = os.path.isfile('tmp/domain_'+now_month.strftime('%Y%m%d'))
    file_domain_last_month = os.path.isfile('tmp/domain_'+last_month.strftime('%Y%m%d'))
    if file_domain_now_month and file_domain_last_month:
        with open('tmp/domain_'+now_month.strftime('%Y%m%d')) as f:
            list_now_month_score = f.readlines()
        for now_month_score in list_now_month_score:
            #print domain_score
            domain = now_month_score.split(',')[0]
            sec_score = now_month_score.split(',')[1]
            code_score = now_month_score.split(',')[2]
            ops_score = now_month_score.split(',')[3]
            attack_score = now_month_score.split(',')[4]
            data_now_month_score.update({domain:(float(sec_score),float(code_score),float(ops_score),float(attack_score))})

        with open('tmp/domain_'+last_month.strftime('%Y%m%d')) as f:
            list_last_month_score = f.readlines()
        for last_month_score in list_last_month_score:
            #print domain_score
            domain = last_month_score.split(',')[0]
            sec_score = last_month_score.split(',')[1]
            code_score = last_month_score.split(',')[2]
            ops_score = last_month_score.split(',')[3]
            attack_score = last_month_score.split(',')[4]
            data_last_month_score.update({domain:(float(sec_score),float(code_score),float(ops_score),float(attack_score))})

        year = last_month.year
        month = last_month.month
        days = calendar.monthrange(year,month)[1]
        full_score = 0.3*days
        for domain,score in data_now_month_score.items():
            data_month_domain_score.update({ domain: round((score[0]-data_last_month_score[domain][0])/full_score*100,2) })
            data_month_code_score.update({ domain: round((score[1]-data_last_month_score[domain][1])/full_score*100,2) })
            data_month_ops_score.update({ domain: round((score[2]-data_last_month_score[domain][2])/full_score*100,2) })
            data_month_attack_score.update({ domain: round((score[3]-data_last_month_score[domain][3])/full_score*100,2) })
    else:
        data_month_domain_score = {}
        data_month_code_score = {}
        data_month_ops_score = {}
        data_month_attack_score = {}


    data_month_domain_score = sorted(data_month_domain_score.iteritems(), key=lambda d:d[1], reverse = False)
    data_month_domain_score = data_month_domain_score[:30]

    data_month_code_score = sorted(data_month_code_score.iteritems(), key=lambda d:d[1], reverse = False)
    data_month_code_score = data_month_code_score[:30]

    data_month_ops_score = sorted(data_month_ops_score.iteritems(), key=lambda d:d[1], reverse = False)
    data_month_ops_score = data_month_ops_score[:30]

    data_month_attack_score = sorted(data_month_attack_score.iteritems(), key=lambda d:d[1], reverse = False)
    data_month_attack_score = data_month_attack_score[:30]


    return render_template('month_every_asset_score.html',
                            data_month_domain_score=json.dumps(data_month_domain_score),
                            data_month_code_score=json.dumps(data_month_code_score),
                            data_month_ops_score=json.dumps(data_month_ops_score),
                            data_month_attack_score=json.dumps(data_month_attack_score),
                            month = last_month.strftime('%Y%m%d')+'--'+now_month.strftime('%Y%m%d'),
                            )
"""


@main.route('/asset_score_stat', methods=['GET','POST'])
@main.route('/asset_score_stat/<start_date>/<end_date>', methods=['GET','POST'])
def asset_score_stat(start_date='20170101',end_date=datetime.date.today):
    #opt = request.args.get('opt','all')
    try:
        startDate = datetime.date(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:8]))
        endDate = datetime.date(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8]))
    except:
        startDate = datetime.date(2017,1,1)
        endDate = datetime.date.today()

    #最后一天的应用安全分记录
    last_asset_score = AssetScore.query.filter(AssetScore.score_cata==u'应用安全能力').order_by(-AssetScore.id).limit(1).first()

    #计算时间段
    if last_asset_score:
        last_date = last_asset_score.score_date
        if last_date < datetime.date.today():
            date_asset_sec_score('sec')
        if last_date < endDate:
            endDate = last_date
    else:
        date_asset_sec_score('sec')



    #应用的平均分排名
    query = db.session.query(AssetScore.domain,db.func.avg(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'应用安全能力',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= startDate,
                                                    AssetScore.score_date <= endDate,   
                                                    ).group_by(
                                                        AssetScore.domain
                                                        ).order_by(db.func.avg(AssetScore.score))


    list_asset_score = query.all()
    #for asset in list_asset_score:
    #    print asset[0],round(asset[1],2)

    #应用的最低分排名
    query = db.session.query(AssetScore.domain,db.func.min(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'应用安全能力',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= startDate,
                                                    AssetScore.score_date <= endDate,   
                                                    ).group_by(
                                                        AssetScore.domain
                                                        ).order_by(db.func.min(AssetScore.score))
    list_asset_min_score = query.all()


    #应用的每周安全最低分
    list_asset_week_min_score = []
    for start,end in date_range(startDate,endDate,7):
        #print start.strftime('%Y%m%d'),end.strftime('%Y%m%d')
        query = db.session.query(db.func.min(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'应用安全能力',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= start,
                                                    AssetScore.score_date <= end,   
                                                    )
        list_asset_week_min_score.append((end.strftime('%Y%m%d')+' ',query.first()))


    #-------------------计算应用安全能力分布 start----------------------
    data_score_lv_count = {
                            u'一级安全能力' : 0,
                            u'二级安全能力' : 0,
                            u'三级安全能力' : 0,
                            u'四级安全能力' : 0,
                            u'五级安全能力' : 0,
                        }

    for domain_score in list_asset_score:
        #print domain_score
        domain = domain_score[0]
        sec_score = domain_score[1]


        if float(sec_score)<=25:
            data_score_lv_count[u'一级安全能力'] += 1
        elif 25<float(sec_score)<=50:
            data_score_lv_count[u'二级安全能力'] += 1
        elif 50<float(sec_score)<=75:
            data_score_lv_count[u'三级安全能力'] += 1
        elif 75<float(sec_score)<100:
            data_score_lv_count[u'四级安全能力'] += 1
        elif float(sec_score)>=100:
            data_score_lv_count[u'五级安全能力'] += 1    


    return render_template('asset_score_stat.html',
                            startDate=startDate,
                            endDate=endDate,
                            asset_count=len(list_asset_score),
                            list_asset_score=json.dumps(list_asset_score[:30]),
                            list_asset_min_score=json.dumps(list_asset_min_score[:30]),
                            list_asset_week_min_score=json.dumps(list_asset_week_min_score),
                            data_score_lv_count = json.dumps(data_score_lv_count),
                            )


def date_range(start_date,end_date,n):
    #start_date = start_date-datetime.timedelta(1)
    while start_date+datetime.timedelta(n) < end_date:
        week_date = start_date+datetime.timedelta(n)
        r_start_date = start_date
        start_date = week_date
        yield r_start_date,week_date-datetime.timedelta(1)



@main.route('/asset_code_score_stat', methods=['GET','POST'])
@main.route('/asset_code_score_stat/<start_date>/<end_date>', methods=['GET','POST'])
def asset_code_score_stat(start_date='20170101',end_date=datetime.date.today):
    #opt = request.args.get('opt','all')
    try:
        startDate = datetime.date(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:8]))
        endDate = datetime.date(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8]))
    except:
        startDate = datetime.date(2017,1,1)
        endDate = datetime.date.today()

    #最后一天的应用安全分记录
    last_asset_code_score = AssetScore.query.filter(AssetScore.score_cata==u'代码安全能力').order_by(-AssetScore.id).limit(1).first()

    #计算时间段
    if last_asset_code_score:
        last_date = last_asset_code_score.score_date
        if last_date < datetime.date.today():
            date_asset_sec_score('code')
        if last_date < endDate:
            endDate = last_date
    else:
        date_asset_sec_score('code')



    #应用的平均代码安全分排名
    query = db.session.query(AssetScore.domain,db.func.avg(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'代码安全能力',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= startDate,
                                                    AssetScore.score_date <= endDate,   
                                                    ).group_by(
                                                        AssetScore.domain
                                                        ).order_by(db.func.avg(AssetScore.score))


    list_asset_code_score = query.all()
    #for asset in list_asset_score:
    #    print asset[0],round(asset[1],2)

    #应用的最低代码安全分排名
    query = db.session.query(AssetScore.domain,db.func.min(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'代码安全能力',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= startDate,
                                                    AssetScore.score_date <= endDate,   
                                                    ).group_by(
                                                        AssetScore.domain
                                                        ).order_by(db.func.min(AssetScore.score))
    list_asset_min_code_score = query.all()


    #应用的每周代码安全最低分
    list_asset_week_min_code_score = []
    for start,end in date_range(startDate,endDate,7):
        #print start.strftime('%Y%m%d'),end.strftime('%Y%m%d')
        query = db.session.query(db.func.min(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'代码安全能力',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= start,
                                                    AssetScore.score_date <= end,   
                                                    )
        list_asset_week_min_code_score.append((end.strftime('%Y%m%d')+' ',query.first()))


    #-------------------计算代码安全能力分布 start----------------------
    data_code_score_lv_count = {
                            u'一级安全能力' : 0,
                            u'二级安全能力' : 0,
                            u'三级安全能力' : 0,
                            u'四级安全能力' : 0,
                            u'五级安全能力' : 0,
                        }

    for domain_score in list_asset_code_score:
        #print domain_score
        domain = domain_score[0]
        code_score = domain_score[1]


        if float(code_score)<=25:
            data_code_score_lv_count[u'一级安全能力'] += 1
        elif 25<float(code_score)<=50:
            data_code_score_lv_count[u'二级安全能力'] += 1
        elif 50<float(code_score)<=75:
            data_code_score_lv_count[u'三级安全能力'] += 1
        elif 75<float(code_score)<100:
            data_code_score_lv_count[u'四级安全能力'] += 1
        elif float(code_score)>=100:
            data_code_score_lv_count[u'五级安全能力'] += 1    


    return render_template('asset_code_score_stat.html',
                            startDate=startDate,
                            endDate=endDate,
                            asset_count=len(list_asset_code_score),
                            list_asset_code_score=json.dumps(list_asset_code_score[:30]),
                            list_asset_min_code_score=json.dumps(list_asset_min_code_score[:30]),
                            list_asset_week_min_code_score=json.dumps(list_asset_week_min_code_score),
                            data_code_score_lv_count = json.dumps(data_code_score_lv_count),
                            )



@main.route('/asset_ops_score_stat', methods=['GET','POST'])
@main.route('/asset_ops_score_stat/<start_date>/<end_date>', methods=['GET','POST'])
def asset_ops_score_stat(start_date='20170101',end_date=datetime.date.today):
    #opt = request.args.get('opt','all')
    try:
        startDate = datetime.date(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:8]))
        endDate = datetime.date(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8]))
    except:
        startDate = datetime.date(2017,1,1)
        endDate = datetime.date.today()

    #最后一天的应用安全分记录
    last_asset_ops_score = AssetScore.query.filter(AssetScore.score_cata==u'运维安全能力').order_by(-AssetScore.id).limit(1).first()

    #计算时间段
    if last_asset_ops_score:
        last_date = last_asset_ops_score.score_date
        if last_date < datetime.date.today():
            date_asset_sec_score('ops')
        if last_date < endDate:
            endDate = last_date
    else:
        date_asset_sec_score('ops')



    #应用的平均代码安全分排名
    query = db.session.query(AssetScore.domain,db.func.avg(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'运维安全能力',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= startDate,
                                                    AssetScore.score_date <= endDate,   
                                                    ).group_by(
                                                        AssetScore.domain
                                                        ).order_by(db.func.avg(AssetScore.score))


    list_asset_ops_score = query.all()
    #for asset in list_asset_score:
    #    print asset[0],round(asset[1],2)

    #应用的最低代码安全分排名
    query = db.session.query(AssetScore.domain,db.func.min(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'运维安全能力',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= startDate,
                                                    AssetScore.score_date <= endDate,   
                                                    ).group_by(
                                                        AssetScore.domain
                                                        ).order_by(db.func.min(AssetScore.score))
    list_asset_min_ops_score = query.all()


    #应用的每周代码安全最低分
    list_asset_week_min_ops_score = []
    for start,end in date_range(startDate,endDate,7):
        #print start.strftime('%Y%m%d'),end.strftime('%Y%m%d')
        query = db.session.query(db.func.min(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'运维安全能力',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= start,
                                                    AssetScore.score_date <= end,   
                                                    )
        list_asset_week_min_ops_score.append((end.strftime('%Y%m%d')+' ',query.first()))


    #-------------------计算代码安全能力分布 start----------------------
    data_ops_score_lv_count = {
                            u'一级安全能力' : 0,
                            u'二级安全能力' : 0,
                            u'三级安全能力' : 0,
                            u'四级安全能力' : 0,
                            u'五级安全能力' : 0,
                        }

    for domain_score in list_asset_ops_score:
        #print domain_score
        domain = domain_score[0]
        ops_score = domain_score[1]


        if float(ops_score)<=25:
            data_ops_score_lv_count[u'一级安全能力'] += 1
        elif 25<float(ops_score)<=50:
            data_ops_score_lv_count[u'二级安全能力'] += 1
        elif 50<float(ops_score)<=75:
            data_ops_score_lv_count[u'三级安全能力'] += 1
        elif 75<float(ops_score)<100:
            data_ops_score_lv_count[u'四级安全能力'] += 1
        elif float(ops_score)>=100:
            data_ops_score_lv_count[u'五级安全能力'] += 1    


    return render_template('asset_ops_score_stat.html',
                            startDate=startDate,
                            endDate=endDate,
                            asset_count=len(list_asset_ops_score),
                            list_asset_ops_score=json.dumps(list_asset_ops_score[:30]),
                            list_asset_min_ops_score=json.dumps(list_asset_min_ops_score[:30]),
                            list_asset_week_min_ops_score=json.dumps(list_asset_week_min_ops_score),
                            data_ops_score_lv_count = json.dumps(data_ops_score_lv_count),
                            )



@main.route('/asset_attack_score_stat', methods=['GET','POST'])
@main.route('/asset_attack_score_stat/<start_date>/<end_date>', methods=['GET','POST'])
def asset_attack_score_stat(start_date='20170101',end_date=datetime.date.today):
    #opt = request.args.get('opt','all')
    try:
        startDate = datetime.date(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:8]))
        endDate = datetime.date(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8]))
    except:
        startDate = datetime.date(2017,1,1)
        endDate = datetime.date.today()

    #最后一天的攻击响应分记录
    last_asset_attack_score = AssetScore.query.filter(AssetScore.score_cata==u'攻击响应分').order_by(-AssetScore.id).limit(1).first()

    #最后一天的总风险分记录
    last_asset_risk_score = AssetScore.query.filter(AssetScore.score_cata==u'总风险分').order_by(-AssetScore.id).limit(1).first()

    #计算时间段
    if last_asset_attack_score:
        last_date = last_asset_attack_score.score_date
        if last_date < datetime.date.today():
            date_asset_sec_score('attack')
        if last_date < endDate:
            endDate = last_date
    else:
        date_asset_sec_score('attack')


    #计算时间段
    if last_asset_risk_score:
        last_date = last_asset_risk_score.score_date
        if last_date < datetime.date.today():
            date_asset_sec_score('risk')
        if last_date < endDate:
            endDate = last_date
    else:
        date_asset_sec_score('risk')



   

    #应用的攻击响应分排名
    query = db.session.query(AssetScore.domain,db.func.sum(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'攻击响应分',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= startDate,
                                                    AssetScore.score_date <= endDate,   
                                                    ).group_by(
                                                        AssetScore.domain
                                                        ).order_by(-db.func.sum(AssetScore.score))
    list_asset_sum_attack_score = query.all()


    #应用的每周攻击响应总分
    list_asset_week_sum_attack_score = []
    #应用的每周风险总分
    list_asset_week_sum_risk_score = []
    #应用每周攻击响应分／风险总分 占比
    list_asset_week_sum_attack_percent_score = []
    for start,end in date_range(startDate,endDate,7):
        #print start.strftime('%Y%m%d'),end.strftime('%Y%m%d')
        query_attack = db.session.query(db.func.sum(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'攻击响应分',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= start,
                                                    AssetScore.score_date <= end,   
                                                    )
        list_asset_week_sum_attack_score.append((end.strftime('%Y%m%d')+' ',query_attack.first()))

        #应用的每周风险总分
        query_risk = db.session.query(db.func.sum(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'总风险分',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= start,
                                                    AssetScore.score_date <= end,   
                                                    )
        list_asset_week_sum_risk_score.append((end.strftime('%Y%m%d')+' ',query_risk.first()))

        #应用每周攻击响应分／风险总分 占比
        if query_attack.first()[0] and query_risk.first()[0]:
            attack_percent = round(float(query_attack.first()[0])/float(query_risk.first()[0])*100,2)
            list_asset_week_sum_attack_percent_score.append((end.strftime('%Y%m%d')+' ',attack_percent))


    #应用的每周风险总分
    list_asset_week_sum_risk_score = []
    for start,end in date_range(startDate,endDate,7):
        query = db.session.query(db.func.sum(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'总风险分',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= start,
                                                    AssetScore.score_date <= end,   
                                                    )
        list_asset_week_sum_risk_score.append((end.strftime('%Y%m%d')+' ',query.first()))


    #漏洞类型-攻击响应排名
    dict_vul_type_attack_percent = {}
    #dict_vul_type_risk = {}
    dict_vul_type_attack = {}
    
    query_vul_type_attack = db.session.query(VulReport.related_vul_type, db.func.count(VulReport.related_vul_type)).filter(
                                                    VulReport.related_vul_type != u'输出文档',
                                                    VulReport.start_date >= startDate,
                                                    VulReport.start_date <= endDate,
                                                    VulReport.related_asset_status == u'线上',
                                                    #VulReport.related_asset_inout == u'外网',
                                                    VulReport.attack_check == u'是',
                                                    ).group_by(
                                                        VulReport.related_vul_type
                                                        ).order_by(
                                                            -db.func.count(VulReport.related_vul_type)
                                                            )

    for k,v in query_vul_type_attack:
        dict_vul_type_attack.update({k:v})


    query_vul_type_risk = db.session.query(VulReport.related_vul_type, db.func.count(VulReport.related_vul_type)).filter(
                                                    VulReport.related_vul_type != u'输出文档',
                                                    VulReport.start_date >= startDate,
                                                    VulReport.start_date <= endDate,
                                                    VulReport.related_asset_status == u'线上',
                                                    #VulReport.related_asset_inout == u'外网',
                                                    ).group_by(
                                                        VulReport.related_vul_type
                                                        ).order_by(
                                                            -db.func.count(VulReport.related_vul_type)
                                                            )
    for k,v in query_vul_type_risk:
        if dict_vul_type_attack.has_key(k):
            attack_percent = round(float(dict_vul_type_attack[k])/float(v)*100,2)
        else:
            attack_percent = -v
        #print attack_percent
        #attack_percent = dict_vul_type_attack[k]/v if dict_vul_type_attack.has_key(k) else 0
        #attack_percent = round(attack_percent*100,2)
        
        dict_vul_type_attack_percent.update({k:attack_percent})
        list_vul_type_attack_percent = sorted(dict_vul_type_attack_percent.iteritems(), key=lambda d:d[1], reverse = True)    




    return render_template('asset_attack_score_stat.html',
                            startDate=startDate,
                            endDate=endDate,
                            asset_count=len(list_asset_sum_attack_score),
                            #list_asset_attack_score=json.dumps(list_asset_attack_score[:30]),
                            list_asset_sum_attack_score=json.dumps(list_asset_sum_attack_score[:30]),
                            list_asset_week_sum_attack_score=json.dumps(list_asset_week_sum_attack_score),
                            list_asset_week_sum_risk_score=json.dumps(list_asset_week_sum_risk_score),
                            list_asset_week_sum_attack_percent_score=json.dumps(list_asset_week_sum_attack_percent_score),
                            list_vul_type_attack_percent=json.dumps(list_vul_type_attack_percent),
                            )


"""
@main.route('/asset_risk_score_stat', methods=['GET','POST'])
@main.route('/asset_risk_score_stat/<start_date>/<end_date>', methods=['GET','POST'])
def asset_risk_score_stat(start_date='20170101',end_date=datetime.date.today):
    #opt = request.args.get('opt','all')
    try:
        startDate = datetime.date(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:8]))
        endDate = datetime.date(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8]))
    except:
        startDate = datetime.date(2017,1,1)
        endDate = datetime.date.today()

    #最后一天的总风险分记录
    last_asset_risk_score = AssetScore.query.filter(AssetScore.score_cata==u'总风险分').order_by(-AssetScore.id).limit(1).first()

    #计算时间段
    if last_asset_risk_score:
        last_date = last_asset_risk_score.score_date
        if last_date < datetime.date.today():
            date_asset_sec_score('risk')
        if last_date < endDate:
            endDate = last_date
    else:
        date_asset_sec_score('risk')



    #应用的平均风险分排名
    query = db.session.query(AssetScore.domain,db.func.avg(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'总风险分',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= startDate,
                                                    AssetScore.score_date <= endDate,   
                                                    ).group_by(
                                                        AssetScore.domain
                                                        ).order_by(db.func.avg(AssetScore.score))


    list_asset_risk_score = query.all()
    #for asset in list_asset_score:
    #    print asset[0],round(asset[1],2)

    #应用的最低风险分排名
    query = db.session.query(AssetScore.domain,db.func.min(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'总风险分',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= startDate,
                                                    AssetScore.score_date <= endDate,   
                                                    ).group_by(
                                                        AssetScore.domain
                                                        ).order_by(db.func.min(AssetScore.score))
    list_asset_min_risk_score = query.all()


    #应用的每周风险总分
    list_asset_week_sum_risk_score = []
    for start,end in date_range(startDate,endDate,7):
        print start.strftime('%Y%m%d'),end.strftime('%Y%m%d')
        query = db.session.query(db.func.sum(AssetScore.score)).filter(
                                                    AssetScore.score_cata == u'总风险分',
                                                    AssetScore.score != -1,
                                                    AssetScore.score_date >= start,
                                                    AssetScore.score_date <= end,   
                                                    )
        list_asset_week_sum_risk_score.append((end.strftime('%Y%m%d')+' ',query.first()))


    #-------------------计算总风险分能力分布 start----------------------
    data_risk_score_lv_count = {
                            u'一级安全能力' : 0,
                            u'二级安全能力' : 0,
                            u'三级安全能力' : 0,
                            u'四级安全能力' : 0,
                            u'五级安全能力' : 0,
                        }

    for domain_score in list_asset_risk_score:
        #print domain_score
        domain = domain_score[0]
        risk_score = domain_score[1]


        if float(risk_score)<=25:
            data_risk_score_lv_count[u'一级安全能力'] += 1
        elif 25<float(risk_score)<=50:
            data_risk_score_lv_count[u'二级安全能力'] += 1
        elif 50<float(risk_score)<=75:
            data_risk_score_lv_count[u'三级安全能力'] += 1
        elif 75<float(risk_score)<100:
            data_risk_score_lv_count[u'四级安全能力'] += 1
        elif float(risk_score)>=100:
            data_risk_score_lv_count[u'五级安全能力'] += 1    


    return render_template('asset_risk_score_stat.html',
                            startDate=startDate,
                            endDate=endDate,
                            asset_count=len(list_asset_risk_score),
                            list_asset_risk_score=json.dumps(list_asset_risk_score[:30]),
                            list_asset_min_risk_score=json.dumps(list_asset_min_risk_score[:30]),
                            list_asset_week_sum_risk_score=json.dumps(list_asset_week_sum_risk_score),
                            data_risk_score_lv_count = json.dumps(data_risk_score_lv_count),
                            )
"""
