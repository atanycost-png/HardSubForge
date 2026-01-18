# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

Este projeto segue o padrão  
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/)  
e utiliza [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [2.3.1] - 2026-01-18

### Added
- Otimizações de performance (Bolt ⚡):
  - Pré-compilação de expressões regulares em nível de módulo para reduzir overhead no loop de processamento.
  - Cache de I/O (via `functools.lru_cache`) para caminhos de fontes e resolução de binários (FFprobe).
  - Otimização do loop de parsing do log do FFmpeg para ignorar buscas redundantes.

### Changed
- Refatoração interna da busca por binários do FFmpeg/FFprobe para maior eficiência.
- Melhoria na sanitização de nomes de arquivos.

## [2.3.0] - 2026-01-14

### Added
- Suporte a drag & drop múltiplo de arquivos de vídeo
- Implementação completa do modo de conversão em lote (batch conversion)
- Novo sinal `files_dropped` para tratamento de múltiplos arquivos
- Gerenciamento automático de fila de conversão
- Notificação ao finalizar cada arquivo no modo de lote
- Notificação final ao concluir toda a fila
- Exibição do tamanho do arquivo após conversão
- Botão para exclusão de presets personalizados

### Changed
- Área de drag & drop atualizada para indicar suporte a múltiplos arquivos
- Pipeline de conversão ajustado para funcionamento sequencial
- Uso de `QTimer.singleShot` para controle do fluxo de conversão em lote
- Melhor organização interna do estado de conversão

### Fixed
- Correção do import do `QTimer` no PySide6
- Correção de falhas na conversão em lote
- Correção no download automático do FFmpeg/FFprobe
- Validação correta de bitrate inserido pelo usuário
- Correção no cálculo de `maxrate` e `bufsize`
- Sanitização de nomes de arquivos para evitar erros no FFmpeg

---

## [2.2.2] - 2026-01-13

### Added
- Notificação do sistema ao finalizar conversões individuais
- Exibição do tamanho final do arquivo convertido
- Gerenciamento de presets personalizados
- Interface aprimorada para controle de qualidade

---

## [2.2.1] - 2026-01-13

### Fixed
- Correção crítica no download do FFmpeg e FFprobe
- Melhor tratamento de erros relacionados ao ambiente do usuário
- Ajustes de estabilidade geral

---

## [2.2.0] - 2026-01-12

### Added
- Seleção manual de faixa de áudio
- Presets de qualidade personalizados
- Interface gráfica baseada em PySide6
- Suporte a NVIDIA NVENC com fallback automático para CPU
- Drag & drop de arquivos
- Embutir legendas externas (SRT, ASS, SSA)
- Inserção de texto/watermark configurável
