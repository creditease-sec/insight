#coding: utf-8

import ldap


def ldap_login(username, password):
    print("开始执行")
    Server = "ldap://x.x.x.x:389"
    baseDN = "OU=XXXX,DC=XXXXXX,DC=XXXX"
    searchScope = ldap.SCOPE_SUBTREE

    # 设置过滤属性，这里只显示cn=test的信息
    searchFilter = "sAMAccountName=" + username
    # 为用户名加上域名
    username = 'creditease\\' + username

    # None表示搜索所有属性，['cn']表示只搜索cn属性
    retrieveAttributes = None

    conn = ldap.initialize(Server)
    #非常重要
    conn.set_option(ldap.OPT_REFERRALS, 0)
    conn.protocol_version = ldap.VERSION3
    # 这里用户名是域账号的全名例如domain/name
    try:
        conn.simple_bind_s(username, password)
    except:
        return False

    print 'ldap connect successfully'
    return True