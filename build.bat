@echo off
rem Gera dist\Transcritor\Transcritor.exe (pasta, sem o modelo Whisper)
cd /d "%~dp0"
.venv\Scripts\flet.exe pack app.py -D -y -n Transcritor -i assets\icon.ico --distpath dist --product-name Transcritor --pyinstaller-build-args=--collect-all=faster_whisper --pyinstaller-build-args=--collect-all=ctranslate2 --pyinstaller-build-args=--collect-all=av --pyinstaller-build-args=--collect-all=onnxruntime
