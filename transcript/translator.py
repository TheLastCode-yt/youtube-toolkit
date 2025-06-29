from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .webdriver_config import create_chrome_driver, scroll_to_top
from .text_utils import clean_and_prepare_text
import time
import os


def split_string_by_length(s, cut_length):
    """
    Divide uma string em chunks de tamanho específico
    
    Args:
        s (str): String a ser dividida
        cut_length (int): Tamanho máximo de cada chunk
    
    Returns:
        list: Lista com os chunks da string
    """
    print(f"Quantidade total de caracteres: {len(s)}")
    if cut_length <= 0:
        raise ValueError("O comprimento de corte deve ser maior que zero.")
    
    result = [s[i:i + cut_length] for i in range(0, len(s), cut_length)]
    return result


def translate_text(input_file_path, output_file_path):
    """
    Traduz texto de um arquivo usando Google Translate
    
    Args:
        input_file_path (str): Caminho do arquivo de entrada
        output_file_path (str): Caminho do arquivo de saída
    
    Returns:
        bool: True se a tradução foi bem-sucedida, False caso contrário
    """
    driver = None
    try:
        # Verificar se o arquivo de entrada existe
        if not os.path.exists(input_file_path):
            print(f"Arquivo de entrada não encontrado: {input_file_path}")
            return False
        
        # Ler o arquivo de entrada
        with open(input_file_path, "r", encoding="utf-8") as file:
            file_text = file.read()
        
        if not file_text.strip():
            print("Arquivo de entrada está vazio")
            return False
        
        print("Preparando texto para tradução...")
        transcription = clean_and_prepare_text(file_text)
        transcription_chunks = split_string_by_length(transcription, 4500)
        
        # Limpar arquivo de saída
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.write("")
        
        print("Inicializando WebDriver para tradução...")
        driver = create_chrome_driver(headless=True)
        
        print("Acessando Google Translate...")
        driver.get("https://translate.google.com/?hl=pt-BR&tab=wT&sl=en&tl=pt&op=translate")
        
        # Aguardar carregamento da página
        time.sleep(5)
        
        success = _translate_chunks(driver, transcription_chunks, output_file_path)
        
        if success:
            print("Tradução concluída com sucesso!")
            return True
        else:
            print("Erro durante a tradução")
            return False
            
    except Exception as e:
        print(f"Erro durante a tradução: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()


def _translate_chunks(driver, chunks, output_file_path):
    """
    Traduz cada chunk de texto
    
    Args:
        driver: Instância do WebDriver
        chunks (list): Lista com os chunks de texto
        output_file_path (str): Caminho do arquivo de saída
    
    Returns:
        bool: True se todas as traduções foram bem-sucedidas
    """
    try:
        # Seletores para elementos do Google Translate
        selectors = {
            'textarea': [
                '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz[1]/span/span/div/textarea',
                '//textarea[@aria-label="Texto de origem"]',
                'textarea[aria-label*="source"]'
            ],
            'clear_button': [
                '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz[1]/div[1]/div/div[1]/span/button/div[3]',
                '//button[@aria-label="Limpar texto de origem"]',
                'button[aria-label*="clear"]'
            ]
        }
        
        # Script JavaScript para coletar texto traduzido
        translation_script = """
        var segments = document.querySelectorAll('span.ryNqvb');
        var texts = [];
        segments.forEach(function(segment) {
            texts.push(segment.textContent.trim());
        });
        return texts.join(' ');
        """
        
        for i, chunk in enumerate(chunks):
            print(f"Traduzindo chunk {i + 1}/{len(chunks)}")
            
            # Encontrar textarea
            textarea = None
            for selector in selectors['textarea']:
                try:
                    textarea = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not textarea:
                print("Não foi possível encontrar a textarea")
                return False
            
            # Limpar texto anterior (se não for o primeiro chunk)
            if i > 0:
                scroll_to_top(driver)
                time.sleep(1)
                print("Limpando texto anterior...")
                
                # Tentar clicar no botão de limpar
                for selector in selectors['clear_button']:
                    try:
                        clear_button = driver.find_element(By.XPATH, selector)
                        clear_button.click()
                        break
                    except:
                        continue
                
                time.sleep(2)
            
            # Inserir texto
            textarea.clear()
            time.sleep(2)
            textarea.send_keys(chunk)
            
            print(f"Texto do chunk {i + 1} enviado para tradução")
            
            # Aguardar tradução
            time.sleep(12)
            
            # Tentar obter texto traduzido
            attempts = 0
            translated_text = ""
            
            while attempts < 3 and not translated_text:
                try:
                    translated_text = driver.execute_script(translation_script)
                    if translated_text.strip():
                        break
                    time.sleep(5)
                    attempts += 1
                except Exception as e:
                    print(f"Tentativa {attempts + 1} falhou: {e}")
                    attempts += 1
                    time.sleep(5)
            
            if not translated_text.strip():
                print(f"Não foi possível obter tradução para o chunk {i + 1}")
                return False
            
            print(f"Chunk {i + 1} traduzido com sucesso")
            
            # Salvar resultado
            with open(output_file_path, "a", encoding="utf-8") as output_file:
                output_file.write(f"Chunk {i + 1}:\n{translated_text}\n\n")
        
        return True
        
    except Exception as e:
        print(f"Erro durante a tradução dos chunks: {e}")
        return False


def _wait_for_translation(driver, max_wait=15):
    """
    Aguarda a tradução ficar pronta
    
    Args:
        driver: Instância do WebDriver
        max_wait (int): Tempo máximo de espera em segundos
    
    Returns:
        bool: True se a tradução foi carregada
    """
    try:
        # Aguardar elementos da tradução aparecerem
        WebDriverWait(driver, max_wait).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.ryNqvb"))
        )
        return True
    except TimeoutException:
        return False