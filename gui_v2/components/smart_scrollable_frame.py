"""Rolagem coerente para áreas aninhadas da GUI v2."""

from __future__ import annotations

import sys
from tkinter import Event, Misc
from weakref import ReferenceType, WeakSet, ref

import customtkinter as ctk

WINDOWS_SCROLL_INCREMENT = 4


class _WheelRoute:
    """Compartilha o destino da roda entre os frames de uma mesma janela."""

    def __init__(self, root: Misc) -> None:
        self.root: ReferenceType[Misc] = ref(root)
        self.frames: WeakSet[SmartScrollableFrame] = WeakSet()
        self.scrollbar_canvases: WeakSet[Misc] = WeakSet()
        self.pointer: tuple[int, int] | None = None
        self.owner: ReferenceType[SmartScrollableFrame] | None = None

    def target_for(self, event: Event) -> SmartScrollableFrame | None:
        """Mantém o alvo até o ponteiro mudar de posição na tela."""
        if event.widget.winfo_toplevel() is not self.root():
            return None
        pointer = (event.x_root, event.y_root)
        owner = self.owner() if self.owner is not None else None
        if (
            pointer != self.pointer
            or owner is None
            or not owner.winfo_exists()
            or not owner.winfo_ismapped()
        ):
            self.pointer = pointer
            owner = self._nearest_frame(event.widget)
            self.owner = ref(owner) if owner is not None else None
        return owner

    def _nearest_frame(self, widget: Misc) -> SmartScrollableFrame | None:
        """Encontra o canvas, a barra ou o conteúdo rolável mais próximo do evento."""
        current: Misc | None = widget
        while current is not None:
            for frame in tuple(self.frames):
                if current in (frame, frame._parent_canvas, frame._scrollbar, frame._scrollbar._canvas):
                    return frame
            if isinstance(current, (ctk.CTkTextbox, ctk.CTkSlider)):
                return None
            current = current.master
        return None


class SmartScrollableFrame(ctk.CTkScrollableFrame):
    """Aplica a mesma velocidade na barra e no conteúdo e estabiliza o alvo da roda."""

    def __init__(self, master: Misc, **kwargs: object) -> None:
        super().__init__(master, **kwargs)
        root = self.winfo_toplevel()
        route = getattr(root, "_asi_wheel_route", None)
        if route is None:
            route = _WheelRoute(root)
            setattr(root, "_asi_wheel_route", route)
        self._wheel_route: _WheelRoute = route
        route.frames.add(self)
        route.scrollbar_canvases.add(self._scrollbar._canvas)

        # A barra do CustomTkinter usa delta/40, enquanto o frame usa delta/6.
        # Substituir apenas o binding da barra deste frame também evita que ela
        # role o quadro errado durante uma sequência iniciada em outro quadro.
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self._scrollbar._canvas.bind(sequence, self._scrollbar_wheel)

    def _mouse_wheel_all(self, event: Event) -> None:
        """Rola somente o destino escolhido para esta sequência da roda."""
        if event.widget in self._wheel_route.scrollbar_canvases:
            return
        if self._wheel_route.target_for(event) is self:
            self._scroll_wheel(event)

    def _scrollbar_wheel(self, event: Event) -> None:
        """Rola uma vez e deixa outros bindings globais observarem o evento."""
        target = self._wheel_route.target_for(event)
        if target is not None:
            target._scroll_wheel(event)

    def protect_textbox(self, textbox: ctk.CTkTextbox) -> None:
        """Mantém a origem da roda quando uma caixa de texto passa sob o ponteiro."""
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            textbox._textbox.bind(sequence, self._textbox_wheel, add="+")
            scrollbar = textbox._y_scrollbar
            scrollbar._canvas.bind(
                sequence,
                lambda event, bar=scrollbar: self._textbox_scrollbar_wheel(event, bar),
            )
        self._wheel_route.scrollbar_canvases.add(textbox._y_scrollbar._canvas)

    def _textbox_wheel(self, event: Event) -> str | None:
        """Bloqueia a rolagem nativa do texto se a sequência pertence ao quadro."""
        target = self._wheel_route.target_for(event)
        if target is None:
            return None
        target._scroll_wheel(event)
        return "break"

    def _textbox_scrollbar_wheel(self, event: Event, scrollbar: ctk.CTkScrollbar) -> None:
        """Preserva a barra do texto quando ele é o alvo da roda."""
        target = self._wheel_route.target_for(event)
        if target is None:
            scrollbar._mouse_scroll_event(event)
        else:
            target._scroll_wheel(event)

    def _scroll_wheel(self, event: Event) -> None:
        """Preserva a conversão de roda do CTkScrollableFrame em cada plataforma."""
        canvas = self._parent_canvas
        if self._shift_pressed:
            if canvas.xview() == (0.0, 1.0):
                return
            scroll = canvas.xview_scroll
        else:
            if canvas.yview() == (0.0, 1.0):
                return
            scroll = canvas.yview_scroll

        if sys.platform.startswith("win"):
            units = -int(event.delta / 6)
        elif sys.platform == "darwin":
            units = -event.delta
        else:
            units = -1 if event.num == 4 else 1
        scroll(units, "units")
