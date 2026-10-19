# gui/layout/modules_builder.py

import tkinter as tk
from datetime import datetime
from tkinter import ttk

from components.modulo_colapsavel import ModuloColapsavel
from components.tooltip import Tooltip
from loguru import logger


class ModulesBuilder(ttk.Frame):
    """
    Responsible for building the modules selection UI
    based on the MODULES catalog and test execution history.

    This class:
    - Renders modules, sections, and test checkboxes
    - Displays execution status icons (Pass, Fail, Skip, None)
    - Controls master checkbox behavior
    - Tracks selected test paths
    - Exposes public API to retrieve selected tests and update history
    """

    def __init__(self, parent, modules_catalog: dict, test_history: dict = None):
        """
        :param parent: Widget pai do Tkinter.
        :param modules_catalog: Dicionário contendo o catálogo de módulos e testes.
        :param test_history: Dicionário opcional contendo o histórico de resultados:
                             { "nodeid": {"resultado": "pass"|"fail"|"skip", "data": "..."}, ... }
        """
        super().__init__(parent)
        self.STATUS_SYMBOLS = {
        "pass": ("✔", "#2e7d32"),  # OK - Verde
        "fail": ("✖", "#c62828"),  # Fail - Vermelho
        "skip": ("⚠", "#ef6c00"),  # Skip - Laranja
        "none": ("•", "#9e9e9e")   # Não rodado / Sem histórico - Cinza
        }
        self._modules_catalog = modules_catalog
        self._test_history = test_history or {}
        self._checkboxes: list[tuple[tk.BooleanVar, str]] = []

        # Structure for filtering:
        # [
        #   {
        #     "colapsavel": ModuloColapsavel,
        #     "sections": [
        #       {
        #         "sep": widget | None,
        #         "title": widget,
        #         "master_chk": widget,
        #         "master_var": BooleanVar,
        #         "section_vars": [BooleanVar, ...],
        #         "items": [(container_frame, chk_widget, name, BooleanVar), ...]
        #       },
        #       ...
        #     ]
        #   },
        #   ...
        # ]
        self._structure: list[dict] = []
        self._pre_filter_state_saved = False
        self._saved_open_state: dict[int, bool] = {}

        # path -> (icon_label, tooltip), preenchido em _build(). Permite
        # atualizar o ícone/tooltip de um teste específico sem reconstruir
        # a árvore inteira (ver update_history).
        self._icon_refs: dict[str, tuple[ttk.Label, Tooltip]] = {}

        self._setup_symbol_styles()
        self._build()

    # ---------- Public API ----------

    def get_selected_tests(self) -> list[str]:
        """
        Returns a list of selected test file paths.
        """
        return [
            path
            for var, path in self._checkboxes
            if var.get()
        ]

    def clear_selection(self):
        """
        Uncheck all checkboxes.
        """
        for var, _ in self._checkboxes:
            var.set(False)

    def update_history(self, new_history: dict, changed_paths: list[str] | None = None):
        """
        Atualiza o dicionário de histórico de testes.

        Se `changed_paths` for informado, só o ícone e o tooltip dos testes
        dessa lista são atualizados no lugar — sem reconstruir a árvore,
        o que preserva a seleção atual de checkboxes, a posição do scroll,
        o filtro de busca e quais módulos estão abertos/fechados. É o caso
        normal depois de rodar testes: só quem rodou muda de status.

        Sem `changed_paths` (None), reconstrói a tela inteira — útil só se
        o histórico mudou de um jeito que não dá pra mapear pra paths
        específicos.
        """
        self._test_history = new_history or {}

        if changed_paths is None:
            self._build()
            return

        for path in changed_paths:
            self._atualizar_icone(path)

    def _atualizar_icone(self, path: str) -> None:
        """
        Atualiza o símbolo, estilo e tooltip do ícone já renderizado pra
        esse path, sem recriar nenhum widget. Não faz nada se o path não
        corresponde a nenhum item atualmente na tela (ex.: catálogo mudou).
        """
        referencia = self._icon_refs.get(path)
        if referencia is None:
            logger.debug("Path sem ícone renderizado, ignorando atualização: {}", path)
            return

        icon_label, tooltip = referencia
        symbol, style_name, tooltip_texto = self._get_status_display_data(path)

        icon_label.configure(text=symbol, style=style_name)
        tooltip.text = tooltip_texto

    # ---------- Internal ----------

    def _setup_symbol_styles(self):
        """
        Configura os estilos estéticos dos rótulos de status usando cores do ttk.
        """
        style = ttk.Style()
        style.configure("StatusPass.TLabel", foreground=self.STATUS_SYMBOLS["pass"][1], font=("Segoe UI", 10, "bold"))
        style.configure("StatusFail.TLabel", foreground=self.STATUS_SYMBOLS["fail"][1], font=("Segoe UI", 10, "bold"))
        style.configure("StatusSkip.TLabel", foreground=self.STATUS_SYMBOLS["skip"][1], font=("Segoe UI", 10, "bold"))
        style.configure("StatusNone.TLabel", foreground=self.STATUS_SYMBOLS["none"][1], font=("Segoe UI", 9))

    _ROTULOS_RESULTADO = {"pass": "Passou", "fail": "Falhou", "skip": "Pulado"}

    def _formatar_data(self, data_iso: str | None) -> str | None:
        """
        Converte a data ISO gravada pelo conftest.py (ex.: "2026-09-04T09:53:01.384883-03:00")
        num formato legível (ex.: "04/09/2026 às 09:53"). Se não der pra interpretar,
        devolve a string original em vez de quebrar o tooltip.
        """
        if not data_iso:
            return None

        try:
            dt = datetime.fromisoformat(data_iso)
            return dt.strftime("%d/%m/%Y às %H:%M")
        except ValueError:
            return data_iso

    def _get_status_display_data(self, test_path: str) -> tuple[str, str, str]:
        """
        Retorna (símbolo, nome_do_estilo, texto_do_tooltip) pro teste, com base
        no histórico de execução carregado.
        """
        test_info = self._test_history.get(test_path)

        if not test_info:
            return (
                self.STATUS_SYMBOLS["none"][0],
                "StatusNone.TLabel",
                "Ainda não foi executado neste cliente.",
            )

        status = test_info.get("resultado", "none")
        symbol = self.STATUS_SYMBOLS.get(status, self.STATUS_SYMBOLS["none"])[0]
        style_name = f"Status{status.capitalize()}.TLabel" if status in self.STATUS_SYMBOLS else "StatusNone.TLabel"

        rotulo = self._ROTULOS_RESULTADO.get(status, status)
        data_formatada = self._formatar_data(test_info.get("data"))
        tooltip_texto = f"{rotulo} em {data_formatada}" if data_formatada else rotulo

        return symbol, style_name, tooltip_texto

    def filter(self, query: str):
        """
        Show/hide tests, sections and modules based on query.
        Matching is case-insensitive substring search on test name.
        Empty query restores all items in original catalog order,
        preserving the open/closed state the user left each module in.
        """
        q = query.strip().lower()

        # Before the first filter call, snapshot the user's open/closed state
        # so we can restore it when the query is cleared.
        if q and not self._pre_filter_state_saved:
            self._saved_open_state = {
                id(entry["colapsavel"]): entry["colapsavel"].is_open.get()
                for entry in self._structure
            }
            self._pre_filter_state_saved = True

        for module_entry in self._structure:
            colapsavel = module_entry["colapsavel"]
            module_has_any = False

            for section_entry in module_entry["sections"]:
                section_has_any = False

                for container, chk, name, _ in section_entry["items"]:
                    visible = (not q) or (q in name.lower())

                    if visible:
                        container.grid()
                        section_has_any = True
                    else:
                        container.grid_remove()
                
                # Show/hide section header elements
                if section_has_any:
                    section_entry["title"].grid()
                    section_entry["master_chk"].grid()
                    if section_entry["sep"] is not None:
                        section_entry["sep"].grid()
                    module_has_any = True
                else:
                    section_entry["title"].grid_remove()
                    section_entry["master_chk"].grid_remove()
                    if section_entry["sep"] is not None:
                        section_entry["sep"].grid_remove()
                
                # Re-sync master checkbox with currently visible vars
                visible_vars = [
                    var
                    for _, _, name, var in section_entry["items"]
                    if (not q) or (q in name.lower())
                ]
                self._sync_section_master(
                    section_entry["master_var"],
                    visible_vars
                )
            
            if q:
                # While filtering: expand modules that have matches, collapse ones that don't.
                
                if module_has_any and not colapsavel.is_open.get() or not module_has_any and colapsavel.is_open.get():
                    colapsavel.toggle()
            else:
                # Query cleared: restore original order and saved open/closed state.
                # Re-pack in original order so pack() stacking is correct.
                colapsavel.container.pack_forget()
                colapsavel.container.pack(anchor="w", fill="x", pady=5)

                # Restore the open/closed state from before the search
                if self._pre_filter_state_saved:
                    was_open = self._saved_open_state.get(id(colapsavel), False)
                    if was_open != colapsavel.is_open.get():
                        colapsavel.toggle()
            
            # Show/hide the entire module container
            if q:
                if module_has_any:
                    colapsavel.container.pack(anchor="w", fill="x", pady=5)
                else:
                    colapsavel.container.pack_forget()
        
        # Reset saved state flag once query is cleared
        if not q:
            self._pre_filter_state_saved = False

    # --- Internal ---

    def _build(self):
        # Limpa widgets anteriores caso esteja reconstruindo via update_history
        for widget in self.winfo_children():
            widget.destroy()

        self._checkboxes.clear()
        self._structure.clear()
        self._icon_refs.clear()

        for module_name, module_data in self._modules_catalog.items():

            colapsavel = ModuloColapsavel(self, module_name)
            colapsavel.pack(anchor="w", fill="x", pady=5)

            sections = module_data.get("sections", {})
            section_list = list(sections.items())

            # Shared grid for all sections in this module
            # so columns are aligned across sections.
            shared_grid = ttk.Frame(colapsavel.body)
            shared_grid.pack(anchor="w", fill="x", padx=20)
            shared_grid.columnconfigure(0, weight=1, uniform="group1")
            shared_grid.columnconfigure(1, weight=1, uniform="group1")

            current_row = 0

            module_entry = {
                "colapsavel": colapsavel,
                "sections": []
            }

            for section_index, (section_name, tests) in enumerate(section_list):

                section_vars: list[tk.BooleanVar] = []
                master_var = tk.BooleanVar(value=False)

                # Separator between sections
                sep_widget = None
                if section_index > 0:
                    sep_widget = ttk.Separator(shared_grid, orient="horizontal")
                    sep_widget.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=(6, 0))
                    current_row += 1

                # Section title
                title_widget = ttk.Label(
                    shared_grid,
                    text=section_name,
                    style="Section.TLabel"
                )
                title_widget.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=(6, 0))
                current_row += 1

                # Master checkbox
                master_chk = ttk.Checkbutton(
                    shared_grid,
                    text="Marcar todos",
                    variable=master_var,
                    command=lambda m=master_var, v=section_vars: self._toggle_section(m, v),
                    takefocus=False
                )
                master_chk.grid(row=current_row, column=0, columnspan=2, sticky="w")
                current_row += 1

                # Individual test checkboxes — row by row across two columns
                valid_tests = [t for t in tests if self._validate_test_path(t)]

                section_entry = {
                    "sep": sep_widget,
                    "title": title_widget,
                    "master_chk": master_chk,
                    "master_var": master_var,
                    "section_vars": section_vars,
                    "items": []
                }

                for i, test in enumerate(valid_tests):
                    label = test["name"]
                    path = test["path"]

                    var = tk.BooleanVar()
                    section_vars.append(var)

                    col = i % 2
                    row = current_row + (i // 2)

                    # Sub-container horizontal para agrupar o ícone e o checkbutton do teste
                    test_item_container = ttk.Frame(shared_grid)
                    test_item_container.grid(row=row, column=col, sticky="w")

                    # Obtém símbolo unicode, estilo visual e texto do tooltip
                    symbol, style_name, tooltip_texto = self._get_status_display_data(path)

                    # Slot de largura FIXA em pixels pro ícone. pack_propagate(False)
                    # trava o tamanho do frame independente do glifo renderizado —
                    # isso evita que símbolos largos (ex.: "⚠") vazem visualmente
                    # por cima do checkbox ao lado.
                    icon_slot = ttk.Frame(
                        test_item_container,
                        width=22,
                        height=20,
                    )
                    icon_slot.pack(side="left", padx=(0, 4))
                    icon_slot.pack_propagate(False)

                    # Rótulo com o símbolo de status
                    icon_label = ttk.Label(
                        icon_slot,
                        text=symbol,
                        style=style_name,
                        anchor="center"
                    )
                    icon_label.pack(fill="both", expand=True)

                    tooltip = Tooltip(icon_label, tooltip_texto)
                    self._icon_refs[path] = (icon_label, tooltip)

                    # Caixa de seleção do teste
                    chk = ttk.Checkbutton(
                        test_item_container,
                        text=label,
                        variable=var,
                        command=lambda m=master_var, v=section_vars: self._sync_section_master(m, v),
                        takefocus=False
                    )
                    chk.pack(side="left", fill="x", expand=True)

                    self._checkboxes.append((var, path))
                    section_entry["items"].append((test_item_container, chk, label, var))

                # Advance current_row by the number of test rows used
                current_row += (len(valid_tests) + 1) // 2

                module_entry["sections"].append(section_entry)
            
            self._structure.append(module_entry)

    def _toggle_section(self, master_var, vars_list):
        value = master_var.get()

        for var in vars_list:
            var.set(value)

    def _sync_section_master(self, master_var, vars_list):
        master_var.set(
            all(var.get() for var in vars_list)
            if vars_list else False
        )

    def _validate_test_path(self, test_config: dict):
        path = test_config.get("path")

        if not path:
            logger.error(
                "Testes '{}' possui path vazio no modules_catalog.",
                test_config.get("name")
            )
            return False

        return True
