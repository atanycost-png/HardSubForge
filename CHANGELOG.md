# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

Este projeto segue o padrão  
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/)  
e utiliza [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [3.0.1] - 2026-06-24

### Alterado
- **Threading model**: Workers refatorados para o padrão `QObject + moveToThread` (não mais `QThread` subclass)
- **Cancellation**: Adicionado `QMutex` + `QMutexLocker` para thread safety no cancelamento
- **Thread cleanup**: worker.finished → thread.quit → worker.deleteLater + thread.deleteLater
- **Style system**: Extraídos tokens de estilo (`styles.py`) e gerenciador de temas (`theme.py`) como módulos separados
- **Presets renomeados**: Mixdrop → Streaming Otimizado, Byse.sx → Econômico
- **Preset Equilibrado**: Resolução ajustada de 1080p para 720p (3500k → 2500k)

---

## [3.0.0] - 2026-01-28

### Adicionado
- **Presets para Sites de Streaming**: Presets otimizados especificamente para Mixdrop e Byse.sx
- **Saída Customizável**: Campo para selecionar caminho de saída e nome personalizado do arquivo
- **Clique para Selecionar**: Área de drag & drop agora aceita clique para abrir o seletor de arquivos
- **Arquitetura Modular**: Código reestruturado em módulos (config, ffmpeg, presets, ui, workers, utils)
- **Sistema de Presets Customizados**: Interface para criar e deletar presets personalizados

### Alterado
- Resolução padrão limitada a 1080p para otimização com sites de streaming
- Lógica de conversão baseada no código original (v2.4.1) para maior estabilidade
- Interface da seção de legenda simplificada (apenas legendas externas por enquanto)

### Corrigido
- **Erro na conversão com legenda embutida**: Removida implementação problemática de legendas embutidas que causava erros no FFmpeg
- **Seleção de áudio não funcionando**: Corrigido o preenchimento do combo box de áudio
- **Detecção de faixas de áudio**: Agora reconhece corretamente todas as faixas de áudio disponíveis
- **Mapeamento de faixas**: Corrigido o mapeamento de áudio e vídeo para conversões corretas
- **Filtros FFmpeg**: Corrigida a aplicação de filtros de escala, legenda e watermark
- **Erro ao final da conversão**: Corrigida a emissão de sinal de finalização

### Removido
- **Presets de Streaming Sites**: Removidos presets específicos para Streamtape e Filemoon
- **Legendas Embutidas**: Removida temporariamente esta funcionalidade (será reimplementada em versão futura com abordagem correta)
- **Processamento em lote**: Removido nesta versão (será reimplementado em versão futura)

### Notas
- Esta versão foca em estabilidade baseando-se no código original (v2.4.1)
- Suporte a legendas embutidas será adicionado em versão futura com implementação correta
- Presets disponíveis: Máxima Qualidade, Mixdrop, Byse.sx e Equilibrado
- Presets customizados podem ser criados pelo usuário

---

## [2.4.1] - 2026-01-18

### Added
- 📂 Seleção de múltiplos vídeos via diálogo de arquivo
  - Suporte para selecionar vários vídeos simultaneamente no diálogo de seleção
  - Ao selecionar 2+ vídeos, pergunta automaticamente se deseja ativar modo de lote
  - Comportamento consistente entre clique na área e drag & drop

### Added
- 📝 Diálogo de configuração de legenda individual em modo de lote
  - Novo diálogo antes de cada conversão em lote para selecionar legenda específica
  - Opções disponíveis:
    - ✅ Usar legenda detectada automaticamente
    - 📁 Selecionar legenda customizada
    - ❌ Converter sem legenda
    - ⏭️ Pular este vídeo (passa para o próximo)
    - ⏭️ Pular Todos (cancela todo o lote)
    - ❌ Cancelar (cancela todo o lote)
  - Exibe progresso atual (Vídeo X/Y)
  - Mostra nome do vídeo sendo processado
  - Interface intuitiva com radio buttons e feedback visual

### Changed
- Atualização da versão para 2.4.1 (patch release)

---

## [2.4.0] - 2026-01-18

### Added
- 🎧 Opção para copiar áudio sem reencode (-c:a copy)
  - Novo checkbox "Copiar áudio sem reencode (mais rápido)" para preservar o codec original do áudio
  - Melhora significativa de performance ao converter vídeos
  - Configuração salva automaticamente nas preferências do usuário

### Added
- 🌍 Tradução amigável dos idiomas de áudio
  - Mapeamento completo de ~180 códigos ISO 639-2/3 para português
  - Nomes traduzidos para idiomas comuns (por → Português, eng → Inglês, spa → Espanhol, etc)
  - Exibição amigável no combo de seleção de faixas de áudio

### Added
- 📊 Exibição do encoder ativo em tempo real
  - Novo label "Encoder: NVENC/CPU" na barra de status
  - Indicador visual colorido (verde para NVENC, cinza para CPU)
  - Atualização automática ao iniciar conversões (single e batch)

### Changed
- Atualização da versão para 2.4.0

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
