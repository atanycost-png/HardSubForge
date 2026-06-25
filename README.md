# HardSubForge v3.1.0

Aplicativo de conversao de video com processamento em lote, legendas hardcoded e suporte a NVIDIA NVENC.

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

- **Presets Otimizados**: Presets para diferentes necessidades (Maxima Qualidade, Streaming, Equilibrado, Economico)
- **Processamento em Lote**: Fila de multiplos videos com configuracao individual
- **Legendas Hardcoded**: Legendas externas (.srt, .ass, .ssa) e embutidas (MKV/MP4)
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
