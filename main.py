import json
import webview

import modules.audio as audio
import modules.diarization as diarization
import modules.logger as logger
import modules.whisper as whisper

class WhisperApp:
    def __init__(self):
        self.logger = logger.Logger()
        self.wp = None

    def get_logs(self):
        return self.logger.pick()

    def load_settings(self):
        # settings.jsonから設定を読み込む
        with open("settings.json", "r") as f:
            return json.load(f)
        
    def save_settings(self, whisper_model, audio_device_name):
        settings = {
            "whisper_model": whisper_model,
            "audio_device_name": audio_device_name
        }
        # settings.jsonに設定を保存
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)
    
    def start(self):
        self.logger.write("起動中です。しばらくお待ち下さい。")

        if self.wp is None:
            self.__setup()
        
        self.wp.start()

    def stop(self):
        if self.wp is not None:
            self.wp.stop()

    def pause(self):
        if self.wp is not None:
            self.wp.pause()

    def test(self):
        if self.wp is None:
            self.__setup()

        self.wp.sample()

    def graphics(self):
        webview.create_window(
            title="リアルタイム音声文字起こし",
            url="web/index.html",
            js_api=self
        )
        webview.start()

    def __setup(self):
        settings = self.load_settings()
        ad = audio.Audio(
            device_name=settings['audio_device_name'],
            duration=10,
            sample_rate=16000,
            mic_channel=2,
            speaker_channel=0
        )
        di = diarization.Diarization(
            speaker_count=2,
            token=""
        )
        self.wp = whisper.Whisper(
            model=settings['whisper_model'],
            logger=self.logger,
            audio=ad,
            diarization=di
        )

def main():
    app = WhisperApp()
    app.graphics()

if __name__ == "__main__":
    main()
