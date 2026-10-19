"""Ponto de entrada da nova GUI."""

try:
    from gui_v2.app import App
except ModuleNotFoundError:
    from app import App


if __name__ == "__main__":
    App().mainloop()
