"""Interface Flet do Transcritor."""
import os
from datetime import datetime

import flet as ft

import transcricao


def main(page: ft.Page):
    page.title = "Transcritor"
    page.window.width = 1000
    page.window.height = 650
    page.padding = 0

    selecionado = {"arquivo": None}  # transcrição aberta no momento

    picker = ft.FilePicker()
    clipboard = ft.Clipboard()
    page.services.extend([picker, clipboard])

    # --- controles ---
    lista = ft.ListView(expand=True, spacing=0)
    texto = ft.TextField(
        read_only=True, multiline=True, expand=True,
        hint_text="Selecione uma transcrição ou crie uma nova.",
    )
    btn_nova = ft.Button("Nova transcrição", icon=ft.Icons.ADD, width=280)
    btn_copiar = ft.Button("Copiar", icon=ft.Icons.COPY, disabled=True)
    btn_pasta = ft.Button("Abrir pasta", icon=ft.Icons.FOLDER_OPEN)
    barra = ft.ProgressBar(visible=False)
    status = ft.Text("", visible=False)

    # --- helpers ---
    def avisar(msg):
        page.show_dialog(ft.SnackBar(ft.Text(msg)))

    def mostrar(arquivo):
        selecionado["arquivo"] = arquivo
        texto.value = arquivo.read_text(encoding="utf-8")
        btn_copiar.disabled = False
        atualizar_lista()

    def atualizar_lista():
        lista.controls.clear()
        for arq in transcricao.listar_transcricoes():
            data = datetime.fromtimestamp(arq.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
            lista.controls.append(ft.ListTile(
                title=ft.Text(arq.stem, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                subtitle=ft.Text(data),
                selected=(arq == selecionado["arquivo"]),
                on_click=lambda e, a=arq: (mostrar(a), page.update()),
                trailing=ft.PopupMenuButton(items=[
                    ft.PopupMenuItem("Copiar", icon=ft.Icons.COPY,
                                     on_click=lambda e, a=arq: page.run_task(copiar_item, a)),
                    ft.PopupMenuItem("Renomear", icon=ft.Icons.EDIT,
                                     on_click=lambda e, a=arq: renomear_item(a)),
                    ft.PopupMenuItem("Excluir", icon=ft.Icons.DELETE,
                                     on_click=lambda e, a=arq: excluir_item(a)),
                ]),
            ))

    async def copiar_item(arq):
        try:
            await clipboard.set(arq.read_text(encoding="utf-8"))
            avisar("Copiado")
        except OSError as e:
            avisar(f"Erro: {e}")

    def renomear_item(arq):
        campo = ft.TextField(value=arq.stem, autofocus=True, label="Novo nome")

        def confirmar(e):
            try:
                novo = transcricao.renomear_transcricao(arq, campo.value)
            except ValueError as err:
                campo.error = str(err)
                campo.update()
                return
            except OSError as err:
                campo.error = f"Erro: {err}"
                campo.update()
                return
            if selecionado["arquivo"] == arq:
                selecionado["arquivo"] = novo
            page.pop_dialog()
            atualizar_lista()
            page.update()

        campo.on_submit = confirmar
        page.show_dialog(ft.AlertDialog(
            title=ft.Text("Renomear"),
            content=campo,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.TextButton("Renomear", on_click=confirmar),
            ],
        ))

    def excluir_item(arq):
        try:
            transcricao.excluir_transcricao(arq)
        except OSError as e:
            avisar(f"Erro: {e}")
            return
        if selecionado["arquivo"] == arq:
            selecionado["arquivo"] = None
            texto.value = ""
            btn_copiar.disabled = True
        atualizar_lista()
        avisar("Movido para a Lixeira")
        page.update()

    def definir_status(msg, progresso=None, ocupado=True):
        status.value = msg
        status.visible = bool(msg)
        barra.visible = ocupado
        barra.value = progresso  # None = indeterminada
        page.update()

    # --- transcrição em thread ---
    def trabalhar(caminho):
        btn_nova.disabled = True
        try:
            definir_status("Baixando modelo (só na primeira vez)...")
            transcricao.carregar_modelo()
            definir_status("Transcrevendo...", 0)
            saida = transcricao.transcrever(
                caminho,
                lambda f: definir_status(f"Transcrevendo... {f:.0%}", f),
            )
            mostrar(saida)
            definir_status("", ocupado=False)
        except Exception as e:
            definir_status(f"Erro: {e}", ocupado=False)
            avisar(f"Erro: {e}")
        finally:
            btn_nova.disabled = False
            page.update()

    # --- eventos ---
    async def nova(e):
        extensoes = [x.lstrip(".") for x in sorted(transcricao.EXTENSOES)]
        arquivos = await picker.pick_files(
            dialog_title="Escolha o áudio",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=extensoes,
        )
        if arquivos:
            page.run_thread(trabalhar, arquivos[0].path)

    async def copiar(e):
        await clipboard.set(texto.value or "")
        avisar("Texto copiado")

    def abrir_pasta(e):
        os.startfile(transcricao.pasta_dados())

    btn_nova.on_click = nova
    btn_copiar.on_click = copiar
    btn_pasta.on_click = abrir_pasta

    # --- layout ---
    esquerda = ft.Container(
        width=300, padding=10,
        content=ft.Column([btn_nova, ft.Divider(), lista], expand=True),
    )
    direita = ft.Container(
        expand=True, padding=10,
        content=ft.Column([
            texto,
            ft.Row([btn_copiar, btn_pasta]),
            status,
            barra,
        ], expand=True),
    )
    page.add(ft.Row([esquerda, ft.VerticalDivider(width=1), direita], expand=True))
    atualizar_lista()


if __name__ == "__main__":
    ft.run(main)
