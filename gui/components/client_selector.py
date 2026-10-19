import tkinter as tk
from tkinter import ttk

try:
    from components.type_ahead_combobox import TypeAheadCombobox
except ImportError:
    from gui.components.type_ahead_combobox import TypeAheadCombobox


# Mapeamento exibição → valor real em ms (espelhado no conftest.py)
VELOCIDADE_OPTIONS = {
    "Rápido": 0,
    "Médio": 750,
    "Lento": 1500,
}


class ClientSelector(ttk.Frame):
    def __init__(self, parent, client_labels: list[str], default_label: str | None = None):
        super().__init__(parent)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0, minsize=90)

        self._original_url = ""
        self._on_save_callback = None
        
        self._build_client_row(client_labels, default_label)
        self._build_ambiente_row()
        self._build_url_row()
        self._build_velocidade_row()
        self._build_save_button()


    # ----- UI -----
    def _build_client_row(self, client_labels, default_label):
        ttk.Label(self, text="Cliente:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )

        self.client_var = tk.StringVar()

        self.client_combo = TypeAheadCombobox(
            self,
            textvariable=self.client_var,
            state="readonly",
            values=client_labels,
        )

        self.client_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        if default_label and default_label in client_labels:
            self.client_combo.set(default_label)
        elif client_labels:
            self.client_combo.current(0)

        self.client_combo.bind("<<ComboboxSelected>>", self._remove_focus)


    def _build_ambiente_row(self):
        ttk.Label(self, text="Ambiente:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        
        self.ambiente_var = tk.StringVar()

        self.ambiente_combo = ttk.Combobox(
            self,
            textvariable=self.ambiente_var,
            state="disabled",
            values=[] # App will populate it
        )

        self.ambiente_combo.grid(row=1, column=1, padx=5, sticky="ew")

        self.ambiente_combo.bind("<<ComboboxSelected>>", self._remove_focus)
    

    def _build_url_row(self):
        ttk.Label(self, text="URL:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )

        self.url_var = tk.StringVar()
        self.url_var.trace_add("write", self._on_url_changed)

        self.url_entry = ttk.Entry(
            self,
            textvariable=self.url_var,
        )

        self.url_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.url_entry.configure(font=("Consolas", 10))


    def _build_velocidade_row(self):
        ttk.Label(self, text="Velocidade:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )

        self.velocidade_var = tk.StringVar(value="Rápido")

        self.velocidade_combo = ttk.Combobox(
            self,
            textvariable=self.velocidade_var,
            state="readonly",
            values=list(VELOCIDADE_OPTIONS.keys()),
            width=12,
        )

        self.velocidade_combo.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.velocidade_combo.bind("<<ComboboxSelected>>", self._remove_focus)


    def _build_save_button(self):
        self.save_container = ttk.Frame(self)
        self.save_container.grid(row=2, column=2, padx=5)

        self.save_button = ttk.Button(
            self.save_container,
            text="Salvar",
            command=self._handle_save
        )

        self.save_button.pack_forget()


    # ----- INTERNAL -----
    def _remove_focus(self, event):
        self.focus_set()
    
    def _on_url_changed(self, *args):
        current = self.url_var.get()

        if current != self._original_url:
            self.save_button.pack()
        else:
            self.save_button.pack_forget()
    
    def _handle_save(self):
        if not self._on_save_callback:
            return 
        
        success = self._on_save_callback(
            self.get_client(),
            self.get_url()
        )

        if success:
            self._original_url = self.get_url()
            self.save_button.pack_forget()

    # -------- PUBLIC API --------

    def get_client(self):
        return self.client_var.get()

    def get_url(self):
        return self.url_var.get()
    
    def get_slow_mo(self) -> int:
        """Retorna o valor de slow_mo em ms conforme a velocidade selecionada."""
        label = self.velocidade_var.get()
        return VELOCIDADE_OPTIONS.get(label, 0)
    
    def get_ambiente(self):
        display_value = self.ambiente_var.get()
        return self._ambiente_display_map.get(display_value)
    
    def set_ambientes(self, ambientes: list[str], default: str | None = None):
        # Mapping for display
        self._ambiente_display_map = {
            ambiente.upper(): ambiente
            for ambiente in ambientes
        }

        display_values = list(self._ambiente_display_map.keys())

        self.ambiente_combo["values"] = display_values

        if default and default in ambientes:
            display_default = default.upper()
        elif display_values:
            display_default = display_values[0]
        else:
            display_default = ""
        
        if display_default:
            self.ambiente_combo.set(display_default)
    

    def set_url(self, url: str):
        self._original_url = url
        self.url_var.set(url)
        self.save_button.pack_forget()
    
    def set_on_save_callback(self, callback):
        self._on_save_callback = callback

    def set_enabled(self, enabled: bool):
        state = "readonly" if enabled else "disabled"

        self.client_combo.configure(state=state)
        #self.ambiente_combo.configure(state=state)

        # URL field behaves differently (Entry uses normal/disabled)
        self.url_entry.configure(state="normal" if enabled else "disabled")

        self.velocidade_combo.configure(state=state)

        # Hide save button while disabled
        if not enabled:
            self.save_button.pack_forget()
        else:
            # Re-evaluate if save button should appear
            self._on_url_changed()
