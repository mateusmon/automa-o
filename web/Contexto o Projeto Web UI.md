# ASI Automação 2.0 — Contexto do Projeto Web

Este arquivo resume tudo que foi decidido sobre a migração da GUI desktop (Tkinter) para web. Use como referência ao iniciar qualquer chat relacionado a esse projeto.

---

## O que é o projeto

**ASI Automação 2.0** é uma aplicação desktop em Python/Tkinter para gerenciamento e execução de testes automatizados do sistema ASI. O objetivo atual é reescrever somente a GUI em formato web, mantendo toda a lógica de backend intacta.

---

## O que o app faz hoje (GUI Tkinter)

1. **Seleção de configuração** — cliente ativo, ambiente (ex: homologação/produção), URL
2. **Seleção de testes** — módulos colapsáveis com checkboxes, filtrados por cliente
3. **Execução** — dispara pytest como subprocesso via `subprocess.Popen`, com streaming de output em tempo real
4. **Exibição de logs** — painel que recebe output linha a linha com auto-scroll
5. **Preparar Ambiente** — botão que executa o `GenesisRunner`, processo separado do pytest

A funcionalidade nova que a versão web terá é uma **barra de pesquisa** para filtrar testes por nome.

---

## Stack decidida para a versão web

| Camada | Tecnologia | Motivo |
|---|---|---|
| Frontend | React | Interface componentizada |
| Estilo | Tailwind CSS | Estilização direta no componente, flexível |
| Build/Dev | Vite | Ferramenta de build, o usuário quase não interage com ela |
| Backend | FastAPI (Python) | Reusa todo o código Python existente |
| Logs em tempo real | SSE (Server-Sent Events) | Feito para streaming unidirecional servidor→cliente |
| TypeScript | Opcional — deixar para depois | Adicionar quando estiver confortável com React |

**Princípio:** quanto menos ferramentas simultâneas, melhor. O usuário está aprendendo tudo do zero.

---

## Por que cada tecnologia

**React** — o browser não consegue executar subprocess, ler arquivos ou matar processos. O React é a interface que fala com o FastAPI via HTTP.

**FastAPI** — servidor Python que expõe o código existente como endpoints HTTP. O `TestRunner`, `GenesisRunner`, `ConfigService` e `module_filter` sobrevivem sem grandes alterações.

**SSE** — o painel de logs precisa receber linhas em tempo real conforme o pytest executa. SSE mantém uma conexão HTTP aberta e o servidor empurra dados aos poucos. É mais simples que WebSocket e suficiente para esse caso (comunicação só servidor→cliente).

**Vite** — transforma o código React em arquivos estáticos. Durante desenvolvimento sobe um servidor local com hot reload. Em produção, o FastAPI serve os arquivos estáticos gerados.

**Tailwind** — classes de estilo diretamente no JSX, sem alternar entre arquivos CSS. Curva de aprendizado curta.

---

## Estrutura de pastas planejada

```
asi-automacao/          ← raiz do projeto atual (não mexer)
├── gui/                ← interface Tkinter (mantida intacta)
├── web/                ← novo
│   ├── frontend/       ← projeto React (criado pelo Vite)
│   └── backend/        ← servidor FastAPI
├── tests/
├── configs/
└── ...
```

---

## Endpoints que o FastAPI precisará expor

| Método | Rota | O que faz |
|---|---|---|
| GET | `/clientes` | Retorna clientes do configs.yaml |
| GET | `/modulos?cliente=id` | Retorna catálogo filtrado por cliente |
| POST | `/testes/rodar` | Inicia o TestRunner |
| POST | `/testes/parar` | Para o TestRunner |
| GET | `/logs` | SSE — streaming de logs em tempo real |
| GET | `/config` | Retorna cliente ativo, ambiente, URL |
| PUT | `/config` | Salva cliente ativo, ambiente, URL |
| POST | `/genesis/rodar` | Inicia o GenesisRunner |

---

## O que muda no código Python existente

Pouca coisa. Os arquivos `core/`, `services/` e `catalog/` ficam intactos. O que muda:

- `TestRunner` e `GenesisRunner` recebem uma queue ou callback agnóstico de UI, em vez de referência direta ao `app` Tkinter
- O ponto de entrada deixa de ser `App().mainloop()` e passa a ser o servidor FastAPI
- `gui/` continua existindo — a versão Tkinter não é removida agora

---

## Ordem de aprendizado e desenvolvimento

1. **React — fundamentos isolados** — componentes, props, useState, renderizar listas. Sem backend.
2. **UI estática com Tailwind** — construir toda a interface com dados falsos. Módulos colapsáveis, checkboxes, painel de logs, seletor de cliente. Objetivo: interface visual pronta antes de pensar em backend.
3. **FastAPI — isolado** — criar endpoints simples, entender como rodar o servidor, como retornar JSON.
4. **Conectar React ao FastAPI** — substituir dados falsos por chamadas reais com `fetch`.
5. **SSE** — conectar o painel de logs ao streaming do FastAPI.

---

## Ambiente de desenvolvimento

Durante o desenvolvimento, dois servidores rodam simultaneamente:

- **Vite** na porta `5173` — serve o React com hot reload
- **FastAPI** na porta `8000` — serve a API

Isso é normal. Em produção, o FastAPI serve tanto a API quanto os arquivos estáticos gerados pelo `npm run build`.

---

## Pré-requisitos para instalar na máquina

- **Node.js** (npm vem junto) — para o frontend
- **Python** — já instalado (projeto atual roda em Python)

Vite, React, Tailwind e FastAPI são instalados dentro do projeto via `npm install` e `pip install`, não na máquina globalmente.

---

## Convenções a seguir (herdadas do projeto atual)

- Callbacks entre componentes são passados explicitamente
- Toda operação que bloqueia (rodar testes, genesis) roda em thread separada no backend
- Strings de log em português
- Não modificar `configs.yaml` diretamente — sempre via `ConfigService`
- Lógica de negócio fica em `core/` e `services/`, nunca em componentes de UI

---

## O que não está decidido ainda

- Biblioteca de componentes UI (shadcn/ui foi mencionado como opção futura, mas não é prioridade agora)
- Autenticação (relevante quando o projeto rodar remotamente em servidor — não é agora)
- TypeScript (opcional, pode entrar depois de estar confortável com React + JavaScript)
