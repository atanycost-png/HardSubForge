# Roadmap - HardSubForge

Este documento descreve o plano de desenvolvimento e funcionalidades planejadas para o HardSubForge.

## Versão Atual: 3.0.0

Lançada em 2026-01-28

## Funcionalidades Implementadas

### ✅ Arquitetura Modular (v3.0.0)
- Estrutura organizada em módulos: config, ffmpeg, presets, ui, workers, utils
- Separação clara de responsabilidades
- Código mais manutenível e testável

### ✅ Presets de Qualidade (v3.0.0)
- Máxima Qualidade (1080p, 5500k)
- Mixdrop (1080p, 4500k)
- Byse.sx (1080p, 4500k)
- Equilibrado (1080p, 3500k)
- Sistema de presets customizados

### ✅ Legendas (v3.0.0)
- Suporte a legendas externas (.srt, .ass, .ssa)
- Detecção automática de legendas
- Seleção manual de legendas

### ✅ Watermark (v3.0.0)
- Texto customizável
- Posição configurável (topo, centro, inferior)
- Tamanho ajustável
- Fundo com transparência

### ✅ Áudio (v3.0.0)
- Seleção de faixas de áudio
- Detecção de idiomas
- Suporte a múltiplas faixas
- Opção de copiar áudio sem reencode

### ✅ Hardware (v3.0.0)
- Aceleração NVIDIA NVENC
- Fallback automático para CPU
- Detecção automática de GPU

### ✅ Interface (v3.0.0)
- Interface moderna com tema escuro
- Área de drag & drop
- Clique para selecionar arquivo
- Barra de progresso em tempo real
- Log detalhado
- System tray
- Notificações

## Próximas Versões

### Versão 3.1.0 - Planejada

#### Funcionalidades Prioritárias
- [ ] Suporte a legendas embutidas no vídeo
- [ ] Processamento em lote (batch)
- [ ] Visualização do vídeo pré-conversão
- [ ] Preview de legenda e watermark

#### Melhorias
- [ ] Suporte a mais formatos de vídeo (WebM, AV1)
- [ ] Configurações avançadas de FFmpeg
- [ ] Presets editáveis
- [ ] Histórico de conversões

### Versão 3.2.0 - Planejada

#### Funcionalidades
- [ ] Suporte a legendas embutidas com estilo customizável
- [ ] Edição de legendas
- [ ] Multi-threading para batch
- [ ] Exportação/importação de presets

#### Melhorias
- [ ] Interface responsiva
- [ ] Modo avançado
- [ ] Temas personalizáveis
- [ ] Atalhos de teclado

### Versão 4.0.0 - Futuro

#### Funcionalidades Planejadas
- [ ] Suporte a mais codecs (H.265, AV1)
- [ ] Processamento na nuvem
- [ ] Integração com APIs de streaming
- [ ] App mobile ou web

## Funcionalidades Consideradas

As seguintes funcionalidades estão sendo consideradas para futuras versões:

- Suporte a AMD VAAPI e Intel Quick Sync
- Processamento distribuído em múltiplas GPUs
- Automação com scripts
- Plugins e extensões
- Traduções da interface

## Contribuições

Se você quiser contribuir com alguma funcionalidade, verifique o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para diretrizes.

## Changelog

Para ver o histórico de mudanças, consulte o arquivo [CHANGELOG.md](CHANGELOG.md).
