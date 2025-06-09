import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from download.download_audio_mp3 import download_audio_as_mp3
from download.download_video_mp4 import download_video_as_mp4
from download.download_thumbnail import download_thumbnail
from transcript.transcript_extractor import get_transcription
from transcript.translator import translate_text


# ================ FUNÇÕES TAB 1 ================
def run_script_tab1():
    youtube_url = url_entry_tab1.get()
    output_path = output_path_var_tab1.get()
    if not youtube_url or not output_path:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
        return

    script = script_var_tab1.get()
    
    def execute_in_thread():
        try:
            if script == "audio":
                log_message_tab1("Iniciando o download do áudio MP3...")
                mp3_file = download_audio_as_mp3(youtube_url, output_path)
                log_message_tab1(f"Áudio MP3 salvo em: {mp3_file}")
            elif script == "thumbnail":
                log_message_tab1("Iniciando o download da thumbnail...")
                download_thumbnail(youtube_url, output_path)
                log_message_tab1("Thumbnail salva com sucesso!")
            elif script == "video":
                log_message_tab1("Iniciando o download do vídeo MP4...")
                mp4_file = download_video_as_mp4(youtube_url, output_path)
                log_message_tab1(f"Vídeo MP4 salvo em: {mp4_file}")
            else:
                messagebox.showerror("Erro", "Selecione um script válido.")
        except Exception as e:
            log_message_tab1(f"Ocorreu um erro: {e}")
        finally:
            # Reabilitar o botão após execução
            execute_button_tab1.config(state='normal')
    
    # Desabilitar o botão durante execução
    execute_button_tab1.config(state='disabled')
    
    # Executar em thread separada para não travar a interface
    thread = threading.Thread(target=execute_in_thread)
    thread.daemon = True
    thread.start()


def log_message_tab1(message):
    display_text_tab1.insert(tk.END, message + "\n")
    display_text_tab1.yview(tk.END)
    root.update_idletasks()


def select_output_directory_tab1():
    directory = filedialog.askdirectory()
    if directory:
        output_path_var_tab1.set(directory)


# ================ FUNÇÕES TAB 2 ================
def run_transcription():
    youtube_url = url_entry_tab2.get()
    output_path = output_path_var_tab2.get()
    
    if not youtube_url or not output_path:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
        return
    
    def execute_transcription():
        try:
            log_message_tab2("Iniciando extração de transcrição...")
            
            # Criar diretório de texto se não existir
            text_dir = os.path.join(output_path, "text")
            os.makedirs(text_dir, exist_ok=True)
            
            output_file = os.path.join(text_dir, "transcription.txt")
            
            success = get_transcription(youtube_url, output_file)
            
            if success:
                log_message_tab2(f"Transcrição salva com sucesso em: {output_file}")
                
                # Habilitar botão de tradução se transcrição foi bem-sucedida
                translate_button_tab2.config(state='normal')
            else:
                log_message_tab2("Erro ao extrair transcrição. Verifique a URL e tente novamente.")
                
        except Exception as e:
            log_message_tab2(f"Erro durante a transcrição: {e}")
        finally:
            transcribe_button_tab2.config(state='normal')
    
    # Desabilitar botão durante execução
    transcribe_button_tab2.config(state='disabled')
    translate_button_tab2.config(state='disabled')
    
    # Executar em thread separada
    thread = threading.Thread(target=execute_transcription)
    thread.daemon = True
    thread.start()


def run_translation():
    output_path = output_path_var_tab2.get()
    
    if not output_path:
        messagebox.showerror("Erro", "Por favor, selecione o diretório de saída.")
        return
    
    def execute_translation():
        try:
            log_message_tab2("Iniciando tradução...")
            
            text_dir = os.path.join(output_path, "text")
            input_file = os.path.join(text_dir, "transcription.txt")
            output_file = os.path.join(text_dir, "translated_text.txt")
            
            if not os.path.exists(input_file):
                log_message_tab2("Arquivo de transcrição não encontrado. Execute a transcrição primeiro.")
                return
            
            success = translate_text(input_file, output_file)
            
            if success:
                log_message_tab2(f"Tradução salva com sucesso em: {output_file}")
            else:
                log_message_tab2("Erro durante a tradução. Verifique o arquivo de transcrição.")
                
        except Exception as e:
            log_message_tab2(f"Erro durante a tradução: {e}")
        finally:
            translate_button_tab2.config(state='normal')
    
    # Desabilitar botão durante execução
    translate_button_tab2.config(state='disabled')
    
    # Executar em thread separada
    thread = threading.Thread(target=execute_translation)
    thread.daemon = True
    thread.start()


def run_both_tab2():
    """Executa transcrição e tradução em sequência"""
    youtube_url = url_entry_tab2.get()
    output_path = output_path_var_tab2.get()
    
    if not youtube_url or not output_path:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
        return
    
    def execute_both():
        try:
            # Desabilitar todos os botões
            transcribe_button_tab2.config(state='disabled')
            translate_button_tab2.config(state='disabled')
            both_button_tab2.config(state='disabled')
            
            log_message_tab2("Iniciando processo completo (Transcrição + Tradução)...")
            
            # Criar diretório de texto se não existir
            text_dir = os.path.join(output_path, "text")
            os.makedirs(text_dir, exist_ok=True)
            
            # Executar transcrição
            transcription_file = os.path.join(text_dir, "transcription.txt")
            log_message_tab2("1/2 - Extraindo transcrição...")
            
            success_transcription = get_transcription(youtube_url, transcription_file)
            
            if success_transcription:
                log_message_tab2("Transcrição concluída com sucesso!")
                
                # Executar tradução
                translation_file = os.path.join(text_dir, "translated_text.txt")
                log_message_tab2("2/2 - Iniciando tradução...")
                
                success_translation = translate_text(transcription_file, translation_file)
                
                if success_translation:
                    log_message_tab2("✅ Processo completo concluído com sucesso!")
                    log_message_tab2(f"Transcrição: {transcription_file}")
                    log_message_tab2(f"Tradução: {translation_file}")
                else:
                    log_message_tab2("❌ Erro durante a tradução.")
            else:
                log_message_tab2("❌ Erro durante a transcrição.")
                
        except Exception as e:
            log_message_tab2(f"Erro durante o processo: {e}")
        finally:
            # Reabilitar botões
            transcribe_button_tab2.config(state='normal')
            translate_button_tab2.config(state='normal')
            both_button_tab2.config(state='normal')
    
    # Executar em thread separada
    thread = threading.Thread(target=execute_both)
    thread.daemon = True
    thread.start()


def log_message_tab2(message):
    display_text_tab2.insert(tk.END, message + "\n")
    display_text_tab2.yview(tk.END)
    root.update_idletasks()


def select_output_directory_tab2():
    directory = filedialog.askdirectory()
    if directory:
        output_path_var_tab2.set(directory)


def clear_log_tab2():
    display_text_tab2.delete(1.0, tk.END)


# ================ INTERFACE PRINCIPAL ================
# Criação da janela principal
root = tk.Tk()
root.title("YouTube Tools")
root.geometry("900x600")
root.resizable(True, True)

# Notebook para abas
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=10)

# ================ TAB 1 ================
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text='Download (Áudio, Vídeo, Thumbnail)')

# Frame principal da Tab 1
frame_tab1 = ttk.Frame(tab1)
frame_tab1.pack(fill='both', expand=True, padx=10, pady=10)

tk.Label(frame_tab1, text="URL do vídeo", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=10, sticky="w")
url_entry_tab1 = tk.Entry(frame_tab1, width=70, font=('Arial', 9))
url_entry_tab1.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

tk.Label(frame_tab1, text="Selecione a função", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=10, pady=10, sticky="w")
script_var_tab1 = tk.StringVar(value="video")
tk.Radiobutton(frame_tab1, text="Baixar Áudio (MP3)", variable=script_var_tab1, value="audio", font=('Arial', 9)).grid(row=1, column=1, sticky="w")
tk.Radiobutton(frame_tab1, text="Baixar Vídeo (MP4)", variable=script_var_tab1, value="video", font=('Arial', 9)).grid(row=2, column=1, sticky="w")
tk.Radiobutton(frame_tab1, text="Baixar Thumbnail", variable=script_var_tab1, value="thumbnail", font=('Arial', 9)).grid(row=3, column=1, sticky="w")

tk.Label(frame_tab1, text="Diretório de saída", font=('Arial', 10, 'bold')).grid(row=4, column=0, padx=10, pady=10, sticky="w")
output_path_var_tab1 = tk.StringVar()
output_path_entry_tab1 = tk.Entry(frame_tab1, textvariable=output_path_var_tab1, width=60, font=('Arial', 9))
output_path_entry_tab1.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
tk.Button(frame_tab1, text="Selecionar Diretório", command=select_output_directory_tab1, font=('Arial', 9)).grid(row=4, column=2, padx=10, pady=10)

execute_button_tab1 = tk.Button(frame_tab1, text="Executar", command=run_script_tab1, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
execute_button_tab1.grid(row=5, column=1, pady=20)

tk.Label(frame_tab1, text="Log de execução:", font=('Arial', 10, 'bold')).grid(row=6, column=0, padx=10, pady=(10,5), sticky="w")
display_text_tab1 = tk.Text(frame_tab1, height=12, width=100, font=('Consolas', 9))
display_text_tab1.grid(row=7, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

# Scrollbar para o log da Tab 1
scrollbar_tab1 = ttk.Scrollbar(frame_tab1, orient="vertical", command=display_text_tab1.yview)
scrollbar_tab1.grid(row=7, column=3, sticky="ns", pady=5)
display_text_tab1.configure(yscrollcommand=scrollbar_tab1.set)

# Configurar redimensionamento da Tab 1
frame_tab1.grid_columnconfigure(1, weight=1)
frame_tab1.grid_rowconfigure(7, weight=1)

# ================ TAB 2 ================
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text='Transcrição e Tradução')

# Frame principal da Tab 2
frame_tab2 = ttk.Frame(tab2)
frame_tab2.pack(fill='both', expand=True, padx=10, pady=10)

# Entrada de URL
tk.Label(frame_tab2, text="URL do vídeo do YouTube", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=10, sticky="w")
url_entry_tab2 = tk.Entry(frame_tab2, width=70, font=('Arial', 9))
url_entry_tab2.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

# Diretório de saída
tk.Label(frame_tab2, text="Diretório de saída", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=10, pady=10, sticky="w")
output_path_var_tab2 = tk.StringVar()
output_path_entry_tab2 = tk.Entry(frame_tab2, textvariable=output_path_var_tab2, width=60, font=('Arial', 9))
output_path_entry_tab2.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
tk.Button(frame_tab2, text="Selecionar Diretório", command=select_output_directory_tab2, font=('Arial', 9)).grid(row=1, column=2, padx=10, pady=10)

# Frame para botões
button_frame = ttk.Frame(frame_tab2)
button_frame.grid(row=2, column=0, columnspan=3, pady=20)

transcribe_button_tab2 = tk.Button(button_frame, text="Extrair Transcrição", command=run_transcription, 
                                  bg='#2196F3', fg='white', font=('Arial', 10, 'bold'), width=18)
transcribe_button_tab2.pack(side='left', padx=5)

translate_button_tab2 = tk.Button(button_frame, text="Traduzir", command=run_translation, 
                                 bg='#FF9800', fg='white', font=('Arial', 10, 'bold'), width=18, state='disabled')
translate_button_tab2.pack(side='left', padx=5)

both_button_tab2 = tk.Button(button_frame, text="Transcrever + Traduzir", command=run_both_tab2, 
                            bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), width=20)
both_button_tab2.pack(side='left', padx=5)

clear_button_tab2 = tk.Button(button_frame, text="Limpar Log", command=clear_log_tab2, 
                             bg='#f44336', fg='white', font=('Arial', 10, 'bold'), width=12)
clear_button_tab2.pack(side='left', padx=5)

# Área de informações
info_frame = ttk.LabelFrame(frame_tab2, text="Informações", padding=10)
info_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

info_text = """
• Transcrição: Extrai a transcrição automática do YouTube usando Selenium
• Tradução: Traduz o texto extraído do inglês para português usando Google Translate  
• Os arquivos serão salvos na pasta 'text' dentro do diretório selecionado
• Arquivos gerados: transcription.txt e translated_text.txt
"""

tk.Label(info_frame, text=info_text, justify='left', font=('Arial', 9)).pack(anchor='w')

# Log de execução
tk.Label(frame_tab2, text="Log de execução:", font=('Arial', 10, 'bold')).grid(row=4, column=0, padx=10, pady=(10,5), sticky="w")
display_text_tab2 = tk.Text(frame_tab2, height=15, width=100, font=('Consolas', 9))
display_text_tab2.grid(row=5, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

# Scrollbar para o log da Tab 2
scrollbar_tab2 = ttk.Scrollbar(frame_tab2, orient="vertical", command=display_text_tab2.yview)
scrollbar_tab2.grid(row=5, column=3, sticky="ns", pady=5)
display_text_tab2.configure(yscrollcommand=scrollbar_tab2.set)

# Configurar redimensionamento da Tab 2
frame_tab2.grid_columnconfigure(1, weight=1)
frame_tab2.grid_rowconfigure(5, weight=1)

# Inicializa a interface
if __name__ == "__main__":
    root.mainloop()