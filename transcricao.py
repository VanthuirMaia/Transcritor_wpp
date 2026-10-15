"""Lógica de transcrição (sem UI)."""
from datetime import datetime
from pathlib import Path

from faster_whisper import WhisperModel

MODELO = "small"
EXTENSOES = {".ogg", ".opus", ".mp3", ".m4a", ".wav", ".mp4"}
# Nomes próprios que o modelo deve acertar: é só editar esta string
VOCABULARIO = "Bernhoeft, HubSpot"
MSG_MEMORIA = "Memória insuficiente. Feche outros programas e tente de novo."

_modelo = None  # cache do modelo


def pasta_dados():
    # Documentos\Transcricoes, criada se não existir
    pasta = Path.home() / "Documents" / "Transcricoes"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _erro_memoria(e):
    # Reconhece falha de alocação (mkl_malloc, MemoryError etc.)
    texto = str(e).lower()
    return isinstance(e, MemoryError) or "malloc" in texto or "alloc" in texto


def carregar_modelo():
    # Carrega só uma vez (baixa na primeira execução)
    global _modelo
    if _modelo is None:
        try:
            _modelo = WhisperModel(MODELO, device="cpu", compute_type="int8")
        except (MemoryError, RuntimeError) as e:
            if _erro_memoria(e):
                raise RuntimeError(MSG_MEMORIA) from e
            raise
    return _modelo


def transcrever(caminho_audio, ao_progresso=None):
    modelo = carregar_modelo()
    caminho_audio = Path(caminho_audio)
    partes = []
    try:
        segmentos, info = modelo.transcribe(
            str(caminho_audio), language="pt",
            vad_filter=True, initial_prompt=VOCABULARIO,
        )
        for seg in segmentos:
            partes.append(seg.text.strip())
            if ao_progresso and info.duration:
                ao_progresso(min(seg.end / info.duration, 1.0))
    except (MemoryError, RuntimeError) as e:
        if _erro_memoria(e):
            raise RuntimeError(MSG_MEMORIA) from e
        raise

    texto = " ".join(partes)
    agora = datetime.now().strftime("%Y%m%d-%H%M%S")
    saida = pasta_dados() / f"{caminho_audio.stem}_{agora}.txt"
    saida.write_text(texto, encoding="utf-8")
    return saida


def listar_transcricoes():
    # .txt da pasta, mais recentes primeiro
    arquivos = pasta_dados().glob("*.txt")
    return sorted(arquivos, key=lambda p: p.stat().st_mtime, reverse=True)


CARACTERES_INVALIDOS = '\\/:*?"<>|'


def validar_nome(novo_nome, atual=None):
    # Devolve o nome limpo ou levanta ValueError com a mensagem para o usuário
    nome = novo_nome.strip()
    if not nome:
        raise ValueError("O nome não pode ser vazio.")
    if any(c in CARACTERES_INVALIDOS for c in nome):
        raise ValueError(f"O nome não pode conter: {' '.join(CARACTERES_INVALIDOS)}")
    if nome.endswith("."):
        raise ValueError("O nome não pode terminar com ponto.")
    destino = pasta_dados() / f"{nome}.txt"
    if destino.exists() and (atual is None or destino != Path(atual)):
        raise ValueError("Já existe uma transcrição com esse nome.")
    return nome


def renomear_transcricao(caminho, novo_nome):
    # Renomeia mantendo a extensão .txt; devolve o novo caminho
    caminho = Path(caminho)
    nome = validar_nome(novo_nome, caminho)
    destino = caminho.with_name(f"{nome}.txt")
    if destino == caminho:
        return caminho
    caminho.rename(destino)  # preserva a data de modificação
    return destino


def excluir_transcricao(caminho):
    # Move para a Lixeira do Windows
    from send2trash import send2trash
    send2trash(str(Path(caminho)))


if __name__ == "__main__":
    # Teste via linha de comando: python transcricao.py <audio>
    import sys
    import time

    import av
    with av.open(sys.argv[1]) as c:
        print(f"Duração do áudio: {c.duration / 1e6:.1f}s")
    t0 = time.time()
    txt = transcrever(sys.argv[1], lambda f: print(f"\r{f:.0%}", end="", flush=True))
    print(f"\nArquivo: {txt}\nTempo: {time.time() - t0:.1f}s\n\n{txt.read_text(encoding='utf-8')}")
