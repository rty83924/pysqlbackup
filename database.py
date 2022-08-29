import time
import os
import pymysql
import asyncio
import contextlib

#上下文
@contextlib.contextmanager
def connect_sql(hosts,user,passwd,port):
    db = pymysql.connect(
        host = hosts,
        user = user,
        password = passwd,
        database = None,
        port = int(port),
        charset = 'utf8'
    )
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)  #在实例化的时候，将属性cursor设置为pymysql.cursors.DictCursor
    #數據庫操作
    try:
        yield cursor
        db.commit()
    except (pymysql.err.OperationalError, pymysql.ProgrammingError, pymysql.InternalError,
            pymysql.IntegrityError, TypeError) as error:
        #取消操作回滾
        db.rollback()
        print(error)
    finally:
        cursor.close()
        db.close()
    #fetchone(): 该方法获取下一个查询结果集。结果集是一个对象
    #獲取所有紀錄
    #return cursor.fetchall()


async def backup(mysqlhost, user, passwd, port, databases, outputpath, table=None):
    print(databases)
    if not os.path.isdir(outputpath):
        os.makedirs(outputpath)
    times = time.strftime('%Y%m%d%H', time.localtime())
    count = 3
    if table is None:
        cmd = 'mysqldump --extended-insert --no-autocommit --set-gtid-purged=OFF --no-tablespaces --quick --hex-blob --skip-triggers --protocol=TCP -h %s -P %s -u%s -p%s --databases %s | gzip > %s%s-%s.sql.gz' % (mysqlhost, port, user, passwd, databases, outputpath, databases, times)
    else:    
        cmd = 'mysqldump --extended-insert --no-autocommit --set-gtid-purged=OFF --no-tablespaces --quick --hex-blob --skip-triggers --protocol=TCP -h %s -P %s -u%s -p%s --databases %s --tables %s | gzip > %s/%s.sql.gz' % (mysqlhost, port, user, passwd, databases, table, outputpath, table)
    while count:
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await proc.communicate()
            await proc.wait()
            if proc.returncode == 0 and table is None:
                print('backup %s-%s.sql done' % (databases, times))
                break
            elif proc.returncode == 0 and table is not None:
                print('backup %s.sql done' % (table))
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
    if sqlfile is None:
        SQL_FILE = '{}-{}.sql.gz'.format(databases, times)
    else:
        SQL_FILE = sqlfile
    cmd = f'gunzip < {inputpath}{SQL_FILE} | mysql --protocol=TCP -h {restorehost} -P {restoreport} -u{restoreuser} -p{restorepwd} {databases}'
    while count:
        with connect_sql(restorehost,restoreuser,restorepwd,restoreport) as cursor:
            try:
                cursor.execute('SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, AUTOCOMMIT = 0;')
                cursor.execute('SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS = 0;')
                cursor.execute('SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS = 0;')
                if table is None:
                    cursor.execute('drop database IF EXISTS {};'.format(databases))
                    cursor.execute('create database IF NOT EXISTS  {} CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;'.format(databases))
                else:
                    pass
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
            finally:
                cursor.execute('SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;')
                cursor.execute('SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;')
                cursor.execute('SET AUTOCOMMIT = @OLD_AUTOCOMMIT;')
                cursor.execute('COMMIT;')


def delete(inputpath, days):
    now = time.time()
    days = now - days * 86400
    for f in  os.listdir(inputpath):
        try: 
            if os.path.getatime(os.path.join(inputpath, f)) < days:
                if os.path.isfile(os.path.join(inputpath, f)):
                    print('delete {}'.format(f))
                    os.remove(os.path.join(inputpath, f))
        except Exception as e:
            print(e)

if __name__ == '__main__':
    #outputpath = '{}/backup'.format(a)
    #backup()
    delete(inputpath='/var/backup/SQL', days=3)

