from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time


def scroll_down(driver, pixels):
    driver.execute_script(f"window.scrollBy(0, {pixels});")


def get_transcription(url, output_file):
    # Configuração do WebDriver com auto-instalação
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--headless")  # Modo headless
    chrome_options.add_argument("--no-sandbox")  # Necessário em alguns ambientes
    chrome_options.add_argument("--disable-dev-shm-usage")  # Necessário em alguns ambientes
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")

    # Usar WebDriverManager para instalar automaticamente o ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Acessar a página desejada
        driver.get(url)
        print("Página carregada com sucesso")

        # Espera explícita para o elemento "Descrição do vídeo"
        print("Indo clicar na descrição")
        scroll_down(driver, 400)
        time.sleep(5)
        
        xpath_open_description = '//*[@id="expand"]'
        try:
            description_video = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, xpath_open_description))
            )
            description_video.click()
            print("Descrição expandida com sucesso")
        except TimeoutException:
            print("O elemento de descrição do vídeo não foi encontrado a tempo.")
            return False

        # Espera explícita para o botão de "Ver Transcrição"
        print("Indo apertar na transcrição")
        scroll_down(driver, 100)
        time.sleep(3)
        
        xpath_view_transcription = '//*[@id="primary-button"]/ytd-button-renderer/yt-button-shape/button/yt-touch-feedback-shape/div'
        try:
            print("Tentando achar botão de ver transcrição")
            view_transcription_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, xpath_view_transcription))
            )
            view_transcription_button.click()
            print("Botão de transcrição clicado")
        except TimeoutException:
            print("O botão de ver transcrição não foi encontrado a tempo.")
            return False

        print("Aguardando carregamento da transcrição...")
        time.sleep(10)
        
        # Espera explícita para garantir que a transcrição foi carregada
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "ytd-transcript-segment-renderer .segment-text")
                )
            )
            print("Transcrição carregada com sucesso")
        except TimeoutException:
            print("A transcrição não foi carregada a tempo.")
            return False

        # Código JavaScript para coletar os textos
        script = """
        var segments = document.querySelectorAll('ytd-transcript-segment-renderer .segment-text');
        var texts = [];
        segments.forEach(function(segment) {
            texts.push(segment.textContent.trim());
        });
        return texts;
        """

        # Executar o script e obter os textos
        texts = driver.execute_script(script)
        
        if not texts:
            print("Nenhuma transcrição foi encontrada")
            return False

        # Salvar os textos em um arquivo .txt
        with open(output_file, "w", encoding="utf-8") as file:
            for text in texts:
                file.write(text + "\n")

        print(f"Transcrição salva com sucesso em: {output_file}")
        print(f"Total de segmentos extraídos: {len(texts)}")
        return True

    except Exception as e:
        print(f"Erro durante a extração da transcrição: {e}")
        return False
    finally:
        driver.quit()
        print("Driver fechado")