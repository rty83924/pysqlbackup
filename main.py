import time
import asyncio
import sys
import os
from database import backup, delete, restore_dump
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
    start = time.time()
    backup_task = list()
    dump_task = list()
    for data in databases:
        backup_task.append(backup(mysqlhost=mysqlhost, user=user, passwd=passwd, port=port, databases=data, outputpath=outputpath))
        dump_task.append(restore_dump(restorehost=restorehost,restoreuser=restoreuser,restorepwd=restorepwd, restoreport=restoreport, databases=data, inputpath=outputpath))
    #await asyncio.gather(*backup_task, asyncio.sleep(0.1))
    await gather_with_concurrency(threads, *backup_task, asyncio.sleep(0.1))
    await gather_with_concurrency(threads, *dump_task, asyncio.sleep(0.1))
    end = time.time()
    print(end - start)
if __name__ == '__main__':
    asyncio.run(main(),debug=True)
