"""Inicia um processo filho e publica sua saída numa fila para a UI."""

from __future__ import annotations

import queue
import os
import ctypes
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from collections.abc import Sequence
from typing import TextIO
from ctypes import wintypes

from gui_v2.models.execution import (
    ExecutionEvent,
    ExecutionEventLevel,
    ExecutionEventType,
)


_JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
_JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION = 1
_JOB_OBJECT_BASIC_PROCESS_ID_LIST = 3
_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
_JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
_CREATE_NEW_PROCESS_GROUP = 0x00000200


class _BasicAccountingInformation(ctypes.Structure):
    _fields_ = [
        ("TotalUserTime", ctypes.c_longlong),
        ("TotalKernelTime", ctypes.c_longlong),
        ("ThisPeriodTotalUserTime", ctypes.c_longlong),
        ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
        ("TotalPageFaultCount", wintypes.DWORD),
        ("TotalProcesses", wintypes.DWORD),
        ("ActiveProcesses", wintypes.DWORD),
        ("TotalTerminatedProcesses", wintypes.DWORD),
    ]


class _BasicProcessIdList(ctypes.Structure):
    _fields_ = [
        ("NumberOfAssignedProcesses", wintypes.DWORD),
        ("NumberOfProcessIdsInList", wintypes.DWORD),
        ("ProcessIdList", ctypes.c_size_t * 1),
    ]


class _ProcessMemoryCounters(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


@dataclass(frozen=True, slots=True)
class ProcessMetrics:
    """Amostra agregada do Job Object pertencente à execução."""

    process_count: int
    browser_count: int
    working_set_bytes: int
    cpu_percent: float | None
    cpu_time_seconds: float


def _job_process_ids(
    query_job, job, active_processes: int
) -> tuple[int, ...] | None:
    """Consulta a lista de PIDs do Job Object, repetindo se ela crescer."""
    capacity = max(1, active_processes)
    for _attempt in range(3):
        buffer_size = ctypes.sizeof(_BasicProcessIdList) + (
            capacity - 1
        ) * ctypes.sizeof(ctypes.c_size_t)
        buffer = ctypes.create_string_buffer(buffer_size)
        process_list = ctypes.cast(buffer, ctypes.POINTER(_BasicProcessIdList))
        if query_job(
            job, _JOB_OBJECT_BASIC_PROCESS_ID_LIST, buffer, buffer_size, None
        ):
            count = min(process_list.contents.NumberOfProcessIdsInList, capacity)
            if not count:
                return ()
            ids_type = ctypes.c_size_t * count
            ids = ctypes.cast(
                ctypes.addressof(process_list.contents.ProcessIdList),
                ctypes.POINTER(ids_type),
            ).contents
            return tuple(int(pid) for pid in ids)
        capacity = max(capacity * 2, capacity + 8)
    return None


class _BasicLimitInformation(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _IoCounters(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong),
    ]


class _ExtendedLimitInformation(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _BasicLimitInformation),
        ("IoInfo", _IoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


def _windows_kernel32():
    return ctypes.WinDLL("kernel32", use_last_error=True)


def _create_kill_on_close_job(process: subprocess.Popen[str]):
    """Põe o processo e seus descendentes em um Job Object próprio."""
    if os.name != "nt":
        return None
    kernel32 = _windows_kernel32()
    kernel32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        return None

    information = _ExtendedLimitInformation()
    information.BasicLimitInformation.LimitFlags = _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        wintypes.LPVOID,
        wintypes.DWORD,
    ]
    kernel32.SetInformationJobObject.restype = wintypes.BOOL
    configured = kernel32.SetInformationJobObject(
        job,
        _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
        ctypes.byref(information),
        ctypes.sizeof(information),
    )
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    assigned = configured and kernel32.AssignProcessToJobObject(
        job, wintypes.HANDLE(process._handle)
    )
    if not assigned:
        _close_job(job)
        return None
    return job


def _terminate_job(job, exit_code: int = 1) -> bool:
    if not job:
        return False
    kernel32 = _windows_kernel32()
    kernel32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel32.TerminateJobObject.restype = wintypes.BOOL
    return bool(kernel32.TerminateJobObject(job, exit_code))


def _send_ctrl_break(process: subprocess.Popen[str]) -> tuple[bool, str]:
    """Envia Ctrl+Break ao grupo privado da execução supervisionada."""
    if os.name != "nt":
        return False, "Ctrl+Break indisponível neste sistema."
    try:
        process.send_signal(signal.CTRL_BREAK_EVENT)
    except (OSError, ValueError) as error:
        return False, f"Ctrl+Break indisponível: {error}"
    return True, "Ctrl+Break enviado; aguardando encerramento gracioso."


def _close_job(job) -> None:
    if job:
        kernel32 = _windows_kernel32()
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle(job)


class ProcessSupervisor:
    """Lê stdout/stderr em threads e entrega saída e término por fila."""

    def __init__(self) -> None:
        self._process: subprocess.Popen[str] | None = None
        self._completed: threading.Event | None = None
        self._terminate_tree = False
        self._job_handle = None
        self._lock = threading.Lock()
        self._last_stop_mode: str | None = None
        self._last_stop_detail: str | None = None
        self._last_cpu_sample: tuple[float, float] | None = None

    def sample_metrics(self) -> ProcessMetrics | None:
        """Mede CPU, memória e navegadores apenas na árvore deste supervisor."""
        if os.name != "nt" or not self._job_handle:
            return None
        with self._lock:
            job = self._job_handle
            if not job:
                return None
            kernel32 = _windows_kernel32()
            query_job = kernel32.QueryInformationJobObject
            query_job.argtypes = [
                wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID,
                wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
            ]
            query_job.restype = wintypes.BOOL

            accounting = _BasicAccountingInformation()
            if not query_job(
                job, _JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION,
                ctypes.byref(accounting), ctypes.sizeof(accounting), None,
            ):
                return None

            pids = _job_process_ids(query_job, job, accounting.ActiveProcesses)
            if pids is None:
                return None

            kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            kernel32.OpenProcess.restype = wintypes.HANDLE
            kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            psapi.GetProcessMemoryInfo.argtypes = [
                wintypes.HANDLE, ctypes.POINTER(_ProcessMemoryCounters), wintypes.DWORD
            ]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
            kernel32.QueryFullProcessImageNameW.argtypes = [
                wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                ctypes.POINTER(wintypes.DWORD),
            ]
            kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL

            working_set = 0
            browser_count = 0
            for pid in pids:
                process = kernel32.OpenProcess(
                    _PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid)
                )
                if not process:
                    continue
                try:
                    counters = _ProcessMemoryCounters()
                    counters.cb = ctypes.sizeof(counters)
                    if psapi.GetProcessMemoryInfo(
                        process, ctypes.byref(counters), counters.cb
                    ):
                        working_set += counters.WorkingSetSize
                    image = ctypes.create_unicode_buffer(1024)
                    image_size = wintypes.DWORD(len(image))
                    if kernel32.QueryFullProcessImageNameW(
                        process, 0, image, ctypes.byref(image_size)
                    ) and image.value.rsplit("\\", 1)[-1].casefold() in {
                        "chrome.exe", "chromium.exe", "chrome-headless-shell.exe",
                        "msedge.exe",
                    }:
                        browser_count += 1
                finally:
                    kernel32.CloseHandle(process)

        cpu_time = (accounting.TotalUserTime + accounting.TotalKernelTime) / 10_000_000
        now = time.monotonic()
        cpu_percent = None
        if self._last_cpu_sample is not None:
            previous_time, previous_cpu = self._last_cpu_sample
            elapsed = now - previous_time
            if elapsed > 0:
                cpu_percent = max(0.0, (cpu_time - previous_cpu) / elapsed * 100)
        self._last_cpu_sample = (now, cpu_time)
        return ProcessMetrics(
            process_count=accounting.ActiveProcesses,
            browser_count=browser_count,
            working_set_bytes=working_set,
            cpu_percent=cpu_percent,
            cpu_time_seconds=cpu_time,
        )

    @property
    def last_stop_mode(self) -> str | None:
        """Modo usado no último pedido de parada: gracioso ou forçado."""
        return self._last_stop_mode

    @property
    def last_stop_detail(self) -> str | None:
        """Detalhe do último pedido de parada para diagnóstico/log da interface."""
        return self._last_stop_detail

    def start(
        self,
        command: Sequence[str],
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        terminate_tree: bool = False,
        execution_id: str | None = None,
    ) -> queue.Queue[ExecutionEvent]:
        """Inicia um comando e devolve a fila de eventos da execução."""
        if self._process is not None and not self._completed.is_set():
            raise RuntimeError("A execução supervisionada ainda não foi concluída.")
        if not command:
            raise ValueError("O comando não pode ser vazio.")

        creationflags = (
            _CREATE_NEW_PROCESS_GROUP
            if terminate_tree and os.name == "nt"
            else 0
        )
        process = subprocess.Popen(
            list(command),
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env=env,
            creationflags=creationflags,
        )
        events: queue.Queue[ExecutionEvent] = queue.Queue()
        self._process = process
        self._completed = threading.Event()
        self._terminate_tree = terminate_tree
        self._last_stop_mode = None
        self._last_stop_detail = None
        self._last_cpu_sample = None
        self._job_handle = (
            _create_kill_on_close_job(process)
            if terminate_tree and os.name == "nt"
            else None
        )
        readers = (
            threading.Thread(
                target=self._read_stream,
                args=(events, process.stdout, ExecutionEventType.STDOUT, execution_id),
                daemon=True,
            ),
            threading.Thread(
                target=self._read_stream,
                args=(events, process.stderr, ExecutionEventType.STDERR, execution_id),
                daemon=True,
            ),
        )
        for reader in readers:
            reader.start()
        threading.Thread(
            target=self._publish_exit,
            args=(process, events, readers, self._completed, execution_id),
            daemon=True,
        ).start()
        return events

    def wait(self, timeout: float | None = None) -> int | None:
        """Aguarda processo, leitura dos pipes e publicação do evento final."""
        if self._process is None or self._completed is None:
            return None
        if not self._completed.wait(timeout):
            raise subprocess.TimeoutExpired(self._process.args, timeout)
        return self._process.returncode

    def stop(self, timeout: float | None = None) -> int | None:
        """Solicita parada graciosa e força a árvore apenas após o prazo."""
        deadline = None if timeout is None else time.monotonic() + max(0.0, timeout)
        if self._process is None or self._completed is None:
            return None
        if not self._completed.is_set():
            if self._process.poll() is not None:
                self._last_stop_mode = "already_completed"
                remaining = None if deadline is None else max(0.0, deadline - time.monotonic())
                return self.wait(remaining)
            if self._terminate_tree and os.name == "nt":
                graceful_timeout = min(10.0, timeout) if timeout is not None else 10.0
                if self._process.poll() is None:
                    graceful_sent, self._last_stop_detail = _send_ctrl_break(self._process)
                else:
                    graceful_sent = False
                    self._last_stop_detail = "Processo principal já havia encerrado."
                completed_gracefully = (
                    graceful_sent and self._completed.wait(graceful_timeout)
                )
                self._last_stop_mode = "graceful" if completed_gracefully else "forced"
                if not completed_gracefully and graceful_sent:
                    self._last_stop_detail = "Prazo gracioso expirou; árvore encerrada à força."
                elif not completed_gracefully:
                    self._last_stop_detail = f"Parada forçada; {self._last_stop_detail}"
                if not completed_gracefully:
                    with self._lock:
                        job = self._job_handle
                        terminated = _terminate_job(job)
                    if not terminated and self._process.poll() is None:
                        subprocess.run(
                            ["taskkill", "/PID", str(self._process.pid), "/T", "/F"],
                            capture_output=True,
                            text=True,
                            check=False,
                        )
                    if self._process.poll() is None:
                        self._process.terminate()
            elif self._process.poll() is None:
                self._last_stop_mode = "forced"
                self._process.terminate()
        elif self._completed.is_set():
            self._last_stop_mode = "already_completed"
        remaining = None if deadline is None else max(0.0, deadline - time.monotonic())
        return self.wait(remaining)

    @staticmethod
    def _read_stream(
        events: queue.Queue[ExecutionEvent],
        stream: TextIO | None,
        event_type: ExecutionEventType,
        execution_id: str | None = None,
    ) -> None:
        """Publica linhas de um pipe e fecha o stream ao chegar ao EOF."""
        if stream is None:
            return
        with stream:
            for line in stream:
                events.put(
                    ExecutionEvent(
                        event_type=event_type,
                        level=(
                            ExecutionEventLevel.ERROR
                            if event_type is ExecutionEventType.STDERR
                            else ExecutionEventLevel.INFO
                        ),
                        message=line.rstrip("\r\n"),
                        execution_id=execution_id,
                    )
                )

    def _publish_exit(
        self,
        process: subprocess.Popen[str],
        events: queue.Queue[ExecutionEvent],
        readers: tuple[threading.Thread, threading.Thread],
        completed: threading.Event,
        execution_id: str | None = None,
    ) -> None:
        """Publica o código de saída após processo e pipes terem terminado."""
        return_code = process.wait()
        # Encerra descendentes antes de esperar EOF e liberar a vaga.
        with self._lock:
            job = self._job_handle
            self._job_handle = None
            _close_job(job)
        for reader in readers:
            reader.join()
        events.put(
            ExecutionEvent(
                event_type=ExecutionEventType.PROCESS_EXITED,
                level=(
                    ExecutionEventLevel.INFO
                    if return_code == 0
                    else ExecutionEventLevel.ERROR
                ),
                message="Processo encerrado.",
                return_code=return_code,
                execution_id=execution_id,
            )
        )
        completed.set()
