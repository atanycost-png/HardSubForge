# HardSubForge 🎬🔥

**HardSubForge** é um conversor de vídeos open source em Python que permite **queimar legendas (hard subtitles)** e **aplicar textos/watermarks diretamente no vídeo**, utilizando o poder do **FFmpeg**, com interface gráfica moderna feita em **PySide6**.

O projeto é focado em **simplicidade para o usuário final**, mas com **robustez técnica**, suporte a **aceleração por GPU NVIDIA (NVENC)** e funcionamento multiplataforma.

---

## ✨ Funcionalidades

- 🎥 Conversão de vídeos com **hard subtitles** (SRT / ASS / SSA)
- 📝 Inserção de **texto/watermark** no vídeo (topo, centro ou rodapé)
- 🎚️ Presets de qualidade (Alta, Padrão, Baixa)
- ⚡ Aceleração por hardware **NVIDIA CUDA / NVENC**
- 📂 Drag & Drop de vídeos
- 🔍 Detecção automática de legendas com mesmo nome do vídeo
- 💾 Preservação opcional de metadados
- 📊 Barra de progresso real baseada no tempo do vídeo
- ❌ Cancelamento seguro da conversão
- 🧠 Salvamento automático das configurações do usuário
- 🖥️ Interface moderna com tema escuro
- 📦 Download automático do FFmpeg (Windows)

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.9+**
- **PySide6 (Qt for Python)**
- **FFmpeg**
- **NVENC (opcional – NVIDIA GPU)**

---

## 📋 Requisitos

### Obrigatórios
- Python **3.9 ou superior**
- FFmpeg instalado **(ou download automático no Windows)**

### Opcionais
- GPU **NVIDIA** com drivers atualizados (para aceleração por hardware)

---

## 🚀 Como executar o projeto

### 1️⃣ Clonar o repositório
```bash
git clone https://github.com/atanycost-png/hardsubforge.git
cd hardsubforge
```

### 2️⃣ Criar ambiente virtual (opcional, recomendado)
```bash
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows
```

### 3️⃣ Instalar dependências
```bash
pip install -r requirements.txt
```

### 4️⃣ Executar a aplicação
```bash
python conversor_atanycost.py
```

📦 FFmpeg

No Windows, o programa oferece download automático do FFmpeg.
No Linux / macOS, instale manualmente:
Ubuntu / Debian
```bash
sudo apt install ffmpeg
```
macOS (Homebrew)
```bash
brew install ffmpeg
```
Verifique:
```bash
ffmpeg -version
```


