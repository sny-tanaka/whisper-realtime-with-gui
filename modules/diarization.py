from pyannote.audio import Pipeline, Audio

class Diarization:
    def __init__(self, speaker_count, token):
        self.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=token)
        self.audio = Audio(sample_rate=16000)
        self.speaker_count = speaker_count

    # 音声ファイルを分割して話者ごとに分ける
    # @return (分割後の音声, 話者ID)
    def generate(self, audio_file):
        print("start diarization")
        diarization = self.pipeline(audio_file, num_speakers=self.speaker_count)
        print("end diarization")
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            print(f"speaker: {speaker}")
            waveform, _ = self.audio.crop(audio_file, segment)
            print("end crop")
            yield (waveform.squeeze().numpy(), speaker)
