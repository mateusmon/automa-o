import shutil
import re

from pathlib import Path
from datetime import datetime
from uuid import uuid4
from playwright.sync_api import Page, expect
from loguru import logger

from utils import retencao

# Timeout próprio da captura de evidência, propositalmente curto: não pode
# herdar os 60s do page.set_default_timeout do conftest.
TIMEOUT_SCREENSHOT = 10_000

_base_dir: Path | None = None               # Diretório base onde as evidências finais serão salvas
_temp_ctx: None = None                      # Contexto da pasta temporária
_temp_dir: Path | None = None               # Caminho da pasta temporária
_page = None                                # Objeto da página (usado para capturas de tela)
_finalized = False                          # Flag para indicar se a coleta de evidências foi finalizada


def iniciar(base_path: Path):
    """
    Chamado uma vez na inicialização do pytest.
    Prepara um diretório temporário seguro para armazenar evidências.

    Args:
        base_path (Path): Caminho base onde as evidências finais serão salvas.
    """
    global _base_dir, _temp_ctx, _temp_dir, _finalized

    base_path.mkdir(parents=True, exist_ok=True)

    _limpar_evidencias_antigas(base_path)
    _limpar_temporarias_orfas(base_path)
    _finalized = False
    _base_dir = base_path

    # Cria um ID único para esta execução: timestamp + primeiros 8 dígitos de um UUID
    _run_id = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{uuid4().hex[:8]}"

    # Cria a pasta temporária para armazenar evidências desta execução
    _temp_dir = base_path / f"_temp_{_run_id}"
    _temp_dir.mkdir(parents=True, exist_ok=True)


def garantir_inicializacao():
    global _temp_dir

    if _temp_dir is None:
        # Caminho absoluto: a pasta de evidência não pode depender de onde o
        # pytest foi disparado (terminal, GUI ou sentinela).
        base = Path(__file__).resolve().parent.parent / "evidencia"
        base.mkdir(parents=True, exist_ok=True)

        logger.debug("Cleanup aconteceu e iniciar() não foi chamado. Inicializando evidência novamente.")
        iniciar(base)


def set_page(page):
    """
    Chamado pelo fixture da página.
    Guarda a referência da página para capturas de tela.

    Args:
        page: Objeto da página (ex.: Playwright ou Selenium)
    """
    global _page
    _page = page


def _nome_de_arquivo(name: str) -> str:
    """
    Sanitiza o nome e respeita o limite de 260 caracteres de caminho do Windows.

    Args:
        name (str): Nome desejado para o arquivo (sem extensão).

    Returns:
        str: Nome utilizável dentro da pasta temporária.
    """
    safe_name = name.replace("/", "_").replace("\\", "_")

    # Windows tem limite de 260 caracteres no caminho completo.
    max_name_len = 255 - len(str(_temp_dir))

    # Piso defensivo: sem ele, uma pasta temporária muito longa zeraria o
    # limite e o arquivo viraria apenas ".png".
    max_name_len = max(max_name_len, 20)

    if len(safe_name) > max_name_len:
        safe_name = safe_name[:max_name_len]

    return safe_name


def screenshot(name: str, full_page: bool = False) -> Path | None:
    """
    Captura uma screenshot da página atual e salva na pasta temporária.

    A captura é best-effort e tem timeout próprio e curto: ela roda quando o
    teste já falhou, muitas vezes com a página travada, e nesse cenário não pode
    segurar a execução nem propagar exceção.

    Args:
        name (str): Nome do arquivo de imagem (sem extensão).
        full_page (bool): Captura a página inteira. Desligado por padrão porque
            o modo full page exige avaliar JavaScript na página (para medir a
            altura do documento), o que nunca retorna quando o renderer está
            bloqueado — por exemplo com um diálogo nativo aberto.

    Returns:
        Path | None: Caminho da imagem salva, ou None se não foi possível capturar.
    """
    if _page is None:
        logger.debug("Nenhuma página registrada. Screenshot ignorado.")
        return None

    if _page.is_closed():
        logger.debug("Página já fechada. Screenshot ignorado.")
        return None

    garantir_inicializacao()

    if _temp_dir is None:
        logger.debug("Diretório temporário indisponível. Screenshot ignorado.")
        return None

    path = _temp_dir / f"{_nome_de_arquivo(name)}.png"

    try:
        _page.screenshot(path=path, full_page=full_page, timeout=TIMEOUT_SCREENSHOT)
    except Exception as e:
        logger.warning("Não foi possível capturar o screenshot de evidência: {}", e)
        return None

    return path


def registrar_pdf_bytes(pdf_bytes: bytes, name: str) -> Path:
    """
    Salva um PDF a partir de bytes brutos na pasta temporária de evidências.

    Este método é usado quando o sistema abre o PDF de forma inline
    (ex.: nova aba / viewer), impossibilitando o uso de expect_download.
    Aparentemente o ASI sempre abre os PDFs desta maneira.

    Args:
        pdf_bytes (bytes): Conteúdo binário do PDF obtido via response.body().
        name (str): Nome do arquivo PDF (sem extensão).

    Returns:
        Path: Caminho completo do arquivo salvo na pasta temporária.

    Raises:
        RuntimeError: Se a pasta temporária não estiver inicializada.
        ValueError: Se pdf_bytes estiver vazio.
    """
    if not _temp_dir:
        garantir_inicializacao()
    
    assert _temp_dir is not None, "Diretório temporário não foi inicializado."
    
    if not pdf_bytes:
        raise ValueError("PDF recebido está vazio.")

    if not pdf_bytes.startswith(b"%PDF"):
        raise ValueError("Conteúdo recebido não é um PDF válido.")
    
    path = _temp_dir / f"{name}.pdf"

    path.write_bytes(pdf_bytes)

    return path


def registrar_pdf(popup_page: Page, nome: str, timeout: int = 30_000) -> Path:
    """
    Registra um PDF aberto em uma nova aba (popup) como evidência.

    Este método é utilizado quando o sistema abre o PDF de forma inline
    (ex.: viewer em nova aba), impossibilitando o uso de `expect_download`.
    O fluxo consiste em:
    
    1. Obter a URL atual da aba do PDF.
    2. Realizar uma requisição HTTP usando o mesmo BrowserContext,
       garantindo sessão, cookies e autenticação.
    3. Validar se a resposta HTTP foi bem-sucedida.
    4. Extrair os bytes brutos do PDF.
    5. Delegar a persistência para `registrar_pdf_bytes`.
    6. Fechar a aba do PDF, garantindo limpeza de recursos.

    Args:
        popup_page (Page): Página do Playwright correspondente ao popup
            onde o PDF foi aberto.
        nome (str): Nome do arquivo PDF (sem extensão).

    Returns:
        Path: Caminho completo do arquivo PDF salvo na pasta temporária
        de evidências.

    Raises:
        RuntimeError: Se a requisição HTTP para obtenção do PDF falhar
        (status HTTP diferente de 2xx).
    """
    try:
        # Só aguarda se a URL ainda não resolveu
        if not popup_page.url.startswith("http"):
            expect(popup_page).to_have_url(re.compile(r"^https?://"), timeout=timeout)

        # URL do PDF exibido no viewer
        pdf_url = popup_page.url

        if not pdf_url.startswith("http"):
                raise RuntimeError(f"URL inválida do popup após aguardar carregamento: '{pdf_url}'")
        
        # Requisição feita com o mesmo contexto do browser
        response = popup_page.context.request.get(pdf_url)

        if not response.ok:
            raise RuntimeError(
                f"Falha ao obter PDF. HTTP {response.status} - {pdf_url}"
            )

        # Conteúdo binário do PDF
        pdf_bytes = response.body()

        # Persistência delegada ao método de baixo nível
        return registrar_pdf_bytes(pdf_bytes, nome)

    finally:
        # Garante que a aba do PDF será sempre fechada
        popup_page.close()


def finalizar_evidencia():
    """
    Chamado uma vez na primeira falha do teste.
    Move as evidências temporárias para uma pasta datada dentro do diretório base.
    """
    global _finalized

    if _finalized or not _temp_dir or not _temp_dir.exists():
        return

    assert _base_dir is not None, "Diretório base não foi inicializado."
    
    _finalized = True

    arquivos = list(_temp_dir.iterdir())

    if arquivos:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        destino = _base_dir / timestamp
        destino.mkdir(parents=True, exist_ok=True)

        # Move todos os arquivos da pasta temporária para a pasta de destino
        for item in _temp_dir.iterdir():
            shutil.move(str(item), destino)
    
    # Limpa a pasta temporária
    cleanup()


def cleanup():
    """
    Limpa recursos temporários utilizados durante a execução dos testes.

    Funcionalidade:
    - Chama a função interna `_cleanup_temp()` para remover arquivos temporários.

    Observações:
    - Esta função geralmente é chamada ao final da sessão de testes, por exemplo,
      no hook `pytest_sessionfinish`.
    - `_cleanup_temp()` é uma função privada responsável pela lógica real de limpeza.
    """
    _cleanup_temp()


def _cleanup_temp():
    """
    Função interna privada.

    Limpa de forma segura o diretório temporário.
    """
    global _temp_ctx, _temp_dir

    if _temp_ctx:
        try:
            _temp_ctx.cleanup()
        except Exception:
            pass
        _temp_ctx = None
    
    if _temp_dir and _temp_dir.exists():
        shutil.rmtree(_temp_dir, ignore_errors=True)

    _temp_dir = None


def _limpar_temporarias_orfas(base_path: Path) -> None:
    """
    Remove pastas `_temp_*` deixadas para trás por execuções que morreram.

    A pasta temporária normalmente é apagada em `finalizar_evidencia()`. Quando a
    sessão morre antes disso (INTERNALERROR, Ctrl+C, GUI encerrada na força), ela
    fica órfã — e o `_limpar_evidencias_antigas` não a remove, porque o nome não
    corresponde ao padrão de timestamp das pastas de evidência.

    Args:
        base_path (Path): Diretório base de evidências.
    """
    retencao.varrer_por_data(
        base_path,
        retencao.FORMATO_TIMESTAMP,
        retencao.horas("temporarias_horas"),
        prefixo="_temp_",
    )


def _limpar_evidencias_antigas(base_path: Path) -> None:
    """
    Remove pastas de evidência expiradas, conforme `configs/retencao.yaml`.

    Considera apenas subpastas cujo nome segue o padrão de timestamp gerado por
    finalizar_evidencia() (ex: 2025-01-10_14-30-00).

    Args:
        base_path (Path): Diretório base de evidências.
    """
    retencao.varrer_por_data(
        base_path,
        retencao.FORMATO_TIMESTAMP,
        retencao.dias("evidencias_dias"),
    )
