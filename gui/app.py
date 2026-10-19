import ctypes  # somente para mostrar o ícone do ASI na barra de tarefas
import json
import os
import queue
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from catalog.modules_catalog import MODULES
from components.client_selector import ClientSelector
from components.log_panel import LogPanel
from components.scrollable_frame import ScrollableFrame
from core.genesis_runner import GenesisRunner
from core.gui_log_sink import GuiLogSink
from core.module_filter import filtrar_modulos_por_cliente
from core.style_config import configure_style
from core.test_runner import TestRunner
from layout.header import Header
from layout.modules_builder import ModulesBuilder
from loguru import logger
from services.config_services import ConfigService

# Somente para mostrar o ícone do ASI na barra de tarefas
APP_ID = "grp.testlauncher"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

# fail sobrepõe skip, que sobrepõe pass — usado ao agregar múltiplos
# testes do mesmo arquivo em um único status.
_SEVERIDADE_RESULTADO = {"pass": 0, "skip": 1, "fail": 2}


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.iconbitmap("gui/app_icon.ico")
        self.title("ASI Automação 2.0")

        # Configura a cor de fundo da janela principal para branco
        self.configure(bg="white")

        # Tamanho preferível de janela
        self.geometry("1000x700")

        # Tamanho mínimo da janela
        self.minsize(800, 500)

        # Permite o tkinter registrar tamanho preferível da janela
        self.update_idletasks()

        # Inicia o programa em tela cheia
        try:
            self.state("zoomed") # Windows
        except tk.TclError:
            self.attributes("-zoomed", True) # Linux

        config_path = Path(__file__).resolve().parent.parent / "configs" / "configs.yaml"
        self.config_service = ConfigService(config_path)
        clientes_config = self.config_service.get_clientes()

        self.test_runner = TestRunner(self)
        self.genesis_runner = GenesisRunner(self)

        self.log_queue = queue.Queue()

        self.clientes_map = {
            dados["label"]: key
            for key, dados in clientes_config.items()
        }
        self.id_to_label = {
            key: dados["label"]
            for key, dados in clientes_config.items()
        }

        # Configura o tema branco para os widgets ttk
        configure_style()
        
        self._build_ui()

        self._configure_loguru()

        self._start_log_updater()

        # Disable option scroll when cursor scrolls over combobox
        self.unbind_class("TCombobox", "<MouseWheel>")
        self.unbind_class("TCombobox", "<Button-4>")
        self.unbind_class("TCombobox", "<Button-5>")

    
    def _configure_loguru(self):

        # remove default stderr logger
        logger.remove()

        # GUI sink
        logger.add(
            GuiLogSink(self),
            level="DEBUG",
            enqueue=True,
        )

        # Only attach stderr if it exists
        if sys.stderr:
            logger.add(
                sys.stderr,
                level="INFO",
                colorize=True,
            )

    def _start_log_updater(self):
        self.after(50, self._process_log_queue)

    def _process_log_queue(self):
        try:
            while True:
                message, level = self.log_queue.get_nowait()
                self.log_panel.append(message, level)
        except queue.Empty:
            pass

        self.after(50, self._process_log_queue)
    

    def log(self, message: str, level="INFO"):
        self.log_queue.put((message, level))

    # ---------- Carregamento do Histórico ----------

    def _load_test_history(self, client_id: str) -> dict:
        """
        Lê o arquivo de histórico JSON do cliente ativo em
        historico_testes/estado_atual/<client_id>.json e agrega o
        resultado por ARQUIVO de teste, que é a granularidade que o
        catálogo da GUI usa (test["path"]).

        O conftest.py grava indexado pelo nodeid do pytest, que inclui
        "::nome_da_função" quando o arquivo tem mais de um teste. Aqui:
        1. tira o "::nome_da_função" de cada chave, sobrando só o
           caminho do arquivo (se a chave já vier sem "::", não muda
           nada — funciona nos dois formatos);
        2. se sobrar mais de uma entrada pro mesmo arquivo, mantém a
           pior (fail > skip > pass), pra um teste que falhou não ficar
           escondido atrás de outro que passou depois.
        """
        if not client_id:
            return {}

        project_root = Path(__file__).resolve().parent.parent
        history_file = project_root / "historico_testes" / "estado_atual" / f"{client_id}.json"

        if not history_file.exists():
            logger.debug(f"Arquivo de histórico não encontrado para o cliente: {client_id}")
            return {}

        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history_data = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler o arquivo de histórico do cliente '{client_id}': {e}")
            return {}

        historico_por_arquivo: dict = {}

        for chave, info in history_data.items():
            caminho_arquivo = chave.split("::")[0]
            resultado = info.get("resultado", "none")

            atual = historico_por_arquivo.get(caminho_arquivo)
            severidade_nova = _SEVERIDADE_RESULTADO.get(resultado, -1)
            severidade_atual = _SEVERIDADE_RESULTADO.get(atual.get("resultado"), -1) if atual else -1

            if atual is None or severidade_nova >= severidade_atual:
                historico_por_arquivo[caminho_arquivo] = info

        logger.info(f"Histórico de testes carregado com sucesso para '{client_id}'.")
        return historico_por_arquivo

    # ---------- UI ----------

    def _build_ui(self):
        root_container = ttk.Frame(self)
        root_container.pack(fill="both", expand=True)

        root_container.columnconfigure(0, weight=1)
        root_container.rowconfigure(0, weight=1) # conteúdo
        root_container.rowconfigure(1, weight=0) # footer (fixo)

        # Conteúdo principal
        content_wrapper = ttk.Frame(root_container)
        content_wrapper.grid(row=0, column=0, sticky="nsew")
        content_wrapper.columnconfigure(0, weight=1)
        content_wrapper.rowconfigure(0, weight=1)
        
        scroll_container = ScrollableFrame(content_wrapper)
        scroll_container.pack(fill="both", expand=True)
        
        scrollable_content = scroll_container.scrollable_frame

        self.header = Header(scrollable_content)
        self.header.pack(fill="x", pady=(0, 15))

        top_bar = ttk.Frame(scrollable_content)
        top_bar.pack(fill="x")

        top_bar.columnconfigure(0, weight=1)
        top_bar.columnconfigure(1, weight=4)

        labels = list(self.clientes_map.keys())
        
        cliente_ativo_id = self.config_service.get_cliente_ativo()

        cliente_ativo_label = self.id_to_label.get(cliente_ativo_id)

        if not cliente_ativo_label:
            logger.warning(
                "cliente_ativo inválido no YAML: {}. Usando primeiro cliente disponível.", 
                cliente_ativo_id
            )
            cliente_ativo_label = labels[0] if labels else None
        else:
            cliente_ativo_label = self.id_to_label[cliente_ativo_id]

        self.client_selector = ClientSelector(
            top_bar, 
            labels, 
            default_label=cliente_ativo_label
        )
        self.client_selector.set_on_save_callback(self._save_client_url)
        self.client_selector.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.client_selector.client_combo.bind(
            "<<ComboboxSelected>>",
            self._on_client_changed
        )

        self.client_selector.ambiente_combo.bind(
            "<<ComboboxSelected>>",
            self._on_ambiente_changed
        )

        if cliente_ativo_label:
            initial_client_id = self.clientes_map.get(cliente_ativo_label)

            if initial_client_id:
                self._populate_ambientes(initial_client_id)

                runtime_config = self._get_runtime_config(initial_client_id)
                initial_url = runtime_config.get("url", "")
                self.client_selector.set_url(initial_url)

        # --- SEARCH BAR ---
        # padx matches modules_frame so left/right edges align exactly.
        search_bar_frame = ttk.Frame(scrollable_content)
        search_bar_frame.pack(fill="x", padx=150, pady=(15, 0))

        _PLACEHOLDER = "Pesquisar"
        _PLACEHOLDER_COLOR = "#aaaaaa"
        _ACTIVE_COLOR = "black"
        _FONT = ("Segoe UI", 13)

        # No textvariable — we drive filtering via <<Modified>> / KeyRelease
        # so the placeholder text never leaks into the filter logic.
        self._search_entry = tk.Entry(
            search_bar_frame,
            font=_FONT,
            fg=_PLACEHOLDER_COLOR,
            relief="solid",
            bd=1,
            justify="center",
            insertbackground=_ACTIVE_COLOR,
        )
        self._search_entry.insert(0, _PLACEHOLDER)
        self._search_entry.pack(fill="x", expand=True, ipady=6)

        def _is_placeholder():
            return (
                self._search_entry.get() == _PLACEHOLDER
                and self._search_entry.cget("fg") == _PLACEHOLDER_COLOR
            )

        def _on_focus_in(event):
            if _is_placeholder():
                self._search_entry.configure(fg=_ACTIVE_COLOR)
                self._search_entry.delete(0, "end")

        def _on_focus_out(event):
            if self._search_entry.get() == "":
                self._search_entry.configure(fg=_PLACEHOLDER_COLOR)
                self._search_entry.insert(0, _PLACEHOLDER)
                if hasattr(self, "modules_builder"):
                    self.modules_builder.filter("")

        def _on_key_release(event):
            if not _is_placeholder():
                query = self._search_entry.get()
                if hasattr(self, "modules_builder"):
                    self.modules_builder.filter(query)

        self._search_entry.bind("<FocusIn>", _on_focus_in)
        self._search_entry.bind("<FocusOut>", _on_focus_out)
        self._search_entry.bind("<KeyRelease>", _on_key_release)

        # Clicking anywhere outside the entry removes focus (stops cursor blinking)
        # self.bind_all("<Button-1>", lambda e: (
        #     self._search_entry.focus_set()
        #     if e.widget is self._search_entry
        #     else self.focus_set()
        # ), add="+")
        def _handle_global_click(event):
            widget = event.widget
            # Se clicou no próprio search entry, mantém foco
            if widget is self._search_entry:
                return
            # Se clicou em qualquer Combobox ou dropdown interno, não interfere
            widget_class = widget.winfo_class()

            if widget_class in (
                "TCombobox",
                "Combobox",
                "Listbox",
                "TEntry",
                "Text",
            ):
                return
            # Remove foco do search entry
            self.focus()

        self.bind_all("<Button-1>", _handle_global_click, add="+")

        self.modules_frame = ttk.Frame(scrollable_content)
        self.modules_frame.pack(fill="both", expand=True, padx=150)

        self._rebuild_modules()

        # Footer (sempre visível)
        self.footer = ttk.Frame(root_container)
        self.footer.grid(row=1, column=0, sticky="ew")

        # --- LOG PANEL ---
        self.log_panel = LogPanel(self.footer, lines_visible=7)
        self.log_panel.pack(fill="x", padx=0, pady=(5, 0))

        # --- BUTTONS ---
        self._build_buttons(self.footer)


    def _build_buttons(self, parent):
        ttk.Separator(parent).pack(fill="x", pady=(5, 10))
        btns = ttk.Frame(parent)
        btns.pack(pady=20)

        self.run_btn = ttk.Button(
            btns,
            text="Rodar Testes",
            command=self.run_tests
        )
        self.run_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(
            btns,
            text="Parar Testes",
            command=self.stop_tests,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=5)

        self.genesis_btn = ttk.Button(
            btns,
            text="Preparar Ambiente",
            command=self.run_genesis
        )
        self.genesis_btn.pack(side="left", padx=5)

    def _rebuild_modules(self):
        # destroy old UI
        for widget in self.modules_frame.winfo_children():
            widget.destroy()

        # Reset search entry to placeholder so the new modules_builder starts clean
        if hasattr(self, "_search_entry"):
            self._search_entry.configure(fg="#aaaaaa")
            self._search_entry.delete(0, "end")
            self._search_entry.insert(0, "Pesquisar")

        client_id = self.config_service.get_cliente_ativo()
        client_id = client_id or next(iter(self.clientes_map.values()))

        clientes_config = self.config_service.get_clientes()
        client_versao = clientes_config.get(client_id, {}).get("versao")
        test_history = self._load_test_history(client_id)

        modules_filtrados = filtrar_modulos_por_cliente(
            MODULES,
            client_id,
            client_versao
        )

        self.modules_builder = ModulesBuilder(
            self.modules_frame,
            modules_filtrados,
            test_history=test_history
        )
        self.modules_builder.pack(fill="both", expand=True)

    def _get_runtime_config(self, client_id: str) -> dict:
        clientes = self.config_service.get_clientes()
        ambiente = self.config_service.get_ambiente()

        if client_id not in clientes:
            logger.warning("Cliente não encontrado na configuração: {}", client_id)
            return {}

        cliente_config = clientes[client_id]
        ambientes = cliente_config.get("ambientes", {})

        if ambiente not in ambientes:
            logger.warning(
                "Ambiente '{}' não configurado para o cliente '{}'",
                ambiente, client_id
            )
            return {}
        
        return ambientes[ambiente]


    def _on_client_changed(self, event):
        selected_label = self.client_selector.get_client()

        client_id = self.clientes_map.get(selected_label)

        if not client_id:
            logger.warning("Label selecionado não mapeado: '{}'.", selected_label)
            return
        
        previous_client_id = self.config_service.get_cliente_ativo()
        previous_label = self.id_to_label.get(previous_client_id)

        try:
            changed = self.config_service.set_cliente_ativo(client_id)

            if changed:
                logger.info(
                    "Cliente ativo alterado para '{}'.",
                    selected_label
                )
        except PermissionError:
            logger.error(
                "Não foi possível salvar configs.yaml. "
                "Verifique se o arquivo está aberto em outro programa e feche-o."
            )

            # revert selection visually
            if previous_label:
                self.client_selector.client_var.set(previous_label)
            
            return
        
        except Exception as e:
            logger.error("Erro ao alterar cliente ativo: {}", e)

            if previous_label:
                self.client_selector.client_var.set(previous_label)

            return

        self._populate_ambientes(client_id)

        runtime_config = self._get_runtime_config(client_id)
        url = runtime_config.get("url", "")
        self.client_selector.set_url(url)

        self._rebuild_modules()
    
    def _on_ambiente_changed(self, event):
        selected_label = self.client_selector.get_client()
        client_id = self.clientes_map.get(selected_label)

        if not client_id:
            logger.warning("Cliente inválido ao alterar ambiente.")
            return
        
        ambiente = self.client_selector.get_ambiente()

        try:
            changed = self.config_service.set_ambiente(ambiente)

            if changed:
                logger.info(
                    "Ambiente ativo alterado para '{}'.",
                    ambiente
                )
        except Exception as e:
            logger.error("Erro ao alterar ambiente: {}", e)
            return

        # Update URL for new client+ambiente combination
        runtime_config = self._get_runtime_config(client_id)
        url = runtime_config.get("url", "")
        self.client_selector.set_url(url)

    def _populate_ambientes(self, client_id: str):
        clientes = self.config_service.get_clientes()

        cliente_config = clientes.get(client_id, {})
        ambientes_dict = cliente_config.get("ambientes", {})

        ambientes = list(ambientes_dict.keys())

        ambiente_ativo = self.config_service.get_ambiente()

        self.client_selector.set_ambientes(
            ambientes,
            default=ambiente_ativo
        )

    def _set_ui_running_state(self, running: bool):
        if running:
            self.run_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.client_selector.set_enabled(False)
            self.genesis_btn.configure(state="disabled")
        else:
            self.run_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.client_selector.set_enabled(True)
            self.genesis_btn.configure(state="normal")

            client_id = self.config_service.get_cliente_ativo()
            novo_historico = self._load_test_history(client_id)
            if hasattr(self, "modules_builder"):
                paths_executados = getattr(self, "_ultimos_testes_executados", None)
                self.modules_builder.update_history(novo_historico, changed_paths=paths_executados)

    # ---------- Actions ----------

    def run_tests(self):
        
        selected_files = self.modules_builder.get_selected_tests()

        if not selected_files:
            messagebox.showwarning(
                "Nenhum teste selecionado. ",
                "Selecione ao menos um teste para executar."
            )
            return

        # Build absolute paths for safety
        absolute_paths = []

        for f in selected_files:
            test_file = os.path.join(os.getcwd(), f)  # full path

            if not os.path.exists(test_file):
                messagebox.showerror(
                    "Arquivo não encontrado",
                    f"O arquivo de teste não existe:\n{test_file}"
                )
                return
            
            absolute_paths.append(test_file)

        # Guardado pra, quando a execução terminar, atualizar só os ícones
        # desses testes em vez de reconstruir a tela inteira.
        self._ultimos_testes_executados = selected_files

        slow_mo = self.client_selector.get_slow_mo()
        self.test_runner.run(absolute_paths, slow_mo)


    def stop_tests(self):
        self.test_runner.stop()
        self.genesis_runner.stop()
    

    def _save_client_url(self, client_label: str, new_url: str) -> bool:
        client_id = self.clientes_map.get(client_label)

        if not client_id:
            logger.warning("Cliente não encontrado ao salvar URL: {}", client_label)
            return False

        ambiente = self.config_service.get_ambiente()

        try:
            self.config_service.update_client_url(
                client_id,
                ambiente,
                new_url
            )

            logger.info(
                "URL atualizada para cliente '{}' no ambiente '{}'.",
                client_label,
                ambiente
            )

            return True
        
        except PermissionError:
            logger.error(
                "Não foi possível salvar configs.yaml. "
                "O arquivo pode estar aberto em outro programa. Feche-o e tente novamente."
            )
            return False
        
        except Exception as e:
            logger.error("Erro ao salvar URL: {}", e)
            return False

    def run_genesis(self):
        if self.test_runner.is_running:
            logger.warning("Testes em execução. Aguarde finalizar.")
            return

        if self.genesis_runner.is_running:
            logger.warning("Genesis já está em execução.")
            return

        self.genesis_runner.run(slow_mo=self.client_selector.get_slow_mo())
