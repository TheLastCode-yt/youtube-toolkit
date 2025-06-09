from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def get_chrome_options(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")  # use "new" headless mode para evitar bugs recentes
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return options



def create_chrome_driver(headless=True):
    print("Inicializando WebDriver...")
    options = get_chrome_options(headless)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Evita detecção como bot
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver


def scroll_down(driver, pixels):
    """
    Rola a página para baixo
    
    Args:
        driver: Instância do WebDriver
        pixels (int): Quantidade de pixels para rolar
    """
    driver.execute_script(f"window.scrollBy(0, {pixels});")


def scroll_to_top(driver):
    """
    Rola a página para o topo
    
    Args:
        driver: Instância do WebDriver
    """
    driver.execute_script("window.scrollTo(0, 0);")