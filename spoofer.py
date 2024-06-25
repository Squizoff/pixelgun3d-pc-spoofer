import os
import sys
import ctypes
import winreg
import json
import random
import shutil
import subprocess
from colorama import init
import re

init()

def clear():
    os.system('cls' if os.name in ('nt', 'dos') else 'clear')

def info(msg):
    print(f"{Fore.LIGHTCYAN_EX}[INFO]{Fore.RESET} {msg}")

def error(msg):
    print(f"{Fore.LIGHTRED_EX}[ERROR]{Fore.RESET} {msg}")

def warning(msg):
    print(f"{Fore.LIGHTYELLOW_EX}[WARNING]{Fore.RESET} {msg}")

def success(msg):
    print(f"{Fore.LIGHTGREEN_EX}[SUCCESS]{Fore.RESET} {msg}")

def verbose(msg):
    print(f"{Fore.LIGHTBLACK_EX}[VERBOSE]{Fore.RESET} {msg}")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit()

def pgisopen():
    for proc in psutil.process_iter():
        if proc.name() == "Pixel Gun 3D.exe":
            try:
                return proc.pid > 0
            except:
                pass
    return False

def change_ip():
    try:
        subprocess.run(["ipconfig", "/release"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["ipconfig", "/renew"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        success("IP address changed!")
    except subprocess.CalledProcessError as e:
        error(f"Failed to change IP address: {e}")

def remove_pixel_gun_traces():
    completed = 0
    user_ids_str = ""
    info("Removing LocalLow/Pixel Gun Team directory...")

    appdataDir = os.getenv("APPDATA")
    if appdataDir is None:
        error("Error getting appdata path... Exiting")
        input(f"\n{Fore.LIGHTWHITE_EX}[>>]{Fore.RESET} [{completed} / 2] Press enter to exit...")
        exit()

    localLowDir = os.path.abspath(os.path.join(appdataDir, "..", "LocalLow"))
    pgteamdir = localLowDir + "\\Pixel Gun Team"
    idDir = pgteamdir + "\\Pixel Gun 3D\\lobby_textures"
    verbose(f"Pixel Gun Team Directory: {pgteamdir}")

    if os.path.isdir(pgteamdir):
        verbose("Directory Exists! Deleting...")
        try:
            directories = os.listdir(idDir)
            user_ids = [int(d.split("-")[1]) for d in directories if d.startswith("user-")]
            user_ids_str = ", ".join(str(id) for id in user_ids)
        except:
            error("Failed to get list of IDs, skipping... (you can ignore this)")
        try:
            shutil.rmtree(pgteamdir)
            success("Deleted Pixel Gun Team!")
            completed += 1
        except Exception as e:
            error(f"Failed to delete directory, error: {e}")
    else:
        error("This directory was not found, it may have been deleted already! Skipping...")

    info("Removing Registry Keys")
    if not is_admin():
        error("This script is not being ran with Administrator Privileges so it is unable to delete registry keys!")
        input(f"\n{Fore.LIGHTWHITE_EX}[>>]{Fore.RESET} [{completed} / 2] Press enter to exit...")
        exit()
    else:
        try:
            pRemTarget = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, "Software" + "\\Pixel Gun Team")
            try:
                winreg.OpenKey(pRemTarget, "Pixel Gun 3D")
                winreg.DeleteKey(pRemTarget, "Pixel Gun 3D")
                success("Deleted Pixel Gun Team Registry keys!")
                completed += 1
            except:
                error("The registry keys were not found, it may have been deleted already! Skipping...")
                pass
        except Exception as e:
            error(f"Error when deleting keys: {e}")
    if not user_ids_str == '':
        success(f"Traces found: {user_ids_str}")

def spoof_hardware(hardware_data):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", 0,
                            winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
            winreg.SetValueEx(key, "ProductName", 0, winreg.REG_SZ, random.choice(hardware_data['CPUs']))
            success("Spoofed CPU name!")
    except Exception as e:
        error(f"Failed to spoof CPU name: {e}")

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Video", 0,
                            winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
            for i in range(100):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as subkey:
                        for j in range(100):
                            try:
                                subsubkey_name = winreg.EnumKey(subkey, j)
                                with winreg.OpenKey(subkey, subsubkey_name, 0,
                                                    winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as subsubkey:
                                    try:
                                        winreg.SetValueEx(subsubkey, "Device Description", 0, winreg.REG_SZ,
                                                          random.choice(hardware_data['GPUs']))
                                        success(f"Spoofed GPU name in subkey {subsubkey_name}!")
                                    except Exception as e:
                                        error(f"Failed to spoof GPU name in subsubkey {subsubkey_name}: {e}")
                            except OSError:
                                break
                except OSError:
                    break
    except Exception as e:
        error(f"Failed to spoof GPU name: {e}")

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", 0,
                            winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
            winreg.SetValueEx(key, "ProcessorNameString", 0, winreg.REG_SZ, random.choice(hardware_data['RAM']))
            success("Spoofed RAM!")
    except Exception as e:
        error(f"Failed to spoof RAM: {e}")

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Disk\Enum", 0,
                            winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
            winreg.SetValueEx(key, "0", 0, winreg.REG_SZ, random.choice(hardware_data['Storage']))
            success("Spoofed Storage!")
    except Exception as e:
        error(f"Failed to spoof Storage: {e}")

def spoof_mac_address(interface):
    try:
        if not all(ord(c) < 128 for c in interface):
            return

        new_mac = "02:00:00:%02x:%02x:%02x" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        subprocess.run(["netsh", "interface", "set", "interface", interface, "admin=disable"], check=True)
        subprocess.run(["netsh", "interface", "set", "interface", interface, f"new={new_mac}"], check=True)
        subprocess.run(["netsh", "interface", "set", "interface", interface, "admin=enable"], check=True)
        success(f"MAC address for {interface} changed to {new_mac}!")
    except subprocess.CalledProcessError as e:
        error(f"Failed to change MAC address for {interface}: {e}")

def main():
    run_as_admin()

    clear()
    print("Hardware Spoofer by: Squizoff")
    os.system("title Hardware Spoofer")

    if pgisopen():
        error("Pixel Gun 3D is currently running! Close it and run again.")
        input(f"\n{Fore.LIGHTWHITE_EX}[>>]{Fore.RESET} Press enter to exit...")
        exit()

    info("Reading hardware data...")
    try:
        with open("hardware.json", "r") as file:
            hardware_data = json.load(file)
    except FileNotFoundError:
        error("hardware.json file not found!")
        exit()

    info("Spoofing hardware...")
    spoof_hardware(hardware_data)

    info("Changing IP address...")
    change_ip()

    interfaces = subprocess.run(["netsh", "interface", "show", "interface"], capture_output=True, text=True).stdout
    interface_list = re.findall(r"(\S+)\s+\S+\s+\S+\s+\S+\s+\S+", interfaces)
    for interface in interface_list:
        spoof_mac_address(interface)

    remove_pixel_gun_traces()

    input(f"\n{Fore.LIGHTWHITE_EX}[>>]{Fore.RESET} Operation completed! Please restart your computer for all changes to take effect. Press enter to exit...")

if __name__ == "__main__":
    from colorama import Fore
    import colorama
    import psutil

    colorama.init()

    main()