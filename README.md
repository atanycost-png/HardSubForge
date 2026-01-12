# HardSub Converter Pro

Aplicação desktop em Python para **converter vídeos com legendas embutidas (hardcoded)**, texto/watermark customizável e controle avançado de qualidade, utilizando **FFmpeg** com suporte opcional a **aceleração NVIDIA NVENC**.

---

## ✨ Funcionalidades

- 🎬 Conversão de vídeos com FFmpeg
- 📝 Embutir legendas externas (`.srt`, `.ass`, `.ssa`)
- 🏷️ Adicionar texto/watermark com posição e tamanho configuráveis
- 🎧 Seleção de faixa de áudio (quando o vídeo possui múltiplas)
- 🎚️ Presets de qualidade (padrões + personalizados)
- ⚙️ Editor de presets com bitrate e preset NVENC
- 🚀 Aceleração por hardware NVIDIA (NVENC), com fallback automático para CPU
- 💾 Preservação opcional de metadados
- 📊 Barra de progresso e log detalhado
- 🖱️ Interface moderna com Drag & Drop
- 💻 Compatível com Windows, Linux e macOS*

\* A aceleração por hardware é aplicada automaticamente apenas em GPUs NVIDIA.

---

## 🧠 Como funciona a aceleração por hardware

- Se uma **GPU NVIDIA** for detectada, o app pode usar **NVENC**
- Caso contrário, a conversão é feita automaticamente via **CPU (libx264)**
- Não é necessária nenhuma configuração manual do usuário

---

## 📦 Requisitos

- Python **3.9+**
- FFmpeg instalado **ou** permitido o download automático (Windows)
- Bibliotecas Python:
  - PySide6

---

## ▶️ Executando o projeto

```bash
pip install PySide6
python conversor2.py
```

No Windows, o aplicativo pode baixar o FFmpeg automaticamente se não estiver instalado.

🗂️ Formatos suportados
Vídeo

.mp4, .mkv, .avi, .mov, .wmv, .flv

Legendas

.srt, .ass, .ssa

⚙️ Presets de Qualidade

O aplicativo inclui:

Presets fixos (Alta / Padrão)

Presets personalizados criados pelo usuário

Modo manual para configuração livre de bitrate

Os presets são salvos localmente em config.json.

📁 Arquivos gerados

O vídeo convertido é salvo na mesma pasta do original

Nome padrão:

nome_do_video@converted.mp4

🧪 Status do Projeto

Estável para uso diário

Focado em simplicidade, estabilidade e compatibilidade

Suporte a AMD/VAAPI não implementado (CPU é usado automaticamente)

🤝 Contribuições

Contribuições são bem-vindas!
Veja o arquivo CONTRIBUTING.md
 para mais detalhes.

📄 Licença

Este projeto é distribuído sob a licença MIT.
Sinta-se livre para usar, modificar e distribuir.
