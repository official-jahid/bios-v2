# ============================================================================
# main.py – REGIX Studio (Stealth Edition)
# Only Aimbot + Aimdrag + Cleanup (F8), no web, no logs, no files.
# HWID (SID) check with hardcoded list.
# ============================================================================

import os
import sys
import ctypes
import threading
import time
import subprocess
import platform
import pymem
from pymem.pattern import pattern_scan_all
from pyinjector import inject
import psutil
import win32security
import keyboard  # for global hotkeys

# ----------------------------------------------------------------------------
# HIDE CONSOLE WINDOW
# ----------------------------------------------------------------------------
if sys.platform == "win32":
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

# ----------------------------------------------------------------------------
# PROCESS RENAME (to appear as "svchost.exe" in Task Manager)
# ----------------------------------------------------------------------------
def rename_process():
    try:
        p = psutil.Process(os.getpid())
        p.name = "svchost.exe"  # Some versions of psutil allow this
        # Alternative: use ctypes to set process name via Windows API
        # (but psutil may not persist; we'll also set window title)
        ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
    except:
        pass

rename_process()

# ----------------------------------------------------------------------------
# HARDCODED SID CHECK (replace with your own SID(s))
# ----------------------------------------------------------------------------
ALLOWED_SIDS = [
    "S-1-5-21-1234567890-1234567890-1234567890-1001",  # example SID
    # Add more SIDs as needed, or use a single one.
]

def get_sid():
    try:
        winuser = os.getlogin()
        sid, _, _ = win32security.LookupAccountName(None, winuser)
        return win32security.ConvertSidToStringSid(sid)
    except:
        return None

def check_sid():
    sid = get_sid()
    if sid is None:
        return False
    return sid in ALLOWED_SIDS

if not check_sid():
    # If SID not allowed, exit silently after a short delay.
    time.sleep(2)
    sys.exit(0)

# ----------------------------------------------------------------------------
# CLEANUP FUNCTION (from bat.bat, runs in a separate thread)
# ----------------------------------------------------------------------------
def cleanup():
    try:
        # Terminate tracking processes
        for proc in ["explorer.exe", "chrome.exe", "msedge.exe", "firefox.exe",
                     "brave.exe", "opera.exe", "Taskmgr.exe"]:
            subprocess.run(["taskkill", "/f", "/im", proc], capture_output=True, shell=True)

        # Registry deletions
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

        # Recent, Jump Lists, History
        paths = [
            os.path.expandvars("%AppData%\\Microsoft\\Windows\\Recent\\*.*"),
            os.path.expandvars("%AppData%\\Microsoft\\Windows\\Recent\\AutomaticDestinations\\*.*"),
            os.path.expandvars("%AppData%\\Microsoft\\Windows\\Recent\\CustomDestinations\\*.*"),
            os.path.expandvars("%LocalAppData%\\Microsoft\\Windows\\History\\*.*"),
        ]
        for p in paths:
            subprocess.run(["del", "/f", "/q", "/s", p], capture_output=True, shell=True)

        # Prefetch
        subprocess.run(["del", "/f", "/q", "/s", os.path.expandvars("%SystemRoot%\\Prefetch\\*.*")], capture_output=True, shell=True)
        subprocess.run(["del", "/f", "/q", "/s", os.path.expandvars("%SystemRoot%\\Prefetch\\ReadyBoot\\*.*")], capture_output=True, shell=True)
        subprocess.run(["REG", "DELETE", r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage\AppLaunch", "/f"], capture_output=True, shell=True)

        # Temp files
        for env in ["TEMP", "TMP"]:
            subprocess.run(["del", "/f", "/q", "/s", os.path.expandvars(f"%{env}%\\*.*")], capture_output=True, shell=True)
        subprocess.run(["del", "/f", "/q", "/s", os.path.expandvars("%SystemRoot%\\Temp\\*.*")], capture_output=True, shell=True)

        # Browser caches
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

        # Crash dumps, WER, Windows Update cache
        crash_paths = [
            os.path.expandvars("%LocalAppData%\\CrashDumps\\*.*"),
            os.path.expandvars("%SystemRoot%\\Minidump\\*.*"),
            os.path.expandvars("%ProgramData%\\Microsoft\\Windows\\WER\\ReportArchive\\*.*"),
            os.path.expandvars("%SystemRoot%\\SoftwareDistribution\\Download\\*.*"),
        ]
        for p in crash_paths:
            subprocess.run(["del", "/f", "/q", "/s", p], capture_output=True, shell=True)

        # Event logs
        try:
            result = subprocess.run(["wevtutil", "el"], capture_output=True, text=True, shell=True)
            for log in result.stdout.splitlines():
                if log.strip():
                    subprocess.run(["wevtutil", "cl", log.strip()], capture_output=True, shell=True)
        except:
            pass

        # Network caches
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, shell=True)
        subprocess.run(["ipconfig", "/release"], capture_output=True, shell=True)
        subprocess.run(["ipconfig", "/renew"], capture_output=True, shell=True)
        subprocess.run(["arp", "-d", "*"], capture_output=True, shell=True)
        subprocess.run(["nbtstat", "-R"], capture_output=True, shell=True)

        # USN Journal (requires admin, ignore failure)
        subprocess.run(["fsutil", "usn", "deletejournal", "/d", "c:"], capture_output=True, shell=True)

        # Restart Explorer
        subprocess.run(["start", "explorer.exe"], capture_output=True, shell=True)

    except:
        pass  # Silent failure

# ----------------------------------------------------------------------------
# MEMORY FUNCTIONS (Aimbot + Drag)
# ----------------------------------------------------------------------------
def mkp(aob: str):
    if '??' in aob:
        if aob.startswith("??"):
            aob = f" {aob}"
            n = aob.replace(" ??", ".").replace(" ", "\\x")
            b = bytes(n.encode())
        else:
            n = aob.replace(" ??", ".").replace(" ", "\\x")
            b = bytes(f"\\x{n}".encode())
        return b
    else:
        m = aob.replace(" ", "\\x")
        c = bytes(f"\\x{m}".encode())
        return c

AIMBOT_PATTERN = "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 A5 43 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 80 BF"
DRAG_PATTERN = "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 00 ?? ?? ?? ?? 00 00 00 00 ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 A5 43"

def get_pid(processName):
    pm = pymem.Pymem(processName)
    return pm.process_id

def find_pattern(pm, pattern):
    if isinstance(pattern, str):
        pattern = mkp(pattern)
    return pattern_scan_all(pm.process_handle, pattern, return_multiple=True)

def adjust_privileges():
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

_aimbot_original = []
_drag_original = []
_aimbot_addresses = []
_drag_addresses = []

def aimbot_load():
    global _aimbot_addresses
    try:
        adjust_privileges()
        pm = pymem.Pymem("HD-Player.exe")
        pattern = mkp(AIMBOT_PATTERN)
        _aimbot_addresses = find_pattern(pm, pattern)
        return bool(_aimbot_addresses)
    except:
        return False

def aimbot_on():
    global _aimbot_original
    if not _aimbot_addresses:
        if not aimbot_load():
            return False
    try:
        pm = pymem.Pymem("HD-Player.exe")
        if not _aimbot_original:
            for addr in _aimbot_addresses:
                target = addr + 0xB4
                _aimbot_original.append(pm.read_int(target))
        for addr in _aimbot_addresses:
            source = addr + 0xB8
            target = addr + 0xB4
            pm.write_int(target, pm.read_int(source))
        return True
    except:
        return False

def aimbot_off():
    global _aimbot_original
    if not _aimbot_addresses or not _aimbot_original:
        return False
    try:
        pm = pymem.Pymem("HD-Player.exe")
        for idx, addr in enumerate(_aimbot_addresses):
            target = addr + 0xB4
            if idx < len(_aimbot_original):
                pm.write_int(target, _aimbot_original[idx])
        _aimbot_original.clear()
        return True
    except:
        return False

def drag_load():
    global _drag_addresses
    try:
        adjust_privileges()
        pm = pymem.Pymem("HD-Player.exe")
        pattern = mkp(DRAG_PATTERN)
        _drag_addresses = find_pattern(pm, pattern)
        return bool(_drag_addresses)
    except:
        return False

def aimdrag_on():
    global _drag_original
    if not _drag_addresses:
        if not drag_load():
            return False
    try:
        pm = pymem.Pymem("HD-Player.exe")
        if not _drag_original:
            for addr in _drag_addresses:
                target = addr + 0xB4
                _drag_original.append(pm.read_int(target))
        for addr in _drag_addresses:
            source = addr + 0xE8
            target = addr + 0xB4
            pm.write_int(target, pm.read_int(source))
        return True
    except:
        return False

def aimdrag_off():
    global _drag_original
    if not _drag_addresses or not _drag_original:
        return False
    try:
        pm = pymem.Pymem("HD-Player.exe")
        for idx, addr in enumerate(_drag_addresses):
            target = addr + 0xB4
            if idx < len(_drag_original):
                pm.write_int(target, _drag_original[idx])
        _drag_original.clear()
        return True
    except:
        return False

# ----------------------------------------------------------------------------
# HOTKEY HANDLERS (no prints, no logs)
# ----------------------------------------------------------------------------
def on_aimbot_on():
    aimbot_on()

def on_aimbot_off():
    aimbot_off()

def on_aimdrag_on():
    aimdrag_on()

def on_aimdrag_off():
    aimdrag_off()

def on_cleanup():
    threading.Thread(target=cleanup, daemon=True).start()

# Register hotkeys (F3/F4 for aimbot, F5/F6 for drag, F8 for cleanup)
try:
    keyboard.add_hotkey('f3', on_aimbot_on)
    keyboard.add_hotkey('f4', on_aimbot_off)
    keyboard.add_hotkey('f5', on_aimdrag_on)
    keyboard.add_hotkey('f6', on_aimdrag_off)
    keyboard.add_hotkey('f8', on_cleanup)
except:
    pass

# ----------------------------------------------------------------------------
# MAIN LOOP – keep the script alive
# ----------------------------------------------------------------------------
def main():
    # Pre-load addresses? Optionally, we can load on first use.
    # Keep the program running.
    try:
        keyboard.wait()  # Blocks until a key is pressed (or forever)
    except KeyboardInterrupt:
        pass
    except:
        # If keyboard.wait fails, fallback to a simple sleep loop
        while True:
            time.sleep(3600)

if __name__ == "__main__":
    main()
