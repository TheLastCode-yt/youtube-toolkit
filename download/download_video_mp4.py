from pytubefix import YouTube
import os


def download_video_as_mp4(youtube_url, output_path="."):
    print("Baixando video...")
    # Baixar o video
    yt = YouTube(youtube_url)
    video = yt.streams.filter(file_extension="mp4").first()

    out_file = video.download(output_path=output_path)

    if not os.path.isfile(out_file):
        raise FileNotFoundError(f"Arquivo de video não encontrado: {out_file}")

    # Renomear o arquivo para MP4, se você quiser
    base, ext = os.path.splitext(out_file)
    mp4_file = base + ".mp4"
    os.rename(out_file, mp4_file)

    return mp4_file


if __name__ == "__main__":
    youtube_url = "https://studio.youtube.com/video/AbhGeZUG5dE/edit"
    output_path = "."  # Defina o diretório de saída, se você quiser

    try:
        # Chama a função para baixar o video
        mp4_file = download_video_as_mp4(youtube_url, output_path)
        print(f"Video MP4 salvo em: {mp4_file}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
