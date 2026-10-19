"""Rolagem dos resultados compartilhada pelos seletores pesquisáveis."""

import customtkinter as ctk
from gui_v2.components.smart_scrollable_frame import SmartScrollableFrame


class PickerResults(SmartScrollableFrame):
    """Mantém o destaque do teclado visível sem deslocar o foco da busca."""

    def reveal(self, index: int) -> None:
        """Rola somente o necessário para mostrar a linha indicada."""
        self.update_idletasks()
        rows = self.winfo_children()
        if not 0 <= index < len(rows):
            return
        canvas = self._parent_canvas
        bounds = canvas.bbox("all")
        if not bounds or bounds[3] <= bounds[1]:
            return
        row = rows[index]
        top = row.winfo_y()
        bottom = top + row.winfo_height()
        visible_top = canvas.canvasy(0)
        visible_height = canvas.winfo_height()
        if top < visible_top:
            canvas.yview_moveto(top / (bounds[3] - bounds[1]))
        elif bottom > visible_top + visible_height:
            canvas.yview_moveto((bottom - visible_height) / (bounds[3] - bounds[1]))

    def reset_scroll(self) -> None:
        """Volta ao começo quando a pesquisa substitui os resultados."""
        self._parent_canvas.yview_moveto(0)
