# main.py – REGIX Studio (Silent – main branch AOB)
# AOB, offsets, mkp() from main branch – 100% confirmed working
# Features: Aimbot (F3/F4), Aimdrag (F5/F6), Cleanup+Restart (F8)
# Fresh scan on every F3/F5 press – works every match
import os
import sys
import ctypes
import threading
import time
import subprocess
import pymem
from pymem.pattern import pattern_scan_all
from pymem.memory import read_bytes, write_bytes
import psutil
import keyboard

# ---- Console Hide ----
if sys.platform == "win32":
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

# ---- Process Rename ----
def rename_process():
    try:
        p = psutil.Process(os.getpid())
        p.name = "svchost.exe"
        ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
    except:
        pass
rename_process()

# ---- main branch's mkp() (?? → .) ----
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

# ---- main branch's AOB patterns ----
AIMBOT_PATTERN = "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 A5 43 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 80 BF"

DRAG_PATTERN = "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 00 ?? ?? ?? ?? 00 00 00 00 ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 A5 43"

# ---- main branch's offsets ----
AIMBOT_READ_OFFSET  = 0xB8
AIMBOT_WRITE_OFFSET = 0xB4
DRAG_READ_OFFSET    = 0xE8
DRAG_WRITE_OFFSET   = 0xB4

# ---- Globals ----
_aimbot_addresses = []
_aimbot_originals = []
_aimbot_active = False

_drag_addresses = []
_drag_originals = []
_drag_active = False

# ---- Debug Log (silent, only for troubleshooting) ----
DEBUG_LOG = os.path.expandvars("%TEMP%\\regix_debug.log")
def debug_log(msg):
    try:
        with open(DEBUG_LOG, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - {msg}\n")
    except:
        pass
debug_log("=== REGIX Studio Started (Silent) ===")

def adjust_privileges():
    try:
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
        debug_log("AdjustPrivileges OK")
        return True
    except Exception as e:
        debug_log(f"AdjustPrivileges error: {e}")
        return False

def scan_pattern(pattern_str: str) -> list:
    try:
        if not adjust_privileges():
            return []
        pm = pymem.Pymem("HD-Player.exe")
        pattern_bytes = mkp(pattern_str)
        debug_log(f"Scanning: {pattern_bytes[:30]}...")
        addresses = pattern_scan_all(pm.process_handle, pattern_bytes, return_multiple=True)
        debug_log(f"Found {len(addresses)} addresses")
        pm.close_process()
        return addresses if addresses else []
    except pymem.exception.ProcessNotFound:
        debug_log("HD-Player.exe not found")
        return []
    except Exception as e:
        debug_log(f"Scan error: {e}")
        return []

# ---- Aimbot (fresh scan every time) ----
def aimbot_on():
    global _aimbot_addresses, _aimbot_originals, _aimbot_active
    
    debug_log("Aimbot ON (fresh scan)")
    
    _aimbot_addresses = scan_pattern(AIMBOT_PATTERN)
    if not _aimbot_addresses:
        debug_log("Aimbot ON failed: No addresses")
        return False
    
    debug_log(f"Found {len(_aimbot_addresses)} addresses")
    
    try:
        pm = pymem.Pymem("HD-Player.exe")
        success_count = 0
        _aimbot_originals.clear()
        
        for addr in _aimbot_addresses:
            try:
                write_addr = addr + AIMBOT_WRITE_OFFSET  # 0xB4
                read_addr = addr + AIMBOT_READ_OFFSET   # 0xB8
                
                orig_write = read_bytes(pm.process_handle, write_addr, 4)
                _aimbot_originals.append(orig_write)
                orig_read = read_bytes(pm.process_handle, read_addr, 4)
                write_bytes(pm.process_handle, write_addr, orig_read, 4)
                success_count += 1
            except Exception as e:
                debug_log(f"Address {hex(addr)} failed: {e}")
        
        pm.close_process()
        
        if success_count > 0:
            _aimbot_active = True
            debug_log(f"Aimbot ON: {success_count} patched")
            return True
        else:
            debug_log("Aimbot ON: 0 addresses patched")
            return False
            
    except Exception as e:
        debug_log(f"Aimbot ON error: {e}")
        return False

def aimbot_off():
    global _aimbot_addresses, _aimbot_originals, _aimbot_active
    
    debug_log("Aimbot OFF")
    
    if not _aimbot_addresses or not _aimbot_originals:
        debug_log("Aimbot OFF: No active aimbot")
        return False
    
    try:
        pm = pymem.Pymem("HD-Player.exe")
        success_count = 0
        
        for idx, addr in enumerate(_aimbot_addresses):
            try:
                write_addr = addr + AIMBOT_WRITE_OFFSET
                if idx < len(_aimbot_originals):
                    write_bytes(pm.process_handle, write_addr, _aimbot_originals[idx], 4)
                    success_count += 1
            except Exception as e:
                debug_log(f"Restore {hex(addr)} failed: {e}")
        
        pm.close_process()
        
        _aimbot_active = False
        _aimbot_addresses = []
        _aimbot_originals.clear()
        
        debug_log(f"Aimbot OFF: {success_count} restored")
        return True
        
    except Exception as e:
        debug_log(f"Aimbot OFF error: {e}")
        return False

# ---- Aimdrag (fresh scan every time) ----
def aimdrag_on():
    global _drag_addresses, _drag_originals, _drag_active
    
    debug_log("Aimdrag ON (fresh scan)")
    
    _drag_addresses = scan_pattern(DRAG_PATTERN)
    if not _drag_addresses:
        debug_log("Aimdrag ON failed: No addresses")
        return False
    
    debug_log(f"Found {len(_drag_addresses)} addresses")
    
    try:
        pm = pymem.Pymem("HD-Player.exe")
        success_count = 0
        _drag_originals.clear()
        
        for addr in _drag_addresses:
            try:
                write_addr = addr + DRAG_WRITE_OFFSET  # 0xB4
                read_addr = addr + DRAG_READ_OFFSET   # 0xE8
                
                orig_write = read_bytes(pm.process_handle, write_addr, 4)
                _drag_originals.append(orig_write)
                orig_read = read_bytes(pm.process_handle, read_addr, 4)
                write_bytes(pm.process_handle, write_addr, orig_read, 4)
                success_count += 1
            except Exception as e:
                debug_log(f"Address {hex(addr)} failed: {e}")
        
        pm.close_process()
        
        if success_count > 0:
            _drag_active = True
            debug_log(f"Aimdrag ON: {success_count} patched")
            return True
        else:
            debug_log("Aimdrag ON: 0 addresses patched")
            return False
            
    except Exception as e:
        debug_log(f"Aimdrag ON error: {e}")
        return False

def aimdrag_off():
    global _drag_addresses, _drag_originals, _drag_active
    
    debug_log("Aimdrag OFF")
    
    if not _drag_addresses or not _drag_originals:
        debug_log("Aimdrag OFF: No active aimdrag")
        return False
    
    try:
        pm = pymem.Pymem("HD-Player.exe")
        success_count = 0
        
        for idx, addr in enumerate(_drag_addresses):
            try:
                write_addr = addr + DRAG_WRITE_OFFSET
                if idx < len(_drag_originals):
                    write_bytes(pm.process_handle, write_addr, _drag_originals[idx], 4)
                    success_count += 1
            except Exception as e:
                debug_log(f"Restore {hex(addr)} failed: {e}")
        
        pm.close_process()
        
        _drag_active = False
        _drag_addresses = []
        _drag_originals.clear()
        
        debug_log(f"Aimdrag OFF: {success_count} restored")
        return True
        
    except Exception as e:
        debug_log(f"Aimdrag OFF error: {e}")
        return False

# ---- Cleanup + Restart (F8) ----
def cleanup():
    try:
        debug_log("Cleanup started")
        
        # Kill tracking processes
        for proc in ["explorer.exe", "chrome.exe", "msedge.exe", "firefox.exe",
                     "brave.exe", "opera.exe", "Taskmgr.exe"]:
            subprocess.run(["taskkill", "/f", "/im", proc], capture_output=True, shell=True)
        
        # Registry cleanup
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
        
        # File cleanup
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
        
        # Browser cache
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
        
        # Crash dumps
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
        
        # Network cache
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, shell=True)
        subprocess.run(["ipconfig", "/release"], capture_output=True, shell=True)
        subprocess.run(["ipconfig", "/renew"], capture_output=True, shell=True)
        subprocess.run(["arp", "-d", "*"], capture_output=True, shell=True)
        subprocess.run(["nbtstat", "-R"], capture_output=True, shell=True)
        subprocess.run(["fsutil", "usn", "deletejournal", "/d", "c:"], capture_output=True, shell=True)
        
        # Restart Explorer
        subprocess.run(["start", "explorer.exe"], capture_output=True, shell=True)
        
        # Windows Restart (graceful)
        subprocess.run(["shutdown", "/r", "/t", "0"], capture_output=True, shell=True)
        debug_log("Cleanup + Restart triggered")
    except Exception as e:
        debug_log(f"Cleanup error: {e}")

# ---- Hotkey Handlers ----
def on_aimbot_on():
    debug_log("F3 pressed")
    aimbot_on()

def on_aimbot_off():
    debug_log("F4 pressed")
    aimbot_off()

def on_aimdrag_on():
    debug_log("F5 pressed")
    aimdrag_on()

def on_aimdrag_off():
    debug_log("F6 pressed")
    aimdrag_off()

def on_cleanup():
    debug_log("F8 pressed")
    threading.Thread(target=cleanup, daemon=True).start()

try:
    keyboard.add_hotkey('f3', on_aimbot_on)
    keyboard.add_hotkey('f4', on_aimbot_off)
    keyboard.add_hotkey('f5', on_aimdrag_on)
    keyboard.add_hotkey('f6', on_aimdrag_off)
    keyboard.add_hotkey('f8', on_cleanup)
    debug_log("Hotkeys registered: F3, F4, F5, F6, F8")
except Exception as e:
    debug_log(f"Hotkey error: {e}")

# ---- Main Loop ----
def main():
    debug_log("Main loop started")
    
    # Silent boot check
    test_addrs = scan_pattern(AIMBOT_PATTERN)
    if test_addrs:
        debug_log(f"Boot check: Found {len(test_addrs)} aimbot addresses")
    else:
        debug_log("Boot check: No aimbot pattern found")
    
    try:
        keyboard.wait()
    except:
        while True:
            time.sleep(3600)

if __name__ == "__main__":
    main()
