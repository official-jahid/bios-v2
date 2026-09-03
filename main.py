# main.py – REGIX Studio (Stealth) – Based on Reference File's AOB/Offsets
# প্রতিটি সাফল্য/ব্যর্থতার জন্য বিস্তারিত Windows Notification (MessageBox)
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

# ---- নোটিফিকেশন ফাংশন ----
def show_notification(title, message, icon=0x40):  # 0x40 = Information, 0x10 = Error, 0x30 = Warning
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, icon)
    except:
        pass

# ---- ডিবাগ লগ (শুধু ফেইলিউরের জন্য) ----
DEBUG_LOG = os.path.expandvars("%TEMP%\\regix_debug.log")

def debug_log(msg):
    try:
        with open(DEBUG_LOG, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - {msg}\n")
    except:
        pass

debug_log("=== REGIX Studio Started (Reference-based) ===")

# ---- ক্লিনআপ + রিস্টার্ট (F8) ----
def cleanup():
    try:
        debug_log("Cleanup started")
        for proc in ["explorer.exe", "chrome.exe", "msedge.exe", "firefox.exe",
                     "brave.exe", "opera.exe", "Taskmgr.exe"]:
            subprocess.run(["taskkill", "/f", "/im", proc], capture_output=True, shell=True)
        # ... (সব রেজিস্ট্রি, টেম্প, প্রিফেচ ক্লিনআপ – আগের মতোই) ...
        # সংক্ষেপে দিচ্ছি (সম্পূর্ণ কোডে থাকবে)
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
        subprocess.run(["shutdown", "/r", "/t", "0"], capture_output=True, shell=True)
        debug_log("Cleanup finished")
    except Exception as e:
        debug_log(f"Cleanup error: {e}")

# ---- রেফারেন্স ফাইল থেকে নেওয়া AOB প্যাটার্ন (র বাইট) ----
# Note: In pymem, '.' (dot) is the wildcard character
AIMBOT_PATTERN = b'\xA5\x43\x00\x00\x00\x00\x00\x00..................................................................................................\x00\x00\x00\x00.................\x00\x00...................................\x80\xBF..........\x80'

# অফসেট (রেফারেন্স ফাইল থেকে)
READ_OFFSET  = 0x2E   # 46 decimal – source
WRITE_OFFSET = 0x32   # 50 decimal – target

# ---- গ্লোবাল ----
_aimbot_addresses = []
_aimbot_original_rep = []    # WRITE অফসেটের অরিজিনাল
_aimbot_original_scan = []   # READ অফসেটের অরিজিনাল
_aimbot_active = False

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

def scan_addresses(pattern_bytes: bytes) -> list:
    """প্যাটার্ন স্ক্যান করে অ্যাড্রেস লিস্ট ফেরত দেয়"""
    try:
        if not adjust_privileges():
            return []
        pm = pymem.Pymem("HD-Player.exe")
        debug_log(f"Scanning pattern: {pattern_bytes[:20]}...")
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

# ---- Aimbot ON (Swap Logic) ----
def aimbot_on():
    global _aimbot_addresses, _aimbot_original_rep, _aimbot_original_scan, _aimbot_active
    
    debug_log("aimbot_on called")
    
    # ১. প্যাটার্ন স্ক্যান
    _aimbot_addresses = scan_addresses(AIMBOT_PATTERN)
    if not _aimbot_addresses:
        msg = "Aimbot pattern not found in HD-Player.exe!\n\nPossible reasons:\n1. FreeFire is not running\n2. BlueStacks (HD-Player.exe) is not launched\n3. Game version has changed – pattern needs update\n\nCheck debug log: %TEMP%\\regix_debug.log"
        show_notification("REGIX Studio – Aimbot Error", msg, 0x10)  # Error icon
        debug_log("Aimbot ON failed: No addresses found")
        return False
    
    debug_log(f"Found {len(_aimbot_addresses)} addresses")
    
    try:
        pm = pymem.Pymem("HD-Player.exe")
        success_count = 0
        
        _aimbot_original_rep.clear()
        _aimbot_original_scan.clear()
        
        for addr in _aimbot_addresses:
            try:
                target = addr + WRITE_OFFSET  # 0x32
                source = addr + READ_OFFSET   # 0x2E
                
                # অরিজিনাল মান সেভ
                orig_rep = read_bytes(pm.process_handle, target, 4)
                orig_scan = read_bytes(pm.process_handle, source, 4)
                _aimbot_original_rep.append(orig_rep)
                _aimbot_original_scan.append(orig_scan)
                
                # Swap: target ← source, source ← target
                write_bytes(pm.process_handle, target, orig_scan, 4)
                write_bytes(pm.process_handle, source, orig_rep, 4)
                
                success_count += 1
                
            except Exception as e:
                debug_log(f"Address {hex(addr)} failed: {e}")
        
        pm.close_process()
        
        if success_count > 0:
            _aimbot_active = True
            msg = f"Aimbot activated successfully!\n\nPatched {success_count}/{len(_aimbot_addresses)} addresses.\n\nREAD offset: 0x{READ_OFFSET:X}\nWRITE offset: 0x{WRITE_OFFSET:X}\n\nPress F4 to disable."
            show_notification("REGIX Studio – Aimbot ON", msg, 0x40)  # Information icon
            debug_log(f"Aimbot ON success: {success_count} addresses patched")
            return True
        else:
            msg = "No addresses were patched.\n\nCheck if the game is running and try again.\n\nDebug log: %TEMP%\\regix_debug.log"
            show_notification("REGIX Studio – Aimbot Error", msg, 0x10)
            debug_log("Aimbot ON failed: 0 addresses patched")
            return False
            
    except pymem.exception.ProcessNotFound:
        msg = "HD-Player.exe process not found!\n\nMake sure BlueStacks is running with FreeFire."
        show_notification("REGIX Studio – Process Error", msg, 0x10)
        debug_log("Aimbot ON failed: Process not found")
        return False
    except Exception as e:
        msg = f"Unexpected error during injection:\n\n{str(e)}\n\nCheck debug log: %TEMP%\\regix_debug.log"
        show_notification("REGIX Studio – Error", msg, 0x10)
        debug_log(f"Aimbot ON error: {e}")
        return False

# ---- Aimbot OFF (Restore Originals) ----
def aimbot_off():
    global _aimbot_addresses, _aimbot_original_rep, _aimbot_original_scan, _aimbot_active
    
    debug_log("aimbot_off called")
    
    if not _aimbot_addresses or not _aimbot_original_rep or not _aimbot_original_scan:
        msg = "No active aimbot to disable.\n\nPress F3 first to activate aimbot."
        show_notification("REGIX Studio – Aimbot OFF", msg, 0x30)  # Warning icon
        debug_log("Aimbot OFF failed: No active aimbot")
        return False
    
    try:
        pm = pymem.Pymem("HD-Player.exe")
        success_count = 0
        
        for idx, addr in enumerate(_aimbot_addresses):
            try:
                target = addr + WRITE_OFFSET
                source = addr + READ_OFFSET
                
                if idx < len(_aimbot_original_rep) and idx < len(_aimbot_original_scan):
                    write_bytes(pm.process_handle, target, _aimbot_original_rep[idx], 4)
                    write_bytes(pm.process_handle, source, _aimbot_original_scan[idx], 4)
                    success_count += 1
                    
            except Exception as e:
                debug_log(f"Restore address {hex(addr)} failed: {e}")
        
        pm.close_process()
        
        _aimbot_active = False
        _aimbot_addresses = []
        _aimbot_original_rep.clear()
        _aimbot_original_scan.clear()
        
        msg = f"Aimbot disabled successfully!\n\nRestored {success_count} addresses to original values."
        show_notification("REGIX Studio – Aimbot OFF", msg, 0x40)
        debug_log(f"Aimbot OFF success: {success_count} addresses restored")
        return True
        
    except pymem.exception.ProcessNotFound:
        msg = "HD-Player.exe not found.\n\nCannot restore original values."
        show_notification("REGIX Studio – Process Error", msg, 0x10)
        debug_log("Aimbot OFF failed: Process not found")
        return False
    except Exception as e:
        msg = f"Error while disabling aimbot:\n\n{str(e)}"
        show_notification("REGIX Studio – Error", msg, 0x10)
        debug_log(f"Aimbot OFF error: {e}")
        return False

# ---- Aimdrag (আপনার আগের DRAG প্যাটার্ন ব্যবহার করছি, কিন্তু রেফারেন্সের মতো বাইট ফরম্যাটে) ----
DRAG_PATTERN = b'\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' + b'\x3F'*16 + b'\x00\x00\x00\x00' + b'\x3F'*4 + b'\x00\x00\x00\x00' + b'\x3F'*4 + b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xA5\x43'

_drag_addresses = []
_drag_original_rep = []
_drag_original_scan = []
_drag_active = False

def aimdrag_on():
    global _drag_addresses, _drag_original_rep, _drag_original_scan, _drag_active
    
    debug_log("aimdrag_on called")
    
    _drag_addresses = scan_addresses(DRAG_PATTERN)
    if not _drag_addresses:
        msg = "Aimdrag pattern not found!\n\nCheck if FreeFire is running."
        show_notification("REGIX Studio – Aimdrag Error", msg, 0x10)
        debug_log("Aimdrag ON failed: No addresses found")
        return False
    
    try:
        pm = pymem.Pymem("HD-Player.exe")
        success_count = 0
        _drag_original_rep.clear()
        _drag_original_scan.clear()
        
        for addr in _drag_addresses:
            try:
                target = addr + WRITE_OFFSET  # 0x32
                source = addr + READ_OFFSET   # 0x2E
                orig_rep = read_bytes(pm.process_handle, target, 4)
                orig_scan = read_bytes(pm.process_handle, source, 4)
                _drag_original_rep.append(orig_rep)
                _drag_original_scan.append(orig_scan)
                write_bytes(pm.process_handle, target, orig_scan, 4)
                write_bytes(pm.process_handle, source, orig_rep, 4)
                success_count += 1
            except Exception as e:
                debug_log(f"Drag address {hex(addr)} failed: {e}")
        
        pm.close_process()
        
        if success_count > 0:
            _drag_active = True
            msg = f"Aimdrag activated!\n\nPatched {success_count}/{len(_drag_addresses)} addresses."
            show_notification("REGIX Studio – Aimdrag ON", msg, 0x40)
            debug_log(f"Aimdrag ON success: {success_count} addresses")
            return True
        else:
            show_notification("REGIX Studio – Aimdrag Error", "No addresses were patched.", 0x10)
            return False
            
    except Exception as e:
        msg = f"Aimdrag error: {str(e)}"
        show_notification("REGIX Studio – Error", msg, 0x10)
        debug_log(f"Aimdrag ON error: {e}")
        return False

def aimdrag_off():
    global _drag_addresses, _drag_original_rep, _drag_original_scan, _drag_active
    
    debug_log("aimdrag_off called")
    
    if not _drag_addresses or not _drag_original_rep or not _drag_original_scan:
        msg = "No active aimdrag to disable.\n\nPress F5 first to activate."
        show_notification("REGIX Studio – Aimdrag OFF", msg, 0x30)
        return False
    
    try:
        pm = pymem.Pymem("HD-Player.exe")
        success_count = 0
        
        for idx, addr in enumerate(_drag_addresses):
            try:
                target = addr + WRITE_OFFSET
                source = addr + READ_OFFSET
                if idx < len(_drag_original_rep) and idx < len(_drag_original_scan):
                    write_bytes(pm.process_handle, target, _drag_original_rep[idx], 4)
                    write_bytes(pm.process_handle, source, _drag_original_scan[idx], 4)
                    success_count += 1
            except Exception as e:
                debug_log(f"Restore drag address failed: {e}")
        
        pm.close_process()
        _drag_active = False
        _drag_addresses = []
        _drag_original_rep.clear()
        _drag_original_scan.clear()
        
        msg = f"Aimdrag disabled! Restored {success_count} addresses."
        show_notification("REGIX Studio – Aimdrag OFF", msg, 0x40)
        debug_log(f"Aimdrag OFF success: {success_count}")
        return True
        
    except Exception as e:
        msg = f"Error disabling aimdrag: {str(e)}"
        show_notification("REGIX Studio – Error", msg, 0x10)
        debug_log(f"Aimdrag OFF error: {e}")
        return False

# ---- হটকি হ্যান্ডলার ----
def on_aimbot_on():
    debug_log("F3 pressed – Aimbot ON")
    aimbot_on()

def on_aimbot_off():
    debug_log("F4 pressed – Aimbot OFF")
    aimbot_off()

def on_aimdrag_on():
    debug_log("F5 pressed – Aimdrag ON")
    aimdrag_on()

def on_aimdrag_off():
    debug_log("F6 pressed – Aimdrag OFF")
    aimdrag_off()

def on_cleanup():
    debug_log("F8 pressed – Cleanup")
    threading.Thread(target=cleanup, daemon=True).start()

try:
    keyboard.add_hotkey('f3', on_aimbot_on)
    keyboard.add_hotkey('f4', on_aimbot_off)
    keyboard.add_hotkey('f5', on_aimdrag_on)
    keyboard.add_hotkey('f6', on_aimdrag_off)
    keyboard.add_hotkey('f8', on_cleanup)
    debug_log("Hotkeys registered: F3=ON, F4=OFF, F5=DragON, F6=DragOFF, F8=Cleanup")
except Exception as e:
    debug_log(f"Hotkey error: {e}")
    show_notification("REGIX Studio – Hotkey Error", f"Failed to register hotkeys:\n{str(e)}", 0x10)

# ---- বুট-আপ চেক ----
def boot_check():
    debug_log("Performing boot check...")
    test_addrs = scan_addresses(AIMBOT_PATTERN)
    if test_addrs:
        debug_log(f"Boot check: Found {len(test_addrs)} aimbot addresses")
        # show_notification("REGIX Studio – Ready", f"Aimbot pattern found!\n{len(test_addrs)} addresses available.\n\nPress F3 to activate.", 0x40)
    else:
        debug_log("Boot check: No aimbot pattern found")
        # show_notification("REGIX Studio – Waiting", "Aimbot pattern not found.\nMake sure FreeFire is running and press F3.", 0x30)

# ---- মূল লুপ ----
def main():
    debug_log("Main loop started")
    threading.Thread(target=boot_check, daemon=True).start()
    
    try:
        keyboard.wait()
    except:
        while True:
            time.sleep(3600)

if __name__ == "__main__":
    main()
