import tkinter as tk
from tkinter import ttk


class LogPanel(ttk.LabelFrame):
    """
    Widget responsável por exibir logs em tempo real.
    """

    def __init__(self, parent, lines_visible=10):
        super().__init__(
            parent,
            text="Painel de Logs",
            padding=(8, 4, 8, 8)
        )

        self.auto_scroll = True
        self._expanded = False
        self._height_normal = lines_visible * 25
        self._height_expanded = self._height_normal * 2

        self.configure(style="Log.TLabelframe")

        container = ttk.Frame(self, style="Log.TFrame")
        container.pack(fill="both", expand=True)

        self.configure(height=self._height_normal)
        self.pack_propagate(False)  # IMPORTANT

        # ---- BOTÃO DE EXPANSÃO ----
        self._toggle_btn = tk.Label(
            self,
            text="▲",
            font=("Segoe UI", 10),
            foreground="#972121",
            background="white",
            cursor="hand2",
        )
        self._toggle_btn.place(relx=1.0, rely=0.0, anchor="center", x=-8, y=-15)
        self._toggle_btn.bind("<Button-1>", lambda e: self._toggle_height())

        # ---- TEXT AREA ----
        self.text = tk.Text(
            container,
            wrap="word",
            height=lines_visible,
            state="disabled",
            bg="#F1F1F1",
            fg="black",
            insertbackground="black",
            font=("Consolas", 10),
            relief="flat",
            borderwidth=0,
            highlightthickness=0
        )

        self.text.tag_configure("INFO", foreground="#000000")
        self.text.tag_configure("SUCCESS", foreground="#0a7f2e")
        self.text.tag_configure("WARNING", foreground="#b36b00")
        self.text.tag_configure("ERROR", foreground="#c62828")
        self.text.tag_configure("DEBUG", foreground="#666666")
        self.text.tag_configure("TEST", foreground="#972121", font=("Consolas", 10, "bold"))

        self.text.bind("<MouseWheel>", lambda e: self._update_scroll_state())
        self.text.bind("<Button-4>", lambda e: self._update_scroll_state())  # Linux 
        self.text.bind("<Button-5>", lambda e: self._update_scroll_state())

        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self._on_user_scroll,
            style="Thin.Vertical.TScrollbar"
        )

        self.text.configure(yscrollcommand=scrollbar.set)

        self.text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _toggle_height(self):
        self._expanded = not self._expanded
        h = self._height_expanded if self._expanded else self._height_normal
        self._toggle_btn.configure(text="▼" if self._expanded else "▲")
        self.configure(height=h)

    def _on_user_scroll(self, *args):
        self.text.yview(*args)
        self._update_scroll_state()

    def _update_scroll_state(self):
        _, bottom = self.text.yview()

        # near bottom -> enable auto-scroll
        self.auto_scroll = bottom >= 0.999

    # ---------- PUBLIC API ----------

    def append(self, message: str, tag: str = "INFO"):

        self.text.configure(state="normal")

        self.text.insert("end", message + "\n", tag)

        # Only scroll if user didn't scroll away
        if self.auto_scroll:
            self.text.see("end")

        self.text.configure(state="disabled")


    def clear(self):
        """Limpa os logs."""
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")
