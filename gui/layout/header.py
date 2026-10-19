# gui/layout/header.py

from tkinter import ttk


class Header(ttk.Frame):
    """
    Layout component responsible for rendering
    the application header section.

    Contains:
    - Title
    - Subtitle
    - Separator

    This class has no business logic.
    """

    def __init__(
        self,
        parent,
        title: str = "ASI Automação",
        subtitle: str = "Testes Automatizados para o Sistema ASI"
    ):
        super().__init__(parent)

        self._build(title, subtitle)

    # ---------- Internal ----------

    def _build(self, title: str, subtitle: str):

        # Title
        title_label = ttk.Label(
            self,
            text=title,
            style="Main.Label"
        )
        title_label.pack(anchor="center")

        # Subtitle
        subtitle_label = ttk.Label(
            self,
            text=subtitle,
            font=("Segoe UI", 10),
            foreground="#777"
        )
        subtitle_label.pack(anchor="center", pady=(10, 0))

        # Separator
        ttk.Separator(self).pack(fill="x", pady=(5, 15))