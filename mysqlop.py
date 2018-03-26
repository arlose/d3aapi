#coding=utf-8

import MySQLdb
import time
import json
from werkzeug.security import generate_password_hash, check_password_hash

configfile = './config.json'
jsondata = json.load(file(configfile))
dbip = jsondata['dbip']
dbport = jsondata['dbport']
dbroot = jsondata['dbroot']
dbname = jsondata['dbname']
dbcharset = jsondata['dbcharset']

class Database(object):
    def __init__(self):
        self.conn = self.initDatabase()

    def initDatabase(self):
        '''
        初始化数据库
        TODO 数据库失败
        '''
        conn = MySQLdb.connect(
            host=dbip,
            port = dbport,
            user = dbroot,
            passwd = '!@#asd123',
            db = dbname,
            charset=dbcharset,
        )
        return conn


    def qureyTaskname(self, usrname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "select name, createtime, process, status, type, trained from Tasks where usrname = '%s'"%usrname
        # sql = "select name, createtime, process, status, type from Tasks where usrname = '%s'"%usrname
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        res = cur.fetchall()
        #print 'result:', res
        cur.close()
        self.conn.close()
        out = []
        for r in res:
            out.append(r)
        return out

    def qureyTaskdesc(self, usrname, taskname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "select description from Tasks where usrname = '%s' and name = '%s'"%(usrname, taskname)
        # sql = "select name, createtime, process, status, type from Tasks where usrname = '%s'"%usrname
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        res = cur.fetchall()
        #print 'result:', res
        cur.close()
        self.conn.close()
        out = []
        for r in res:
            out.append(r)
        return out[0][0]

    def setTaskdesc(self, usrname, taskname, desc):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "update  Tasks set description = %s where usrname = '%s' and name = '%s'"%(desc, usrname, taskname)
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return 

    def getTaskname(self, usrname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "select name from Tasks where usrname = '%s'"%usrname
        # sql = "select name, createtime, process, status, type from Tasks where usrname = '%s'"%usrname
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        res = cur.fetchall()
        #print 'result:', res
        cur.close()
        self.conn.close()
        out = []
        for r in res:
            out.append(r)
        return out

    def writeTask(self, name, tasktype, process, usrname):
        '''
        将结果写入数据库
        '''
        ISOTIMEFORMAT='%Y-%m-%d %X'
        t = time.strftime( ISOTIMEFORMAT, time.localtime() )
        cur = self.conn.cursor()
        sql = "select * from Workers where usrname = '%s'"%(usrname)
        cur.execute(sql)
        res = cur.fetchall()
        exclusworker = 0
        if len(res)>0:
            exclusworker = 1
        sql = "insert Tasks(name, type, createtime, process, usrname, exclusworker, workerpid, stop, trained) values('%s', %d, '%s', '%lf', '%s', %d, 0, 0, 0)" %(name, tasktype, t, process, usrname, exclusworker)
        #print sql
        cur.execute(sql)
        self.conn.commit()
        #cur.close()
        return

    def getTasktype(self, usrname, taskname):
        tasktype = 0
        cur = self.conn.cursor()
        sql = "select  type from Tasks where  name = '%s' and usrname = '%s'"%(taskname, usrname)
        cur.execute(sql)
        res = cur.fetchall()
        if len(res)>0:
            tasktype = int(res[0][0])
        return tasktype

    def delTask(self, usrname, taskname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "delete from Tasks where usrname = '%s' and name = '%s'"%(usrname, taskname)
        #sql = "describe tags"
        # print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def startTask(self, usrname, taskname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        # todo task status ==2???
        cur = self.conn.cursor()
        sql = "update  Tasks set status = 1, stop = 0  where usrname = '%s' and name = '%s'"%(usrname, taskname)
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def updateTask(self, usrname, taskname, percent, pid):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "update Tasks set process = %lf, workerpid = %d where  name = '%s' and usrname = '%s'"%(percent, pid, taskname, usrname)
        #sql = "describe tags"
        # print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def getTaskpid(self, usrname, taskname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "select  workerpid from Tasks where  name = '%s' and usrname = '%s'"%(taskname, usrname)
        #sql = "describe tags"
        # print sql
        # 执行sql语句
        cur.execute(sql)
        res = cur.fetchall()

        return res

    def getTaskStatus(self, usrname, taskname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "select  status, stop from Tasks where  name = '%s' and usrname = '%s'"%(taskname, usrname)
        #sql = "describe tags"
        # print sql
        # 执行sql语句
        cur.execute(sql)
        res = cur.fetchall()

        return res

    def startTaskTrain(self, usrname, taskname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        # todo task status ==2???
        cur = self.conn.cursor()
        sql = "update  Tasks set status = 2  where usrname = '%s' and name = '%s'"%(usrname, taskname)
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def FinishTaskTrain(self, usrname, taskname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        # todo task status ==2???
        cur = self.conn.cursor()
        sql = "update  Tasks set status = 3, stop = 0, workerpid = 0 where usrname = '%s' and name = '%s'"%(usrname, taskname)
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def TaskTrainError(self, usrname, taskname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        # todo task status ==2???
        cur = self.conn.cursor()
        sql = "update  Tasks set status = 4  where usrname = '%s' and name = '%s'"%(usrname, taskname)
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def stopTask(self, usrname, taskname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        # todo task status ==2???
        cur = self.conn.cursor()
        sql = "update  Tasks set status = 0, process = 0.0, workerpid = 0, stop = 1 where usrname = '%s' and name = '%s'"%(usrname, taskname)
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def clearTask(self, usrname, taskname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        # todo task status ==2???
        cur = self.conn.cursor()
        sql = "update  Tasks set status = 0, process = 0.0, workerpid = 0, stop = 0 where usrname = '%s' and name = '%s'"%(usrname, taskname)
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def queryOperations(self, usrname, start, num):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        # todo task status ==2???
        cur = self.conn.cursor()
        if usrname=='all':
            sql = "select usrname, ipaddr, updatetime, types, operation from Operations order by id desc limit %d, %d"%(start, num)
        else:
            sql = "select usrname, ipaddr, updatetime, types, operation from Operations where usrname = '%s' order by id desc limit %d, %d"%(usrname, start, num)
        # 执行sql语句
        cur.execute(sql)
        res = cur.fetchall()
        return res

    def queryOperationsCount(self, usrname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        # todo task status ==2???
        cur = self.conn.cursor()
        if usrname=='all':
            sql = "select count(*) from Operations"
        else:
            sql = "select count(*) from Operations where usrname = '%s'"%(usrname)
        # 执行sql语句
        cur.execute(sql)
        res = cur.fetchall()
        return res

    def addWorker(self, name, gpustatus, memunused):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        ISOTIMEFORMAT='%Y-%m-%d %X'
        t = time.strftime( ISOTIMEFORMAT, time.localtime() )
        cur = self.conn.cursor()
        sql = "select * from Workers where name= '%s'"%(name)
        cur.execute(sql)
        res = cur.fetchall()
        if len(res)==0:
            cur = self.conn.cursor()
            sql = "insert into Workers(name, status, taskname, GPUMemery, Memusage, updatetime)values('%s', 0, 'None', '%s', %d, '%s')"%(name, gpustatus, memunused, t)
            #sql = "describe tags"
            #print sql
            # 执行sql语句
            cur.execute(sql)
            self.conn.commit()
        return

    def insertWorker(self, name, status, taskname, gpustatus, memunused):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        ISOTIMEFORMAT='%Y-%m-%d %X'
        t = time.strftime( ISOTIMEFORMAT, time.localtime() )
        cur = self.conn.cursor()
        sql = "select * from Workers where name= '%s'"%(name)
        cur.execute(sql)
        res = cur.fetchall()
        if len(res)==0:
            cur = self.conn.cursor()
            sql = "insert into Workers(name, status, taskname, GPUMemery, Memusage, updatetime)values('%s', '%d', '%s', '%s', '%s')"%(name, status, taskname, gpustatus, memunused, t)
            #sql = "describe tags"
            #print sql
            # 执行sql语句
            cur.execute(sql)
            self.conn.commit()
        return

    def clearWorker(self, taskname):
        ISOTIMEFORMAT='%Y-%m-%d %X'
        t = time.strftime( ISOTIMEFORMAT, time.localtime() )
        cur = self.conn.cursor()
        sql = "update Workers set status = 0,  updatetime = '%s', taskname = 'None' where taskname = '%s'"%(t, taskname)
        #sql = "describe tags"
        # print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def updateWorker(self, name, status, taskname, gpustatus, memunused):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        ISOTIMEFORMAT='%Y-%m-%d %X'
        t = time.strftime( ISOTIMEFORMAT, time.localtime() )
        cur = self.conn.cursor()
        sql = "update Workers set status = %d,  taskname = '%s',  GPUMemery = '%s', Memusage = %d, updatetime = '%s' where name = '%s'"%(status, taskname, gpustatus, memunused, t, name)
        #sql = "describe tags"
        # print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def qureyWorkerlist(self, usrname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "select name, status, taskname, GPUMemery, updatetime, usrname from Workers"
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        res = cur.fetchall()
        #print 'result:', res
        #cur.close()
        #self.conn.close()
        return res

    def getmanagerusrlist(self):
        cur = self.conn.cursor()
        sql = "select name from Users where level>=2"
        #sql = "describe tags"
        print sql
        # 执行sql语句
        cur.execute(sql)
        res = cur.fetchall()
        #print 'result:', res
        #cur.close()
        #self.conn.close()
        return res

    def gettrainingtaskinfo(self):
        cur = self.conn.cursor()
        sql = "select usrname, name, createtime, type, status, process from Tasks where status>=1"
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        res = cur.fetchall()
        #print 'result:', res
        #cur.close()
        #self.conn.close()
        return res

    def qureyWorkerStatus(self):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "select name, status, Memusage from Workers"
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        res = cur.fetchall()
        #print 'result:', res
        #cur.close()
        #self.conn.close()
        return res

    def modifyworkerowner(self, workername, ownername):
        cur = self.conn.cursor()
        # select old owner of the worker
        sql = "select usrname from Workers where name = '%s'"%(workername)
        cur.execute(sql)
        res = cur.fetchall()
        oldownername = res[0][0]
        # update new owner of the worker
        sql = "update Workers set usrname = '%s' where name = '%s'"%(ownername, workername)
        cur.execute(sql)
        #self.conn.commit()
        # old owner don't own worker
        sql = "select * from Workers where usrname = '%s'"%(oldownername)
        cur.execute(sql)
        res = cur.fetchall()
        isexlu = 0
        if len(res)>0:
            isexlu = 1
        if isexlu==0:
            sql = "update Tasks set exclusworker = 0 where usrname = '%s'"%(oldownername)
            cur.execute(sql)
        # new owner own the worker
        if ownername != 'all':
            sql = "update Tasks set exclusworker = 1 where usrname = '%s'"%(ownername)
            cur.execute(sql)

        self.conn.commit()

        return

    def delWorker(self, name):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "select usrname from Workers where name = '%s'"%(name)
        cur.execute(sql)
        res = cur.fetchall()
        oldownername = res[0][0]

        sql = "delete from Workers where name = '%s'"%(name)
        cur.execute(sql)

        sql = "select * from Workers where usrname = '%s'"%(oldownername)
        cur.execute(sql)
        res = cur.fetchall()
        isexlu = 0
        if len(res)>0:
            isexlu = 1
        if isexlu==0:
            sql = "update Tasks set exclusworker = 0 where usrname = '%s'"%(oldownername)
            cur.execute(sql)

        self.conn.commit()
        return

    def addusr(self, usrname, email, passwd, active, level, groups, ipaddr):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "select * from Users where name= '%s' or email = '%s'"%(usrname, email)
        cur.execute(sql)
        res = cur.fetchall()
        if len(res)==0:
            ISOTIMEFORMAT='%Y-%m-%d %X'
            t = time.strftime( ISOTIMEFORMAT, time.localtime() )
            sql = "insert into Users(name, email, passwd, active, level, groups, regip, regtime)values('%s', '%s', '%s', %d, %d, '%s', '%s', '%s')"%(usrname, email, passwd, active, level, groups, ipaddr, t)
            cur.execute(sql)
            self.conn.commit()
            return True
        return False

    def verifyusr(self, usrname, passwd):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "select level, passwd, groups from Users where name= '%s'"%(usrname)
        cur.execute(sql)
        res = cur.fetchall()
        if len(res)==0:
            return False, 0, "common"
        else:
            if check_password_hash(res[0][1], passwd):
                return True, res[0][0], res[0][2]
            else:
                return False, 0, "common"

    def updateusrlogininfo(self, usrname, ipaddr):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        ISOTIMEFORMAT='%Y-%m-%d %X'
        t = time.strftime( ISOTIMEFORMAT, time.localtime() )
        cur = self.conn.cursor()
        sql = "update Users set lastlogintime = '%s', lastloginip = '%s' where name = '%s'"%(t, ipaddr, usrname)
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return False

    def getusernamelist(self):
        cur = self.conn.cursor()
        sql = "select name from Users"
        cur.execute(sql)
        res = cur.fetchall()
        return res

    def getusernamelistgroup(self, groupname):
        cur = self.conn.cursor()
        sql = "select name from Users where groups = '%s'"%(groupname)
        cur.execute(sql)
        res = cur.fetchall()
        return res

    def getuserlist(self):
        cur = self.conn.cursor()
        sql = "select name, email, active, level, groups from Users"
        cur.execute(sql)
        res = cur.fetchall()
        return res

    def delusr(self, usrname):
        cur = self.conn.cursor()
        sql = "delete from Users where name = '%s'"%(usrname)
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        # del task
        sql = "delete from Tasks where usrname = '%s'"%(usrname)
        cur.execute(sql)
        self.conn.commit()
        return

    def setusrlevel(self, usrname, level):
        cur = self.conn.cursor()
        sql = "update Users set level = %d where name = '%s'"%(level, usrname)
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def setusrgroup(self, usrname, group):
        cur = self.conn.cursor()
        sql = "update Users set groups = '%s' where name = '%s'"%(group, usrname)
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def setusremail(self, usrname, email):
        cur = self.conn.cursor()
        sql = "update Users set email = '%s' where name = '%s'"%(email, usrname)
        #sql = "describe tags"
        # print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def setusrpasswd(self, usrname, passwd):
        cur = self.conn.cursor()
        sql = "update Users set passwd = '%s' where name = '%s'"%(passwd, usrname)
        #sql = "describe tags"
        # print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def getgrouplist(self):
        cur = self.conn.cursor()
        sql = "select name from Groups"
        cur.execute(sql)
        res = cur.fetchall()
        return res

    def addgroup(self, groupname):
        cur = self.conn.cursor()
        sql = "select name from Groups where name= '%s'"%(groupname)
        cur.execute(sql)
        res = cur.fetchall()
        if len(res)==0:
            sql = "insert into Groups(name)values('%s')"%(groupname)
            cur.execute(sql)
            self.conn.commit()
            cur.close()
            self.conn.close()
            return
        cur.close()
        self.conn.close()
        return

    def delgroup(self, groupname):
        cur = self.conn.cursor()
        sql = "delete from Groups where name = '%s'"%(groupname)
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        self.conn.commit()
        return

    def qureyUserLevel(self, usrname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "select level from Users where name = '%s'"%usrname
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        res = cur.fetchall()
        #print 'result:', res
        cur.close()
        self.conn.close()
        return res

    def qureyusersgroup(self, usrname):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        cur = self.conn.cursor()
        sql = "select groups from Users where name = '%s'"%(usrname)
        cur.execute(sql)
        res = cur.fetchall()
        cur.close()
        self.conn.close()

        if len(res)>0:
            return res[0][0]
        else:
            return 'None'

    def qureyGroupUserList(self, usrname, include):
        """根据查找id

        Arguments:
            taskname {[string]} -- [标签名称]
        """
        groupname = ""
        cur = self.conn.cursor()
        sql = "select groups from Users where name = '%s'"%(usrname)
        cur.execute(sql)
        res = cur.fetchall()
        if len(res)>0:
            groupname = res[0][0]
        else:
            return []

        if include:
            sql = "select name, level from Users where groups = '%s' and level < 2"%(groupname)
        else:
            sql = "select name, level from Users where name != '%s' and groups = '%s' and level < 2 "%(usrname, groupname)
        #sql = "describe tags"
        #print sql
        # 执行sql语句
        cur.execute(sql)
        res = cur.fetchall()
        #print 'result:', res
        cur.close()
        self.conn.close()
        return res

    def operationrecord(self, info, types, usrname, ip):
        ISOTIMEFORMAT='%Y-%m-%d %X'
        t = time.strftime( ISOTIMEFORMAT, time.localtime() )
        cur = self.conn.cursor()
        sql = "insert into Operations(operation, types, usrname, ipaddr, updatetime)values('%s', '%s', '%s', '%s', '%s')"%(info, types, usrname, ip, t)
        cur.execute(sql)
        self.conn.commit()
        cur.close()
        self.conn.close()

if __name__ == "__main__":
    db = Database()
    #db.qureyTask()
    #db.writeTask('task1', 0.0, 'fj')
    res = db.qureyWorkerlist('fj1')
    print res[0]
