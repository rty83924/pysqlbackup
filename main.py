from database import backup, delete, restore_dump
from get_config import config
import time
import asyncio

async def main():
    info = config(local_config=True)
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
    for data in databases:
        backup_task.append(backup(mysqlhost=mysqlhost, user=user, passwd=passwd, port=port, databases=data, outputpath=outputpath))
    await asyncio.gather(*backup_task, asyncio.sleep(0.1))
    end = time.time()
    print(end - start)
if __name__ == '__main__':
    asyncio.run(main(),debug=True)
    #backup()
    #dump()
    #delete()