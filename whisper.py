import datetime
import mlx_whisper
import os
import threading
import queue

import audio

class Whisper:
    def __init__(self, audio: audio.Audio, on_console, model):
        self.stop_event = None
        self.thread = None
        self.audio_queue = queue.Queue()
        self.audio = audio
        self.on_console = on_console
        self.model = model

        # 起動時の日時を取得してファイル名にする（yyyymmddhhMMss）
        start_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.output_file = os.path.join("./output", f'{start_time}.txt')

    # リアルタイム音声認識を開始する
    def start(self):
        self.__start_main_thread()
        print("リアルタイム音声認識を開始しました")
        print(f"結果は {self.output_file} に出力されます")

    # リアルタイム音声認識を停止する
    def stop(self):
        print("リアルタイム音声認識を停止します。しばらくお待ち下さい。")
        self.stop_event.set()
        self.thread.join()
        # 録音されたものがまだ残っている場合は処理する
        while not self.audio_queue.empty():
            self.__put_text_transcription()
        print("リアルタイム音声認識を停止しました")
        print(f"結果は {self.output_file} に出力されています")

    # サンプル音声ファイルを文字起こしする
    def sample(self):
        return self.__transcribe_audio(
            audio_file="sample.mp3",
            should_delete=False
        )
    
    # スレッドを立て直す
    def __start_main_thread(self):
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.__realtime_transcription)
        self.thread.start()

    # キューから音声ファイルを取り出して文字起こしし、ファイルに書き込む
    def __put_text_transcription(self):
        # キューから音声ファイルを取得し、Whisperで文字起こし
        audio_file = self.audio_queue.get(timeout=1)
        text = self.__transcribe_audio(audio_file)

        if self.on_console:
            print(text)

        # テキストをファイルに改行区切りで書き込み
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(text + '\n')

    # 音声を録音してファイルを次々と作成し、キューに追加していく
    def __capture_audio(self):
        while not self.stop_event.is_set():
            # durationごとに音声ファイルを作成し、キューに追加
            wav_file = self.audio.create_wav_file()
            self.audio_queue.put(wav_file)

    # キューから音声ファイルを取得し、Whisperで文字起こし
    def __process_audio(self):
        while not self.stop_event.is_set():
            try:
                self.__put_text_transcription()
            except queue.Empty:
                # キューが空の場合は何もしないで待つ
                continue

    # 音声ファイルをリアルタイムで文字起こしするためのスレッドを起動する
    def __realtime_transcription(self):
        capture_thread = threading.Thread(target=self.__capture_audio)
        process_thread = threading.Thread(target=self.__process_audio)

        capture_thread.start()
        process_thread.start()

        capture_thread.join()
        process_thread.join()

    # 音声ファイルをWhisperで文字起こしする
    def __transcribe_audio(self, audio_file, should_delete=True):
        text = mlx_whisper.transcribe(audio_file, path_or_hf_repo=self.model)["text"]

        # 読み取りが終わったら音声ファイルを削除
        if should_delete and os.path.exists(audio_file):
            os.remove(audio_file)
        
        return text
