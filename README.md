# whisper-realtime-with-gui

refs: https://github.com/openai/whisper

## Install
Assuming Python 3.9.9 is installed.
You can execute `setup.command`.
```sh
brew install ffmpeg # requires by whisper
brew install blackhole-2ch # combine mic and speaker
# You must reboot for the installation of blackhole-2ch to take effect.
brew install pipenv
pipenv install
```

### beta
You should setup ollama if you want to summarize.
```sh
brew install ollama # for summarize
ollama serve
ollama pull gemma3
```

## Settings
### Audio MIDI Settings
Create "機器セット" like this screenshot.
![MIDI Settings Screenshot](midi.png)

## Start
You can execute `start.command`.
```sh
pipenv run python main.py
# A GUI with “Start” and “Stop” buttons will launch.
# Pressing “Start” begins voice recognition, and pressing “Stop” stops it.
# First time, you need to download whisper model.
# So, it takes a little time to start up.
```
