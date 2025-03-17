from dotenv import load_dotenv
import os
import tkinter

import audio
import whisper

class WhisperApp:
    def __init__(self):
        self.wp = None

    def setup(self):
        # .envから設定値を取得
        load_dotenv()

        ad = audio.Audio(
            device_name=os.environ['AUDIO_DEVICE_NAME'],
            duration=int(os.environ['AUDIO_DURATION']),
            sample_rate=int(os.environ['AUDIO_SAMPLE_RATE']),
            mic_channel=int(os.environ['AUDIO_MIC_CHANNEL']),
            speaker_channel=int(os.environ['AUDIO_SPEAKER_CHANNEL'])
        )
        self.wp = whisper.Whisper(
            audio=ad,
            on_console=bool(os.environ['ON_CONSOLE']),
            model=os.environ['WHISPER_MODEL']
        )

    def start(self):
        print("起動中です。しばらくお待ち下さい。")

        if self.wp is None:
            self.setup()
        
        self.wp.start()

    def stop(self):
        if self.wp is not None:
            self.wp.stop()

    def test(self):
        if self.wp is None:
            self.setup()

        print("サンプル音声ファイルを文字起こしします")
        text = self.wp.sample()
        print(text)

    def graphics(self):
        root = tkinter.Tk()
        root.title("リアルタイム音声文字起こし")
        root.geometry("200x100")

        start_button = tkinter.Button(root, text="Start", command=self.start)
        start_button.pack()

        stop_button = tkinter.Button(root, text="Stop", command=self.stop)
        stop_button.pack()

        test_button = tkinter.Button(root, text="Test", command=self.test)
        test_button.pack()

        root.mainloop()

def main():
    app = WhisperApp()
    app.graphics()

if __name__ == "__main__":
    main()
