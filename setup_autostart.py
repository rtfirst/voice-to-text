"""Set up or remove autostart for Voice-to-Text."""

import sys
import os

APP_NAME = "VoiceToText"
SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")


def _enable_windows():
    import winreg
    python_dir = os.path.dirname(sys.executable)
    pythonw = os.path.join(python_dir, "pythonw.exe")
    command = f'"{pythonw}" "{SCRIPT_PATH}"'
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)
    print(f"Autostart enabled: {command}")


def _disable_windows():
    import winreg
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
        print("Autostart disabled.")
    except FileNotFoundError:
        print("Autostart was not enabled.")


def _enable_macos():
    import plistlib
    plist_dir = os.path.expanduser("~/Library/LaunchAgents")
    os.makedirs(plist_dir, exist_ok=True)
    plist_path = os.path.join(plist_dir, f"com.{APP_NAME.lower()}.plist")
    plist = {
        "Label": f"com.{APP_NAME.lower()}",
        "ProgramArguments": [sys.executable, SCRIPT_PATH],
        "RunAtLoad": True,
        "KeepAlive": False,
    }
    with open(plist_path, "wb") as f:
        plistlib.dump(plist, f)
    print(f"Autostart enabled: {plist_path}")


def _disable_macos():
    plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.{APP_NAME.lower()}.plist")
    if os.path.exists(plist_path):
        os.remove(plist_path)
        print("Autostart disabled.")
    else:
        print("Autostart was not enabled.")


def enable_autostart():
    if sys.platform == "darwin":
        _enable_macos()
    else:
        _enable_windows()


def disable_autostart():
    if sys.platform == "darwin":
        _disable_macos()
    else:
        _disable_windows()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--disable":
        disable_autostart()
    else:
        enable_autostart()
