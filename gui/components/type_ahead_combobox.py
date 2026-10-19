from tkinter import ttk


class TypeAheadCombobox(ttk.Combobox):
    """
    Combobox com busca rápida por digitação (type-ahead) inteligente.
    Permite digitar as iniciais/letras do item em modo readonly,
    selecionando automaticamente o item correspondente e disparando <<ComboboxSelected>>.
    Funciona tanto com o combobox focado quanto com a lista suspensa (popdown) aberta.
    """

    def __init__(self, master=None, timeout_ms: int = 1200, **kwargs):
        super().__init__(master, **kwargs)
        self._buffer: str = ""
        self._after_id: str | None = None
        self._timeout_ms: int = timeout_ms

        self.bind("<KeyPress>", self._on_combobox_key, add="+")
        self.bind("<FocusOut>", self._on_focus_out, add="+")
        self._bind_popdown_events()

    def _normalize(self, text: str) -> str:
        return (
            str(text)
            .lower()
            .replace("-", "")
            .replace("_", "")
            .replace(" ", "")
            .replace("/", "")
            .replace(".", "")
        )

    def _find_match(self, query: str) -> str | None:
        values = list(self["values"])
        if not values or not query:
            return None

        q_lower = query.lower()
        q_norm = self._normalize(query)

        # 1. Correspondência direta por prefixo (case-insensitive)
        for v in values:
            if str(v).lower().startswith(q_lower):
                return str(v)

        # 2. Correspondência por prefixo normalizado (ignora traços, espaços, pontos, etc.)
        for v in values:
            if self._normalize(str(v)).startswith(q_norm):
                return str(v)

        # 3. Correspondência por substring normalizada (fallback)
        for v in values:
            if q_norm in self._normalize(str(v)):
                return str(v)

        return None

    def _reset_buffer(self):
        self._buffer = ""
        self._after_id = None

    def _on_focus_out(self, event):
        self._reset_buffer()

    def _bind_popdown_events(self):
        """Conecta eventos de teclado à janela popdown (dropdown listbox) via comando registrado no Tcl."""
        try:
            popdown = self.tk.eval(f"ttk::combobox::PopdownWindow {self}")
            listbox_name = f"{popdown}.f.l"
            cmd_name = self.register(self._on_popdown_key)
            self.tk.call(
                "bind",
                listbox_name,
                "<KeyPress>",
                f"if {{[{cmd_name} %K %A] eq {{break}}}} break",
            )
        except Exception:
            pass

    def _sync_popdown_selection(self, selected_value: str):
        """Atualiza a seleção visual na listbox do popdown se estiver visível."""
        try:
            values = list(self["values"])
            if selected_value in values:
                index = values.index(selected_value)
                popdown = self.tk.eval(f"ttk::combobox::PopdownWindow {self}")
                listbox_name = f"{popdown}.f.l"
                exists = str(self.tk.call("winfo", "exists", listbox_name))
                if exists in ("1", "true"):
                    self.tk.call(listbox_name, "selection", "clear", 0, "end")
                    self.tk.call(listbox_name, "selection", "set", index)
                    self.tk.call(listbox_name, "activate", index)
                    self.tk.call(listbox_name, "see", index)
        except Exception:
            pass

    def _select_and_notify(self, match: str):
        current_val = self.get()
        if current_val != match:
            self.set(match)
            self._sync_popdown_selection(match)
            self.event_generate("<<ComboboxSelected>>")
        else:
            self._sync_popdown_selection(match)

    def _handle_key_input(self, keysym: str, char: str) -> str:
        if str(self.cget("state")) == "disabled":
            return ""

        if keysym in ("Escape", "Tab", "Return", "Up", "Down", "Prior", "Next"):
            self._reset_buffer()
            return ""

        if keysym == "BackSpace":
            if self._buffer:
                self._buffer = self._buffer[:-1]
                if self._buffer:
                    match = self._find_match(self._buffer)
                    if match:
                        self._select_and_notify(match)
            return "break"

        if not char or not char.isprintable() or char in ("\x00", "\r", "\n", "\t"):
            return ""

        # Agenda reset do buffer após _timeout_ms de inatividade
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(self._timeout_ms, self._reset_buffer)

        new_buffer = self._buffer + char
        match = self._find_match(new_buffer)

        if match:
            self._buffer = new_buffer
            self._select_and_notify(match)
            return "break"
        else:
            # Se o buffer acumulado não bater com nada, tenta char avulso como início de nova busca
            single_match = self._find_match(char)
            if single_match:
                self._buffer = char
                self._select_and_notify(single_match)
                return "break"

        return "break"

    def _on_combobox_key(self, event):
        return self._handle_key_input(event.keysym, event.char)

    def _on_popdown_key(self, keysym: str, char: str) -> str:
        return self._handle_key_input(keysym, char)
