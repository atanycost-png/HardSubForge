# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/)  
e este projeto segue [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [2.0.0] - 2026-01-12

### Added
- Interface gráfica moderna baseada em PySide6
- Suporte a hard subtitles (SRT, ASS, SSA)
- Inserção de texto/watermark no vídeo (topo, centro e rodapé)
- Presets de qualidade (Alta, Padrão, Baixa)
- Aceleração por hardware NVIDIA (CUDA / NVENC)
- Detecção automática de GPU NVIDIA
- Download automático do FFmpeg no Windows
- Barra de progresso baseada na duração real do vídeo
- Cancelamento seguro da conversão
- Drag & Drop de arquivos de vídeo
- Salvamento automático das configurações do usuário
- Preservação opcional de metadados
- Log detalhado do processo de conversão

### Changed
- Reestruturação completa do projeto
- Pipeline de conversão baseado em FFmpeg com thread dedicada
- Melhor tratamento de paths e escaping para filtros FFmpeg
- Melhor UX e feedback visual durante a conversão

### Fixed
- Possíveis travamentos da interface durante conversão
- Problemas com caminhos de arquivos no Windows
- Erros ao aplicar texto com caracteres especiais
- Melhor compatibilidade entre Windows, Linux e macOS

---

## [1.0.0] - 2025-xx-xx

### Added
- Primeira versão funcional do conversor
- Conversão básica de vídeos via FFmpeg
- Interface gráfica inicial
