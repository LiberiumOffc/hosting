import socket
import threading
import time

# Словарь для хранения статусов портов
ports_status = {}

def start_port(port):
    """Запускает сервер на указанном порту"""
    def run_server():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('0.0.0.0', port))
            server.listen(5)
            ports_status[port] = "🟢 ONLINE (слушает)"
            print(f"\n[+] Порт {port} открыт и слушает клиентов")

            while ports_status.get(port) == "🟢 ONLINE (слушает)":
                server.settimeout(2)
                try:
                    client, addr = server.accept()
                    print(f"[!] Подключение на порт {port} от {addr}")
                    client.send(b"RAT Connection Established\n")
                    client.close()
                except socket.timeout:
                    continue
                except:
                    break
        except Exception as e:
            ports_status[port] = f"🔴 ОШИБКА: {e}"
        finally:
            server.close()

    if port not in ports_status or "OFFLINE" in ports_status[port] or "ОШИБКА" in ports_status[port]:
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        time.sleep(1)
        if port not in ports_status:
            ports_status[port] = "🟢 ONLINE (слушает)"
    else:
        print(f"Порт {port} уже запущен.")

def stop_port(port):
    """Останавливает порт (помечает как офлайн)"""
    if port in ports_status and "ONLINE" in ports_status[port]:
        ports_status[port] = "🔴 OFFLINE (остановлен)"
        print(f"[-] Порт {port} остановлен.")
    else:
        print(f"Порт {port} не активен.")

def show_status():
    print("\n--- СТАТУС ПОРТОВ ---")
    if not ports_status:
        print("Нет активных портов.")
    for port, status in ports_status.items():
        print(f"Порт {port}: {status}")

def main():
    print("=== RAT PORT MANAGER ===")
    print("Создавай порты для RAT и смотри статус 🟢🔴")
    while True:
        print("\n1. Открыть порт")
        print("2. Закрыть порт")
        print("3. Показать статусы")
        print("0. Выход")
        choice = input("Выбери: ")

        if choice == "1":
            try:
                port = int(input("Введи порт для открытия: "))
                start_port(port)
            except:
                print("Ошибка ввода порта.")
        elif choice == "2":
            try:
                port = int(input("Введи порт для закрытия: "))
                stop_port(port)
            except:
                print("Ошибка ввода.")
        elif choice == "3":
            show_status()
        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Неверный выбор.")

if __name__ == "__main__":
    main()
