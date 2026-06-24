# HardSubForge v3.0.1

Aplicativo de conversão de vídeo otimizado para sites de streaming (Mixdrop, Byse.sx).

## Instalação

```bash
pip install -r requirements.txt
python main.py
```

## Presets Disponíveis

- **Máxima Qualidade**: Arquivamento (1080p, 5500k)
- **Streaming Otimizado**: Upload sites (1080p, 4500k)
- **Equilibrado**: Bom equilíbrio (720p, 2500k)
- **Econômico**: Arquivo leve (480p, 1200k)

## Presets Customizados

Crie seus próprios presets clicando no botão "+" na seção de qualidade.

## Funcionalidades

- **Presets Otimizados**: Presets específicos para Mixdrop e Byse.sx
- **Legendas Hardcoded**: Embarque legendas (.srt, .ass, .ssa) no vídeo
- **Watermark**: Adicione texto com posição e tamanho customizáveis
- **Resolução 1080p**: Vídeos convertidos em Full HD
- **Saída Customizável**: Escolha o caminho e nome do arquivo de saída
- **Seleção de Áudio**: Escolha faixas de áudio em vídeos multitrack
- **Aceleração NVIDIA**: Suporte a NVENC para conversão mais rápida
- **Interface Moderna**: UI limpa com tema escuro
- **Clique para Selecionar**: Clique na área para abrir o seletor de arquivos

## Uso

1. **Selecionar Vídeo**: Clique na área ou arraste o arquivo
2. **Escolher Legenda**: Detectada automaticamente ou selecione manualmente
3. **Configurar Áudio**: Selecione a faixa de áudio desejada
4. **Adicionar Watermark**: Configure texto e posição (opcional)
5. **Escolher Preset**: Selecione o preset de qualidade
6. **Definir Saída**: Configure caminho e nome do arquivo
7. **Converter**: Clique em "INICIAR CONVERSÃO"

## Requisitos

- Python 3.9+
- FFmpeg (baixado automaticamente no Windows ou manualmente em outros sistemas)
- PySide6

## Licença

MIT
