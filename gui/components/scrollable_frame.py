import tkinter as tk
from tkinter import ttk


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Create canvas and vetical scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0, bg=ttk.Style().lookup("TFrame", "background"))
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        # Create the frame that will hold scrollable content
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Place the frame inside the canvas
        window_id = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        # Update width when canvas resizes
        def _on_canvas_configure(event):
            self.canvas.itemconfig(window_id, width=event.width)
        
        self.canvas.bind("<Configure>", _on_canvas_configure)

        # Update scrollregion
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._bind_mousewheel(self.canvas)
    
    def _bind_mousewheel(self, canvas):

        def _on_mousewheel(event):
            # Get mouse position relative to canvas
            x, y = canvas.winfo_pointerxy()
            widget = canvas.winfo_containing(x, y)

            # Scroll ONLY if cursor is inside canvas
            if widget is None:
                return
            
            if not str(widget).startswith(str(canvas)):
                return
            
            top, bottom = canvas.yview()

            if event.delta:
                direction = -1 if event.delta > 0 else 1
            elif event.num == 4:
                direction = -1
            elif event.num == 5:
                direction = 1
            else:
                return
            
            # Prevent overscroll
            if direction < 0 and top <= 0:
                return "break"
            
            if direction > 0 and bottom >= 1:
                return "break"
            
            canvas.yview_scroll(direction, "units")
            return "break"

        self.bind_all("<MouseWheel>", _on_mousewheel)
        self.bind_all("<Button-4>", _on_mousewheel)
        self.bind_all("<Button-5>", _on_mousewheel)
