import time
import os
import pymysql
import asyncio

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


async def backup(mysqlhost, user, passwd, port, databases, outputpath, table=None):
    if not os.path.isdir(outputpath):
        os.makedirs(outputpath)
    times = time.strftime('%Y%m%d%H', time.localtime())
    count = 3
    while count:
        if table is None:
            cmd = 'mysqldump --set-gtid-purged=OFF --no-tablespaces --quick --hex-blob --skip-triggers --protocol=TCP -h %s -P %s -u%s -p%s --databases %s > %s/%s-%s.sql' % (mysqlhost, port, user, passwd, databases, outputpath, databases, times)
            #cmd = 'mysqldump --single-transaction --protocol=TCP -h %s -P %s -u%s -p%s --databases %s > %s/%s-%s.sql' % (mysqlhost, port, user, passwd, databases, outputpath, databases, times)        
        else:    
            cmd = 'mysqldump --set-gtid-purged=OFF --no-tablespaces --quick --hex-blob --skip-triggers --protocol=TCP -h %s -P %s -u%s -p%s --databases %s --tables %s > %s/%s.sql' % (mysqlhost, port, user, passwd, databases, table, outputpath, table)
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await proc.communicate()
            await proc.wait()
            if proc.returncode == 0:
                print('backup %s-%s.sql done' % (databases, times))
                break
            if stderr:
                print(stderr.decode())
                count -= 1
        except:
            print('command not working')
            break

async def restore(restorehost, restoreuser, restorepwd, restoreport, databases, inputpath, sqlfile=None, table=None):
    times = time.strftime('%Y%m%d%H', time.localtime())
    count = 3
    while count:
        Query1 = 'drop database IF EXISTS {};'.format(databases)
        Query2 = 'create database IF NOT EXISTS  {} CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;'.format(databases)
        try:
            connect_sql(restorehost,restoreuser,restorepwd,restoreport,Query1)
            connect_sql(restorehost,restoreuser,restorepwd,restoreport,Query2)
            if sqlfile is None:
                SQL_FILE = '{}-{}.sql'.format(databases, times)
            else:
                SQL_FILE = sqlfile
            if table is not None:
                cmd = 'mysql --protocol=TCP -h %s -P %s -u%s -p%s %s %s < %s%s' % (restorehost, restoreport, restoreuser, restorepwd, databases, table, inputpath, SQL_FILE)
            else:
                cmd = 'mysql --protocol=TCP -h %s -P %s -u%s -p%s %s %s < %s%s' % (restorehost, restoreport, restoreuser, restorepwd, databases, inputpath, SQL_FILE)
            print(cmd)
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await proc.communicate()
            await proc.wait()
            if proc.returncode == 0:
                print('restore {} done'.format(SQL_FILE))
                break
            if stderr:
                print(stderr.decode())
                count -= 1
        except:
            print('command not working')
            break


def delete(inputpath, days):
    #info = config()
    #inputpath = info['outputpath']
    #days = int(info['days'])
    now = time.time()
    days = now - days * 86400
    for f in  os.listdir(inputpath):
        if os.path.getatime(os.path.join(inputpath, f)) < days:
            if os.path.isfile(os.path.join(inputpath, f)):
                print('delete {}'.format(f))
                os.remove(os.path.join(inputpath, f))



if __name__ == '__main__':
    #outputpath = '{}/backup'.format(a)
    backup()
    #dump()
    delete()

