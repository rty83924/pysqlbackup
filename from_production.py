import time
import asyncio
import sys
import os
from database import backup, delete, restore
from get_config import config
from limit_asyncio import gather_with_concurrency

async def main():
    try:
        if sys.argv[2] == 'local':
            info = config(local_config=True)
        else:
            print('please enter # python main.py local')
            exit(1)
    except IndexError:
        info = os.environ
    threads = int(sys.argv[1])
    mysqlhost = info['mysqlhost']
    user = info['user']
    passwd = info['passwd']
    port = info['port']
    restorehost = info['restorehost']
    restoreuser = info['restoreuser']
    restorepwd = info['restorepwd']
    restoreport = info['restoreport']
    outputpath = info['outputpath']
    databases = info['data'].split(',')
    table = dict(info['table'].split("/") for x in str.split(","))
    start = time.time()
    backup_task = list()
    dump_task = list()
    for data in databases:
        backup_task.append(backup(mysqlhost=mysqlhost, user=user, passwd=passwd, port=port, databases=data, outputpath=outputpath))
        dump_task.append(restore(restorehost=restorehost,restoreuser=restoreuser,restorepwd=restorepwd, restoreport=restoreport, databases=data, inputpath=outputpath))
    for k, v in table.items():
        await backup(mysqlhost=restorehost, user=restoreuser, passwd=restorepwd, port=restoreport, databases=k, table=v, outputpath=outputpath)    
    #await asyncio.gather(*backup_task, asyncio.sleep(0.1))
    await gather_with_concurrency(threads, *backup_task, asyncio.sleep(0.1))
    await gather_with_concurrency(threads, *dump_task, asyncio.sleep(0.1))
    for k, v in table.items():
        await restore(restorehost=restorehost,restoreuser=restoreuser,restorepwd=restorepwd, restoreport=restoreport, databases=k, inputpath=outputpath, sqlfile='%s.sql' % v, table=v)   
    end = time.time()
    print(end - start)
if __name__ == '__main__':
    print('version: 1.5.4 laster')
    asyncio.run(main())
