"""Setzt oder entfernt den Windows-Autostart-Eintrag für Voice-to-Text."""
import sys
import os
import winreg

APP_NAME = "VoiceToText"
# Always use pythonw.exe (no console window)
PYTHON_EXE = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def enable_autostart():
    command = f'"{PYTHON_EXE}" "{SCRIPT_PATH}"'
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)
    print(f"Autostart aktiviert: {command}")


def disable_autostart():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
        print("Autostart deaktiviert.")
    except FileNotFoundError:
        print("Autostart war nicht aktiviert.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--disable":
        disable_autostart()
    else:
        enable_autostart()
