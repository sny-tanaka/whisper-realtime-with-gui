from dotenv import load_dotenv
import os
import webview

import audio
import llm
import whisper

class WhisperApp:
    def __init__(self):
        self.wp = None
        self.llm = None

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

    def setup_llm(self):
        self.llm = llm.LLM(model="llama-3-elyza-8b")

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

    # 調整中
    # まともに要約してくれないので今は使うべきでない
    def summarize(self):
        if self.llm is None:
            self.setup_llm()
        print("要約を生成します")
        role_prompt = "ユーザから与えられたミーティングの文字起こしデータをもとに、その議事録を作成してください。文字起こしの性質上、誤った文字になっていたり、関係ない音を文字起こししてしまっている可能性がありますが、文脈から推測してください。"
        output_format_prompt = "議事録はマークダウンで出力してください。文字起こしデータに登場するすべての議題を含めてください。省略はしないでください。"
        human_prompt = "ひとつ前の投稿がミーティングの文字起こしデータです。リリースが何件あったかなど読み取ってまとめてください。"
        transcribed_text = ""
        file_name = ""
        with open(f"output/{file_name}.txt", "r") as f:
            transcribed_text = f.read()
        result = self.llm.generate([
            llm.LLM.create_message("system", role_prompt),
            llm.LLM.create_message("system", output_format_prompt),
            llm.LLM.create_message("human", transcribed_text),
            llm.LLM.create_message("human", human_prompt),
        ])
        # ファイルに書き込む
        with open(f"output/{file_name}.md", "w") as f:
            f.write(result)
        print("要約が生成されました")

    def text(self, text):
        return text

    def graphics(self):
        window = webview.create_window(
            title="リアルタイム音声文字起こし",
            url="web/index.html",
            js_api=self
        )
        webview.start()

def main():
    app = WhisperApp()
    app.graphics()

if __name__ == "__main__":
    main()
