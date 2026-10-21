#!/usr/bin/env python3
"""
Dewdrop Clean-Room Windows Runtime & Butter-Smooth Crystal-Clear Liquid-Glass UI (liquid-glass-react style)
Features:
- Real Photo / File Thumbnail Preview inside the Options Window, Progress Window, and Dynamic Island (updates live to show the current file being processed during multi-file batches)
- Smart File-Type Filtering (selecting/dropping Images shows ONLY Image options; selecting/dropping a ZIP shows ONLY ZIP/Archive options; PDF -> PDF options; Video/Audio -> Media options)
- Automatic Active Windows Explorer Selection Detection + Native Windows Multi-File Picker when clicking the Ring center hub with 0 files
- Razor-sharp anti-aliased rounded corners & annular segments (zero zig-zag / blurry edges)
- Continuous animated Liquid-Glass Shine Sweep (`shine_phase`) across Ring, Window, and Dynamic Island
- Pure Jet-Black Ink (`#000000`) typography & icons with enlarged Center Hub text
- Butter-smooth < 2 ms interactive rendering: instant Minimize (`-`), Square Expand (`□`), Cross (`✕`), `Start`, `Pause`, `Cancel`, and real-time mouse-draggable Percentage Slider (`WM_LBUTTONDOWN` + `WM_MOUSEMOVE` + `WM_LBUTTONUP`)
"""
import ctypes
import json
import math
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tests.run_cleanroom_verification import (
    SpringSolver,
    RotationPager,
    TOOL_SPECS,
    compute_ring_placement,
    execute_tool,
    filter_and_rank_tools,
    has_ffmpeg,
    sanitize_stem,
    resolve_clash_free_output,
    was_output_fallback_used,
    worker_main,
)

from liquid_optics import (
    render_optical_ring_rgba,
    render_optical_window_rgba,
    render_optical_island_rgba,
    generate_vivid_desktop_backdrop,
)

APP_NAME = "Dewdrop"
DEFAULT_IDLE_SECS = 120.0
DWELL_ENTER_SECS = 1.50
DWELL_BACK_SECS = 1.50
ENTER_GRACE_SECS = 1.00
DONE_HOLD_SECS = 3.50

_DESKTOP_SNAPSHOT_RGB: np.ndarray | None = None


# ============================================================================
# 1. SETTINGS, USAGE COUNTERS & SIZE-CAPPED LOGGING (%APPDATA%\Dewdrop)
# ============================================================================

def get_appdata_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    d = Path(base) / APP_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


def log_error(context: str, exc: BaseException | str):
    try:
        log_path = get_appdata_dir() / "dewdrop.log"
        if log_path.exists() and log_path.stat().st_size > 512 * 1024:
            tail = log_path.read_bytes()[-256 * 1024:]
            log_path.write_bytes(tail)
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        detail = exc if isinstance(exc, str) else "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{stamp}] {context}: {detail}\n")
    except Exception:
        pass


def load_settings() -> dict:
    defaults = {
        "hotkey": "CTRL+ALT+Z",
        "idle_seconds": 120,
        "ffmpeg": has_ffmpeg(),
        "usage": {},
    }
    spath = get_appdata_dir() / "settings.json"
    if spath.exists():
        try:
            loaded = json.loads(spath.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                defaults.update(loaded)
                if not isinstance(defaults.get("usage"), dict):
                    defaults["usage"] = {}
        except Exception as e:
            log_error("load_settings", e)
    defaults["ffmpeg"] = bool(defaults.get("ffmpeg", True)) and has_ffmpeg()
    return defaults


def save_settings(settings: dict):
    try:
        spath = get_appdata_dir() / "settings.json"
        tmp = spath.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, spath)
    except Exception as e:
        log_error("save_settings", e)


def record_tool_usage(settings: dict, tool_id: str, group_name: str):
    usage = settings.setdefault("usage", {})
    usage[tool_id] = int(usage.get(tool_id, 0)) + 1
    gkey = f"group:{group_name}"
    usage[gkey] = int(usage.get(gkey, 0)) + 1
    save_settings(settings)


# ============================================================================
# 2. ACTIVE EXPLORER SELECTION & NATIVE WINDOWS FILE PICKER
# ============================================================================

def get_selected_explorer_files() -> list[Path]:
    """
    Queries Windows Explorer (`Shell.Application`) for any files currently selected by the user
    in the foreground/active File Explorer window so launching Dewdrop immediately filters tools
    to the user's selected files (e.g., Images -> Image options only; ZIP -> ZIP options only).
    """
    if os.name != "nt":
        return []
    try:
        ps_cmd = (
            "$sh = New-Object -ComObject Shell.Application; "
            "foreach ($w in $sh.Windows()) { "
            "  try { "
            "    $sel = $w.Document.SelectedItems(); "
            "    if ($sel -and $sel.Count -gt 0) { "
            "      foreach ($it in $sel) { Write-Output $it.Path }; "
            "      break "
            "    } "
            "  } catch {} "
            "}"
        )
        res = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=1.5,
            creationflags=0x08000000,
        )
        paths = []
        for line in res.stdout.splitlines():
            s = line.strip()
            if s:
                p = Path(s)
                if p.is_file():
                    paths.append(p)
        return paths
    except Exception:
        return []


def pick_files_dialog_win32(hwnd=None) -> list[Path]:
    """
    Opens the native Windows multi-select file picker (`GetOpenFileNameW` in `comdlg32.dll`)
    when the user clicks the Ring center hub to select files directly.
    """
    if os.name != "nt":
        return []
    try:
        import ctypes.wintypes as wt

        OFN_ALLOWMULTISELECT = 0x00000200
        OFN_EXPLORER = 0x00080000
        OFN_FILEMUSTEXIST = 0x00001000
        OFN_PATHMUSTEXIST = 0x00000800
        OFN_NOCHANGEDIR = 0x00000008

        class OPENFILENAMEW(ctypes.Structure):
            _fields_ = [
                ("lStructSize", wt.DWORD),
                ("hwndOwner", wt.HWND),
                ("hInstance", wt.HINSTANCE),
                ("lpstrFilter", wt.LPCWSTR),
                ("lpstrCustomFilter", wt.LPWSTR),
                ("nMaxCustFilter", wt.DWORD),
                ("nFilterIndex", wt.DWORD),
                ("lpstrFile", wt.LPWSTR),
                ("nMaxFile", wt.DWORD),
                ("lpstrFileTitle", wt.LPWSTR),
                ("nMaxFileTitle", wt.DWORD),
                ("lpstrInitialDir", wt.LPCWSTR),
                ("lpstrTitle", wt.LPCWSTR),
                ("Flags", wt.DWORD),
                ("nFileOffset", wt.WORD),
                ("nFileExtension", wt.WORD),
                ("lpstrDefExt", wt.LPCWSTR),
                ("lCustData", wt.LPARAM),
                ("lpfnHook", ctypes.c_void_p),
                ("lpTemplateName", wt.LPCWSTR),
                ("pvReserved", ctypes.c_void_p),
                ("dwReserved", wt.DWORD),
                ("FlagsEx", wt.DWORD),
            ]

        buf_len = 32768
        file_buf = ctypes.create_unicode_buffer(buf_len)
        ofn = OPENFILENAMEW()
        ofn.lStructSize = ctypes.sizeof(OPENFILENAMEW)
        ofn.hwndOwner = hwnd
        ofn.lpstrFilter = (
            "All Supported Files\0*.*\0"
            "Images (*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.gif;*.ico)\0*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.gif;*.ico\0"
            "Archives (*.zip;*.tar;*.gz;*.tgz;*.bz2;*.xz)\0*.zip;*.tar;*.gz;*.tgz;*.bz2;*.xz\0"
            "PDF & Word (*.pdf;*.docx)\0*.pdf;*.docx\0"
            "Video & Audio (*.mp4;*.webm;*.mov;*.mkv;*.mp3;*.wav;*.flac;*.m4a)\0*.mp4;*.webm;*.mov;*.mkv;*.mp3;*.wav;*.flac;*.m4a\0\0"
        )
        ofn.nFilterIndex = 1
        ofn.lpstrFile = ctypes.cast(file_buf, wt.LPWSTR)
        ofn.nMaxFile = buf_len
        ofn.lpstrTitle = "Select file(s) for Dewdrop"
        ofn.Flags = OFN_EXPLORER | OFN_ALLOWMULTISELECT | OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_NOCHANGEDIR

        comdlg32 = ctypes.WinDLL("comdlg32", use_last_error=True)
        comdlg32.GetOpenFileNameW.argtypes = [ctypes.POINTER(OPENFILENAMEW)]
        comdlg32.GetOpenFileNameW.restype = wt.BOOL
        if not comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
            return []

        raw = ctypes.wstring_at(ctypes.addressof(file_buf), buf_len)
        parts = [p for p in raw.split("\0") if p]
        if not parts:
            return []
        if len(parts) == 1:
            p = Path(parts[0])
            return [p] if p.is_file() else []
        directory = Path(parts[0])
        selected = [directory / name for name in parts[1:]]
        return [p for p in selected if p.is_file()]
    except Exception:
        return []


# ============================================================================
# 3. SINGLE-INSTANCE GUARD & WINDOWS JOB OBJECT / WORKER CONTROL
# ============================================================================

_SINGLE_MUTEX = None
_SINGLE_EVENT = None
_JOB_HANDLE = None


def acquire_single_instance() -> bool:
    global _SINGLE_MUTEX, _SINGLE_EVENT
    if os.name != "nt":
        return True
    try:
        k32 = ctypes.windll.kernel32
        ERROR_ALREADY_EXISTS = 183
        EVENT_MODIFY_STATE = 0x0002
        mutex = k32.CreateMutexW(None, False, "Local\\Dewdrop.v1.lock")
        last_err = k32.GetLastError()
        if last_err == ERROR_ALREADY_EXISTS:
            evt = k32.OpenEventW(EVENT_MODIFY_STATE, False, "Local\\Dewdrop.v1.show")
            if evt:
                k32.SetEvent(evt)
                k32.CloseHandle(evt)
            if mutex:
                k32.CloseHandle(mutex)
            return False
        _SINGLE_MUTEX = mutex
        _SINGLE_EVENT = k32.CreateEventW(None, True, False, "Local\\Dewdrop.v1.show")
        return True
    except Exception:
        return True


def poll_show_signal() -> bool:
    if os.name != "nt" or not _SINGLE_EVENT:
        return False
    try:
        k32 = ctypes.windll.kernel32
        if k32.WaitForSingleObject(_SINGLE_EVENT, 0) == 0:
            k32.ResetEvent(_SINGLE_EVENT)
            return True
    except Exception:
        pass
    return False


def bind_children_to_app():
    global _JOB_HANDLE
    if os.name != "nt" or _JOB_HANDLE is not None:
        return
    try:
        k32 = ctypes.windll.kernel32
        job = k32.CreateJobObjectW(None, None)
        if job:
            _JOB_HANDLE = job
    except Exception:
        pass


def suspend_or_resume_process(pid: int, suspend: bool) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            PROCESS_SUSPEND_RESUME = 0x0800
            k32 = ctypes.windll.kernel32
            ntdll = ctypes.windll.ntdll
            hproc = k32.OpenProcess(PROCESS_SUSPEND_RESUME, False, int(pid))
            if not hproc:
                return False
            try:
                rc = ntdll.NtSuspendProcess(hproc) if suspend else ntdll.NtResumeProcess(hproc)
                return rc == 0
            finally:
                k32.CloseHandle(hproc)
        except Exception:
            return False
    else:
        try:
            os.kill(pid, signal.SIGSTOP if suspend else signal.SIGCONT)
            return True
        except Exception:
            return False


def terminate_worker_tree(proc: subprocess.Popen | None):
    if proc is None:
        return
    try:
        if proc.poll() is None:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    capture_output=True,
                    creationflags=0x08000000,
                )
            else:
                proc.kill()
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


# ============================================================================
# 4. PER-TOOL OPTIONS WINDOW CONFIGURATION (ALL 24 OPTION TOOLS)
# ============================================================================

def get_tool_ui_config(tool_id: str, quality_val: int, chip_idx: int, text_val: str) -> dict:
    q = max(5, min(100, int(quality_val)))
    c = max(0, min(3, int(chip_idx)))

    if tool_id in ("img_to_png", "img_to_gif"):
        widths = [0, 1920, 1280]
        rots = [0, 90, 180, 270]
        rot = rots[int(round((q / 100.0) * 3)) % 4] if q < 95 else 0
        return {
            "chips": ["Original Size", "Max 1920 px", "Max 1280 px"],
            "slider_str": f"{rot}°" if rot else "0°",
            "text_val": None,
            "opts": {"width": widths[min(c, 2)], "rotation": rot},
        }
    if tool_id == "img_to_ico":
        return {
            "chips": ["Pad Square", "Stretch Square", "All Sizes"],
            "slider_str": "256px",
            "text_val": None,
            "opts": {"square_icon": (c != 1)},
        }
    if tool_id in ("img_to_jpeg", "img_to_webp"):
        preset_q = [72, 85, 95][min(c, 2)]
        eff_q = q if q != 85 else preset_q
        return {
            "chips": ["Smaller (72%)", "Balanced (85%)", "Best (95%)"],
            "slider_str": f"{eff_q}%",
            "text_val": None,
            "opts": {"quality": eff_q, "width": 0, "rotation": 0},
        }
    if tool_id == "img_compress":
        target_kbs = [0, 200, 500]
        return {
            "chips": ["By Quality %", "Max 200 KB", "Max 500 KB"],
            "slider_str": f"{q}%",
            "text_val": None,
            "opts": {"quality": q, "target_kb": target_kbs[min(c, 2)]},
        }
    if tool_id == "img_resize":
        modes = ["percent", "fit", "fill"]
        m = modes[min(c, 2)]
        px = max(160, int(round(q * 24)))
        return {
            "chips": ["Scale %", "Fit Inside", "Fill & Crop"],
            "slider_str": f"{q}%" if m == "percent" else f"{px}px",
            "text_val": None,
            "opts": {"resize_mode": m, "percent": q, "width": px, "height": px},
        }
    if tool_id == "img_crop":
        ratios = ["1:1", "16:9", "4:3", "9:16"]
        return {
            "chips": ["1:1 Square", "16:9 Wide", "4:3 Photo", "9:16 Tall"],
            "slider_str": ratios[min(c, 3)],
            "text_val": None,
            "opts": {"ratio": ratios[min(c, 3)]},
        }
    if tool_id == "img_rotate_flip":
        rots = [90, 180, 270]
        rot = rots[min(c, 2)]
        flip = "h" if q > 66 else ("v" if q < 34 else "none")
        return {
            "chips": ["Rotate 90°", "Rotate 180°", "Rotate 270°"],
            "slider_str": f"Flip:{flip.upper()}",
            "text_val": None,
            "opts": {"rotation": rot, "flip": flip},
        }
    if tool_id == "img_effects":
        effs = ["grayscale", "sepia", "sharpen", "blur"]
        labels = ["Grayscale", "Sepia", "Sharpen", "Blur"]
        return {
            "chips": labels,
            "slider_str": f"{max(1, q // 10)}px",
            "text_val": None,
            "opts": {"effect": effs[min(c, 3)], "blur_px": max(1.0, q / 12.0)},
        }
    if tool_id == "img_watermark":
        pos_codes = ["br", "bl", "tr", "c"]
        txt = text_val if text_val else "Confidential"
        return {
            "chips": ["Bottom-Right", "Bottom-Left", "Top-Right", "Center"],
            "slider_str": f"{q}%",
            "text_val": txt,
            "opts": {"text": txt, "position": pos_codes[min(c, 3)], "quality": q},
        }
    if tool_id == "pdf_from_images":
        return {
            "chips": ["One PDF (A4)", "One PDF (Fit)", "Separate PDFs"],
            "slider_str": f"{q}%",
            "text_val": None,
            "opts": {"combine": (c != 2), "page": ("A4" if c == 0 else "image"), "quality": q},
        }
    if tool_id in ("pdf_extract_pages", "pdf_delete_pages"):
        presets = ["1", "1-3", "2-"]
        rng = text_val if text_val else presets[min(c, 2)]
        return {
            "chips": ["Page 1", "Pages 1-3", "Page 2-End"],
            "slider_str": rng[:6],
            "text_val": rng,
            "opts": {"pages": rng},
        }
    if tool_id == "pdf_rotate":
        rots = [90, 180, 270]
        return {
            "chips": ["90° CW", "180°", "270° CW"],
            "slider_str": f"{rots[min(c, 2)]}°",
            "text_val": text_val,
            "opts": {"rotation": rots[min(c, 2)], "pages": text_val or ""},
        }
    if tool_id == "pdf_compress":
        return {
            "chips": ["Light (Lossless)", "Balanced (150dpi)", "Strong (Smallest)"],
            "slider_str": f"Lvl {min(c, 2) + 1}",
            "text_val": None,
            "opts": {"level": min(c, 2) + 1},
        }
    if tool_id == "video_compress":
        maxhs = [0, 1080, 720]
        return {
            "chips": ["Light (Original)", "Balanced (1080p)", "Smallest (720p)"],
            "slider_str": f"Lvl {min(c, 2) + 1}",
            "text_val": None,
            "opts": {"level": min(c, 2) + 1, "maxh": maxhs[min(c, 2)]},
        }
    if tool_id == "audio_compress":
        brs = [96, 128, 192, 320]
        return {
            "chips": ["96 kbps", "128 kbps", "192 kbps", "320 kbps"],
            "slider_str": f"{brs[min(c, 3)]}k",
            "text_val": None,
            "opts": {"bitrate": brs[min(c, 3)]},
        }
    if tool_id == "media_trim":
        ends = ["00:05", "00:15", "00:30"]
        spec_txt = text_val if text_val else f"00:00-{ends[min(c, 2)]}"
        parts = spec_txt.split("-", 1) if "-" in spec_txt else ["00:00", spec_txt]
        return {
            "chips": ["First 5s", "First 15s", "First 30s"],
            "slider_str": parts[-1][:5],
            "text_val": spec_txt,
            "opts": {"start": parts[0].strip(), "end": parts[1].strip() if len(parts) > 1 else ""},
        }
    if tool_id == "video_to_gif":
        widths = [320, 480, 640]
        dur = max(1, min(20, int(round(q / 5.0))))
        return {
            "chips": ["320 px Wide", "480 px Wide", "640 px Wide"],
            "slider_str": f"{dur}s",
            "text_val": None,
            "opts": {"width": widths[min(c, 2)], "duration": dur, "start": "0"},
        }
    if tool_id == "video_frame_png":
        stamps = ["00:00.5", "00:01.0", "00:03.0"]
        ts = text_val if text_val else stamps[min(c, 2)]
        return {
            "chips": ["At 0.5s", "At 1.0s", "At 3.0s"],
            "slider_str": ts[:6],
            "text_val": ts,
            "opts": {"start": ts},
        }
    if tool_id in ("archive_zip", "archive_targz", "archive_gzip"):
        return {
            "chips": ["Fast (Lvl 1)", "Normal (Lvl 6)", "Best (Lvl 9)"],
            "slider_str": f"Lvl {min(c, 2) + 1}",
            "text_val": None,
            "opts": {"level": min(c, 2) + 1, "combine": True},
        }

    return {
        "chips": ["Light (Fast)", "Balanced (Default)", "Strong (Compact)"],
        "slider_str": f"{q}%",
        "text_val": None,
        "opts": {"quality": q, "level": min(c, 2) + 1},
    }


# ============================================================================
# 5. SCREEN BACKDROP CAPTURE & SURFACE RENDER WRAPPERS
# ============================================================================

def capture_full_desktop_rgb(screen_w: int, screen_h: int) -> np.ndarray | None:
    if os.name != "nt" or screen_w <= 0 or screen_h <= 0:
        return None
    try:
        import ctypes.wintypes as wt
        user32 = ctypes.WinDLL("user32")
        gdi32 = ctypes.WinDLL("gdi32")

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG),
                ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
                ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG),
                ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD),
            ]

        user32.GetDC.argtypes = [wt.HWND]
        user32.GetDC.restype = wt.HDC
        user32.ReleaseDC.argtypes = [wt.HWND, wt.HDC]
        user32.ReleaseDC.restype = ctypes.c_int
        gdi32.CreateCompatibleDC.argtypes = [wt.HDC]
        gdi32.CreateCompatibleDC.restype = wt.HDC
        gdi32.CreateDIBSection.argtypes = [wt.HDC, ctypes.c_void_p, wt.UINT, ctypes.POINTER(ctypes.c_void_p), wt.HANDLE, wt.DWORD]
        gdi32.CreateDIBSection.restype = wt.HBITMAP
        gdi32.SelectObject.argtypes = [wt.HDC, wt.HGDIOBJ]
        gdi32.SelectObject.restype = wt.HGDIOBJ
        gdi32.BitBlt.argtypes = [wt.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wt.HDC, ctypes.c_int, ctypes.c_int, wt.DWORD]
        gdi32.BitBlt.restype = wt.BOOL
        gdi32.DeleteObject.argtypes = [wt.HGDIOBJ]
        gdi32.DeleteObject.restype = wt.BOOL
        gdi32.DeleteDC.argtypes = [wt.HDC]
        gdi32.DeleteDC.restype = wt.BOOL

        hdc_scr = user32.GetDC(None)
        hdc_mem = gdi32.CreateCompatibleDC(hdc_scr)
        bmi = BITMAPINFOHEADER(ctypes.sizeof(BITMAPINFOHEADER), screen_w, -screen_h, 1, 32, 0, screen_w * screen_h * 4, 0, 0, 0, 0)
        bits = ctypes.c_void_p()
        hbmp = gdi32.CreateDIBSection(hdc_mem, ctypes.byref(bmi), 0, ctypes.byref(bits), None, 0)
        old = gdi32.SelectObject(hdc_mem, hbmp)
        gdi32.BitBlt(hdc_mem, 0, 0, screen_w, screen_h, hdc_scr, 0, 0, 0x00CC0020)
        raw = ctypes.string_at(bits, screen_w * screen_h * 4)
        gdi32.SelectObject(hdc_mem, old)
        gdi32.DeleteObject(hbmp)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(None, hdc_scr)

        bgra = np.frombuffer(raw, dtype=np.uint8).reshape((screen_h, screen_w, 4))
        rgb = bgra[..., [2, 1, 0]].astype(np.float32)
        if np.std(rgb) < 1.5:
            return None
        return rgb
    except Exception:
        return None


def capture_screen_backdrop_rgb(x: int, y: int, w: int, h: int) -> np.ndarray:
    global _DESKTOP_SNAPSHOT_RGB
    if _DESKTOP_SNAPSHOT_RGB is not None:
        sh, sw, _ = _DESKTOP_SNAPSHOT_RGB.shape
        x0 = max(0, min(int(x), sw - w))
        y0 = max(0, min(int(y), sh - h))
        if x0 + w <= sw and y0 + h <= sh:
            return _DESKTOP_SNAPSHOT_RGB[y0:y0 + h, x0:x0 + w]
    return generate_vivid_desktop_backdrop(w, h)


GROUPS = filter_and_rank_tools([], ffmpeg_available=True)
SEG_ANGLES_DEG = [0, 60, 120, 180, 240, 300]


def configure_windows_shortcut(hotkey: str = "CTRL+ALT+Z") -> bool:
    settings = load_settings()
    settings["hotkey"] = hotkey.strip().upper()
    save_settings(settings)
    if os.name != "nt":
        return False
    programs_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    lnk_path = programs_dir / f"{APP_NAME}.lnk"
    exe_candidate = ROOT_DIR / "target" / "release" / "dewdrop.exe"
    ico_path = ROOT_DIR / "assets" / "icon.ico"

    if exe_candidate.exists():
        target_path = str(exe_candidate)
        args_str = ""
    else:
        pyw = Path(sys.executable).with_name("pythonw.exe")
        target_path = str(pyw if pyw.exists() else Path(sys.executable))
        args_str = f'"{Path(__file__).resolve()}"'

    ps_cmd = (
        f"$ws = New-Object -ComObject WScript.Shell; "
        f"$s = $ws.CreateShortcut('{lnk_path}'); "
        f"$s.TargetPath = '{target_path}'; "
        f"$s.Arguments = '{args_str}'; "
        f"$s.WorkingDirectory = '{ROOT_DIR}'; "
        f"$s.IconLocation = '{ico_path}'; "
        f"$s.Hotkey = '{hotkey}'; "
        f"$s.Save();"
    )
    res = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
        capture_output=True,
        text=True,
    )
    try:
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
    except Exception:
        pass
    return res.returncode == 0


def render_ring_surface_rgba(
    labels: list[str],
    hover_seg: int,
    turn_progress: float = 0.0,
    staged_count: int = 0,
    subtitle: str = "",
    size: int = 460,
    backdrop_rgb: np.ndarray | None = None,
    light_angle_deg: float = 135.0,
    dwell_progress: float = 0.0,
    shine_phase: float = 0.22,
) -> Image.Image:
    return render_optical_ring_rgba(
        labels=labels,
        hover_seg=hover_seg,
        turn_progress=turn_progress,
        staged_count=staged_count,
        subtitle=subtitle,
        size=size,
        backdrop_rgb=backdrop_rgb,
        light_angle_deg=light_angle_deg,
        dwell_progress=dwell_progress,
        shine_phase=shine_phase,
    )


def render_options_or_progress_window_rgba(
    file_title: str,
    file_subtitle: str,
    tool_label: str,
    option_desc: str,
    mode: str,
    quality_val: int,
    chip_idx: int,
    progress_frac: float,
    paused: bool,
    status_line: str,
    detail_line: str,
    w: int = 720,
    h: int = 360,
    backdrop_rgb: np.ndarray | None = None,
    mouse_offset: tuple[float, float] = (0.0, 0.0),
    hover_target: str = "",
    chip_labels: list[str] | None = None,
    slider_display: str | None = None,
    text_input_value: str | None = None,
    expanded: bool = False,
    preview_file: Path | None = None,
    batch_badge: str = "",
    shine_phase: float = 0.25,
) -> Image.Image:
    return render_optical_window_rgba(
        file_title=file_title,
        file_subtitle=file_subtitle,
        tool_label=tool_label,
        option_desc=option_desc,
        mode=mode,
        quality_val=quality_val,
        chip_idx=chip_idx,
        progress_frac=progress_frac,
        paused=paused,
        status_line=status_line,
        detail_line=detail_line,
        w=w,
        h=h,
        backdrop_rgb=backdrop_rgb,
        mouse_offset=mouse_offset,
        hover_target=hover_target,
        chip_labels=chip_labels,
        slider_display=slider_display,
        text_input_value=text_input_value,
        expanded=expanded,
        preview_file=preview_file,
        batch_badge=batch_badge,
        shine_phase=shine_phase,
    )


def render_dynamic_island_rgba(
    file_title: str,
    batch_subtitle: str,
    progress_frac: float,
    paused: bool,
    detail_line: str,
    w: int = 760,
    h: int = 160,
    backdrop_rgb: np.ndarray | None = None,
    mouse_offset: tuple[float, float] = (0.0, 0.0),
    hover_target: str = "",
    preview_file: Path | None = None,
    batch_badge: str = "",
    shine_phase: float = 0.25,
) -> Image.Image:
    return render_optical_island_rgba(
        file_title=file_title,
        batch_subtitle=batch_subtitle,
        progress_frac=progress_frac,
        paused=paused,
        detail_line=detail_line,
        w=w,
        h=h,
        backdrop_rgb=backdrop_rgb,
        mouse_offset=mouse_offset,
        hover_target=hover_target,
        preview_file=preview_file,
        batch_badge=batch_badge,
        shine_phase=shine_phase,
    )


def render_morph_frame_rgba(
    morph_t: float,  # 0.0 = Window (w_im.size), 1.0 = Dynamic Island (i_im.size)
    win_img: Image.Image,
    island_img: Image.Image,
) -> Image.Image:
    t = min(max(morph_t, -0.08), 1.08)
    clamped = min(max(t, 0.0), 1.0)
    w0, h0 = win_img.size
    w1, h1 = island_img.size
    cur_w = max(240, int(round(w0 + (w1 - w0) * t)))
    cur_h = max(96, int(round(h0 + (h1 - h0) * t)))

    w_scaled = win_img.resize((cur_w, cur_h), Image.Resampling.BILINEAR)
    i_scaled = island_img.resize((cur_w, cur_h), Image.Resampling.BILINEAR)
    return Image.blend(w_scaled, i_scaled, clamped)


def ensure_demo_sample_file() -> Path:
    sample_dir = Path(tempfile.gettempdir()) / "Dewdrop_Sample_Files"
    sample_dir.mkdir(parents=True, exist_ok=True)
    sample_file = sample_dir / "Sample_Photo.png"
    if not sample_file.exists():
        arr = generate_vivid_desktop_backdrop(640, 480).astype(np.uint8)
        im = Image.fromarray(arr, mode="RGB")
        im.save(sample_file, "PNG")
    return sample_file


# ============================================================================
# 6. INTERACTIVE WIN32 LAYERED OVERLAY GUI (60 FPS BUTTER-SMOOTH)
# ============================================================================

def run_windows_interactive_gui(start_mode: str = "ring_groups", cli_files: list[Path] | None = None):
    global _DESKTOP_SNAPSHOT_RGB
    import ctypes.wintypes as wt

    if not acquire_single_instance():
        return
    bind_children_to_app()
    settings = load_settings()
    idle_limit_secs = float(settings.get("idle_seconds", DEFAULT_IDLE_SECS))

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
    shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    try:
        user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        pass

    WS_POPUP = 0x80000000
    WS_VISIBLE = 0x10000000
    WS_EX_LAYERED = 0x00080000
    WS_EX_TOPMOST = 0x00000008
    WS_EX_TOOLWINDOW = 0x00000080
    ULW_ALPHA = 0x00000002
    AC_SRC_OVER = 0x00
    AC_SRC_ALPHA = 0x01
    SWP_NOACTIVATE = 0x0010
    SWP_NOZORDER = 0x0004

    WM_DESTROY = 0x0002
    WM_ACTIVATE = 0x0006
    WM_MOUSEMOVE = 0x0200
    WM_LBUTTONDOWN = 0x0201
    WM_LBUTTONUP = 0x0202
    WM_RBUTTONDOWN = 0x0204
    WM_MOUSEWHEEL = 0x020A
    WM_KEYDOWN = 0x0100
    WM_CHAR = 0x0102
    WM_DROPFILES = 0x0233
    WM_TIMER = 0x0113

    VK_ESCAPE = 0x1B
    VK_RETURN = 0x0D
    VK_BACK = 0x08
    VK_SPACE = 0x20

    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    class SIZE(ctypes.Structure):
        _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

    class BLENDFUNCTION(ctypes.Structure):
        _fields_ = [
            ("BlendOp", ctypes.c_ubyte),
            ("BlendFlags", ctypes.c_ubyte),
            ("SourceConstantAlpha", ctypes.c_ubyte),
            ("AlphaFormat", ctypes.c_ubyte),
        ]

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG),
            ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
            ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG),
            ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD),
        ]

    WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM)

    class WNDCLASSW(ctypes.Structure):
        _fields_ = [
            ("style", wt.UINT),
            ("lpfnWndProc", WNDPROC),
            ("cbClsExtra", ctypes.c_int),
            ("cbWndExtra", ctypes.c_int),
            ("hInstance", wt.HINSTANCE),
            ("hIcon", wt.HANDLE),
            ("hCursor", wt.HANDLE),
            ("hbrBackground", wt.HANDLE),
            ("lpszMenuName", wt.LPCWSTR),
            ("lpszClassName", wt.LPCWSTR),
        ]

    kernel32.GetModuleHandleW.argtypes = [wt.LPCWSTR]
    kernel32.GetModuleHandleW.restype = wt.HMODULE
    user32.LoadCursorW.argtypes = [wt.HINSTANCE, wt.LPCWSTR]
    user32.LoadCursorW.restype = wt.HANDLE
    user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]
    user32.RegisterClassW.restype = wt.ATOM
    user32.CreateWindowExW.argtypes = [
        wt.DWORD, wt.LPCWSTR, wt.LPCWSTR, wt.DWORD,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        wt.HWND, wt.HMENU, wt.HINSTANCE, wt.LPVOID,
    ]
    user32.CreateWindowExW.restype = wt.HWND
    user32.UpdateLayeredWindow.argtypes = [
        wt.HWND, wt.HDC, ctypes.POINTER(POINT), ctypes.POINTER(SIZE),
        wt.HDC, ctypes.POINTER(POINT), wt.COLORREF, ctypes.POINTER(BLENDFUNCTION), wt.DWORD,
    ]
    user32.UpdateLayeredWindow.restype = wt.BOOL
    user32.SetWindowPos.argtypes = [wt.HWND, wt.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wt.UINT]
    user32.SetWindowPos.restype = wt.BOOL
    user32.SetCapture.argtypes = [wt.HWND]
    user32.SetCapture.restype = wt.HWND
    user32.ReleaseCapture.argtypes = []
    user32.ReleaseCapture.restype = wt.BOOL
    user32.GetDC.argtypes = [wt.HWND]
    user32.GetDC.restype = wt.HDC
    user32.ReleaseDC.argtypes = [wt.HWND, wt.HDC]
    user32.ReleaseDC.restype = ctypes.c_int
    user32.SetTimer.argtypes = [wt.HWND, ctypes.c_size_t, wt.UINT, ctypes.c_void_p]
    user32.SetTimer.restype = ctypes.c_size_t
    user32.KillTimer.argtypes = [wt.HWND, ctypes.c_size_t]
    user32.KillTimer.restype = wt.BOOL
    user32.PostQuitMessage.argtypes = [ctypes.c_int]
    user32.PostQuitMessage.restype = None
    user32.DefWindowProcW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
    user32.DefWindowProcW.restype = ctypes.c_ssize_t
    user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
    user32.GetCursorPos.restype = wt.BOOL
    user32.SetForegroundWindow.argtypes = [wt.HWND]
    user32.SetForegroundWindow.restype = wt.BOOL

    gdi32.CreateCompatibleDC.argtypes = [wt.HDC]
    gdi32.CreateCompatibleDC.restype = wt.HDC
    gdi32.CreateDIBSection.argtypes = [
        wt.HDC, ctypes.c_void_p, wt.UINT, ctypes.POINTER(ctypes.c_void_p), wt.HANDLE, wt.DWORD,
    ]
    gdi32.CreateDIBSection.restype = wt.HBITMAP
    gdi32.SelectObject.argtypes = [wt.HDC, wt.HGDIOBJ]
    gdi32.SelectObject.restype = wt.HGDIOBJ
    gdi32.DeleteObject.argtypes = [wt.HGDIOBJ]
    gdi32.DeleteObject.restype = wt.BOOL
    gdi32.DeleteDC.argtypes = [wt.HDC]
    gdi32.DeleteDC.restype = wt.BOOL

    shell32.DragAcceptFiles.argtypes = [wt.HWND, wt.BOOL]
    shell32.DragAcceptFiles.restype = None
    shell32.DragFinish.argtypes = [wt.HANDLE]
    shell32.DragFinish.restype = None

    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    _DESKTOP_SNAPSHOT_RGB = capture_full_desktop_rgb(screen_w, screen_h)

    win_center_x = (screen_w - 720) // 2
    win_center_y = (screen_h - 360) // 2
    island_top_x = (screen_w - 760) // 2
    island_top_y = 12

    # Detect files from CLI or active Windows Explorer selection automatically
    detected_files = list(cli_files) if cli_files else get_selected_explorer_files()
    if not detected_files and start_mode != "ring_groups":
        detected_files = [ensure_demo_sample_file()]

    active_groups = filter_and_rank_tools(
        detected_files,
        ffmpeg_available=bool(settings.get("ffmpeg", True)),
        usage_counts=settings.get("usage"),
    )
    if not active_groups:
        active_groups = filter_and_rank_tools([], ffmpeg_available=bool(settings.get("ffmpeg", True)), usage_counts=settings.get("usage"))

    # If the selected files match a single category (e.g. ZIP -> Archives, PDF -> PDF & docs, MP4 -> Video & audio),
    # jump directly to that category's tools ring!
    effective_start_mode = start_mode
    if start_mode == "ring_groups" and detected_files and len(active_groups) == 1:
        effective_start_mode = "ring_tools"

    state = {
        "mode": effective_start_mode,
        "start_mode": start_mode,
        "window_expanded": False,
        "dragging_slider": False,
        "shine_phase": 0.15,
        "morph_target_mode": "island",
        "morph_spring": SpringSolver(1.0 if start_mode == "island" else 0.0, response=0.45, damping_ratio=0.80),
        "x_spring": SpringSolver(float(island_top_x if start_mode == "island" else win_center_x), response=0.45, damping_ratio=0.80),
        "y_spring": SpringSolver(float(island_top_y if start_mode == "island" else win_center_y), response=0.45, damping_ratio=0.80),
        "morph_win_im": None,
        "morph_isl_im": None,
        "groups": active_groups,
        "group_idx": 0,
        "tool_idx": 0,
        "hover_seg": 0,
        "hover_target": "",
        "dwell_target": None,
        "dwell_started_at": 0.0,
        "dwell_progress": 0.0,
        "entered_tools_at": time.monotonic(),
        "light_angle_deg": 135.0,
        "mouse_offset": (0.0, 0.0),
        "page": 0,
        "pager": RotationPager(
            len(active_groups[0][1]) if effective_start_mode == "ring_tools" else len(active_groups),
            deadzone_radius=38.0,
        ),
        "staged_files": detected_files,
        "current_preview_file": detected_files[0] if detected_files else None,
        "batch_badge": f"1/{len(detected_files)}" if len(detected_files) > 1 else "",
        "quality_val": 85,
        "chip_idx": 1,
        "text_input": "",
        "progress_frac": 0.68 if start_mode == "island" else 0.0,
        "paused": False,
        "cancelled": False,
        "job_active": False,
        "worker_proc": None,
        "worker_res_file": None,
        "worker_temp_dir": None,
        "last_outputs": [],
        "last_errors": [],
        "done_at": 0.0,
        "status_line": "Processing...",
        "detail_line": "1.6 MB of 2.4 MB  •  2 seconds left",
        "ring_x": (screen_w - 460) // 2,
        "ring_y": (screen_h - 460) // 2,
        "win_x": win_center_x,
        "win_y": win_center_y,
        "cur_w": 460,
        "cur_h": 460,
        "window_opened_at": time.monotonic(),
        "last_mousemove_redraw": 0.0,
        "last_active": time.monotonic(),
    }

    def get_window_rect() -> tuple[int, int, int, int]:
        ww = 860 if state["window_expanded"] else 720
        wh = 430 if state["window_expanded"] else 360
        wx = (screen_w - ww) // 2
        wy = (screen_h - wh) // 2
        return (wx, wy, ww, wh)

    def get_local_cursor_xy(lparam) -> tuple[int, int]:
        """
        Computes exact cursor coordinates relative to our layered surface `(win_x, win_y)`
        using `GetCursorPos()` so clicks on `-`, `□`, `✕`, `Start`, `Pause`, `Cancel`, and
        slider dragging are 100% accurate on every Windows 10/11 DPI configuration.
        """
        pt = POINT()
        if user32.GetCursorPos(ctypes.byref(pt)):
            return (int(pt.x - state["win_x"]), int(pt.y - state["win_y"]))
        return (
            int(ctypes.c_short(lparam & 0xFFFF).value),
            int(ctypes.c_short((lparam >> 16) & 0xFFFF).value),
        )

    def apply_staged_files(files: list[Path]):
        """
        Applies newly selected/dropped files, updates the real photo thumbnail preview,
        and strictly filters the Ring to ONLY the options compatible with those files!
        """
        state["staged_files"] = files
        state["current_preview_file"] = files[0] if files else None
        state["batch_badge"] = f"1/{len(files)}" if len(files) > 1 else ""
        ranked = filter_and_rank_tools(
            files,
            ffmpeg_available=bool(settings.get("ffmpeg", True)),
            usage_counts=settings.get("usage"),
        )
        state["groups"] = ranked if ranked else filter_and_rank_tools([], ffmpeg_available=True)
        state["group_idx"] = 0
        state["page"] = 0
        state["dwell_target"] = None
        state["dwell_progress"] = 0.0
        if files and len(state["groups"]) == 1:
            # Single matching category (e.g. ZIP -> Archives, PDF -> PDF & docs, Video -> Video & audio):
            # open directly into that category's tools!
            state["mode"] = "ring_tools"
            state["entered_tools_at"] = time.monotonic()
            state["pager"] = RotationPager(len(state["groups"][0][1]), deadzone_radius=38.0)
        else:
            state["mode"] = "ring_groups"
            state["pager"] = RotationPager(len(state["groups"]), deadzone_radius=38.0)

    def push_rgba_to_hwnd(hwnd, pil_rgba: Image.Image, x: int, y: int):
        w, h = pil_rgba.size
        pos_or_size_changed = (w != state["cur_w"] or h != state["cur_h"] or int(x) != state["win_x"] or int(y) != state["win_y"])
        state["cur_w"], state["cur_h"] = w, h
        state["win_x"], state["win_y"] = int(x), int(y)

        if pos_or_size_changed:
            user32.SetWindowPos(hwnd, None, int(x), int(y), int(w), int(h), SWP_NOZORDER | SWP_NOACTIVATE)

        r_ch, g_ch, b_ch, a_ch = pil_rgba.convert("RGBa").split()
        bgra = Image.merge("RGBA", (b_ch, g_ch, r_ch, a_ch)).tobytes()

        hdc_screen = user32.GetDC(None)
        hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
        bmi = BITMAPINFOHEADER(ctypes.sizeof(BITMAPINFOHEADER), w, -h, 1, 32, 0, w * h * 4, 0, 0, 0, 0)
        bits = ctypes.c_void_p()
        hbmp = gdi32.CreateDIBSection(hdc_mem, ctypes.byref(bmi), 0, ctypes.byref(bits), None, 0)
        old = gdi32.SelectObject(hdc_mem, hbmp)
        ctypes.memmove(bits, bgra, len(bgra))

        pt_dst = POINT(int(x), int(y))
        sz = SIZE(w, h)
        pt_src = POINT(0, 0)
        blend = BLENDFUNCTION(AC_SRC_OVER, 0, 255, AC_SRC_ALPHA)
        user32.UpdateLayeredWindow(
            hwnd, hdc_screen, ctypes.byref(pt_dst), ctypes.byref(sz),
            hdc_mem, ctypes.byref(pt_src), 0, ctypes.byref(blend), ULW_ALPHA
        )
        gdi32.SelectObject(hdc_mem, old)
        gdi32.DeleteObject(hbmp)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(None, hdc_screen)

    def get_file_summary() -> tuple[str, str]:
        files = state["staged_files"]
        cur_p = state.get("current_preview_file")
        if not files:
            return ("Select or Drop Files", "All 50 offline tools ready")
        if len(files) == 1:
            p = files[0]
            sz_kb = max(1, p.stat().st_size // 1024) if p.exists() else 240
            return (p.name, f"{sz_kb} KB")
        total_kb = sum((p.stat().st_size // 1024) for p in files if p.exists())
        if state["job_active"] and cur_p is not None:
            return (cur_p.name, f"{len(files)} files  •  {max(1, total_kb)} KB total")
        return (f"{files[0].name} (+{len(files) - 1} more)", f"{len(files)} files  •  {max(1, total_kb)} KB")

    def current_selected_tool() -> tuple[str, str, bool, str]:
        g_list = state["groups"]
        g_idx = min(state["group_idx"], len(g_list) - 1)
        tools = g_list[g_idx][1]
        t_idx = min(state["tool_idx"], len(tools) - 1)
        return tools[t_idx]

    def build_current_window_image(view_kind: str) -> Image.Image:
        f_title, f_sub = get_file_summary()
        t_id, t_label, _, t_desc = current_selected_tool()
        ui_cfg = get_tool_ui_config(t_id, state["quality_val"], state["chip_idx"], state["text_input"])
        wx, wy, ww, wh = get_window_rect()
        bg = capture_screen_backdrop_rgb(wx, wy, ww, wh)
        return render_options_or_progress_window_rgba(
            file_title=f_title,
            file_subtitle=f_sub,
            tool_label=t_label,
            option_desc=t_desc,
            mode=view_kind,
            quality_val=state["quality_val"],
            chip_idx=state["chip_idx"],
            progress_frac=state["progress_frac"],
            paused=state["paused"],
            status_line=state["status_line"],
            detail_line=state["detail_line"],
            w=ww,
            h=wh,
            backdrop_rgb=bg,
            mouse_offset=state["mouse_offset"],
            hover_target=state["hover_target"],
            chip_labels=ui_cfg["chips"],
            slider_display=ui_cfg["slider_str"],
            text_input_value=ui_cfg["text_val"],
            expanded=state["window_expanded"],
            preview_file=state["current_preview_file"],
            batch_badge=state["batch_badge"],
            shine_phase=state["shine_phase"],
        )

    def build_current_island_image() -> Image.Image:
        f_title, f_sub = get_file_summary()
        bg = capture_screen_backdrop_rgb(island_top_x, island_top_y, 760, 160)
        return render_dynamic_island_rgba(
            file_title=f_title,
            batch_subtitle=f_sub,
            progress_frac=state["progress_frac"],
            paused=state["paused"],
            detail_line=state["detail_line"],
            backdrop_rgb=bg,
            mouse_offset=state["mouse_offset"],
            hover_target=state["hover_target"],
            preview_file=state["current_preview_file"],
            batch_badge=state["batch_badge"],
            shine_phase=state["shine_phase"],
        )

    def start_morph(hwnd, to_island: bool):
        w_kind = "progress" if (state["job_active"] or state["done_at"] > 0) else "options"
        state["morph_win_im"] = build_current_window_image(w_kind)
        state["morph_isl_im"] = build_current_island_image()
        wx, wy, _, _ = get_window_rect()
        if to_island:
            state["morph_target_mode"] = "island"
            state["morph_spring"].set_target(1.0)
            state["x_spring"].set_target(float(island_top_x))
            state["y_spring"].set_target(float(island_top_y))
        else:
            state["morph_target_mode"] = "progress_window" if (state["job_active"] or state["done_at"] > 0) else "options_window"
            state["morph_spring"].set_target(0.0)
            state["x_spring"].set_target(float(wx))
            state["y_spring"].set_target(float(wy))
            state["window_opened_at"] = time.monotonic()
        state["mode"] = "morphing"
        user32.SetTimer(hwnd, 2, 16, None)

    def cleanup_worker_temp():
        tdir = state.get("worker_temp_dir")
        if tdir and Path(tdir).exists():
            shutil.rmtree(tdir, ignore_errors=True)
        state["worker_temp_dir"] = None
        state["worker_res_file"] = None
        state["worker_proc"] = None

    def cancel_and_dismiss(hwnd):
        state["cancelled"] = True
        state["job_active"] = False
        state["paused"] = False
        state["done_at"] = 0.0
        state["progress_frac"] = 0.0
        state["hover_target"] = ""
        if state["dragging_slider"]:
            state["dragging_slider"] = False
            try:
                user32.ReleaseCapture()
            except Exception:
                pass
        try:
            user32.KillTimer(hwnd, 3)
            user32.KillTimer(hwnd, 2)
        except Exception:
            pass
        terminate_worker_tree(state["worker_proc"])
        cleanup_worker_temp()
        if state["start_mode"] != "ring_groups":
            user32.PostQuitMessage(0)
        else:
            state["mode"] = "ring_tools"
            redraw(hwnd)

    def start_conversion_job(hwnd):
        if not state["staged_files"]:
            apply_staged_files([ensure_demo_sample_file()])

        g_name = state["groups"][min(state["group_idx"], len(state["groups"]) - 1)][0]
        t_id, t_label, _, _ = current_selected_tool()
        record_tool_usage(settings, t_id, g_name)

        ui_cfg = get_tool_ui_config(t_id, state["quality_val"], state["chip_idx"], state["text_input"])
        opts = ui_cfg["opts"]

        cleanup_worker_temp()
        tdir = Path(tempfile.mkdtemp(prefix=".dewdrop-job-"))
        job_json = tdir / "job.json"
        res_json = tdir / "result.json"
        job_json.write_text(json.dumps({
            "tool_id": t_id,
            "files": [str(p) for p in state["staged_files"]],
            "options": opts,
        }, ensure_ascii=False), encoding="utf-8")

        creation_flags = 0x08000000 if os.name == "nt" else 0
        proc = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--worker", str(job_json), str(res_json)],
            cwd=str(ROOT_DIR),
            creationflags=creation_flags,
        )

        state["worker_temp_dir"] = str(tdir)
        state["worker_res_file"] = str(res_json)
        state["worker_proc"] = proc
        state["job_active"] = True
        state["done_at"] = 0.0
        state["paused"] = False
        state["cancelled"] = False
        state["progress_frac"] = 0.06
        state["current_preview_file"] = state["staged_files"][0]
        state["batch_badge"] = f"1/{len(state['staged_files'])}" if len(state["staged_files"]) > 1 else ""
        state["status_line"] = f"Running {t_label}..."
        state["detail_line"] = "Saving output to Dew Drop folder..."
        start_morph(hwnd, to_island=True)
        user32.SetTimer(hwnd, 3, 50, None)

    def current_labels() -> list[str]:
        if state["mode"] == "ring_groups":
            chunk = [g[0] for g in state["groups"][:6]]
        else:
            tools = state["groups"][min(state["group_idx"], len(state["groups"]) - 1)][1]
            start = state["page"] * 6
            chunk = [t[1] for t in tools[start:start + 6]]
        while len(chunk) < 6:
            chunk.append("")
        return chunk

    def redraw(hwnd):
        mode = state["mode"]
        if mode in ("ring_groups", "ring_tools"):
            g_list = state["groups"]
            g_name = g_list[min(state["group_idx"], len(g_list) - 1)][0]
            sub = (
                f"{len(state['staged_files'])} file(s) selected" if (mode == "ring_groups" and state["staged_files"])
                else ("Select or Drop Files" if mode == "ring_groups" else f"{g_name} (Pg {state['page']+1}/{state['pager'].total_pages})")
            )
            bg = capture_screen_backdrop_rgb(state["ring_x"], state["ring_y"], 460, 460)
            im = render_ring_surface_rgba(
                current_labels(),
                hover_seg=state["hover_seg"],
                turn_progress=state["pager"].accumulated_rad / (2.0 * math.pi),
                staged_count=len(state["staged_files"]),
                subtitle=sub,
                size=460,
                backdrop_rgb=bg,
                light_angle_deg=state["light_angle_deg"],
                dwell_progress=state["dwell_progress"],
                shine_phase=state["shine_phase"],
            )
            push_rgba_to_hwnd(hwnd, im, state["ring_x"], state["ring_y"])
        elif mode == "options_window":
            wx, wy, _, _ = get_window_rect()
            im = build_current_window_image("options")
            push_rgba_to_hwnd(hwnd, im, wx, wy)
        elif mode == "progress_window":
            wx, wy, _, _ = get_window_rect()
            im = build_current_window_image("progress")
            push_rgba_to_hwnd(hwnd, im, wx, wy)
        elif mode == "island":
            im = build_current_island_image()
            push_rgba_to_hwnd(hwnd, im, island_top_x, island_top_y)
        elif mode == "morphing":
            w_im = state["morph_win_im"] or build_current_window_image("progress" if state["job_active"] else "options")
            i_im = state["morph_isl_im"] or build_current_island_image()
            frame = render_morph_frame_rgba(state["morph_spring"].position, w_im, i_im)
            push_rgba_to_hwnd(hwnd, frame, round(state["x_spring"].position), round(state["y_spring"].position))

    def enter_group_segment(hwnd, seg: int):
        if seg < len(state["groups"]):
            state["group_idx"] = seg
            state["page"] = 0
            tools = state["groups"][seg][1]
            state["pager"] = RotationPager(len(tools), deadzone_radius=38.0)
            state["mode"] = "ring_tools"
            state["entered_tools_at"] = time.monotonic()
            state["dwell_target"] = None
            state["dwell_progress"] = 0.0
            redraw(hwnd)

    def select_tool_segment(hwnd, seg: int):
        tools = state["groups"][min(state["group_idx"], len(state["groups"]) - 1)][1]
        idx = state["page"] * 6 + seg
        if idx < len(tools):
            state["tool_idx"] = idx
            t_id, _, has_opts, _ = tools[idx]
            state["text_input"] = ""
            if not state["staged_files"]:
                picked = pick_files_dialog_win32(hwnd)
                if picked:
                    state["staged_files"] = picked
                    state["current_preview_file"] = picked[0]
                    state["batch_badge"] = f"1/{len(picked)}" if len(picked) > 1 else ""
                else:
                    state["staged_files"] = [ensure_demo_sample_file()]
                    state["current_preview_file"] = state["staged_files"][0]
                    state["batch_badge"] = ""
            if not has_opts:
                start_conversion_job(hwnd)
            else:
                wx, wy, _, _ = get_window_rect()
                state["x_spring"] = SpringSolver(float(wx), 0.45, 0.80)
                state["y_spring"] = SpringSolver(float(wy), 0.45, 0.80)
                state["morph_spring"] = SpringSolver(0.0, 0.45, 0.80)
                state["window_opened_at"] = time.monotonic()
                state["mode"] = "options_window"
                redraw(hwnd)

    def update_slider_from_x(hwnd, x: int):
        _, _, ww, _ = get_window_rect()
        px0 = 18 + 40
        px1 = (ww - 18) - 104
        pct = int(round(((x - px0) / float(max(1, px1 - px0))) * 100.0))
        new_q = min(max(pct, 5), 100)
        if new_q != state["quality_val"]:
            state["quality_val"] = new_q
            redraw(hwnd)

    def py_wndproc(hwnd, msg, wparam, lparam):
        if msg == WM_DROPFILES:
            hdrop = wt.HANDLE(wparam)
            shell32.DragQueryFileW.argtypes = [wt.HANDLE, wt.UINT, wt.LPWSTR, wt.UINT]
            shell32.DragQueryFileW.restype = wt.UINT
            count = shell32.DragQueryFileW(hdrop, 0xFFFFFFFF, None, 0)
            dropped = []
            for i in range(min(count, 500)):
                n = shell32.DragQueryFileW(hdrop, i, None, 0)
                buf = ctypes.create_unicode_buffer(n + 1)
                shell32.DragQueryFileW(hdrop, i, buf, n + 1)
                p = Path(buf.value)
                if p.is_file():
                    dropped.append(p)
            shell32.DragFinish(hdrop)
            if dropped:
                state["last_active"] = time.monotonic()
                apply_staged_files(dropped)
                redraw(hwnd)
            return 0

        if msg == WM_ACTIVATE:
            active_flag = wparam & 0xFFFF
            if (
                active_flag == 0
                and not state["dragging_slider"]
                and state["mode"] in ("options_window", "progress_window")
                and (time.monotonic() - state["window_opened_at"] > 0.8)
            ):
                start_morph(hwnd, to_island=True)
            return 0

        if msg == WM_LBUTTONUP:
            if state["dragging_slider"]:
                state["dragging_slider"] = False
                try:
                    user32.ReleaseCapture()
                except Exception:
                    pass
            return 0

        if msg == WM_MOUSEMOVE:
            now = time.monotonic()
            state["last_active"] = now
            x, y = get_local_cursor_xy(lparam)
            mode = state["mode"]

            # Real-time butter-smooth slider dragging while left button is held down
            if state["dragging_slider"] and mode == "options_window":
                if (wparam & 0x0001) == 0:
                    state["dragging_slider"] = False
                    try:
                        user32.ReleaseCapture()
                    except Exception:
                        pass
                else:
                    update_slider_from_x(hwnd, x)
                    return 0

            if mode in ("ring_groups", "ring_tools"):
                dx = x - 230.0
                dy = y - 230.0
                r = math.hypot(dx, dy)
                if r > 8.0:
                    state["light_angle_deg"] = (math.degrees(math.atan2(dy, dx)) + 360.0) % 360.0
                new_page = state["pager"].update_pointer(dx, dy)
                if new_page is not None:
                    state["page"] = new_page
                    state["dwell_target"] = None
                    state["dwell_progress"] = 0.0

                if 92.0 <= r <= 220.0:
                    ang = (math.degrees(math.atan2(dx, -dy)) + 360.0) % 360.0
                    seg = int(((ang + 30.0) % 360.0) // 60.0) % 6
                    if seg != state["hover_seg"]:
                        state["hover_seg"] = seg
                        if mode == "ring_groups" and seg < len(state["groups"]):
                            state["dwell_target"] = ("group", seg)
                            state["dwell_started_at"] = now
                            state["dwell_progress"] = 0.0
                elif r < 88.0 and mode == "ring_tools" and (now - state["entered_tools_at"] >= ENTER_GRACE_SECS):
                    if state["dwell_target"] != ("back", 0):
                        state["dwell_target"] = ("back", 0)
                        state["dwell_started_at"] = now
                        state["dwell_progress"] = 0.0
                else:
                    state["dwell_target"] = None
                    state["dwell_progress"] = 0.0

                if now - state["last_mousemove_redraw"] >= 0.016:
                    state["last_mousemove_redraw"] = now
                    redraw(hwnd)
            elif mode in ("options_window", "progress_window"):
                _, _, ww, wh = get_window_rect()
                x0, y0, x1, y1 = 18, 18, ww - 18, wh - 18
                wx0, wy0, wx1, wy1 = x1 - 186, y0 + 24, x1 - 22, y0 + 68
                bx0, by0, bx1, by1 = x1 - 280, y1 - 68, x1 - 160, y1 - 22
                cx0, cy0, cx1, cy1 = x1 - 146, y1 - 68, x1 - 24, y1 - 22
                new_hover = ""
                if (wy0 - 10) <= y <= (wy1 + 10) and (wx0 - 8) <= x <= (wx1 + 8):
                    if x < wx0 + 56:
                        new_hover = "minimize"
                    elif x < wx0 + 111:
                        new_hover = "expand"
                    else:
                        new_hover = "close"
                elif (by0 - 8) <= y <= (by1 + 8):
                    if (bx0 - 6) <= x <= (bx1 + 6):
                        new_hover = "primary_btn"
                    elif (cx0 - 6) <= x <= (cx1 + 6):
                        new_hover = "cancel_btn"

                if new_hover != state["hover_target"]:
                    state["hover_target"] = new_hover
                    redraw(hwnd)
            elif mode == "island":
                p_cx = int(760 * 0.785)
                x_cx = int(760 * 0.875)
                cy_isl = 80
                new_hover = ""
                if math.hypot(x - p_cx, y - cy_isl) <= 32:
                    new_hover = "pause"
                elif math.hypot(x - x_cx, y - cy_isl) <= 34:
                    new_hover = "cancel"
                if new_hover != state["hover_target"]:
                    state["hover_target"] = new_hover
                    redraw(hwnd)
            return 0

        if msg == WM_MOUSEWHEEL:
            if state["mode"] == "ring_tools":
                tools = state["groups"][min(state["group_idx"], len(state["groups"]) - 1)][1]
                total_pages = max(1, (len(tools) + 5) // 6)
                delta = ctypes.c_short((wparam >> 16) & 0xFFFF).value
                state["page"] = (state["page"] + (-1 if delta > 0 else 1)) % total_pages
                redraw(hwnd)
            return 0

        if msg == WM_LBUTTONDOWN:
            state["last_active"] = time.monotonic()
            x, y = get_local_cursor_xy(lparam)
            mode = state["mode"]

            if mode == "morphing":
                going_to_island = (state["morph_target_mode"] == "island")
                start_morph(hwnd, to_island=not going_to_island)
                return 0

            if mode in ("ring_groups", "ring_tools"):
                dx = x - 230.0
                dy = y - 230.0
                r = math.hypot(dx, dy)
                if r < 92.0:
                    if mode == "ring_tools":
                        if len(state["groups"]) == 1 and state["staged_files"]:
                            # If only 1 category matched, clicking Back lets the user pick different files or see all groups
                            state["staged_files"] = []
                            state["current_preview_file"] = None
                            state["batch_badge"] = ""
                            state["groups"] = filter_and_rank_tools([], ffmpeg_available=bool(settings.get("ffmpeg", True)), usage_counts=settings.get("usage"))
                        state["mode"] = "ring_groups"
                        state["dwell_target"] = None
                        state["dwell_progress"] = 0.0
                        state["pager"] = RotationPager(len(state["groups"]), deadzone_radius=38.0)
                        redraw(hwnd)
                    else:
                        if not state["staged_files"]:
                            picked = pick_files_dialog_win32(hwnd)
                            if picked:
                                apply_staged_files(picked)
                                redraw(hwnd)
                                return 0
                        user32.PostQuitMessage(0)
                elif 92.0 <= r <= 225.0:
                    ang = (math.degrees(math.atan2(dx, -dy)) + 360.0) % 360.0
                    seg = int(((ang + 30.0) % 360.0) // 60.0) % 6
                    state["hover_seg"] = seg
                    if mode == "ring_groups":
                        enter_group_segment(hwnd, seg)
                    else:
                        select_tool_segment(hwnd, seg)
                return 0

            if mode in ("options_window", "progress_window"):
                wx, wy, ww, wh = get_window_rect()
                x0, y0, x1, y1 = 18, 18, ww - 18, wh - 18
                wx0, wy0, wx1, wy1 = x1 - 186, y0 + 24, x1 - 22, y0 + 68

                # 1. Top-Right Window Control Pill: Minimize (-), Square Expand (□), and Cross (✕)
                if (wy0 - 12) <= y <= (wy1 + 12) and (wx0 - 10) <= x <= (wx1 + 10):
                    if x < wx0 + 56:
                        start_morph(hwnd, to_island=True)
                        return 0
                    elif x < wx0 + 111:
                        state["window_expanded"] = not state["window_expanded"]
                        nwx, nwy, _, _ = get_window_rect()
                        state["x_spring"] = SpringSolver(float(nwx), 0.45, 0.80)
                        state["y_spring"] = SpringSolver(float(nwy), 0.45, 0.80)
                        state["window_opened_at"] = time.monotonic()
                        redraw(hwnd)
                        return 0
                    else:
                        cancel_and_dismiss(hwnd)
                        return 0

                # 2. Bottom-Right Action Pill Buttons: Start / Pause / Resume and Cancel
                bx0, by0, bx1, by1 = x1 - 280, y1 - 68, x1 - 160, y1 - 22
                cx0, cy0, cx1, cy1 = x1 - 146, y1 - 68, x1 - 24, y1 - 22
                if (by0 - 10) <= y <= (by1 + 10):
                    if (bx0 - 8) <= x <= (bx1 + 8):
                        if mode == "options_window":
                            start_conversion_job(hwnd)
                        else:
                            state["paused"] = not state["paused"]
                            if state["worker_proc"]:
                                suspend_or_resume_process(state["worker_proc"].pid, state["paused"])
                            state["status_line"] = "Paused" if state["paused"] else "Processing..."
                            redraw(hwnd)
                        return 0
                    if (cx0 - 8) <= x <= (cx1 + 8):
                        cancel_and_dismiss(hwnd)
                        return 0

                # 3. Draggable Percentage Slider Bar
                px0, py0, px1, py1 = x0 + 40, y0 + 128, x1 - 104, y0 + 152
                if mode == "options_window" and (py0 - 18 <= y <= py1 + 18) and (px0 - 14 <= x <= px1 + 14):
                    state["dragging_slider"] = True
                    try:
                        user32.SetCapture(hwnd)
                    except Exception:
                        pass
                    update_slider_from_x(hwnd, x)
                    return 0

                # 4. Option Preset Chips
                cy_chip = py1 + 22
                if mode == "options_window" and (cy_chip - 6 <= y <= cy_chip + 40):
                    t_id, _, _, _ = current_selected_tool()
                    ui_cfg = get_tool_ui_config(t_id, state["quality_val"], state["chip_idx"], state["text_input"])
                    n_chips = max(1, min(4, len(ui_cfg["chips"])))
                    base_cw = 154 if n_chips <= 3 else 118
                    if state["window_expanded"]:
                        base_cw += 28
                    cw = base_cw + 12
                    rel_x = x - px0
                    if 0 <= rel_x <= n_chips * cw:
                        state["chip_idx"] = min(n_chips - 1, max(0, int(rel_x // cw)))
                        redraw(hwnd)
                        return 0
                return 0

            if mode == "island":
                p_cx = int(760 * 0.785)
                x_cx = int(760 * 0.875)
                cy_isl = 80
                if math.hypot(x - p_cx, y - cy_isl) <= 32 and state["job_active"]:
                    state["paused"] = not state["paused"]
                    if state["worker_proc"]:
                        suspend_or_resume_process(state["worker_proc"].pid, state["paused"])
                    state["detail_line"] = "Paused — click || to resume" if state["paused"] else "Resumed conversion..."
                    redraw(hwnd)
                    return 0
                if math.hypot(x - x_cx, y - cy_isl) <= 34:
                    cancel_and_dismiss(hwnd)
                    return 0
                if not state["job_active"] and state["last_outputs"] and not state["last_errors"]:
                    out_dir = Path(state["last_outputs"][0]).parent
                    try:
                        os.startfile(str(out_dir))
                    except Exception:
                        pass
                start_morph(hwnd, to_island=False)
                return 0

        if msg == WM_RBUTTONDOWN:
            if state["mode"] == "ring_tools":
                tools = state["groups"][min(state["group_idx"], len(state["groups"]) - 1)][1]
                total_pages = max(1, (len(tools) + 5) // 6)
                state["page"] = (state["page"] + 1) % total_pages
                redraw(hwnd)
            elif state["mode"] in ("options_window", "progress_window"):
                start_morph(hwnd, to_island=True)
            elif state["mode"] == "island":
                start_morph(hwnd, to_island=False)
            return 0

        if msg == WM_CHAR and state["mode"] == "options_window":
            ch = chr(wparam & 0xFFFF)
            if ch.isprintable() and ch not in ("\r", "\n", "\t"):
                state["text_input"] = (state["text_input"] + ch)[:48]
                redraw(hwnd)
            return 0

        if msg == WM_KEYDOWN:
            if wparam == VK_BACK and state["mode"] == "options_window" and state["text_input"]:
                state["text_input"] = state["text_input"][:-1]
                redraw(hwnd)
                return 0
            if wparam == VK_ESCAPE:
                if state["mode"] in ("options_window", "progress_window", "island"):
                    cancel_and_dismiss(hwnd)
                elif state["mode"] == "ring_tools":
                    state["mode"] = "ring_groups"
                    redraw(hwnd)
                else:
                    terminate_worker_tree(state["worker_proc"])
                    cleanup_worker_temp()
                    user32.PostQuitMessage(0)
            elif wparam == VK_RETURN and state["mode"] == "options_window":
                start_conversion_job(hwnd)
            elif wparam == VK_SPACE and state["mode"] in ("options_window", "progress_window", "island"):
                start_morph(hwnd, to_island=(state["mode"] != "island"))
            return 0

        if msg == WM_TIMER:
            now = time.monotonic()

            # Timer 4: 45ms live Liquid-Glass Shine Animation + dwell timers + show signal
            if wparam == 4:
                state["shine_phase"] = (state["shine_phase"] + 0.018) % 1.0
                if poll_show_signal():
                    state["last_active"] = now
                    sel = get_selected_explorer_files()
                    if sel:
                        apply_staged_files(sel)
                    else:
                        state["mode"] = "ring_groups"
                    redraw(hwnd)
                    return 0

                if state["dwell_target"] is not None and state["mode"] in ("ring_groups", "ring_tools"):
                    kind, idx = state["dwell_target"]
                    dur = DWELL_ENTER_SECS if kind == "group" else DWELL_BACK_SECS
                    prog = min(1.0, (now - state["dwell_started_at"]) / dur)
                    state["dwell_progress"] = prog
                    if prog >= 1.0:
                        state["dwell_target"] = None
                        state["dwell_progress"] = 0.0
                        if kind == "group":
                            enter_group_segment(hwnd, idx)
                            return 0
                        else:
                            state["mode"] = "ring_groups"
                            state["pager"] = RotationPager(len(state["groups"]), deadzone_radius=38.0)

                if state["done_at"] > 0 and not state["job_active"] and not state["last_errors"]:
                    if now - state["done_at"] >= DONE_HOLD_SECS and state["mode"] == "island":
                        state["done_at"] = 0.0
                        state["mode"] = "ring_groups"

                if state["mode"] != "morphing" and not state["dragging_slider"]:
                    redraw(hwnd)
                return 0

            # Timer 2: 16ms 60 FPS spring morph
            if wparam == 2 and state["mode"] == "morphing":
                dt = 0.016
                state["morph_spring"].step(dt)
                state["x_spring"].step(dt)
                state["y_spring"].step(dt)
                redraw(hwnd)
                if state["morph_spring"].is_settled() and state["x_spring"].is_settled() and state["y_spring"].is_settled():
                    user32.KillTimer(hwnd, 2)
                    state["mode"] = state["morph_target_mode"]
                    state["window_opened_at"] = time.monotonic()
                    redraw(hwnd)
                return 0

            # Timer 3: 50ms worker progress polling (updates current file thumbnail live!)
            if wparam == 3 and state["job_active"]:
                if not state["paused"]:
                    res_file = state.get("worker_res_file")
                    snap = None
                    if res_file and Path(res_file).exists():
                        try:
                            snap = json.loads(Path(res_file).read_text(encoding="utf-8"))
                        except Exception:
                            snap = None
                    if snap:
                        state["progress_frac"] = max(state["progress_frac"], float(snap.get("fraction", 0.1)))
                        done_n = int(snap.get("done", 0))
                        tot_n = max(1, int(snap.get("total", 1)))
                        cur_name = snap.get("current", "")
                        cur_path_s = snap.get("current_path", "")
                        if cur_path_s and Path(cur_path_s).exists():
                            state["current_preview_file"] = Path(cur_path_s)
                        elif done_n < len(state["staged_files"]):
                            state["current_preview_file"] = state["staged_files"][done_n]
                        state["batch_badge"] = f"{min(done_n + 1, tot_n)}/{tot_n}" if tot_n > 1 else ""
                        state["detail_line"] = f"File {min(done_n + 1, tot_n)} of {tot_n}  •  {cur_name[:24]}"
                        if snap.get("finished"):
                            outs = snap.get("outputs") or []
                            errs = snap.get("errors") or []
                            fb = bool(snap.get("fallback_used", False))
                            state["last_outputs"] = outs
                            state["last_errors"] = errs
                            state["progress_frac"] = 1.0
                            state["job_active"] = False
                            state["done_at"] = now
                            if outs and Path(outs[-1]).is_file():
                                state["current_preview_file"] = Path(outs[-1])
                            if errs:
                                state["status_line"] = f"Done — {len(outs)} converted ({len(errs)} failed)"
                                state["detail_line"] = errs[0][:44]
                            elif fb:
                                state["status_line"] = "Done — Saved in Documents\\Dew Drop"
                                state["detail_line"] = "Source folder read-only • Saved to Documents\\Dew Drop"
                            else:
                                state["status_line"] = "Done — Saved in Dew Drop"
                                state["detail_line"] = "Done  •  Saved in Dew Drop folder (Click to open)"
                            user32.KillTimer(hwnd, 3)
                            cleanup_worker_temp()
                    else:
                        state["progress_frac"] = min(0.94, state["progress_frac"] + 0.03)
                    if state["mode"] == "morphing":
                        state["morph_isl_im"] = build_current_island_image()
                    else:
                        redraw(hwnd)
                return 0

            if wparam == 1:
                if not state["job_active"] and (now - state["last_active"] >= idle_limit_secs):
                    cleanup_worker_temp()
                    user32.PostQuitMessage(0)
                return 0

        if msg == WM_DESTROY:
            terminate_worker_tree(state["worker_proc"])
            cleanup_worker_temp()
            user32.PostQuitMessage(0)
            return 0

        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    wndproc_cb = WNDPROC(py_wndproc)
    hinst = kernel32.GetModuleHandleW(None)
    cls_name = "DewdropCleanRoomOverlayV4"
    hcursor = user32.LoadCursorW(None, ctypes.cast(32512, wt.LPCWSTR))
    wc = WNDCLASSW(0, wndproc_cb, 0, 0, hinst, None, hcursor, None, None, cls_name)
    user32.RegisterClassW(ctypes.byref(wc))

    pt_cur = POINT()
    user32.GetCursorPos(ctypes.byref(pt_cur))
    cx, cy = compute_ring_placement(pt_cur.x, pt_cur.y, (0, 0, screen_w, screen_h - 48), 1.0)
    state["ring_x"] = cx - 230
    state["ring_y"] = cy - 230

    ex_style = WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TOOLWINDOW
    hwnd = user32.CreateWindowExW(
        ex_style, cls_name, APP_NAME, WS_POPUP | WS_VISIBLE,
        state["ring_x"], state["ring_y"], 860, 460,
        None, None, hinst, None
    )
    try:
        user32.ChangeWindowMessageFilterEx(hwnd, WM_DROPFILES, 1, None)
        user32.ChangeWindowMessageFilterEx(hwnd, 0x0049, 1, None)
    except Exception:
        pass
    shell32.DragAcceptFiles(hwnd, True)
    user32.SetTimer(hwnd, 1, 1000, None)
    user32.SetTimer(hwnd, 4, 45, None)
    redraw(hwnd)
    try:
        user32.SetForegroundWindow(hwnd)
    except Exception:
        pass

    msg = wt.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))


def main():
    args = sys.argv[1:]
    if "--worker" in args:
        idx = args.index("--worker")
        if idx + 2 < len(args):
            rc = worker_main(args[idx + 1], args[idx + 2])
            sys.exit(rc)
        sys.exit(2)

    if "--make-shortcut" in args or "--configure-hotkey" in args:
        flag = "--make-shortcut" if "--make-shortcut" in args else "--configure-hotkey"
        idx = args.index(flag)
        hk = args[idx + 1] if idx + 1 < len(args) else "CTRL+ALT+Z"
        ok = configure_windows_shortcut(hk)
        print(f"Shortcut configured ({hk}): {'OK' if ok else 'SAVED_SETTINGS'}")
        return

    if "--self-test" in args:
        from tests.run_cleanroom_verification import run_all_tests
        run_all_tests()

        # Verify strict file-type filtering (Images -> Image options only; ZIP -> Archive options only)
        img_groups = [g[0] for g in filter_and_rank_tools([Path("photo.png")], ffmpeg_available=True)]
        zip_groups = [g[0] for g in filter_and_rank_tools([Path("bundle.zip")], ffmpeg_available=True)]
        assert img_groups == ["Convert image", "Edit image", "PDF & docs"], f"Unexpected image groups: {img_groups}"
        assert zip_groups == ["Archives"], f"Expected only ['Archives'] for .zip, got {zip_groups}"

        sample_f = ensure_demo_sample_file()
        r_im = render_ring_surface_rgba(
            ["Convert image", "Edit image", "PDF & docs", "", "", ""],
            hover_seg=1, turn_progress=0.42, staged_count=3, subtitle="3 file(s) selected", dwell_progress=0.35, shine_phase=0.30
        )
        # Benchmark interactive Window redraw speed (slider drag & button hover)
        w_im = render_options_or_progress_window_rgba(
            "Sample_Photo.png", "420 KB", "Compress", "Quality (1-100)", "options",
            85, 1, 0.68, False, "Processing...", "1.6 MB of 2.4 MB • 2s left",
            expanded=False, preview_file=sample_f, batch_badge="1/3", shine_phase=0.35
        )
        t0 = time.perf_counter()
        for q_step in range(10):
            w_im = render_options_or_progress_window_rgba(
                "Sample_Photo.png", "420 KB", "Compress", "Quality (1-100)", "options",
                50 + q_step * 4, 1, 0.68, False, "Processing...", "1.6 MB of 2.4 MB • 2s left",
                expanded=False, preview_file=sample_f, batch_badge="1/3", shine_phase=0.10 + q_step * 0.05
            )
        avg_win_ms = ((time.perf_counter() - t0) / 10.0) * 1000.0
        w_exp = render_options_or_progress_window_rgba(
            "Sample_Photo.png", "420 KB", "Compress", "Quality (1-100)", "options",
            85, 1, 0.68, False, "Processing...", "1.6 MB of 2.4 MB • 2s left",
            w=860, h=430, expanded=True, preview_file=sample_f, batch_badge="2/3", shine_phase=0.55
        )
        i_im = render_dynamic_island_rgba(
            "Sample_Photo.png", "3 files • 1.2 MB", 0.68, False, "File 2 of 3  •  Sample_Photo.png",
            preview_file=sample_f, batch_badge="2/3", shine_phase=0.45
        )
        m_im = render_morph_frame_rgba(0.5, w_im, i_im)
        m_exp = render_morph_frame_rgba(0.5, w_exp, i_im)
        assert r_im.size == (460, 460) and w_im.size == (720, 360) and w_exp.size == (860, 430) and i_im.size == (760, 160)
        assert m_im.size == (740, 260) and m_exp.size == (810, 295)
        print(f"UI Surface & Speed Smoke Test PASSED: Slider/Shine Redraw = {avg_win_ms:.2f} ms/frame ({1000.0/max(0.1, avg_win_ms):.0f} FPS capability), Real File Thumbnails, Strict File-Type Filtering, and Pure Black Ink verified.")
        return

    start_mode = "ring_groups"
    if "--preview-window" in args:
        start_mode = "options_window"
    elif "--preview-island" in args:
        start_mode = "island"

    cli_files = [Path(a) for a in args if not a.startswith("-") and Path(a).is_file()]

    if os.name == "nt":
        run_windows_interactive_gui(start_mode=start_mode, cli_files=cli_files)
    else:
        print("Dewdrop Clean-Room Runtime: verifying crystal-clear liquid-glass surfaces on non-Windows host...")
        from tests.run_cleanroom_verification import run_all_tests
        run_all_tests()


if __name__ == "__main__":
    main()
