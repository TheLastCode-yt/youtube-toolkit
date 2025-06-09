from pytubefix import YouTube
import os
import urllib.request


def download_thumbnail(youtube_url, output_path="."):
    print("Baixando thumbnail...")
    video = YouTube(youtube_url)
    thumbnail_url = video.thumbnail_url
    urllib.request.urlretrieve(
        thumbnail_url, os.path.join(output_path, "thumbnail.jpg")
    )


if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=AbhGeZUG5dE&feature=youtu.be"
    output_path = "."  # Defina o diretório de saída, se você quiser

    try:
        print("Baixando thumbnail...")
        download_thumbnail(youtube_url, output_path)
    except Exception as e:
        print(f"Ocorreu um erro ao baixar a thumbnail: {e}")
