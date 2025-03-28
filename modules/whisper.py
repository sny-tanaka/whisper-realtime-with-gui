import datetime
import mlx_whisper
import os
import threading
import queue

import modules.audio as audio
import modules.diarization as diarization
import modules.logger as logger

class Whisper:
    def __init__(self, model, logger: logger.Logger, audio: audio.Audio, diarization: diarization.Diarization):
        self.logger = logger
        self.stop_event = None
        self.thread = None
        self.audio_queue = queue.Queue()
        self.audio = audio
        self.model = model
        self.finished = False
        self.diarization = diarization
        self.__set_output_file()

    # リアルタイム音声認識を開始する
    def start(self):
        if self.finished:
            self.__set_output_file()
            self.finished = False
        self.__start_main_thread()
        self.logger.write("リアルタイム音声認識を開始しました")
        self.logger.write(f"結果は {self.output_file} に出力されます")

    # リアルタイム音声認識を停止する
    def stop(self):
        self.logger.write("リアルタイム音声認識を停止します。しばらくお待ち下さい。")
        self.stop_event.set()
        self.thread.join()
        # 録音されたものがまだ残っている場合は処理する
        while not self.audio_queue.empty():
            self.__put_text_transcription()
        self.logger.write("リアルタイム音声認識を停止しました")
        self.logger.write(f"結果は {self.output_file} に出力されています")

        self.finished = True

    # リアルタイム音声認識を一時停止する
    def pause(self):
        self.logger.write("リアルタイム音声認識を一時停止します。")
        self.stop_event.set()
        self.thread.join()
        self.logger.write("リアルタイム音声認識を一時停止しました")

    # サンプル音声ファイルを文字起こしする
    def sample(self):
        self.logger.write("これはテストです。正しく音声認識ができているかを確認しています。")
        self.logger.write("という合成音声の文字起こしを行います。このあとに文字起こしの結果が表示されます。")

        for waveform, speaker in self.diarization.generate("sample.mp3"):
            text = self.__transcribe_audio(waveform, should_delete=False)
            formatted = f"({speaker}) {text}"
            self.logger.write(formatted)
        self.logger.write("サンプル音声の文字起こしが完了しました。")
    
    # 起動中かどうかを返す
    def is_running(self):
        return self.thread is not None and self.thread.is_alive()
    
    # スレッドを立て直す
    def __start_main_thread(self):
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.__realtime_transcription)
        self.thread.start()

    # 出力ファイル名を設定する
    def __set_output_file(self):
        start_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.output_file = os.path.join("./output", f'{start_time}.txt')

    # キューから音声ファイルを取り出して文字起こしし、ファイルに書き込む
    def __put_text_transcription(self):
        # キューから音声ファイルを取得し、Whisperで文字起こし
        audio_file = self.audio_queue.get(timeout=1)
        
        # 話者分離
        for waveform, speaker in self.diarization.generate(audio_file):
            text = self.__transcribe_audio(waveform)
            formatted = f"({speaker}) {text}"
            self.logger.write(formatted)

            # テキストをファイルに改行区切りで書き込み
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(formatted + '\n')

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
