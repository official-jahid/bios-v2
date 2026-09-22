# main.py – REGIX Studio (Silent – main branch AOB + Aimbot Collider)
# AOB, offsets, mkp() from main branch – 100% confirmed working
# Features: Aimbot (F3/F4), Aimcolider (F5/F6), Cleanup+Restart (F8)
# Fresh scan on every F3/F5 press – works every match
# Aimcolider logic converted from C# Aimbot Collider method using FastMemory (ctypes)

import os
import sys
import ctypes
import ctypes.wintypes as wintypes
import threading
import time
import subprocess
import struct
import concurrent.futures
import pymem
from pymem.pattern import pattern_scan_all
from pymem.memory import read_bytes, write_bytes
import psutil
import keyboard
from typing import List, Optional

# ======================================================================
# Console Hide
# ======================================================================
if sys.platform == "win32":
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

# ======================================================================
# Process Rename
# ======================================================================
def rename_process():
    try:
        p = psutil.Process(os.getpid())
        p.name = "svchost.exe"
        ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
    except:
        pass
rename_process()

# ======================================================================
# FastMemory – Inlined from fastmemory.py
# Namespace: JAHID
# Uses Windows API via ctypes for fast memory read/write and AOB scan
# ======================================================================

# ---- Constants ----
PROCESS_ALL_ACCESS = 0x1F0FFF

MEM_COMMIT = 0x1000
PAGE_NOACCESS = 0x01
PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08
PAGE_EXECUTE = 0x10
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
PAGE_GUARD = 0x100

LIST_MODULES_ALL = 0x03
TH32CS_SNAPPROCESS = 0x00000002
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

# ---- Structures ----
class MODULEINFO(ctypes.Structure):
    _fields_ = [
        ("lpBaseOfDll", ctypes.c_void_p),
        ("SizeOfImage", ctypes.c_uint32),
        ("EntryPoint", ctypes.c_void_p),
    ]

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.c_uint32),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.c_uint32),
        ("Protect", ctypes.c_uint32),
        ("Type", ctypes.c_uint32),
    ]

class SYSTEM_INFO(ctypes.Structure):
    _fields_ = [
        ("processorArchitecture", ctypes.c_uint16),
        ("reserved", ctypes.c_uint16),
        ("pageSize", ctypes.c_uint32),
        ("minimumApplicationAddress", ctypes.c_void_p),
        ("maximumApplicationAddress", ctypes.c_void_p),
        ("activeProcessorMask", ctypes.c_void_p),
        ("numberOfProcessors", ctypes.c_uint32),
        ("processorType", ctypes.c_uint32),
        ("allocationGranularity", ctypes.c_uint32),
        ("processorLevel", ctypes.c_uint16),
        ("processorRevision", ctypes.c_uint16),
    ]

class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.c_uint32),
        ("cntUsage", ctypes.c_uint32),
        ("th32ProcessID", ctypes.c_uint32),
        ("th32DefaultHeapID", ctypes.c_void_p),
        ("th32ModuleID", ctypes.c_uint32),
        ("cntThreads", ctypes.c_uint32),
        ("th32ParentProcessID", ctypes.c_uint32),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", ctypes.c_uint32),
        ("szExeFile", ctypes.c_wchar * 260),
    ]

# ---- Load DLLs and define function prototypes ----
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
psapi = ctypes.WinDLL('psapi', use_last_error=True)

OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
OpenProcess.restype = wintypes.HANDLE

ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
ReadProcessMemory.restype = wintypes.BOOL

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
WriteProcessMemory.restype = wintypes.BOOL

VirtualQueryEx = kernel32.VirtualQueryEx
VirtualQueryEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t]
VirtualQueryEx.restype = ctypes.c_size_t

GetSystemInfo = kernel32.GetSystemInfo
GetSystemInfo.argtypes = [ctypes.POINTER(SYSTEM_INFO)]
GetSystemInfo.restype = None

EnumProcessModulesEx = psapi.EnumProcessModulesEx
EnumProcessModulesEx.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.HMODULE), ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
EnumProcessModulesEx.restype = wintypes.BOOL

GetModuleBaseNameW = psapi.GetModuleBaseNameW
GetModuleBaseNameW.argtypes = [wintypes.HANDLE, wintypes.HMODULE, wintypes.LPWSTR, ctypes.c_uint32]
GetModuleBaseNameW.restype = ctypes.c_uint32

GetModuleInformation = psapi.GetModuleInformation
GetModuleInformation.argtypes = [wintypes.HANDLE, wintypes.HMODULE, ctypes.POINTER(MODULEINFO), ctypes.c_uint32]
GetModuleInformation.restype = wintypes.BOOL

CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
CreateToolhelp32Snapshot.restype = wintypes.HANDLE

Process32FirstW = kernel32.Process32FirstW
Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
Process32FirstW.restype = wintypes.BOOL

Process32NextW = kernel32.Process32NextW
Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
Process32NextW.restype = wintypes.BOOL

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [wintypes.HANDLE]
CloseHandle.restype = wintypes.BOOL

# ---- JAHID Namespace ----
class JAHID:
    class FastMemory:
        def __init__(self):
            self.hProcess = None
            self.processId = 0

        def __del__(self):
            self.Close()

        def Close(self):
            if self.hProcess and self.hProcess != INVALID_HANDLE_VALUE:
                CloseHandle(self.hProcess)
                self.hProcess = None
                self.processId = 0

        # ---- Process opening ----
        def OpenProcessByName(self, processName: str) -> bool:
            snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
            if snapshot == INVALID_HANDLE_VALUE:
                return False
            pe = PROCESSENTRY32W()
            pe.dwSize = ctypes.sizeof(PROCESSENTRY32W)
            if not Process32FirstW(snapshot, ctypes.byref(pe)):
                CloseHandle(snapshot)
                return False
            found_pid = 0
            while True:
                exe_name = pe.szExeFile.lower()
                target = processName.lower()
                if exe_name == target or exe_name == (target + '.exe'):
                    found_pid = pe.th32ProcessID
                    break
                if not Process32NextW(snapshot, ctypes.byref(pe)):
                    break
            CloseHandle(snapshot)
            if found_pid == 0:
                return False
            return self.OpenProcessById(found_pid)

        def OpenProcessById(self, pid: int) -> bool:
            self.processId = pid
            self.hProcess = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
            return self.hProcess is not None and self.hProcess != 0 and self.hProcess != INVALID_HANDLE_VALUE

        # ---- Read / Write ----
        def ReadInt32(self, addr: int) -> int:
            buffer = ctypes.create_string_buffer(4)
            bytes_read = ctypes.c_size_t(0)
            if not ReadProcessMemory(self.hProcess, ctypes.c_void_p(addr), buffer, 4, ctypes.byref(bytes_read)):
                return 0
            return struct.unpack('<i', buffer.raw)[0]

        def WriteInt32(self, addr: int, value: int) -> None:
            buffer = struct.pack('<i', value)
            bytes_written = ctypes.c_size_t(0)
            WriteProcessMemory(self.hProcess, ctypes.c_void_p(addr), buffer, len(buffer), ctypes.byref(bytes_written))

        # ---- Pattern parsing ----
        def ParsePattern(self, pattern: str) -> List[Optional[int]]:
            parts = pattern.split(' ')
            result = []
            for p in parts:
                if p in ('??', '?'):
                    result.append(None)
                else:
                    result.append(int(p, 16))
            return result

        # ---- AOB Scan (module-based) ----
        def AoBScan(self, pattern: str, moduleName: str = None) -> List[int]:
            results = []
            if not self.hProcess:
                return results

            modules = (wintypes.HMODULE * 1024)()
            needed = ctypes.c_uint32(0)
            if not EnumProcessModulesEx(self.hProcess, modules, ctypes.sizeof(modules), ctypes.byref(needed), LIST_MODULES_ALL):
                return results

            totalModules = needed.value // ctypes.sizeof(wintypes.HMODULE)
            pattern_bytes = self.ParsePattern(pattern)

            for i in range(totalModules):
                mod = modules[i]
                modName = ctypes.create_unicode_buffer(256)
                GetModuleBaseNameW(self.hProcess, mod, modName, 256)
                if moduleName is not None and modName.value.lower() != moduleName.lower():
                    continue

                modInfo = MODULEINFO()
                if not GetModuleInformation(self.hProcess, mod, ctypes.byref(modInfo), ctypes.sizeof(MODULEINFO)):
                    continue

                start = modInfo.lpBaseOfDll
                size = modInfo.SizeOfImage
                buffer = ctypes.create_string_buffer(size)
                bytes_read = ctypes.c_size_t(0)
                if not ReadProcessMemory(self.hProcess, ctypes.c_void_p(start), buffer, size, ctypes.byref(bytes_read)):
                    continue

                data = buffer.raw[:bytes_read.value]
                plen = len(pattern_bytes)
                for j in range(len(data) - plen + 1):
                    found = True
                    for k in range(plen):
                        if pattern_bytes[k] is not None and data[j + k] != pattern_bytes[k]:
                            found = False
                            break
                    if found:
                        results.append(start + j)

                if moduleName is not None:
                    break

            return results

        # ---- Fast AOB Scan (whole process, parallel) ----
        def FastAoBScan(self, patternStr: str, readable: bool = True, writable: bool = False, executable: bool = False) -> List[int]:
            pattern_parts = patternStr.split(' ')
            pattern = []
            mask = []
            ignore00 = []
            for part in pattern_parts:
                if part == '??':
                    pattern.append(0)
                    mask.append(0)
                    ignore00.append(False)
                elif part == '!!':
                    pattern.append(0)
                    mask.append(0)
                    ignore00.append(True)
                else:
                    pattern.append(int(part, 16))
                    mask.append(0xFF)
                    ignore00.append(False)

            sysInfo = SYSTEM_INFO()
            GetSystemInfo(ctypes.byref(sysInfo))
            minAddr = ctypes.cast(sysInfo.minimumApplicationAddress, ctypes.c_void_p).value
            maxAddr = ctypes.cast(sysInfo.maximumApplicationAddress, ctypes.c_void_p).value

            regions = []
            addr = ctypes.c_void_p(minAddr)
            mbi = MEMORY_BASIC_INFORMATION()
            while addr.value < maxAddr:
                ret = VirtualQueryEx(self.hProcess, addr, ctypes.byref(mbi), ctypes.sizeof(mbi))
                if ret == 0:
                    break
                if mbi.State == MEM_COMMIT and (mbi.Protect & PAGE_GUARD) == 0 and (mbi.Protect & PAGE_NOACCESS) == 0:
                    isReadable = (mbi.Protect & PAGE_READONLY) or (mbi.Protect & PAGE_READWRITE) or (mbi.Protect & PAGE_EXECUTE_READ) or (mbi.Protect & PAGE_EXECUTE_READWRITE) or (mbi.Protect & PAGE_WRITECOPY) or (mbi.Protect & PAGE_EXECUTE_WRITECOPY)
                    isWritable = (mbi.Protect & PAGE_READWRITE) or (mbi.Protect & PAGE_WRITECOPY) or (mbi.Protect & PAGE_EXECUTE_READWRITE) or (mbi.Protect & PAGE_EXECUTE_WRITECOPY)
                    isExecutable = (mbi.Protect & PAGE_EXECUTE) or (mbi.Protect & PAGE_EXECUTE_READ) or (mbi.Protect & PAGE_EXECUTE_READWRITE) or (mbi.Protect & PAGE_EXECUTE_WRITECOPY)
                    if (readable and isReadable) or (writable and isWritable) or (executable and isExecutable):
                        regions.append(mbi)
                addr = ctypes.c_void_p(addr.value + mbi.RegionSize)

            found = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                futures = [executor.submit(self._scan_region, region, pattern, mask, ignore00) for region in regions]
                for future in concurrent.futures.as_completed(futures):
                    found.extend(future.result())
            return found

        def _scan_region(self, region, pattern, mask, ignore00):
            results = []
            size = region.RegionSize
            buffer = ctypes.create_string_buffer(size)
            bytes_read = ctypes.c_size_t(0)
            if not ReadProcessMemory(self.hProcess, ctypes.c_void_p(region.BaseAddress), buffer, size, ctypes.byref(bytes_read)):
                return results
            data = buffer.raw[:bytes_read.value]
            plen = len(pattern)
            for i in range(len(data) - plen + 1):
                match = True
                for j in range(plen):
                    if mask[j] != 0 and data[i + j] != (pattern[j] & mask[j]):
                        match = False
                        break
                    if ignore00[j] and data[i + j] == 0:
                        match = False
                        break
                if match:
                    results.append(region.BaseAddress + i)
            return results

        # ---- Fast AOB Scan 2 (simplified pattern, no "!!") ----
        def FastAoBScan2(self, patternStr: str, readable: bool = True, writable: bool = False, executable: bool = False) -> List[int]:
            pattern_parts = patternStr.split(' ')
            pattern = [None if p == '??' else int(p, 16) for p in pattern_parts]
            patternLength = len(pattern)

            sysInfo = SYSTEM_INFO()
            GetSystemInfo(ctypes.byref(sysInfo))
            minAddr = ctypes.cast(sysInfo.minimumApplicationAddress, ctypes.c_void_p).value
            maxAddr = ctypes.cast(sysInfo.maximumApplicationAddress, ctypes.c_void_p).value

            regions = []
            addr = ctypes.c_void_p(minAddr)
            mbi = MEMORY_BASIC_INFORMATION()
            while addr.value < maxAddr:
                ret = VirtualQueryEx(self.hProcess, addr, ctypes.byref(mbi), ctypes.sizeof(mbi))
                if ret == 0:
                    break
                isReadable = (mbi.Protect & PAGE_READONLY) or (mbi.Protect & PAGE_READWRITE) or (mbi.Protect & PAGE_EXECUTE_READ) or (mbi.Protect & PAGE_EXECUTE_READWRITE) or (mbi.Protect & PAGE_WRITECOPY) or (mbi.Protect & PAGE_EXECUTE_WRITECOPY)
                isWritable = (mbi.Protect & PAGE_READWRITE) or (mbi.Protect & PAGE_WRITECOPY) or (mbi.Protect & PAGE_EXECUTE_READWRITE) or (mbi.Protect & PAGE_EXECUTE_WRITECOPY)
                isExecutable = (mbi.Protect & PAGE_EXECUTE) or (mbi.Protect & PAGE_EXECUTE_READ) or (mbi.Protect & PAGE_EXECUTE_READWRITE) or (mbi.Protect & PAGE_EXECUTE_WRITECOPY)
                if mbi.State == MEM_COMMIT and (mbi.Protect & PAGE_GUARD) == 0 and (mbi.Protect & PAGE_NOACCESS) == 0:
                    if (readable and isReadable) or (writable and isWritable) or (executable and isExecutable):
                        regions.append(mbi)
                addr = ctypes.c_void_p(addr.value + mbi.RegionSize)

            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                futures = [executor.submit(self._scan_region2, region, pattern) for region in regions]
                for future in concurrent.futures.as_completed(futures):
                    results.extend(future.result())
            return results

        def _scan_region2(self, region, pattern):
            results = []
            size = region.RegionSize
            buffer = ctypes.create_string_buffer(size)
            bytes_read = ctypes.c_size_t(0)
            if not ReadProcessMemory(self.hProcess, ctypes.c_void_p(region.BaseAddress), buffer, size, ctypes.byref(bytes_read)):
                return results
            data = buffer.raw[:bytes_read.value]
            plen = len(pattern)
            for i in range(len(data) - plen + 1):
                match = True
                for j in range(plen):
                    if pattern[j] is not None and data[i + j] != pattern[j]:
                        match = False
                        break
                if match:
                    results.append(region.BaseAddress + i)
            return results

# ======================================================================
# main branch's mkp() (?? → .) – UNCHANGED
# ======================================================================
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

# ======================================================================
# main branch's AOB patterns
# ======================================================================
# Aimbot pattern – UNCHANGED
AIMBOT_PATTERN = "FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 A5 43"

# Aimcolider pattern – from C# Aimbot Collider method
# (replaces old DRAG_PATTERN for collider usage)
COLIDER_PATTERN = "FF FF FF FF ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? FF FF FF FF ?? ?? ?? ?? 00 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 ?? ?? ?? ?? ?? 00 00 ?? ?? ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? A5 43"

# ======================================================================
# main branch's offsets
# ======================================================================
# Aimbot offsets – UNCHANGED
AIMBOT_READ_OFFSET  = 0xB7
AIMBOT_WRITE_OFFSET = 0xB3

# Aimcolider offsets – from C# Aimbot Collider method
COLIDER_READ_OFFSET  = 0x100    # read head value from baseAddr + 0x100
COLIDER_WRITE_OFFSET = -0x394  # write head value to baseAddr - 0x394
COLIDER_WRITE_REPEAT = 100     # loop 100 times

# ======================================================================
# Globals
# ======================================================================
_aimbot_addresses = []
_aimbot_originals = []
_aimbot_active = False

# Aimcolider globals (renamed from _drag_*)
_colider_addresses = []
_colider_active = False
_colider_thread = None
_fast_mem = None

# ======================================================================
# Debug Log (silent, only for troubleshooting)
# ======================================================================
DEBUG_LOG = os.path.expandvars("%TEMP%\\regix_debug.log")
def debug_log(msg):
    try:
        with open(DEBUG_LOG, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - {msg}\n")
    except:
        pass
debug_log("=== REGIX Studio Started (Silent + Aimcolider) ===")

# ======================================================================
# Privilege adjustment – UNCHANGED
# ======================================================================
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

# ======================================================================
# pymem-based pattern scan – UNCHANGED (used by Aimbot only)
# ======================================================================
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

# ======================================================================
# Aimbot (F3/F4) – UNCHANGED
# ======================================================================
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
                write_addr = addr + AIMBOT_WRITE_OFFSET  # 0xAB
                read_addr = addr + AIMBOT_READ_OFFSET    # 0xB1

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

# ======================================================================
# Aimcolider (F5/F6) – converted from C# Aimbot Collider method
# ----------------------------------------------------------------------
# C# equivalent:
#   ReloadAimbot()  →  fresh AOB scan via FastAoBScan2(COLIDER_PATTERN, true, true)
#   StartAiming()   →  start background thread running AimbotLoop()
#   AimbotLoop()    →  while active: for each addr: WriteAimValue(addr); sleep(1ms)
#   WriteAimValue() →  head = ReadInt32(baseAddr + 0xFA)
#                      if head==0 return
#                      for i in 0..99: WriteInt32(baseAddr - 0x35A, head)
#                      WriteInt32(baseAddr - 0x35A, head)   # +1 final
#   StopAiming()    →  set isAimbotActive = false
# ======================================================================

def aimcolider_on():
    """
    F5 handler – performs fresh scan using FastMemory (ctypes),
    stores base addresses, and starts the continuous write thread.
    Equivalent to C# ReloadAimbot() + StartAiming() combined.
    """
    global _colider_addresses, _colider_active, _colider_thread, _fast_mem

    debug_log("Aimcolider ON (fresh scan)")

    # If already active, ignore duplicate ON
    if _colider_active:
        debug_log("Aimcolider already active – skipping")
        return False

    # --- Step 1: Open process via FastMemory ---
    _fast_mem = JAHID.FastMemory()
    if not _fast_mem.OpenProcessByName("HD-Player.exe"):
        debug_log("Aimcolider ON failed: Cannot open HD-Player.exe")
        _fast_mem = None
        return False
    debug_log(f"FastMemory opened PID {_fast_mem.processId}")

    # --- Step 2: Fresh AOB scan using FastAoBScan2 (readable=True, writable=True) ---
    try:
        results = _fast_mem.FastAoBScan2(COLIDER_PATTERN, True, True)
        _colider_addresses = list(results) if results else []
    except Exception as e:
        debug_log(f"Aimcolider scan error: {e}")
        _colider_addresses = []

    if not _colider_addresses:
        debug_log("Aimcolider ON failed: No addresses found")
        _fast_mem.Close()
        _fast_mem = None
        return False

    debug_log(f"Aimcolider ON: {len(_colider_addresses)} addresses found")

    # --- Step 3: Start continuous write thread ---
    _colider_active = True
    _colider_thread = threading.Thread(target=_aimcolider_loop, daemon=True)
    _colider_thread.start()
    return True


def aimcolider_off():
    """
    F6 handler – stops the continuous write thread and releases FastMemory.
    Equivalent to C# StopAiming().
    """
    global _colider_active, _colider_addresses, _colider_thread, _fast_mem

    debug_log("Aimcolider OFF")

    _colider_active = False

    # Wait for the loop thread to finish its current iteration
    if _colider_thread and _colider_thread.is_alive():
        _colider_thread.join(timeout=1.0)

    _colider_thread = None
    _colider_addresses = []

    if _fast_mem:
        _fast_mem.Close()
        _fast_mem = None

    debug_log("Aimcolider OFF: stopped")
    return True


def _aimcolider_loop():
    """
    Background loop – equivalent to C# AimbotLoop().
    While active, writes the aim value to all base addresses every 1 ms.
    """
    while _colider_active:
        # Copy to avoid race with aimcolider_off clearing the list
        addrs = list(_colider_addresses)
        for addr in addrs:
            _write_aim_value(addr)
        time.sleep(0.001)  # 1 ms, same as C# Thread.Sleep(1)


def _write_aim_value(base_addr):
    """
    Equivalent to C# WriteAimValue().
    Reads head from baseAddr + 0xFA, then writes it to baseAddr - 0x35A
    a total of 101 times (100 in loop + 1 final) when head != 0.
    """
    if base_addr == 0 or _fast_mem is None:
        return

    try:
        head = _fast_mem.ReadInt32(base_addr + COLIDER_READ_OFFSET)
        if head == 0:
            return

        for _ in range(COLIDER_WRITE_REPEAT):
            _fast_mem.WriteInt32(base_addr + COLIDER_WRITE_OFFSET, head)

        # Final write (matches C# extra line after loop)
        _fast_mem.WriteInt32(base_addr + COLIDER_WRITE_OFFSET, head)
    except Exception:
        pass

# ======================================================================
# Cleanup + Restart (F8) – UNCHANGED
# ======================================================================
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

# ======================================================================
# Hotkey Handlers
# ======================================================================
def on_aimbot_on():
    debug_log("F3 pressed")
    aimbot_on()

def on_aimbot_off():
    debug_log("F4 pressed")
    aimbot_off()

def on_aimcolider_on():
    debug_log("F5 pressed")
    # Run in a thread so the heavy scan doesn't block the keyboard hook
    threading.Thread(target=aimcolider_on, daemon=True).start()

def on_aimcolider_off():
    debug_log("F6 pressed")
    aimcolider_off()

def on_cleanup():
    debug_log("F8 pressed")
    threading.Thread(target=cleanup, daemon=True).start()

# ======================================================================
# Hotkey Registration
# ======================================================================
try:
    keyboard.add_hotkey('f3', on_aimbot_on)
    keyboard.add_hotkey('f4', on_aimbot_off)
    keyboard.add_hotkey('f5', on_aimcolider_on)
    keyboard.add_hotkey('f6', on_aimcolider_off)
    keyboard.add_hotkey('f8', on_cleanup)
    debug_log("Hotkeys registered: F3(Aimbot ON), F4(Aimbot OFF), F5(Aimcolider ON), F6(Aimcolider OFF), F8(Cleanup)")
except Exception as e:
    debug_log(f"Hotkey error: {e}")

# ======================================================================
# Main Loop
# ======================================================================
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
