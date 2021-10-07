import config, time
from datetime import date, timedelta
from sched import scheduler
from os import system, path

s = scheduler(time.time, time.sleep)

def backup(sc):
    count = 0
    CYAN = '\033[96m'
    ENDC = '\033[0m'

    # Get today and yesterday's date stamp
    timeA = date.today()
    yesterday = timeA - timedelta(days = 1)
    dateStamp = timeA.strftime("%b-%d-%Y")
    yesterdayDateStamp = yesterday.strftime("%b-%d-%Y")

    # Backup MySQL Database
    print(f"{CYAN}Creating backup of MySQL database{ENDC}")
    system(f"mysqldump -u root {config.databaseName} > {config.mainDir}/{dateStamp}.sql")

    # Backup NGINX configuration
    print(f"{CYAN}Creating backup of NGINX config{ENDC}")
    system(f"cp {config.nginxDir} {config.mainDir}")

    # Create RAR archive of the whole server
    print(f"{CYAN}Creating RAR archive of {config.mainDir} ({dateStamp}.rar){ENDC}")
    if path.exists(f"{config.selfDir}{yesterdayDateStamp}.rar"):
        system(f"rm {config.mainDir}/{yesterdayDateStamp}.sql")
        system(f"rm {yesterdayDateStamp}.rar")
    system(f"rar a {dateStamp}.rar {config.mainDir}")

    # Upload new backup and delete yesterday's backup
    print(f"{CYAN}Uploading {dateStamp}.rar to MEGA servers{ENDC}")
    system(f'megaput --username {config.megaEmail} --password {config.megaPassword} --path=/Root/{dateStamp}.rar --disable-previews "{dateStamp}.rar"')
    if count > 0:
        system(f'megarm --username {config.megaEmail} --password {config.megaPassword} /Root/{yesterdayDateStamp}.rar')
    count += 1
    s.enter(86400, 1, backup, (sc,))

s.enter(1, 1, backup, (s,))
s.run()
