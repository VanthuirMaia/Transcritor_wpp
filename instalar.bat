@echo off
rem Copia dist\Transcritor para %LOCALAPPDATA%\Programs\Transcritor e recria os atalhos
cd /d "%~dp0"
if not exist dist\Transcritor\Transcritor.exe (
    echo Rode build.bat primeiro.
    exit /b 1
)
set DESTINO=%LOCALAPPDATA%\Programs\Transcritor

rem Fecha o app se estiver aberto
taskkill /f /im Transcritor.exe >nul 2>&1
taskkill /f /im flet.exe >nul 2>&1

rem Substitui a versao anterior (robocopy: codigos 0-7 sao sucesso)
robocopy dist\Transcritor "%DESTINO%" /MIR /NFL /NDL /NJH /NJS /NP
if errorlevel 8 exit /b 1

rem Atalhos na Area de Trabalho (real, pode estar no OneDrive) e no Menu Iniciar
powershell -NoProfile -Command "$exe = Join-Path $env:LOCALAPPDATA 'Programs\Transcritor\Transcritor.exe'; $ws = New-Object -ComObject WScript.Shell; foreach ($pasta in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) { $l = $ws.CreateShortcut((Join-Path $pasta 'Transcritor.lnk')); $l.TargetPath = $exe; $l.WorkingDirectory = Split-Path $exe; $l.IconLocation = $exe + ',0'; $l.Save() }"
echo Instalado em %DESTINO%
