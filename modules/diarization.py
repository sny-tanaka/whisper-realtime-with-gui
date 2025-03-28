import os
import pathlib

from pyannote.audio import Pipeline, Audio

class Diarization:
    def __init__(self, speaker_count):
        # モデルのキャッシュディレクトリをポータブルなものに変更
        cache_dir = str(pathlib.Path("./pyannote").absolute())
        os.environ['HUGGINGFACE_HUB_CACHE'] = cache_dir
        config = pathlib.Path("./pyannote/config.yaml").absolute()
        config_dir = config.parent
        cwd = os.getcwd()
        os.chdir(config_dir)

        self.pipeline = Pipeline.from_pretrained(checkpoint_path=str(config), cache_dir=cache_dir)
        os.chdir(cwd)
        self.audio = Audio(sample_rate=16000)
        self.speaker_count = speaker_count

    # 音声ファイルを分割して話者ごとに分ける
    # @return (分割後の音声, 話者ID)
    def generate(self, audio_file):
        diarization = self.pipeline(audio_file, num_speakers=self.speaker_count)
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            try:
                waveform, _ = self.audio.crop(audio_file, segment)
                yield (waveform.squeeze().numpy(), speaker)
            except:
                continue
