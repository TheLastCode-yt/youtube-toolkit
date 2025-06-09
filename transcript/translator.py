from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from .text_utils import clean_and_prepare_text
import time
import os


def split_string_by_length(s, cut_length):
    print(f"Quantidade total de caracteres: {len(s)}")
    if cut_length <= 0:
        raise ValueError("O comprimento de corte deve ser maior que zero.")
    result = [s[i : i + cut_length] for i in range(0, len(s), cut_length)]
    return result


def translate_text(input_file_path, output_file_path):
    # Ler o arquivo de entrada
    try:
        with open(input_file_path, "r", encoding="utf-8") as file:
            file_text = file.read()
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {input_file_path}")
        return False
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return False

    transcription = clean_and_prepare_text(file_text)
    transcription_chunks = split_string_by_length(transcription, 4500)

    # Limpar arquivo de saída
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write("")

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

    print("INICIALIZANDO GOOGLE TRANSLATE")

    try:
        driver.get("https://translate.google.com/?hl=pt-BR&tab=wT&sl=en&tl=pt&op=translate")
        print("Google Translate carregado com sucesso")

        # Código JavaScript para coletar os textos traduzidos
        script = """
        var segments = document.querySelectorAll('span.ryNqvb');
        var texts = [];
        segments.forEach(function(segment) {
            texts.push(segment.textContent.trim());
        });
        return texts.join(' ');
        """

        for i, chunk in enumerate(transcription_chunks):
            print(f"Traduzindo chunk {i + 1}/{len(transcription_chunks)}")

            try:
                # XPath para a área de texto de entrada
                xpath_textarea = '//textarea[@aria-label="Texto de origem"]'
                
                # Aguardar elemento aparecer
                textarea = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, xpath_textarea))
                )

                if i > 0:
                    # Limpar texto anterior
                    print("LIMPANDO O TEXTO")
                    try:
                        # Tentar diferentes seletores para o botão de limpar
                        clear_selectors = [
                            '//button[@aria-label="Limpar texto de origem"]',
                            '//button[contains(@class, "clear")]',
                            '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz[1]/div[1]/div/div[1]/span/button'
                        ]
                        
                        cleared = False
                        for selector in clear_selectors:
                            try:
                                btn_clear = driver.find_element(By.XPATH, selector)
                                btn_clear.click()
                                cleared = True
                                break
                            except NoSuchElementException:
                                continue
                        
                        if not cleared:
                            # Se não encontrou o botão, limpar manualmente
                            textarea.clear()
                            
                        time.sleep(2)
                    except Exception as clear_error:
                        print(f"Erro ao limpar texto: {clear_error}")
                        textarea.clear()

                # Enviar novo texto
                textarea.clear()
                time.sleep(2)
                textarea.send_keys(chunk)
                print(f"Texto do chunk {i + 1} enviado para tradução")

                # Aguardar tradução
                time.sleep(12)

                # Executar script para obter tradução
                translated_text = driver.execute_script(script)
                
                if not translated_text or translated_text.strip() == "":
                    print(f"Tradução vazia para chunk {i + 1}, tentando novamente...")
                    time.sleep(5)
                    translated_text = driver.execute_script(script)

                print(f"Texto traduzido do chunk {i + 1}: {translated_text[:100]}...")

                # Salvar no arquivo
                with open(output_file_path, "a", encoding="utf-8") as output_file:
                    output_file.write(f"Chunk {i + 1}:\n{translated_text}\n\n")

            except TimeoutException:
                print(f"Timeout ao processar chunk {i + 1}")
                continue
            except Exception as chunk_error:
                print(f"Erro ao processar chunk {i + 1}: {chunk_error}")
                continue

        print("Tradução concluída com sucesso!")
        return True

    except Exception as e:
        print(f"Erro durante a tradução: {e}")
        return False
    finally:
        driver.quit()
        print("Driver fechado")