import os
import psutil
import time
import json
from datetime import datetime
from colorama import Fore, Style, init

init()

# Variables globales
ANOMALY_LOG = "anomaly_log.json"
USERS = {}

def get_system_data():
    users = psutil.users()
    system_data = []
    for user in users:
        system_data.append({
            "name": user.name,
            "terminal": user.terminal,
            "host": user.host,
            "started": datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S')
        })
    return system_data

def detect_anomalies(current_data):
    anomalies = []
    for user in current_data:
        if user["name"] not in USERS:
            USERS[user["name"]] = []
        USERS[user["name"]].append(user["started"])
        if len(USERS[user["name"]]) > 5:
            USERS[user["name"]].pop(0)
        if len(USERS[user["name"]]) == 5 and (datetime.strptime(USERS[user["name"]][4], '%Y-%m-%d %H:%M:%S') - datetime.strptime(USERS[user["name"]][0], '%Y-%m-%d %H:%M:%S')).seconds < 300:
            anomalies.append({
                "name": user["name"],
                "terminal": user["terminal"],
                "host": user["host"],
                "started": user["started"],
                "reason": "Multiple logins in short period"
            })
    return anomalies

def save_anomaly_log(anomalies):
    with open(ANOMALY_LOG, 'a') as file:
        for anomaly in anomalies:
            file.write(json.dumps(anomaly) + "\n")

def show_interface():
    try:
        while True:
            os.system("clear")
            os.system("figlet -f slant 'User Behavior' | lolcat")
            print(Fore.GREEN + "Created by Thomas O'neil Álvarez" + Style.RESET_ALL)
            print("=" * 50)
            print(Fore.YELLOW + "Monitoreo en tiempo real de usuarios" + Style.RESET_ALL)
            print("=" * 50)
            print(Fore.RED + "Pulsa Ctrl + C para finalizar" + Style.RESET_ALL)
            print("=" * 50)
            
            current_data = get_system_data()
            anomalies = detect_anomalies(current_data)
            save_anomaly_log(anomalies)
            
            for user in current_data:
                print(f"{Fore.CYAN}User: {user['name']} | Terminal: {user['terminal']} | Host: {user['host']} | Started: {user['started']}{Style.RESET_ALL}")
            
            print("=" * 50)
            
            if anomalies:
                print(Fore.RED + "Anomalías detectadas:" + Style.RESET_ALL)
                for anomaly in anomalies:
                    print(f"{Fore.RED}User: {anomaly['name']} | Terminal: {anomaly['terminal']} | Host: {anomaly['host']} | Started: {anomaly['started']}{Style.RESET_ALL}")
                    print(f"{Fore.RED}Reason: {anomaly['reason']}{Style.RESET_ALL}")
            
            time.sleep(10)
    
    except KeyboardInterrupt:
        print(Fore.RED + "\nMonitoreo finalizado por el usuario." + Style.RESET_ALL)

if __name__ == "__main__":
    show_interface()
