import time
import os
import yaml
import pymysql
a = os.path.dirname(os.path.abspath(__file__))
def config():
    if not os.path.isfile('{}/config/config.yaml'.format(a)):
        cfg = os.environ
    else:
        with open('{}/config/config.yaml'.format(a), 'r') as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
            f.close()
    return cfg

def connect_sql(hosts,user,passwd,port,query):
    db = pymysql.connect(
        host = hosts,
        user = user,
        password = passwd,
        database = None,
        port = int(port),
        charset = 'utf8'
    )
    cursor = db.cursor()
    #數據庫操作
    try:
        cursor.execute(query)
        db.commit()
        #關閉DB
        db.close()
    except (pymysql.err.OperationalError, pymysql.ProgrammingError, pymysql.InternalError,
            pymysql.IntegrityError, TypeError) as error:
        #取消操作回滾
        db.rollback()
        print(error)
    #fetchone(): 该方法获取下一个查询结果集。结果集是一个对象
    #獲取所有紀錄
    return cursor.fetchall()


def backup():
    info = config()
    mysqlhost = info['mysqlhost']
    user = info['user']
    passwd = info['passwd']
    port = info['port']
    databases = info['data'].split(',')
    outputpath = info['outputpath']
    if not os.path.isdir(outputpath):
        os.makedirs(outputpath)
    times = time.strftime('%Y%m%d%H', time.localtime())
    for i in databases:
        count = 3
        while count:
            try:
                if os.system('mysqldump --single-transaction --quick --hex-blob --skip-triggers --protocol=TCP --set-gtid-purged=OFF -h %s -P %s -u%s -p%s --databases %s > %s/%s-%s.sql' 
                % (mysqlhost, port, user, passwd, i, outputpath, i, times)) == 0: 
                    print('backup %s-%s.sql done' % (i, times))
                    break
                else:
                    count -= 1
                    if count == 0:
                        print('backup false!')
                    time.sleep(30)
            except:
                print('command not working')
                break
def dump():
    info = config()
    restorehost = info['restorehost']
    restoreuser = info['restoreuser']
    restorepwd = info['restorepwd']
    restoreport = info['restoreport']
    databases = info['data'].split(',')
    outputpath = info['outputpath']
    times = time.strftime('%Y%m%d%H', time.localtime())
    for i in databases:
        count = 3
        while count:
            SQL_FILE = '{}-{}.sql'.format(i, times)
            Query1 = 'drop database {};'.format(i)
            Query2 = 'create database {} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'.format(i)
            try:
                connect_sql(restorehost,restoreuser,restorepwd,restoreport,Query1)
                connect_sql(restorehost,restoreuser,restorepwd,restoreport,Query2)
                if os.system('mysql --protocol=TCP -h %s -P %s -u%s -p%s --database=%s < %s/%s' 
                % (restorehost, restoreport, restoreuser, restorepwd, i, outputpath, SQL_FILE)) == 0:
                    print('restore {} done'.format(SQL_FILE))
                    break
                else:
                    count -= 1
                    if count == 0:
                        print('restore false!')
                    time.sleep(30)
            except:
                print('command not working')
                break


def delete():
    info = config()
    outputpath = info['outputpath']
    days = int(info['days'])
    now = time.time()
    days = now - days * 86400
    for f in  os.listdir(outputpath):
        if os.path.getatime(os.path.join(outputpath, f)) < days:
            if os.path.isfile(os.path.join(outputpath, f)):
                print('delete {}'.format(f))
                os.remove(os.path.join(outputpath, f))



if __name__ == '__main__':
    #outputpath = '{}/backup'.format(a)
    backup()
    dump()
    delete()

