import os
import socket
import threading
import time

ports = {}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def start_port(port, name):
    def run_server():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('0.0.0.0', port))
            server.listen(5)
            ports[port]["status"] = "🟢 ONLINE"
            print(f"\n[+] Порт {port} открыт как '{name}'")
            print(f"[+] ХОСТ: 0.0.0.0:{port}")

            while ports[port]["status"] == "🟢 ONLINE":
                server.settimeout(2)
                try:
                    client, addr = server.accept()
                    print(f"[!] Подключение к {name} ({port}) от {addr}")
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
        ports[port] = {"name": name, "status": "🟡 ЗАПУСК..."}
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

def show_menu():
    clear_screen()
    print("=== RAT PORT MANAGER ===\n")
    print("Список портов (0.0.0.0:порт):")
    if not ports:
        print("  Пусто. Создай первый порт.")
    else:
        for p, data in ports.items():
            print(f"  {data['status']} [{data['name']}] → 0.0.0.0:{p}")
    print("\nКоманды:")
    print("  1. Создать порт")
    print("  2. Закрыть порт")
    print("  3. Обновить статусы")
    print("  0. Выход")

def main():
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
            continue

        elif cmd == "0":
            print("Выход.")
            break

        else:
            print("Неверная команда.")
            input("Нажми Enter...")

if __name__ == "__main__":
    main()
