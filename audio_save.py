import pyaudio
import wave
import audioop
import keyboard
from datetime import datetime
import time

def is_silent(data, threshold):
    rms = audioop.rms(data, 2)
    return rms < threshold

def record_audio_with_silence_detection(output_prefix, silence_threshold=200, min_silence_duration=3, min_record_duration=1, sample_rate=44100, chunk_size=1024, channels=2):
    audio_format = pyaudio.paInt16
    p = pyaudio.PyAudio()

    DEVICE_INDEX = 0  # デフォルトのマイクインデックスを0とします
    stream = p.open(format=audio_format,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk_size, input_device_index=DEVICE_INDEX)

    print("録音を開始します。録音を停止するにはスペースキーを押してください。")

    frames = []
    recording = False
    silence_duration = 0
    last_record_time = time.time()

    for _ in range(0, int(sample_rate / chunk_size * min_silence_duration)):
        data = stream.read(chunk_size)
        if is_silent(data, silence_threshold):
            silence_duration += 1
        else:
            silence_duration = 0
            break

    while True:
        try:
            data = stream.read(chunk_size)
            frames.append(data)

            if recording and is_silent(data, silence_threshold):
                silence_duration += 1
                if silence_duration >= int(sample_rate / chunk_size * min_silence_duration):
                    print(f"無音時間が{min_silence_duration}秒間続きました。録音を停止します。")
                    recording = False
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # ミリ秒まで含める
                    file_path = f"{output_prefix}_{timestamp}.wav"
                    save_audio(file_path, frames, sample_rate, channels, audio_format)
                    frames = []
                    last_record_time = time.time()

            else:
                silence_duration = 0
                if not recording and not is_silent(data, silence_threshold) and time.time() - last_record_time >= min_record_duration:
                    print("音が検出されました。録音を開始します。")
                    recording = True

            if recording and   keyboard.is_pressed("space"):
                print("スペースキーが押されました。録音を停止します。")
                recording = False
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # ミリ秒まで含める
                file_path = f"{output_prefix}_{timestamp}.wav"
                save_audio(file_path, frames, sample_rate, channels, audio_format)
                frames = []
                last_record_time = time.time()

        except KeyboardInterrupt:
            # Ctrl-Cが押された場合
            break
    
    # キーが押されたら最後のファイルを保存
    if recording:
        print("録音が終了しました。最後のファイルを保存します。")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # ミリ秒まで含める
        file_path = f"{output_prefix}_{timestamp}.wav"
        save_audio(file_path, frames, sample_rate, channels, audio_format)

    print("録音が終了しました。")

    stream.stop_stream()
    stream.close()
    p.terminate()

def save_audio(filename, frames, sample_rate, channels, audio_format):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(pyaudio.get_sample_size(audio_format))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

if __name__ == "__main__":
    output_prefix = "./audio/recorded_audio"  # 保存する音声ファイルの接頭辞
    silence_threshold = 300  # 無音と判定する閾値
    min_silence_duration = 1  # 無音と判定する最小の時間（秒）
    min_record_duration = 1  # 最小の録音時間（秒）

    record_audio_with_silence_detection(output_prefix, silence_threshold, min_silence_duration, min_record_duration)

