
# main.py - Stealth aimbot daemon with global hotkeys (F3 toggle, F4 off, F8 cleanup+reboot)
import sys, os, ctypes, time, threading
import pymem
import pymem.pattern
from ctypes import wintypes

# ---- Suppress all outputs ----
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

# ---- Globals ----
pm = None
active = False
patched_addresses = []  # (addr_rep, orig_rep, orig_scan)
hook_id = None
hook_proc = None

# ---- Privilege adjustment (from original) ----
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
        ctypes.windll.advapi32.LookupPrivilegeValueA(0, SE_DEBUG_NAME.encode('ascii'), ctypes.byref(luid))
        class LUID_AND_ATTRIBUTES(ctypes.Structure):
            _fields_ = [("Luid", ctypes.c_longlong), ("Attributes", ctypes.c_ulong)]
        class TOKEN_PRIVILEGES(ctypes.Structure):
            _fields_ = [("PrivilegeCount", ctypes.c_ulong), ("Privileges", LUID_AND_ATTRIBUTES)]
        new_privileges = TOKEN_PRIVILEGES(1, LUID_AND_ATTRIBUTES(luid.value, SE_PRIVILEGE_ENABLED))
        ctypes.windll.advapi32.AdjustTokenPrivileges(token_handle, False, ctypes.byref(new_privileges), 0, None, None)
        ctypes.windll.kernel32.CloseHandle(token_handle)
        return True
    except:
        return False

# ---- Injection logic ----
def perform_aimbot_injection():
    global pm, active, patched_addresses
    try:
        pm = pymem.Pymem("HD-Player.exe")
        pattern = b'\xA5\x43\x00\x00\x00\x00\x00\x00..................................................................................................................................................................\x00\x00\x00\x00.................\x00\x00...................................\x80\xBF..........\x80'
        addresses = pymem.pattern.pattern_scan_all(pm.process_handle, pattern, return_multiple=True)
        if not addresses:
            return False
        for addr in addresses:
            addr_rep = addr + 0x32
            addr_scan = addr + 0x2E
            orig_rep = pymem.memory.read_bytes(pm.process_handle, addr_rep, 4)
            orig_scan = pymem.memory.read_bytes(pm.process_handle, addr_scan, 4)
            pymem.memory.write_bytes(pm.process_handle, addr_rep, orig_scan, 4)
            pymem.memory.write_bytes(pm.process_handle, addr_scan, orig_rep, 4)
            patched_addresses.append((addr_rep, orig_rep, orig_scan))
        active = True
        return True
    except:
        return False

def restore_aimbot():
    global active, patched_addresses, pm
    if pm and active:
        for addr_rep, orig_rep, orig_scan in patched_addresses:
            try:
                pymem.memory.write_bytes(pm.process_handle, addr_rep, orig_rep, 4)
                pymem.memory.write_bytes(pm.process_handle, addr_rep - 4, orig_scan, 4)
            except:
                pass
        patched_addresses = []
        active = False
    if pm:
        pm.close_process()
        pm = None

def toggle_aimbot():
    if active:
        restore_aimbot()
    else:
        perform_aimbot_injection()

def disable_aimbot():
    restore_aimbot()

# ---- F8: cleanup and normal restart ----
def cleanup_and_restart():
    restore_aimbot()
    if hook_id:
        ctypes.windll.user32.UnhookWindowsHookEx(hook_id)
    # Normal restart (not forced)
    ctypes.windll.user32.ExitWindowsEx(0x00000002, 0)
    # Fallback
    os.system("shutdown /r /t 0")

# ---- Global keyboard hook ----
F3_VK = 0x72
F4_VK = 0x73
F8_VK = 0x78

def keyboard_hook(nCode, wParam, lParam):
    if nCode >= 0:
        if wParam == 0x0100:  # WM_KEYDOWN
            vk = ctypes.cast(lParam, ctypes.POINTER(ctypes.c_long)).contents.value
            if vk == F3_VK:
                toggle_aimbot()
            elif vk == F4_VK:
                disable_aimbot()
            elif vk == F8_VK:
                cleanup_and_restart()
    return ctypes.windll.user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

def install_hook():
    global hook_id, hook_proc
    hook_proc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))(keyboard_hook)
    hook_id = ctypes.windll.user32.SetWindowsHookExW(0x0D, hook_proc, None, 0)  # WH_KEYBOARD_LL
    if not hook_id:
        return False
    # Message loop
    msg = wintypes.MSG()
    while ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
        ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))
    return True

def main():
    # Suppress system error dialogs
    ctypes.windll.kernel32.SetErrorMode(0x8001)
    adjust_privileges()
    install_hook()

if __name__ == "__main__":
    main()
