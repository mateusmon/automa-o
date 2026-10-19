"""Coordenação do estado da nova interface, sem dependência da camada visual."""

from __future__ import annotations

from collections.abc import Iterable

from gui_v2.models.app_state import AppState


class AppController:
    """Aplica as regras básicas de cliente, módulo e seleção ao ``AppState``."""

    def __init__(self, state: AppState | None = None) -> None:
        self.state = state or AppState()

    def select_client(self, client_key: str) -> bool:
        """Seleciona o cliente e limpa a seleção quando ele realmente mudou."""
        if client_key == self.state.client_key:
            return False
        self.state.client_key = client_key
        self.state.selected_test_ids.clear()
        return True

    def select_module(self, module: str) -> bool:
        """Seleciona o módulo sem alterar os testes já escolhidos."""
        if module == self.state.current_module:
            return False
        self.state.current_module = module
        return True

    def set_test_selected(self, selection_id: str, selected: bool) -> None:
        """Inclui ou remove um path/nodeid da seleção atual."""
        if selected:
            self.state.selected_test_ids.add(selection_id)
        else:
            self.state.selected_test_ids.discard(selection_id)

    def clear_selected_tests(self) -> None:
        """Remove todos os testes da seleção atual."""
        self.state.selected_test_ids.clear()

    def toggle_section(self, selection_ids: Iterable[str]) -> None:
        """Marca todos os itens da seção ou os desmarca quando todos já estavam ativos."""
        ids = set(selection_ids)
        if not ids:
            return
        if ids.issubset(self.state.selected_test_ids):
            self.state.selected_test_ids.difference_update(ids)
        else:
            self.state.selected_test_ids.update(ids)
