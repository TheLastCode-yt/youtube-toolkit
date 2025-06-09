from pytubefix import YouTube
import os

def download_audio_as_mp3(youtube_url, output_path="."):
    print("Baixando áudio...")
    # Baixar o vídeo
    yt = YouTube(youtube_url)
    video = yt.streams.filter(only_audio=True).first()

    out_file = video.download(output_path=output_path)

    if not os.path.isfile(out_file):
        raise FileNotFoundError(f"Arquivo de áudio não encontrado: {out_file}")

    # Renomear o arquivo para MP3, se necessário
    base, ext = os.path.splitext(out_file)
    mp3_file = base + ".mp3"
    os.rename(out_file, mp3_file)

    return mp3_file

if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=rBKweNDaY8A"
    output_path = "."  # Defina o diretório de saída, se necessário

    try:
        # Chama a função para baixar o áudio
        mp3_file = download_audio_as_mp3(youtube_url, output_path)
        print(f"Áudio MP3 salvo em: {mp3_file}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
