from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page
from loguru import logger


class BrowserManager:
    """
    Single authority over Playwright lifecycle inside Genesis.

    Responsibilities:
        - Start Playwright
        - Launch browser
        - Create context
        - Create page
        - Reset context (session boundary)
        - Close everything safely

    Contains NO business logic
    """

    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._started: bool = False


    # --- Public API ---
    def start(self, headless: bool = True, slow_mo: int = 0) -> None:
        """
        Starts Playwright and launches browser.

        Raises:
            RuntimeError: if already started.
        """
        if self._started:
            raise RuntimeError("BrowserManager already started.")
        
        logger.info("Iniciando Playwright.")

        try:
            self._playwright = sync_playwright().start()

            self._browser = self._playwright.chromium.launch(
                headless=headless,
                args=["--start-maximized"],
                slow_mo=slow_mo
            )

            self._context = self._browser.new_context(
                no_viewport=True
            )

            self._page = self._context.new_page()
            self._started = True

        except Exception:
            self._cleanup_partial_start()
            raise

        logger.success("O browser iniciou com sucesso.")


    @property
    def page(self) -> Page:
        """
        Returns active Playwright page.

        Raises:
            RuntimeError: if not started
        """
        if not self._started or self._page is None:
            raise RuntimeError("BrowserManager not started.")
        
        return self._page
    
    @property
    def context(self) -> BrowserContext:
        if not self._started or self._context is None:
            raise RuntimeError("BrowserManager not started.")

        return self._context

    @property
    def started(self) -> bool:
        """
        Whether the browser is up and has a usable context.

        Allows callers to check before touching `page` or `context`, which raise
        when the browser never started.
        """
        return self._started and self._context is not None


    def reset_context(self) -> None:
        """
        Destroys current browser context and creates a new one.

        Used for session isolation between user roles.

        Raises:
            RuntimeError: if not started.
        """
        if not self._started or not self._browser:
            raise RuntimeError("Cannot reset context before start().")

        logger.info("Redefinindo contexto.")

        # Close existing context safely. Cada etapa já finalizou seu próprio trace.
        if self._context:
            self._context.close()
        
        self._context = None
        self._page = None

        # Create new isolated context
        self._context = self._browser.new_context(
            no_viewport=True
        )

        self._page = self._context.new_page()

        logger.success("Contexto do browser redefinido com sucesso.")
    

    def close(self) -> None:
        """
        Closes context, browser and Playwright safely.

        Safe to call multiple times.
        """
        if not self._started:
            return
        
        logger.info("Fechando browser.")

        try:
            if self._context:
                self._context.close()
        except Exception as e: 
            logger.error("Erro ao fechar contexto: {}", e)
        
        try:
            if self._browser:
                self._browser.close()
        except Exception as e:
            logger.error("Erro ao fechar navegador: {}", e)
        
        try:
            if self._playwright:
                self._playwright.stop()
        except Exception as e:
            logger.error("Erro ao parar Playwright: {}", e)
        
        self._context = None
        self._browser = None
        self._playwright = None
        self._page = None
        self._started = False

        logger.success("Browser fechado.")


    # --- Internal ---
    def _cleanup_partial_start(self):
            """
            This function is called in case browser initialization doesn't work properly.
            """
            try:
                if self._browser:
                    self._browser.close()
            except Exception:
                pass

            try:
                if self._playwright:
                    self._playwright.stop()
            except Exception:
                pass

            self._playwright = None
            self._browser = None
            self._context = None
            self._page = None
            self._started = False
