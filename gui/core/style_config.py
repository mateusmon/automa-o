from tkinter import ttk

def configure_style():
    """
    Configures ttk styles for the entire application.
    Must be called after Tk root is initialized.
    """

    style = ttk.Style()

    style.configure(
        "Main.Label",
        font=("Segoe UI", 20, "bold"),
        foreground="#972121",
        background="white"
    )

    style.configure(
        "TFrame",
        background="white"
    )

    style.configure(
        "TLabel",
        background="white"
    )

    style.configure(
        "Module.TLabel",
        font=("Segoe UI", 15, "bold"),
        foreground="#972121",
    )

    style.configure(
        "Module.TButton",
        background="white",
        font=("Segoe UI", 15, "bold"),
        foreground="#972121",
        anchor="w"
    )

    style.configure(
        "Section.TLabel",
        font=("Segoe UI", 12, "bold")
    )

    style.configure(
        "TCheckbutton",
        background="white"
    )

    style.configure(
        "TButton",
        background="white"
    )

    # Log Panel
    style.configure(
        "TLabelframe.Label",
        font=("Segoe UI", 10, "bold"),
        foreground="#972121",
        background="white"
    )

    style.configure(
        "Log.TLabelframe",
        background="white"
    )

    style.configure(
        "Log.TLabelframe.Label",
        background="white",
        foreground="#972121",
        font=("Segoe UI", 10, "bold")
    )

    style.configure(
        "Log.TFrame",
        background="white"
    )

    # Thin scrollbar
    style.layout(
        "Thin.Vertical.TScrollbar",
        [
            ("Vertical.Scrollbar.trough",
             {"children": [
                 ("Vertical.Scrollbar.thumb",
                  {"expand": "1", "sticky": "nswe"})
             ],
             "sticky": "ns"})
        ],
    )

    style.configure(
        "Thin.Vertical.TScrollbar",
        gripcount=0,
        background="#f3f3f3",
        troughcolor="#f5f5f5",
        borderwidth=0,
        arrowsize=10,
        width=8,
    )