from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .webdriver_config import create_chrome_driver, scroll_down
import time


def get_transcription(url, output_file):
    """
    Extrai a transcrição de um vídeo do YouTube
    
    Args:
        url (str): URL do vídeo do YouTube
        output_file (str): Caminho para salvar o arquivo de transcrição
    
    Returns:
        bool: True se a transcrição foi extraída com sucesso, False caso contrário
    """
    driver = None
    try:
        print("Inicializando WebDriver...")
        driver = create_chrome_driver(headless=False)
        
        print("Acessando o vídeo...")
        driver.get(url)
        
        # Aguardar carregamento da página
        time.sleep(5)
        
        print("Procurando botão de descrição...")
        success = _click_description_button(driver)
        if not success:
            print("Não foi possível encontrar o botão de descrição")
            return False
        
        print("Tentando fechar modal do YouTube Premium...")
        success =_close_youtube_premium_modal(driver)
        if not success:
            print("Não foi possível fechar o modal do YouTube Premium")
            return False

        print("Procurando botão de transcrição...")
        success = _click_transcription_button(driver)
        if not success:
            print("Não foi possível encontrar o botão de transcrição")
            return False
        
        print("Extraindo transcrição...")
        success = _extract_transcription_text(driver, output_file)
        if not success:
            print("Não foi possível extrair a transcrição")
            return False
        
        print("Transcrição extraída com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro durante a extração da transcrição: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()


def _click_description_button(driver):
    """
    Clica no botão para expandir a descrição do vídeo

    Args:
        driver: Instância do WebDriver

    Returns:
        bool: True se conseguiu clicar, False caso contrário
    """
    try:
        scroll_down(driver, 450)
        time.sleep(2)

        description_selectors = [
            '//*[@id="description-inline-expander"]',
            '//*[@id="expand"]',
            '//tp-yt-paper-button[@id="expand"]',
            '//button[@id="expand"]',
            '//*[@aria-label="Mostrar mais"]',
        ]

        for attempt in range(2):  # Tenta duas vezes: normal + após fechar modal
            for selector in description_selectors:
                try:
                    description_button = WebDriverWait(driver, 6).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    description_button.click()
                    time.sleep(2)
                    return True
                except TimeoutException:
                    continue

            if attempt == 0:
                modal_closed = _close_youtube_premium_modal(driver)
                if modal_closed:
                    print("Tentando novamente clicar na descrição após fechar o modal...")
                    for selector in description_selectors:
                        try:
                            description_button = WebDriverWait(driver, 6).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            description_button.click()
                            time.sleep(2)
                            return True
                        except TimeoutException:
                            continue

        return False

    except Exception as e:
        print(f"Erro ao clicar no botão de descrição: {e}")
        return False

def _click_transcription_button(driver): 
    try:
        scroll_down(driver, 100)
        time.sleep(2)

        _close_youtube_premium_modal(driver)
        time.sleep(1)

        js_code = '''
        const btn = [...document.querySelectorAll("button")]
          .find(el => el.textContent.includes("Mostrar transcrição") || el.getAttribute("aria-label") === "Mostrar transcrição");
        if (btn) {
          btn.scrollIntoView({ behavior: "smooth", block: "center" });
          setTimeout(() => btn.click(), 500);
        }
        '''
        driver.execute_script(js_code)
        print("Comando JavaScript enviado")

        # Aguarda a transcrição aparecer
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-transcript-segment-renderer"))
        )
        print("Transcrição aberta com sucesso via JS!")
        return True

    except TimeoutException:
        print("Transcrição não apareceu após clique via JavaScript")
        return False
    except Exception as e:
        print(f"Erro ao tentar abrir transcrição com JS: {e}")
        return False



def _close_youtube_premium_modal(driver):
    """
    Fecha o modal do YouTube Premium, se estiver visível.

    Args:
        driver: Instância do WebDriver
    """
    try:
        print("Verificando se o modal do YouTube Premium está visível...")
        modal_selectors = [
            '//*[@id="dismiss-button"]',
           '//*[@id="dismiss-button"]/yt-button-shape', 
            '//yt-button-renderer[@id="dismiss-button"]//button',
            '//*[@id="dismiss-button"]/yt-button-shape/button',
            '//*[@id="dismiss-button"]/yt-button-shape',
            '//button[@aria-label="Fechar"]',
            '//button[contains(@aria-label, "Close")]',
            '//button[contains(text(), "Não agora")]',
            '//button[contains(text(), "No thanks")]',
            '//button[contains(text(), "Agora não")]',
        ]
        for selector in modal_selectors:
            try:
                button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                button.click()
                print("Modal do YouTube Premium fechado.")
                return True
            except TimeoutException:
                continue
        print("Nenhum modal do YouTube Premium encontrado.")
        return False
    except Exception as e:
        print(f"Erro ao tentar fechar o modal: {e}")
        return False


def _extract_transcription_text(driver, output_file):
    """
    Extrai o texto da transcrição e salva em arquivo
    
    Args:
        driver: Instância do WebDriver
        output_file (str): Caminho do arquivo de saída
    
    Returns:
        bool: True se conseguiu extrair, False caso contrário
    """
    try:
        print("Aguardando carregamento da transcrição...")
        time.sleep(10)
        
        # Aguardar elementos da transcrição aparecerem
        transcript_selectors = [
            "ytd-transcript-segment-renderer .segment-text",
            ".ytd-transcript-segment-renderer",
            "[class*='transcript'] [class*='segment']"
        ]
        
        texts = []
        for selector in transcript_selectors:
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                # Script JavaScript para extrair texto
                if selector == "ytd-transcript-segment-renderer .segment-text":
                    script = """
                    var segments = document.querySelectorAll('ytd-transcript-segment-renderer .segment-text');
                    var texts = [];
                    segments.forEach(function(segment) {
                        texts.push(segment.textContent.trim());
                    });
                    return texts;
                    """
                else:
                    script = f"""
                    var segments = document.querySelectorAll('{selector}');
                    var texts = [];
                    segments.forEach(function(segment) {{
                        texts.push(segment.textContent.trim());
                    }});
                    return texts;
                    """
                
                texts = driver.execute_script(script)
                
                if texts and len(texts) > 0:
                    break
                    
            except TimeoutException:
                continue
        
        if not texts:
            print("Nenhum texto de transcrição encontrado")
            return False
        
        # Salvar em arquivo
        with open(output_file, "w", encoding="utf-8") as file:
            for text in texts:
                if text.strip():  # Só escreve se o texto não estiver vazio
                    file.write(text + "\n")
        
        print(f"Transcrição salva com {len(texts)} segmentos")
        return True
        
    except Exception as e:
        print(f"Erro ao extrair texto da transcrição: {e}")
        return False