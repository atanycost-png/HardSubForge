@echo off
echo ========================================
echo HardSubForge Build Script v3.0.0
echo ========================================
echo.

echo [1/4] Atualizando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO ao instalar dependencias!
    pause
    exit /b 1
)
echo Dependencias instaladas com sucesso!
echo.

echo [2/4] Limpando build anterior...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist HardSubForge.spec.bak del HardSubForge.spec.bak
echo Limpeza concluida!
echo.

echo [3/4] Gerando executavel com PyInstaller...
pyinstaller HardSubForge.spec --clean --noconfirm
if errorlevel 1 (
    echo ERRO ao gerar executavel!
    pause
    exit /b 1
)
echo Executavel gerado com sucesso!
echo.

echo [4/4] Verificando resultado...
if exist dist\HardSubForge.exe (
    echo SUCESSO! Executavel criado em: dist\HardSubForge.exe
    echo.
    echo Tamanho:
    dir dist\HardSubForge.exe | find "HardSubForge.exe"
) else (
    echo ERRO: Executavel nao encontrado em dist\
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build concluido!
echo ========================================
echo.
echo Pressione qualquer tecla para sair...
pause >nul
