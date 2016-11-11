#coding: utf-8

import sys,ldap

LDAP_HOST = ''
USER = 'creditease\\username'
PASSWORD = 'password'
BASE_DN = 'OU=HABROOT,DC=creditease,DC=corp'

class LDAPTool:
      
    def __init__(self,ldap_host=None,base_dn=None,user=None,password=None):
        if not ldap_host:
            ldap_host = LDAP_HOST
        if not base_dn:
            self.base_dn = BASE_DN
        if not user:
            user = USER
        if not password:
            password = PASSWORD
        try:
            #self.ldapconn = ldap.open(ldap_host, 389)
            self.ldapconn = ldap.initialize('ldap://10.151.6.253:389')
            self.ldapconn.set_option(ldap.OPT_REFERRALS, 0)
            self.ldapconn.protocol_version = ldap.VERSION3
            self.ldapconn.simple_bind(user,password)
            print 'self.ldapconn', self.ldapconn
            print 'init _______********_______********** error before', self.ldapconn.whoami_s()
        except ldap.LDAPError,e:
            print e
            print 'init _______********_______********** error'
  
#根据表单提交的用户名，检索该用户的dn,一条dn就相当于数据库里的一条记录。
#在ldap里类似cn=username,ou=users,dc=gccmx,dc=cn,验证用户密码，必须先检索出该DN
    def ldap_search_dn(self,uid=None):
        obj = self.ldapconn
        print '*** obj *** :', obj
        obj.protocal_version = ldap.VERSION3
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        #searchFilter = "mail=" + uid
        searchFilter = "sAMAccountName=" + uid
         
        try:
            ldap_result_id = obj.search(self.base_dn, searchScope, searchFilter, retrieveAttributes)
            print 'ldap_result_id: ', ldap_result_id

            print '*****1*****'
            result_set = []
            while 1:
                result_type, result_data = obj.result(ldap_result_id, 0)
                if result_data == []:
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        result_set.append(result_data)
            
            print result_set
            Name,Attrs = result_set[0][0]
            if hasattr(Attrs, 'has_key') and Attrs.has_key('name'):
                print "test3"
                distinguishedName = Attrs['mail'][0]
                print "Login Info for user : %s" % distinguishedName
                print Attrs['mail'][0]

                return distinguishedName
            else:
                return None
            
        except ldap.LDAPError, e:
            print e
    

#查询用户记录，返回需要的信息
    def ldap_get_user(self,uid=None):
        obj = self.ldapconn
        obj.protocal_version = ldap.VERSION3
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        searchFilter = "mail=" + uid
        try:
            ldap_result_id = obj.search(self.base_dn, searchScope, searchFilter, retrieveAttributes)
            result_type, result_data = obj.result(ldap_result_id, 0)
            if result_type == ldap.RES_SEARCH_ENTRY:
                username = result_data[0][1]['cn'][0]
                email = result_data[0][1]['mail'][0]
                nick = result_data[0][1]['sn'][0]
                result = {'username':username,'email':email,'nick':nick}
                return result
            else:
                return None
        except ldap.LDAPError, e:
            print e
          
#用户验证，根据传递来的用户名和密码，搜索LDAP，返回boolean值
    def ldap_get_vaild(self,uid=None,passwd=None):
        obj = self.ldapconn
        target_cn = self.ldap_search_dn(uid)
        print 'aaaaaaaaaaaaaa: ', target_cn    
        try:
            if obj.simple_bind_s(target_cn,passwd):
                return True
            else:
                return False
        except ldap.LDAPError,e:
            print e
 
#修改用户密码
    def ldap_update_pass(self,uid=None,oldpass=None,newpass=None):
        modify_entry = [(ldap.MOD_REPLACE,'userpassword',newpass)]
        obj = self.ldapconn
        target_cn = self.ldap_search_dn(uid)      
        try:
            obj.simple_bind_s(target_cn,oldpass)
            obj.passwd_s(target_cn,oldpass,newpass)
            return True
        except ldap.LDAPError,e:
            return False