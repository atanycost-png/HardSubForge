# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue o padrão [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/)  
e o projeto utiliza [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [2.2.0] - 2026-01-12

### Added
- Seleção manual de faixa de áudio em vídeos com múltiplos áudios
- Detecção automática de faixas de áudio via ffprobe
- Editor de presets de qualidade personalizados
- Presets salvos localmente pelo usuário
- Suporte a texto/watermark configurável (posição e tamanho)
- Preservação opcional de metadados do vídeo
- Barra de progresso baseada na duração real do vídeo
- Log detalhado do processo de conversão
- Download automático do FFmpeg no Windows

### Changed
- Pipeline de conversão reorganizado para maior estabilidade
- Sistema de qualidade agora suporta presets fixos e personalizados
- Interface aprimorada para melhor usabilidade
- Comportamento padrão ajustado para maior compatibilidade

### Fixed
- Travamentos da interface durante a conversão
- Problemas ao lidar com caminhos de arquivos no Windows
- Erros ao aplicar texto com caracteres especiais
- Falhas ao converter vídeos com múltiplas faixas de áudio
- Melhor tratamento de erros do FFmpeg

---

## [2.1.0] - 2025-12-20

### Added
- Interface gráfica moderna baseada em PySide6
- Suporte a hard subtitles (SRT, ASS, SSA)
- Drag & Drop para seleção de arquivos
- Presets de
