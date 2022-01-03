from datetime import date, timedelta
from time import time, sleep
from sched import scheduler
from os import system
import config

s = scheduler(time, sleep)
CYAN = '\033[96m'
ENDC = '\033[0m'

def printConsole(msg):
    print(f"{CYAN}{msg}{ENDC}")

def backup(sc):
    system("clear")
    count = 0

    # Get today and yesterday's date stamp
    time_stamp = date.today()
    today_date = time_stamp.strftime("%b-%d-%Y")
    yesterday_date = time_stamp - timedelta(days=1)
    yesterday_stamp = yesterday_date.strftime("%b-%d-%Y")

    # Backup MySQL Database
    printConsole(msg="Creating backup of MySQL database")
    system(f"mysqldump -u root {config.databaseName} > {config.mainDir}/{today_date}.sql")

    # Backup NGINX configuration
    printConsole(msg="Creating backup of NGINX config")
    system(f"cp {config.nginxDir} {config.mainDir}")

    # Create RAR archive of the whole server
    printConsole(f"Creating RAR archive of {config.mainDir} ({today_date}.rar)")
    system(f"rar a {today_date}.rar {config.mainDir}")

    # Upload new backup and delete yesterday's backup
    printConsole(f"Uploading {today_date}.rar to MEGA servers")
    system(f'megaput --username {config.megaEmail} --password {config.megaPassword} --path=/Root/{today_date}.rar --disable-previews "{today_date}.rar"')

    # If we have a backup on MEGA, delete it.
    if count > 0:
        printConsole(msg="Deleting yesterday's backup")
        system(f'megarm --username {config.megaEmail} --password {config.megaPassword} --reload /Root/')
        system(f'megarm --username {config.megaEmail} --password {config.megaPassword} /Root/{yesterday_stamp}.rar')

    # Delete the current backup from our system to save storage space
    printConsole(f"Deleting backup from system")
    system(f"rm {config.mainDir}/{today_date}.sql")
    system(f"rm {today_date}.rar")

    count += 1
    s.enter(86400, 1, backup, (sc,))

s.enter(1, 1, backup, (s,))
s.run()
