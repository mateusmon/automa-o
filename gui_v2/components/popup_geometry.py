"""Calcula posição de popups flutuantes em relação ao monitor proprietário."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from tkinter import Misc


@dataclass(frozen=True)
class PopupPosition:
    """Posição global do popup e lado escolhido para abertura."""

    x: int
    y: int
    above: bool
    width: int
    height: int


class _Rect(ctypes.Structure):
    _fields_ = (
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    )


class _MonitorInfo(ctypes.Structure):
    _fields_ = (
        ("size", wintypes.DWORD),
        ("monitor", _Rect),
        ("work", _Rect),
        ("flags", wintypes.DWORD),
    )


def _work_area(widget: Misc) -> tuple[int, int, int, int]:
    """Retorna a área útil do monitor da janela, ou a área virtual do Tk."""
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        monitor_from_window = user32.MonitorFromWindow
        monitor_from_window.argtypes = (wintypes.HWND, wintypes.DWORD)
        monitor_from_window.restype = wintypes.HANDLE
        get_monitor_info = user32.GetMonitorInfoW
        get_monitor_info.argtypes = (wintypes.HANDLE, ctypes.POINTER(_MonitorInfo))
        get_monitor_info.restype = wintypes.BOOL

        owner = widget.winfo_toplevel()
        monitor = monitor_from_window(wintypes.HWND(owner.winfo_id()), 2)
        info = _MonitorInfo()
        info.size = ctypes.sizeof(info)
        if monitor and get_monitor_info(monitor, ctypes.byref(info)):
            area = info.work
            return area.left, area.top, area.right, area.bottom
    except (AttributeError, OSError, TypeError, ValueError, ctypes.ArgumentError):
        pass

    left = widget.winfo_vrootx()
    top = widget.winfo_vrooty()
    return (
        left,
        top,
        left + widget.winfo_vrootwidth(),
        top + widget.winfo_vrootheight(),
    )


def position_popup(widget: Misc, width: int, height: int) -> PopupPosition:
    """Ancora o popup ao seletor e limita-o à área útil do monitor correto."""
    left, top, right, bottom = _work_area(widget)
    width = min(width, max(1, right - left))
    height = min(height, max(1, bottom - top))

    anchor_x = widget.winfo_rootx()
    anchor_top = widget.winfo_rooty()
    anchor_bottom = anchor_top + widget.winfo_height()
    x = min(max(anchor_x, left), right - width)

    fits_below = anchor_bottom + height <= bottom
    fits_above = anchor_top - height >= top
    above = not fits_below and fits_above
    if above:
        y = anchor_top - height
    elif fits_below:
        y = anchor_bottom
    else:
        y = min(max(anchor_bottom, top), bottom - height)
    return PopupPosition(x=x, y=y, above=above, width=width, height=height)
