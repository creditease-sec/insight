#-*- coding:utf-8 -*-
from flask import render_template
from . import main
import chartkick
from .. import db
from ..admin.models import VulType, Asset
from ..src.models import VulReport, VulLog
from datetime import datetime
from datetime import date
import json
from ..decorators import permission_required
from ..src.views import get_asset_sec_score
from ..src.views import get_asset_code_score
from ..src.views import get_asset_attack_score




@main.route('/')
@main.route('/<start_date>/<end_date>')
def index(start_date=0, end_date=0):
    try:
        startDate = datetime.strptime(start_date, '%Y%m%d')
        endDate = datetime.strptime(end_date, '%Y%m%d')
    except:
        startDate = datetime(2015,1,1)
        endDate = datetime(2099,1,1)


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
                                                    date.today() > VulReport.end_date,
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
        startDate = datetime.strptime(start_date, '%Y%m%d')
        endDate = datetime.strptime(end_date, '%Y%m%d')
    except:
        startDate = datetime(2015,1,1)
        endDate = datetime(2099,1,1)


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
            if date.today() > vul_asset[0].end_date:
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
def index_stats_time(start_date=0, end_date=0):
    try:
        startDate = datetime.strptime(start_date, '%Y%m%d')
        endDate = datetime.strptime(end_date, '%Y%m%d')
    except:
        startDate = datetime(2015,1,1)
        endDate = datetime(2099,1,1)

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
                    if 223200 > vul_retest_time > 50400:
                        vul_retest_time -= 50400
                    # 如果超过2天，认为是周末，减去62个小时，24+24+14=62
                    elif vul_retest_time >= 223200:
                        vul_retest_time -= 223200
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



@main.route('/asset_sec_score_stat', methods=['GET','POST'])
@main.route('/asset_sec_score_stat/<start_date>/<end_date>', methods=['GET','POST'])
@permission_required('main.asset_sec_score_stat')
def asset_sec_score_stat(start_date=0, end_date=0):
    #opt = request.args.get('opt','all')
    try:
        startDate = date(int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:8]))
        endDate = date(int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8]))
    except:
        startDate = date(2017,1,1)
        endDate = date.today()

    asset_list = Asset.query.filter(
                                Asset.sec_owner!='',
                                Asset.business_cata!='',
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

    data_sec_score_all = []
    data_code_score_all = []
    data_ops_score_all = []
    data_attack_score_all = []

    for i_date in list_date:
        endDate = date(int(i_date[0:4]), int(i_date[4:6]), int(i_date[6:8]))
        (s,c,o,a) = get_asset_score_all(asset_list,startDate,endDate)
        data_sec_score_all.append((str(i_date[4:6])+u'月',s))
        data_code_score_all.append((str(i_date[4:6])+u'月',c))
        data_ops_score_all.append((str(i_date[4:6])+u'月',o))
        data_attack_score_all.append((str(i_date[4:6])+u'月',a))

    #print '--------------------'
    #print data_sec_score_all
    #print data_code_score_all
    #print data_ops_score_all
    #print data_attack_score_all




    #asset_code_score = get_asset_code_score(opt,startDate,endDate,u'代码层面')
    
    return render_template('asset_sec_score_stat.html',
                            asset_count = asset_count, 
                            data_sec_score_all=json.dumps(data_sec_score_all),
                            data_code_score_all=json.dumps(data_code_score_all),
                            data_ops_score_all=json.dumps(data_ops_score_all),
                            data_attack_score_all=json.dumps(data_attack_score_all),
                            )


def get_asset_score_all(asset_list,startDate,endDate):
    asset_sec_score_all = 0
    asset_code_score_all = 0
    asset_ops_score_all = 0
    asset_attack_score_all = 0
    for asset in asset_list:
        asset_sec_score = get_asset_sec_score(asset.domain,startDate,endDate)
        asset_sec_score_all += asset_sec_score

        asset_code_score = get_asset_code_score(asset.domain,startDate,endDate,u'代码层面')
        asset_code_score_all += asset_code_score

        asset_ops_score = get_asset_code_score(asset.domain,startDate,endDate,u'运维层面')
        asset_ops_score_all += asset_ops_score

        asset_attack_score = get_asset_attack_score(asset.domain,startDate,endDate)
        asset_attack_score_all += asset_attack_score

    return (round(asset_sec_score_all,2),
            round(asset_code_score_all,2),
            round(asset_ops_score,2),
            round(asset_attack_score_all,2),
            )


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
    return datetime(year,month,1)

def getFirstDayOfMonth(v_date):
    d = v_date
    #c = calendar.Calendar()
     
    year = d.year
    month = d.month

    return datetime(year,month,1)


