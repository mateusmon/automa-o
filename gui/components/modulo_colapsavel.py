import tkinter as tk
from tkinter import ttk


class ModuloColapsavel:

    def __init__(self, parent, title):

        self.container = ttk.Frame(parent)

        self.is_open = tk.BooleanVar(value=False) # Inicialmente fechado

        # Cabeçalho clicável para expandir/colapsar
        self.header = ttk.Button(
            self.container, 
            text=f"▶ {title}",
            cursor="hand2",
            style="Module.TButton",
            command=self.toggle,
            takefocus=False
        )
        self.header.pack(anchor="w", fill="x")

        # Frame para conteúdo, inicialmente invisível
        self.body = ttk.Frame(self.container)

    def toggle(self):

        if self.is_open.get():
            self.body.pack_forget()  # Esconde o conteúdo
            self.header.config(text=self.header["text"].replace("▼", "▶"))
            self.is_open.set(False)
        else:
            self.body.pack(anchor="w", fill="x", padx=15)  # Mostra o conteúdo
            self.header.config(text=self.header["text"].replace("▶", "▼"))
            self.is_open.set(True)
        
    def pack(self, **kwargs):
        self.container.pack(**kwargs)