from dotenv import load_dotenv
import os
import tkinter

import audio
import whisper

class WhisperApp:
    def __init__(self):
        self.wp = None

    def start(self):
        print("起動中です。しばらくお待ち下さい。")

        # .envから設定値を取得
        load_dotenv()

        ad = audio.Audio(
            device_name=os.environ['AUDIO_DEVICE_NAME'],
            duration=int(os.environ['AUDIO_DURATION']),
            sample_rate=int(os.environ['AUDIO_SAMPLE_RATE']),
            mic_channel=int(os.environ['AUDIO_MIC_CHANNEL']),
            speaker_channel=int(os.environ['AUDIO_SPEAKER_CHANNEL'])
        )
        self.wp = whisper.Whisper(audio=ad, on_console=bool(os.environ['ON_CONSOLE']))
        self.wp.start()

    def stop(self):
        self.wp.stop()

    def graphics(self):
        root = tkinter.Tk()
        root.title("リアルタイム音声文字起こし")
        root.geometry("200x100")

        start_button = tkinter.Button(root, text="Start", command=self.start)
        start_button.pack()

        stop_button = tkinter.Button(root, text="Stop", command=self.stop)
        stop_button.pack()

        root.mainloop()

def main():
    app = WhisperApp()
    app.graphics()

if __name__ == "__main__":
    main()
