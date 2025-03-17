import sounddevice as sd
import scipy.io.wavfile as wav
import numpy
import tempfile

# 音声データを操作するクラス
class Audio:
    def __init__(self, device_name, duration, sample_rate, mic_channel, speaker_channel):
        self.duration = duration
        self.sample_rate = sample_rate
        self.mic_channel = mic_channel
        self.speaker_channel = speaker_channel
        
        # デバイス名からデバイスIDを取得
        self.device_id = None
        devices = sd.query_devices()
        for id, device in enumerate(devices):
            if device_name in device['name']:
                self.device_id = id
                break
        if self.device_id is None:
            raise ValueError(f"デバイス '{device_name}' が見つかりませんでした。処理を中止します。利用可能なデバイス: {[d['name'] for d in devices]}")

    # マイク入力とスピーカー出力を合成した音声ファイル(.wav)を作成
    def create_wav_file(self):
        # 音声データを取得
        audio_data = self.__rec()
        
        # マイク入力とスピーカー出力を選択
        mic_audio = audio_data[:, self.mic_channel]
        speaker_audio = audio_data[:, self.speaker_channel]
        
        # 2つのチャンネルを結合
        combined_audio = numpy.column_stack((mic_audio, speaker_audio))
        
        # float32からint16に変換
        combined_audio_int16 = (combined_audio * 32767).astype(numpy.int16)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir="./output") as temp_audio_file:
            wav.write(temp_audio_file.name, self.sample_rate, combined_audio_int16)
            return temp_audio_file.name
        
    # 音声の入力デバイスを設定
    def __setup_device(self):
        sd.default.device = (self.device_id, None)
        
    # 音声の録音
    def __rec(self):
        self.__setup_device()

        # 入力音声を録音
        flames = int(self.duration * self.sample_rate)
        audio_data = sd.rec(flames, samplerate=self.sample_rate, channels=3, dtype='float32')
        sd.wait()
        return audio_data