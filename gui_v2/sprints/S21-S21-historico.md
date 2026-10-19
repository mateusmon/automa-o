# Sprint 21 — remoção do status estático da sidebar

- [x] **S21.1 — remover o widget “Ambiente disponível”.** O bloco verde e o texto
  “Ambiente pronto para execução” foram removidos porque eram fixos e não verificavam
  disponibilidade real. A sidebar continua recolhível, e o indicador de erros da GUI permanece
  independente e inalterado.

  **Validação:** revisão do diff e smoke visual da GUI v2 com o Python do `.venv`, nos modos
  expandido e compacto; nenhuma execução ASI foi iniciada.
