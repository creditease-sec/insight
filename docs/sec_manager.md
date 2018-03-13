## 安全管理员账号

安全管理员需要注册账号后，由超级管理员修改【普通用户】权限为【安全管理员】权限。

## 安全管理员登录

[http://127.0.0.1:9000/srcpm/auth/login](http://127.0.0.1:9000/srcpm/auth/login)

## 待审核漏洞报告查看

当有新漏洞提交后，安全管理员会收到【新漏洞等待审核】的邮件通知。

点击漏洞链接，即可在登录状态下查看漏洞详情。

如果漏洞报告不合格则可以【删除】后要求安全人员重新提交；如果漏洞报告合格则点击【审核】按钮进入审核页面。

## 漏洞报告审核

审核页面可编辑字段有：
* 漏洞层面：安全管理员可重新确认漏洞层面选项
* 漏洞类型：安全管理员可重新确认漏洞类型选项
* Rank：安全管理员评定Rank值，根据评定的Rank值系统会自动计算风险值，由自动计算的风险值，系统自动计算下面的限定修复日期。
* 通告日期：默认为当前日期
* 限定修复日期：默认为系统根据安全管理员评定的Rank进行自动计算得出。

不可编辑字段：
* 邮件收件人：系统会列出和该漏洞相关的资产负责人、部门经理、安全人员。

审核完成后，点击提交，系统自动给邮件收件人发送新漏洞通告邮件。

> Rank值范围为0-20，说明如下
>> 1-5 低危、6-10 中危、11-15 高危、16-20 严重
>
> 风险值计算方法：
>> 风险值 = Rank值 * 资产重要程度系数 * 转换因子（固定为5） * 内外网系数
>
> 资产重要程度系数：
>> 一级 1、二级 0.9、三级 0.8、四级 0.7
>>
> 内外网系数：
>> 外网 1、内网 0.8
>>
> 根据风险值计算修复天数：
>> 风险值为75-100分，则修复天数为3-5天；风险值为50-75分，则修复天数为7-10天；风险值为25-50分，则修复天数为14-20天；风险值为1-25分，则修复天数为21-30天；

* 相关系数硬编码在代码里，如需变更需修改相应代码，代码位置详情如下：

```
# vulpm/srcpm/app/src/views.py 977-1022行

''' 根据资产的rank值计算风险值和修复天数 '''
def get_risk_score_and_end_date(rank, asset):
    #设置业务等级系数
    asset_level_value = 0
    if asset.level == u'一级':
        asset_level_value = 1
    elif asset.level == u'二级':
        asset_level_value = 0.9
    elif asset.level == u'三级':
        asset_level_value = 0.8
    else:
        asset_level_value = 0.7

    #设置内外网系数
    asset_inout_value = 0
    if asset.in_or_out == u'外网':
        asset_inout_value = 1
    elif asset.in_or_out == u'内网':
        asset_inout_value = 0.8
    else:
        asset_inout_value = 0

    #风险值＝rank * 业务等级系数 ＊ 风险值权重 ＊ 内外网系数
    risk_score = round(rank * asset_level_value * 5 * asset_inout_value,2)

    #计算修复天数
    if 75<risk_score<=100:
        #days = 3-5
        days = round( 5 - (risk_score-75)*0.08, 0)
    elif  50<risk_score<=75:
        #days = 7-10
        days = round( 10 - (risk_score-50)*0.12, 0)
    elif  25<risk_score<=50:
        #days = 14-20
        days = round( 20 - (risk_score-25)*0.24, 0)
    elif  0<risk_score<=25:
        #days = 21-30
        days = round( 30 - (risk_score-0)*0.36, 0)
    else:
        days = 0

    #如果系统为上线前测试，将修复天数延长至1年
    if asset.status == u'上线前' and days != 0:
        days = 365

    return risk_score, days
```
