# main.py – REGIX Studio (Fixed Aimbot & Aimdrag)
# প্রতিবার F3/F5 চাপলে নতুন স্ক্যান – পরবর্তী ম্যাচেও কাজ করবে।
import os
import sys
import ctypes
import threading
import time
import subprocess
import pymem
from pymem.pattern import pattern_scan_all
import psutil
import keyboard

# ---- কনসোল হাইড ----
if sys.platform == "win32":
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

# ---- প্রসেস নাম পরিবর্তন ----
def rename_process():
    try:
        p = psutil.Process(os.getpid())
        p.name = "svchost.exe"
        ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
    except:
        pass
rename_process()

# ---- ক্লিনআপ + রিস্টার্ট (F8) ----
def cleanup():
    try:
        # (ক্লিনআপ ফাংশন আগের মতোই, সংক্ষেপে দিচ্ছি)
        for proc in ["explorer.exe", "chrome.exe", "msedge.exe", "firefox.exe",
                     "brave.exe", "opera.exe", "Taskmgr.exe"]:
            subprocess.run(["taskkill", "/f", "/im", proc], capture_output=True, shell=True)
        reg_keys = [
            r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs",
            r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist",
            r"HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache",
            r"HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\BagMRU",
            r"HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\Bags",
            r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
            r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths",
            r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlMRU",
            r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU",
            r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery",
            r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Applets\Regedit",
        ]
        for key in reg_keys:
            subprocess.run(["REG", "DELETE", key, "/f"], capture_output=True, shell=True)
        subprocess.run(["REG", "DELETE", r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Applets\Regedit", "/v", "LastKey", "/f"], capture_output=True, shell=True)
        paths = [
            os.path.expandvars("%AppData%\\Microsoft\\Windows\\Recent\\*.*"),
            os.path.expandvars("%AppData%\\Microsoft\\Windows\\Recent\\AutomaticDestinations\\*.*"),
            os.path.expandvars("%AppData%\\Microsoft\\Windows\\Recent\\CustomDestinations\\*.*"),
            os.path.expandvars("%LocalAppData%\\Microsoft\\Windows\\History\\*.*"),
        ]
        for p in paths:
            subprocess.run(["del", "/f", "/q", "/s", p], capture_output=True, shell=True)
        subprocess.run(["del", "/f", "/q", "/s", os.path.expandvars("%SystemRoot%\\Prefetch\\*.*")], capture_output=True, shell=True)
        subprocess.run(["del", "/f", "/q", "/s", os.path.expandvars("%SystemRoot%\\Prefetch\\ReadyBoot\\*.*")], capture_output=True, shell=True)
        subprocess.run(["REG", "DELETE", r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage\AppLaunch", "/f"], capture_output=True, shell=True)
        for env in ["TEMP", "TMP"]:
            subprocess.run(["del", "/f", "/q", "/s", os.path.expandvars(f"%{env}%\\*.*")], capture_output=True, shell=True)
        subprocess.run(["del", "/f", "/q", "/s", os.path.expandvars("%SystemRoot%\\Temp\\*.*")], capture_output=True, shell=True)
        browser_paths = [
            os.path.expandvars("%LocalAppData%\\Google\\Chrome\\User Data\\Default\\Cache\\*.*"),
            os.path.expandvars("%LocalAppData%\\Google\\Chrome\\User Data\\Default\\History"),
            os.path.expandvars("%LocalAppData%\\Google\\Chrome\\User Data\\Default\\Download History"),
            os.path.expandvars("%LocalAppData%\\Microsoft\\Edge\\User Data\\Default\\Cache\\*.*"),
            os.path.expandvars("%LocalAppData%\\Microsoft\\Edge\\User Data\\Default\\History"),
            os.path.expandvars("%LocalAppData%\\Microsoft\\Windows\\INetCache\\*.*"),
            os.path.expandvars("%LocalAppData%\\Microsoft\\Windows\\WebCache\\*.*"),
        ]
        for p in browser_paths:
            subprocess.run(["del", "/f", "/q", "/s", p], capture_output=True, shell=True)
        crash_paths = [
            os.path.expandvars("%LocalAppData%\\CrashDumps\\*.*"),
            os.path.expandvars("%SystemRoot%\\Minidump\\*.*"),
            os.path.expandvars("%ProgramData%\\Microsoft\\Windows\\WER\\ReportArchive\\*.*"),
            os.path.expandvars("%SystemRoot%\\SoftwareDistribution\\Download\\*.*"),
        ]
        for p in crash_paths:
            subprocess.run(["del", "/f", "/q", "/s", p], capture_output=True, shell=True)
        try:
            result = subprocess.run(["wevtutil", "el"], capture_output=True, text=True, shell=True)
            for log in result.stdout.splitlines():
                if log.strip():
                    subprocess.run(["wevtutil", "cl", log.strip()], capture_output=True, shell=True)
        except:
            pass
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, shell=True)
        subprocess.run(["ipconfig", "/release"], capture_output=True, shell=True)
        subprocess.run(["ipconfig", "/renew"], capture_output=True, shell=True)
        subprocess.run(["arp", "-d", "*"], capture_output=True, shell=True)
        subprocess.run(["nbtstat", "-R"], capture_output=True, shell=True)
        subprocess.run(["fsutil", "usn", "deletejournal", "/d", "c:"], capture_output=True, shell=True)
        subprocess.run(["start", "explorer.exe"], capture_output=True, shell=True)
        # Windows Restart (graceful)
        subprocess.run(["shutdown", "/r", "/t", "0"], capture_output=True, shell=True)
    except:
        pass

# ---- সঠিক mkp ফাংশন ----
def mkp(pattern_str: str) -> bytes:
    """
    Convert pattern string like "FF ?? 00 AB" to bytes with 0x3F for wildcards.
    pymem's pattern_scan_all uses 0x3F (b'?') as wildcard.
    """
    parts = pattern_str.split()
    result = bytearray()
    for p in parts:
        if p == "??":
            result.append(0x3F)   # wildcard
        else:
            # hex string, e.g., "FF" -> 0xFF
            try:
                result.append(int(p, 16))
            except ValueError:
                # যদি কোনো অক্ষর বাদ পড়ে, তাহলে সেটিকেও wildcard ধরব
                result.append(0x3F)
    return bytes(result)

# ---- আপনার দেওয়া প্যাটার্ন (হুবহু) ----
AIMBOT_PATTERN = "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 A5 43 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 80 BF"
DRAG_PATTERN = "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 00 ?? ?? ?? ?? 00 00 00 00 ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 A5 43"

# ---- অফসেট ----
AIMBOT_READ_OFFSET  = 0xAF
AIMBOT_WRITE_OFFSET = 0xAB
DRAG_READ_OFFSET    = 0xE8
DRAG_WRITE_OFFSET   = 0xB4

# ---- অ্যাড্রেস গ্লোবাল ----
_aimbot_addresses = []
_aimbot_original = []
_drag_addresses = []
_drag_original = []

def adjust_privileges():
    # SeDebugPrivilege সক্রিয় করা
    SE_DEBUG_NAME = "SeDebugPrivilege"
    SE_PRIVILEGE_ENABLED = 0x00000002
    token_handle = ctypes.c_void_p()
    luid = ctypes.c_longlong()
    ctypes.windll.advapi32.OpenProcessToken(
        ctypes.windll.kernel32.GetCurrentProcess(),
        0x20 | 0x8,
        ctypes.byref(token_handle)
    )
    ctypes.windll.advapi32.LookupPrivilegeValueA(
        0, SE_DEBUG_NAME.encode('ascii'), ctypes.byref(luid)
    )
    class LUID_AND_ATTRIBUTES(ctypes.Structure):
        _fields_ = [("Luid", ctypes.c_longlong), ("Attributes", ctypes.c_ulong)]
    class TOKEN_PRIVILEGES(ctypes.Structure):
        _fields_ = [("PrivilegeCount", ctypes.c_ulong), ("Privileges", LUID_AND_ATTRIBUTES)]
    new_privileges = TOKEN_PRIVILEGES(1, LUID_AND_ATTRIBUTES(luid.value, SE_PRIVILEGE_ENABLED))
    ctypes.windll.advapi32.AdjustTokenPrivileges(
        token_handle, False, ctypes.byref(new_privileges), 0, None, None
    )
    ctypes.windll.kernel32.CloseHandle(token_handle)

def scan_pattern(pattern_bytes: bytes) -> list:
    """প্যাটার্ন স্ক্যান করে অ্যাড্রেসের লিস্ট ফেরত দেয়, ব্যর্থ হলে খালি লিস্ট"""
    try:
        adjust_privileges()
        pm = pymem.Pymem("HD-Player.exe")
        return pattern_scan_all(pm.process_handle, pattern_bytes, return_multiple=True)
    except:
        return []

# ---- Aimbot ----
def aimbot_on():
    global _aimbot_addresses, _aimbot_original
    # ১. নতুন স্ক্যান
    _aimbot_addresses = scan_pattern(mkp(AIMBOT_PATTERN))
    if not _aimbot_addresses:
        return False
    try:
        pm = pymem.Pymem("HD-Player.exe")
        _aimbot_original.clear()
        # ২. অরিজিনাল ভ্যালু সেভ (WRITE অফসেট থেকে)
        for addr in _aimbot_addresses:
            target = addr + AIMBOT_WRITE_OFFSET
            _aimbot_original.append(pm.read_int(target))
        # ৩. প্যাচ (READ থেকে WRITE-এ কপি)
        for addr in _aimbot_addresses:
            source = addr + AIMBOT_READ_OFFSET
            target = addr + AIMBOT_WRITE_OFFSET
            val = pm.read_int(source)
            pm.write_int(target, val)
        return True
    except:
        return False

def aimbot_off():
    global _aimbot_addresses, _aimbot_original
    if not _aimbot_addresses or not _aimbot_original:
        return False
    try:
        pm = pymem.Pymem("HD-Player.exe")
        for idx, addr in enumerate(_aimbot_addresses):
            target = addr + AIMBOT_WRITE_OFFSET
            if idx < len(_aimbot_original):
                pm.write_int(target, _aimbot_original[idx])
        _aimbot_original.clear()
        return True
    except:
        return False

# ---- Aimdrag ----
def aimdrag_on():
    global _drag_addresses, _drag_original
    _drag_addresses = scan_pattern(mkp(DRAG_PATTERN))
    if not _drag_addresses:
        return False
    try:
        pm = pymem.Pymem("HD-Player.exe")
        _drag_original.clear()
        for addr in _drag_addresses:
            target = addr + DRAG_WRITE_OFFSET
            _drag_original.append(pm.read_int(target))
        for addr in _drag_addresses:
            source = addr + DRAG_READ_OFFSET
            target = addr + DRAG_WRITE_OFFSET
            val = pm.read_int(source)
            pm.write_int(target, val)
        return True
    except:
        return False

def aimdrag_off():
    global _drag_addresses, _drag_original
    if not _drag_addresses or not _drag_original:
        return False
    try:
        pm = pymem.Pymem("HD-Player.exe")
        for idx, addr in enumerate(_drag_addresses):
            target = addr + DRAG_WRITE_OFFSET
            if idx < len(_drag_original):
                pm.write_int(target, _drag_original[idx])
        _drag_original.clear()
        return True
    except:
        return False

# ---- হটকি হ্যান্ডলার ----
def on_aimbot_on():   aimbot_on()
def on_aimbot_off():  aimbot_off()
def on_aimdrag_on():  aimdrag_on()
def on_aimdrag_off(): aimdrag_off()
def on_cleanup():     threading.Thread(target=cleanup, daemon=True).start()

try:
    keyboard.add_hotkey('f3', on_aimbot_on)
    keyboard.add_hotkey('f4', on_aimbot_off)
    keyboard.add_hotkey('f5', on_aimdrag_on)
    keyboard.add_hotkey('f6', on_aimdrag_off)
    keyboard.add_hotkey('f8', on_cleanup)
except:
    pass

# ---- মূল লুপ ----
def main():
    try:
        keyboard.wait()
    except:
        while True:
            time.sleep(3600)

if __name__ == "__main__":
    main()
