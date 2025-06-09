import re


def clean_and_prepare_text(transcription):
    cleaned_transcription = re.sub(r"\d+:\d+\n", "", transcription)
    final_transcription = cleaned_transcription.replace("\n", " ")
    return final_transcription

def remove_extra_spaces(text):
    return re.sub(r'\s+', ' ', text).strip()

if __name__ == "__main__":
    with open ('./text/remove_time.txt', 'r', encoding='utf-8') as file:
        file_text = file.read()
    
    transcription = clean_and_prepare_text(file_text)
    transcription = remove_extra_spaces(transcription)

    with open('./text/remove_time.txt', 'w', encoding='utf-8') as output_file:
        output_file.write(transcription)

    print(transcription)
