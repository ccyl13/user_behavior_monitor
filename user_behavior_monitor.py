import os
import psutil
import time
import json
import requests
from datetime import datetime
from colorama import Fore, Style, init
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

init()

# Variables globales
ANOMALY_LOG = "anomaly_log.json"
USERS = {}
MONITORED_DIRS = ["/path/to/monitor"]  # Añadir directorios a monitorizar

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.log = []

    def process(self, event):
        if event.event_type in ['created', 'modified', 'deleted']:
            self.log.append({
                "path": event.src_path,
                "event_type": event.event_type,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

    def on_any_event(self, event):
        self.process(event)

def get_system_data():
    """
    Obtiene la información del sistema, incluyendo usuarios actuales, terminales, tiempos de inicio,
    uso de CPU, memoria y eventos críticos.
    """
    users = psutil.users()
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    
    system_data = []
    for user in users:
        system_data.append({
            "name": user.name,
            "terminal": user.terminal,
            "host": user.host,
            "started": datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S'),
            "cpu_usage": cpu_usage,
            "memory_usage": memory_info.percent
        })
    return system_data

def detect_anomalies(current_data):
    """
    Detecta anomalías en los datos de inicio de sesión y otros eventos críticos del sistema.
    """
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
        
        # Detección básica de patrones inusuales de uso de CPU y memoria
        if user["cpu_usage"] > 80:
            anomalies.append({
                "name": user["name"],
                "cpu_usage": user["cpu_usage"],
                "memory_usage": user["memory_usage"],
                "reason": "High CPU usage detected"
            })
        if user["memory_usage"] > 80:
            anomalies.append({
                "name": user["name"],
                "cpu_usage": user["cpu_usage"],
                "memory_usage": user["memory_usage"],
                "reason": "High memory usage detected"
            })
    
    return anomalies

def monitor_file_changes():
    """
    Configura y arranca el monitor de cambios en archivos.
    """
    event_handler = FileChangeHandler()
    observer = Observer()
    for directory in MONITORED_DIRS:
        observer.schedule(event_handler, path=directory, recursive=True)
    observer.start()
    return event_handler

def save_anomaly_log(anomalies):
    """
    Guarda las anomalías detectadas en un archivo de registro.
    """
    with open(ANOMALY_LOG, 'a') as file:
        for anomaly in anomalies:
            file.write(json.dumps(anomaly) + "\n")
            # Enviar anomalías a un sistema SIEM (simulación)
            try:
                response = requests.post('https://siem.example.com/api/logs', json=anomaly)
                if response.status_code != 200:
                    print(Fore.RED + f"Error al enviar datos a SIEM: {response.status_code}" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"Excepción al enviar datos a SIEM: {e}" + Style.RESET_ALL)

def show_interface():
    """
    Muestra la interfaz de usuario y ejecuta el monitoreo en tiempo real.
    """
    try:
        file_change_handler = monitor_file_changes()
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
                print(f"{Fore.CYAN}User: {user['name']} | Terminal: {user['terminal']} | Host: {user['host']} | Started: {user['started']} | CPU Usage: {user['cpu_usage']}% | Memory Usage: {user['memory_usage']}%{Style.RESET_ALL}")
            
            print("=" * 50)
            
            if anomalies:
                print(Fore.RED + "Anomalías detectadas:" + Style.RESET_ALL)
                for anomaly in anomalies:
                    print(f"{Fore.RED}User: {anomaly['name']} | Terminal: {anomaly.get('terminal', 'N/A')} | Host: {anomaly.get('host', 'N/A')} | Started: {anomaly.get('started', 'N/A')} | CPU Usage: {anomaly.get('cpu_usage', 'N/A')}% | Memory Usage: {anomaly.get('memory_usage', 'N/A')}%")
                    print(f"{Fore.RED}Reason: {anomaly['reason']}{Style.RESET_ALL}")
            
            # Mostrar eventos críticos de archivos
            if file_change_handler.log:
                print(Fore.MAGENTA + "Eventos críticos de archivos:" + Style.RESET_ALL)
                for event in file_change_handler.log:
                    print(f"{Fore.MAGENTA}Path: {event['path']} | Event Type: {event['event_type']} | Timestamp: {event['timestamp']}{Style.RESET_ALL}")
                file_change_handler.log = []
            
            time.sleep(10)
    
    except KeyboardInterrupt:
        print(Fore.RED + "\nMonitoreo finalizado por el usuario." + Style.RESET_ALL)

if __name__ == "__main__":
    show_interface()

