"""Janela principal da GUI."""

from __future__ import annotations

import ctypes
import sys
import uuid
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from types import TracebackType
from tkinter import Event, Misc, messagebox
from typing import TYPE_CHECKING

import customtkinter as ctk

from gui_v2.components.sidebar import Sidebar
from gui_v2.controllers.demo_execution_controller import DemoExecutionController
from gui_v2.controllers.sentinel_controller import SentinelController
from gui_v2.pages.sentinel_page import SentinelPage
from gui_v2.pages.settings_page import SettingsPage
from gui_v2.services.configuration_service import ConfigurationService
from gui_v2.services.preferences_service import (
    LOG_LEVELS,
    GuiPreferences,
    PreferencesService,
)
from gui_v2.services.gui_error_service import GuiErrorService
from gui_v2.services.sentinel_command_service import SentinelCommandService
from gui_v2.theme import COLORS, apply_accent

if TYPE_CHECKING:
    from gui_v2.services.gui_error_service import GuiErrorLogSnapshot


ROOT = Path(__file__).resolve().parent.parent
APP_USER_MODEL_ID = "asi.automacao.gui_v2"

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        APP_USER_MODEL_ID
    )


_WM_SETREDRAW = 0x000B
_REDRAW_ALL = 0x0001 | 0x0004 | 0x0080 | 0x0100 | 0x0400
# RDW_INVALIDATE | RDW_ERASE | RDW_ALLCHILDREN | RDW_UPDATENOW | RDW_FRAME


def _apply_without_partial_repaint(window: ctk.CTk, change: Callable[[], None]) -> None:
    """Aplica uma mudança de layout ampla sem exibir a repintura parcial.

    O CTk redesenha cada widget no próprio canvas, um a um; quando a página
    inteira muda de largura (recolher a sidebar), o Windows mostraria estados
    intermediários. Congela apenas os dois painéis internos: enviar WM_SETREDRAW
    à janela principal a torna temporariamente invisível para a barra de tarefas.
    """
    if sys.platform != "win32":
        change()
        return
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.GetAncestor.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    user32.GetAncestor.restype = ctypes.c_void_p
    user32.SendMessageW.argtypes = [
        ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t
    ]
    user32.SendMessageW.restype = ctypes.c_ssize_t
    user32.RedrawWindow.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint
    ]
    user32.RedrawWindow.restype = ctypes.c_int
    window_handle = user32.GetAncestor(ctypes.c_void_p(window.winfo_id()), 2)  # GA_ROOT
    if not window_handle:
        change()
        return
    panel_handles = [window.sidebar.winfo_id(), window.content.winfo_id()]
    for handle in panel_handles:
        user32.SendMessageW(handle, _WM_SETREDRAW, 0, 0)
    try:
        change()
        window.update_idletasks()
    finally:
        for handle in panel_handles:
            user32.SendMessageW(handle, _WM_SETREDRAW, 1, 0)
        user32.RedrawWindow(window_handle, None, None, _REDRAW_ALL)


def _set_taskbar_identity(window: ctk.CTk, icon_path: Path) -> None:
    """Associa a janela ao ícone ASI usado pelo Shell na barra de tarefas."""
    if sys.platform != "win32":
        return

    class Guid(ctypes.Structure):
        _fields_ = [
            ("data1", ctypes.c_uint32),
            ("data2", ctypes.c_uint16),
            ("data3", ctypes.c_uint16),
            ("data4", ctypes.c_ubyte * 8),
        ]

    class PropertyKey(ctypes.Structure):
        _fields_ = [("format_id", Guid), ("property_id", ctypes.c_uint32)]

    class VariantValue(ctypes.Union):
        _fields_ = [("pointer", ctypes.c_void_p)]

    class PropVariant(ctypes.Structure):
        _anonymous_ = ("value",)
        _fields_ = [
            ("variant_type", ctypes.c_uint16),
            ("reserved1", ctypes.c_uint16),
            ("reserved2", ctypes.c_uint16),
            ("reserved3", ctypes.c_uint16),
            ("value", VariantValue),
        ]

    def guid(value: str) -> Guid:
        return Guid.from_buffer_copy(uuid.UUID(value).bytes_le)

    property_store = ctypes.c_void_p()
    vtable = None
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        get_ancestor = user32.GetAncestor
        get_ancestor.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        get_ancestor.restype = ctypes.c_void_p
        window_handle = get_ancestor(ctypes.c_void_p(window.winfo_id()), 2)  # GA_ROOT
        if not window_handle:
            return

        shell = ctypes.WinDLL("shell32", use_last_error=True)
        get_property_store = shell.SHGetPropertyStoreForWindow
        get_property_store.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(Guid),
            ctypes.POINTER(ctypes.c_void_p),
        ]
        get_property_store.restype = ctypes.c_long

        iid_property_store = guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99")
        result = get_property_store(
            ctypes.c_void_p(window_handle),
            ctypes.byref(iid_property_store),
            ctypes.byref(property_store),
        )
        if not property_store.value:
            return

        vtable = ctypes.cast(
            property_store, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))
        ).contents
        if result < 0:
            return
        # IPropertyStore: SetValue=6, Commit=7; IUnknown.Release=2.
        set_value = ctypes.WINFUNCTYPE(
            ctypes.c_long,
            ctypes.c_void_p,
            ctypes.POINTER(PropertyKey),
            ctypes.POINTER(PropVariant),
        )(vtable[6])
        commit = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p)(vtable[7])
        app_user_model_format = guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3")

        def set_string(key: PropertyKey, value: str) -> bool:
            text = ctypes.create_unicode_buffer(value)
            variant = PropVariant()
            variant.variant_type = 31  # VT_LPWSTR
            variant.pointer = ctypes.cast(text, ctypes.c_void_p)
            return (
                set_value(property_store, ctypes.byref(key), ctypes.byref(variant)) >= 0
            )

        icon_resource = f"{icon_path},0"
        icon_key = PropertyKey(app_user_model_format, 3)  # RelaunchIconResource
        app_id_key = PropertyKey(app_user_model_format, 5)  # AppUserModel.ID
        icon_set = set_string(icon_key, icon_resource)
        app_id_set = set_string(app_id_key, APP_USER_MODEL_ID)
        if icon_set or app_id_set:
            commit(property_store)
    except (AttributeError, OSError, TypeError, ValueError):
        return
    finally:
        if property_store.value and vtable is not None:
            release = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(vtable[2])
            release(property_store)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """Compõe a janela, a navegação e as páginas da GUI."""

    def __init__(self) -> None:
        gui_error_service = GuiErrorService()
        gui_error_service.configure()
        gui_error_service.install_global_exception_hooks()
        preferences_service = PreferencesService()
        preferences = preferences_service.load()
        current_theme = preferences.theme
        ctk.set_appearance_mode({"Sistema": "System", "Claro": "Light", "Escuro": "Dark"}[current_theme])
        super().__init__()
        self._gui_error_service = gui_error_service
        self._preferences_service = preferences_service
        self._preferences = preferences
        self._sentinel_ttl_days = (
            preferences.sentinel_ttl_days
            if preferences.sentinel_ttl_days is not None
            else SentinelCommandService.load_ttl_default()
        )
        self._theme = current_theme
        self._accent_id = preferences.accent_id
        apply_accent(self._accent_id)
        self._settings_initial_tab = "Geral"
        self._window_was_unmapped = False
        self._repaint_after_restore_id: str | None = None
        self._settings_page: SettingsPage | None = None
        self._pages: dict[str, ctk.CTkFrame] = {}
        self._gui_error_poll_id: str | None = None
        self.title("ASI Automação")
        self.geometry("1440x900")
        self.minsize(1024, 700)
        self.configure(fg_color=COLORS["page"])
        # Binds na raiz entram nas bindtags de todos os widgets filhos (centenas de
        # callbacks por troca de página); a tag própria restringe-os à janela.
        root_tag = "AsiAutomacaoRoot"
        self.bindtags((root_tag, *self.bindtags()))
        self.bind_class(root_tag, "<Unmap>", self._on_window_unmap, add="+")
        self.bind_class(root_tag, "<Map>", self._on_window_map, add="+")
        self.bind_class(root_tag, "<Configure>", self._resize_expanded_logs, add="+")
        self.protocol("WM_DELETE_WINDOW", self._request_close)
        self.after(50, lambda: self.state("zoomed"))

        icon_path = ROOT / "gui" / "app_icon.ico"
        if icon_path.exists():
            self.iconbitmap(icon_path)
            _set_taskbar_identity(self, icon_path)

        self.current_page = "Execução"
        configuration = ConfigurationService().load()  # lida uma vez para os dois controllers
        self.execution = DemoExecutionController(
            self,
            speed_ms=self._preferences.speed_ms,
            on_speed_changed=self._change_speed,
            get_log_level=lambda: self._preferences.log_level,
            get_browser_visible=lambda: self._preferences.browser_visible,
            get_full_output=lambda: self._preferences.full_output,
            on_full_output_changed=self._change_full_output,
            get_logs_expanded=lambda: self._preferences.logs_expanded,
            on_logs_expanded_changed=self._change_logs_expanded,
            can_start_execution=lambda: not self.sentinel.is_running,
            configuration=configuration,
        )
        self.sentinel = SentinelController(
            can_start_execution=lambda: not self.execution.is_running,
            ttl_days=self._sentinel_ttl_days,
            get_logs_expanded=lambda: self._preferences.sentinel_logs_expanded,
            on_logs_expanded_changed=self._change_sentinel_logs_expanded,
            configuration=configuration,
        )
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = Sidebar(
            self,
            on_page_selected=self._show_page,
            on_collapsed_changed=self._change_sidebar_collapsed,
            apply_layout_change=lambda change: _apply_without_partial_repaint(self, change),
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.set_collapsed(self._preferences.sidebar_collapsed)
        self.content = ctk.CTkFrame(self, fg_color=COLORS["page"])
        self.content.grid(row=0, column=1, sticky="nsew")
        self._show_page("Execução")
        self._update_gui_error_indicator()
        self._schedule_gui_error_poll()

    def _on_window_unmap(self, event: Event) -> None:
        """Registra quando a janela principal sai da área visível."""
        if event.widget is self:
            self._window_was_unmapped = True

    def _resize_expanded_logs(self, event: Event) -> None:
        """Mantém o painel ampliado proporcional à altura da janela."""
        if event.widget is self and hasattr(self, "execution"):
            if page := self.execution._active_page():
                page.log_panel.resize_expanded()
            if self.current_page == "Sentinela" and self.sentinel._page is not None:
                self.sentinel._page.resize_expanded_logs()

    def _on_window_map(self, event: Event) -> None:
        """Agenda a repintura da interface quando a janela volta a ficar visível."""
        if event.widget is not self or not self._window_was_unmapped:
            return

        self._window_was_unmapped = False
        if self._repaint_after_restore_id is not None:
            self.after_cancel(self._repaint_after_restore_id)
        self._repaint_after_restore_id = self.after(50, self._repaint_after_restore)

    def _repaint_after_restore(self) -> None:
        """Redesenha os widgets atuais sem recriar páginas ou alterar seu estado."""
        self._repaint_after_restore_id = None
        if not self.winfo_exists() or self.state() == "iconic":
            return

        for child in self.winfo_children():
            self._repaint_widget_tree(child)
        self.update_idletasks()

    @classmethod
    def _repaint_widget_tree(cls, widget: Misc) -> None:
        """Redesenha contêineres visuais e percorre apenas seus filhos compostos."""
        if isinstance(widget, ctk.CTkScrollableFrame):
            widget.configure(fg_color=widget.cget("fg_color"))
        elif isinstance(widget, ctk.CTkSegmentedButton):
            widget.configure(fg_color=widget.cget("fg_color"))
        elif isinstance(widget, (ctk.CTkFrame, ctk.CTkTabview, ctk.CTkTextbox)):
            widget.configure(require_redraw=True)

        for child in widget.winfo_children():
            if isinstance(
                child,
                (
                    ctk.CTkFrame,
                    ctk.CTkScrollableFrame,
                    ctk.CTkSegmentedButton,
                    ctk.CTkTabview,
                    ctk.CTkTextbox,
                ),
            ):
                cls._repaint_widget_tree(child)

    def _request_close(self) -> None:
        """Confirma o fechamento e aguarda as árvores de processo terminarem."""
        if self.execution.is_running or self.sentinel.is_running:
            process_name = (
                "as execuções da Sentinela"
                if self.sentinel.is_running
                else "o Pytest"
            )
            confirmar = messagebox.askyesno(
                "Execução em andamento",
                f"{process_name.capitalize()} está em execução. Deseja interromper e fechar?",
                parent=self,
            )
            if not confirmar:
                return
            if self.sentinel.is_running:
                stopped = self.sentinel.stop_all_and_wait(timeout=10.0)
            else:
                stopped = self.execution.stop_and_wait(timeout=10.0)
            if not stopped or self.execution.is_running or self.sentinel.is_running:
                messagebox.showwarning(
                    "Execução ainda ativa",
                    "A execução ainda está encerrando. Aguarde o término antes de fechar a janela.",
                    parent=self,
                )
                return
        if self._gui_error_poll_id is not None:
            try:
                self.after_cancel(self._gui_error_poll_id)
            except Exception:
                pass
            self._gui_error_poll_id = None
        self._gui_error_service.restore_global_exception_hooks()
        self.destroy()

    def report_callback_exception(
        self,
        exception_type: type[BaseException],
        exception: BaseException,
        traceback: TracebackType | None,
    ) -> None:
        """Registra erros de callbacks e preserva o tratamento padrão do Tk."""
        self._gui_error_service.log_uncaught_exception(
            "callback Tk", exception_type, exception, traceback
        )
        super().report_callback_exception(exception_type, exception, traceback)

    def _show_page(self, name: str) -> None:
        """Alterna páginas; Execução e Sentinela são criadas uma vez e só ocultadas."""
        self.current_page = name
        if name != "Configurações":
            self._settings_initial_tab = "Geral"
        self.sidebar.set_active(name)
        if self._settings_page is not None:
            self._settings_page.destroy()
            self._settings_page = None
        for page in self._pages.values():
            page.grid_remove()
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
        if name in ("Execução", "Sentinela"):
            page = self._pages.get(name)
            if page is None or not page.winfo_exists():
                controller = self.execution if name == "Execução" else self.sentinel
                page = controller.create_page(self.content)
                self._pages[name] = page
            if name == "Execução":
                page.log_panel.set_font_size(self._preferences.log_font_size)
            else:
                page.set_log_font_size(self._preferences.log_font_size)
            page.grid(row=0, column=0, sticky="nsew")
        else:
            self._settings_page = SettingsPage(
                self.content,
                on_theme_changed=self._change_theme,
                current_theme=self._theme,
                log_level=self._preferences.log_level,
                log_levels=LOG_LEVELS,
                log_font_size=self._preferences.log_font_size,
                full_output=self._preferences.full_output,
                browser_visible=self._preferences.browser_visible,
                sentinel_ttl_days=self._sentinel_ttl_days,
                on_log_level_changed=self._change_log_level,
                on_log_font_size_changed=self._change_log_font_size,
                on_full_output_changed=self._change_full_output,
                on_browser_visible_changed=self._change_browser_visible,
                on_sentinel_ttl_changed=self._change_sentinel_ttl,
                accent_id=self._accent_id,
                on_accent_changed=self._change_accent,
                gui_error_snapshot=self._gui_error_service.read(),
                on_refresh_gui_errors=self._gui_error_service.read,
                on_gui_errors_viewed=self._mark_gui_errors_viewed,
                on_clear_gui_errors=self._clear_gui_errors,
                initial_tab=self._settings_initial_tab,
            )
            self._settings_page.grid(row=0, column=0, sticky="nsew")

    def _mark_gui_errors_viewed(self, snapshot: GuiErrorLogSnapshot) -> None:
        """Persiste a assinatura consultada e atualiza o ponto da navegação."""
        self._gui_error_service.mark_viewed(snapshot)
        self._update_gui_error_indicator()

    def _clear_gui_errors(self) -> str | None:
        """Limpa os arquivos de diagnóstico e atualiza o indicador lateral."""
        error = self._gui_error_service.clear()
        if error is None:
            snapshot = self._gui_error_service.read()
            if not snapshot.available:
                return snapshot.error_message
            if not self._gui_error_service.mark_viewed(snapshot):
                return "O histórico foi limpo, mas não foi possível atualizar o indicador de erros."
            self._update_gui_error_indicator()
        return error

    def _update_gui_error_indicator(self) -> None:
        self.sidebar.set_error_indicator(self._gui_error_service.has_unseen_errors)

    def _schedule_gui_error_poll(self) -> None:
        self._gui_error_poll_id = self.after(1000, self._poll_gui_error_indicator)

    def _poll_gui_error_indicator(self) -> None:
        self._gui_error_poll_id = None
        if not self.winfo_exists():
            return
        if (
            self._gui_error_service.has_unseen_errors
            and self.current_page == "Configurações"
            and self._settings_page is not None
            and self._settings_page.current_tab == "Erros da GUI"
        ):
            self._settings_page.refresh_gui_errors(mark_viewed=True)
        self._update_gui_error_indicator()
        self._schedule_gui_error_poll()

    def _change_accent(self, accent_id: str, active_tab: str) -> None:
        """Aplica um preset durante a sessão e redesenha a página comum aberta."""
        if not apply_accent(accent_id):
            return
        self._accent_id = accent_id
        self._update_preferences(replace(self._preferences, accent_id=accent_id))
        self._settings_initial_tab = active_tab
        self.sidebar.refresh_accent()
        page_name = self.current_page
        # Páginas persistentes guardam as cores antigas; recria-as na próxima visita.
        for name in [name for name in self._pages if name != "Sentinela" or name != page_name]:
            self._pages.pop(name).destroy()
        if page_name != "Sentinela":
            self.after_idle(lambda: self._show_page(page_name))

    def _change_theme(self, value: str) -> None:
        theme_modes = {"Sistema": "System", "Claro": "Light", "Escuro": "Dark"}
        if value not in theme_modes:
            return
        ctk.set_appearance_mode(theme_modes[value])
        self._theme = value
        self._update_preferences(replace(self._preferences, theme=value))

    def _change_log_level(self, value: str) -> None:
        self._update_preferences(replace(self._preferences, log_level=value))

    def _change_log_font_size(self, value: int) -> None:
        if value == self._preferences.log_font_size:
            return
        self._update_preferences(replace(self._preferences, log_font_size=value))
        if page := self.execution._active_page():
            page.log_panel.set_font_size(value)
        if self.sentinel._page is not None and self.sentinel._page.winfo_exists():
            self.sentinel._page.set_log_font_size(value)
        if self._settings_page is not None and self._settings_page.winfo_exists():
            self._settings_page.set_log_font_size(value)

    def _change_speed(self, value: int) -> None:
        self._update_preferences(replace(self._preferences, speed_ms=value))

    def _change_full_output(self, value: bool) -> None:
        self._update_preferences(replace(self._preferences, full_output=value))
        self.execution.set_full_output(value)

    def _change_browser_visible(self, value: bool) -> None:
        self._update_preferences(replace(self._preferences, browser_visible=value))

    def _change_sentinel_ttl(self, value: int) -> None:
        if type(value) is not int or not 1 <= value <= 365:
            return
        self._sentinel_ttl_days = value
        self.sentinel.set_ttl_days(value)
        self._update_preferences(replace(self._preferences, sentinel_ttl_days=value))

    def _change_sidebar_collapsed(self, value: bool) -> None:
        self._update_preferences(replace(self._preferences, sidebar_collapsed=value))

    def _change_logs_expanded(self, value: bool) -> None:
        self._update_preferences(replace(self._preferences, logs_expanded=value))

    def _change_sentinel_logs_expanded(self, value: bool) -> None:
        self._update_preferences(replace(self._preferences, sentinel_logs_expanded=value))

    def _update_preferences(self, preferences: GuiPreferences) -> None:
        self._preferences = preferences
        try:
            self._preferences_service.save(preferences)
        except OSError as error:
            messagebox.showwarning(
                "Preferência não salva",
                f"A alteração foi aplicada, mas não foi possível salvar as preferências locais.\n\n{error}",
                parent=self,
            )


if __name__ == "__main__":
    App().mainloop()
