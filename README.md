# Transcritor_wpp

App desktop para Windows que transcreve áudios do WhatsApp (e outros) para texto, localmente e sem enviar nada para a internet. Usa [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (modelo `small`, CPU) e interface em [Flet](https://flet.dev).

## Recursos

- Transcrição em português de `.ogg`, `.opus`, `.mp3`, `.m4a`, `.wav` e `.mp4`
- Barra de progresso e filtro de silêncio (VAD)
- Lista das transcrições anteriores, com botões para copiar o texto e abrir a pasta
- Vocabulário próprio para acertar nomes (edite `VOCABULARIO` em `transcricao.py`)

As transcrições ficam em `Documentos\Transcricoes`. No primeiro uso o modelo (~480 MB) é baixado para o cache do usuário.

## Rodar pelo código

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python app.py
```

## Gerar o executável

```
build.bat      # gera dist\Transcritor\Transcritor.exe
instalar.bat   # copia para %LOCALAPPDATA%\Programs\Transcritor e cria os atalhos
```

O `build.bat` usa o PyInstaller via `flet pack`. O ícone pode ser regerado com `gerar_icone.py` (requer Pillow).

## Estrutura

- `app.py` — interface Flet
- `transcricao.py` — lógica de transcrição, sem UI
- `assets/` — ícone
