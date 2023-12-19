import os
import shutil
import openai
from googletrans import Translator
import time
openai.api_key = os.getenv("OPENAI_API_KEY")

def translate_text(text, target_lang='en'):
    translator = Translator()
    translated = translator.translate(text, src='ja', dest=target_lang)
    return translated.text

def move_wav_files(source_folder, destination_folder):
    try:
        # 移動先フォルダが存在しない場合は作成
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # 移動元フォルダ内のファイル一覧を取得し、更新日時でソート
        files = os.listdir(source_folder)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(source_folder, x)))

        # .wavファイルを見つけて移動
        for file in files:
            if file.endswith(".wav"):
                source_file = os.path.join(source_folder, file)
                destination_file = os.path.join(destination_folder, file)
                try:
                    shutil.move(source_file, destination_file)
                    # print(f"Moved {file} to {destination_folder}")

                    # 音声ファイルを文字変換
                    audio_file= open(destination_file, "rb")
                    transcript = openai.Audio.transcribe("whisper-1", audio_file)
                    transcription = str(transcript["text"])
                    translated_text = translate_text(transcription)
                    print(transcription)
                    print(translated_text)

                except Exception as e:
                    print(f"Error moving {file}: {str(e)}. Skipping.")

        # print("File moving completed.")

    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    source_folder = "./audio/"  # 移動元フォルダのパスを指定
    destination_folder = "./audio_out/"  # 移動先フォルダのパスを指定
    while True:
        move_wav_files(source_folder, destination_folder)
        time.sleep(1)

