# 🎬 HardSub Converter Pro

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PySide6](https://img.shields.io/badge/PySide6-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge)

Aplicação desktop em Python para **converter vídeos com legendas embutidas (hardcoded)**, texto/watermark customizável e controle avançado de qualidade, utilizando **FFmpeg** com suporte opcional a **aceleração NVIDIA NVENC**.

---

## ✨ Funcionalidades

* **🎬 Conversão de Vídeo:** Processamento robusto via FFmpeg.
* **📝 Legendas Hardcoded:** Embutir legendas externas nos formatos `.srt`, `.ass` e `.ssa`.
* **🏷️ Watermark:** Adicionar texto ou marca d'água com posição e tamanho configuráveis.
* **🎧 Gestão de Áudio:** Seleção manual de faixas de áudio para arquivos multi-idioma com nomes traduzidos.
* **🎚️ Presets de Qualidade:** Opções prontas (Alta/Padrão) e editor de presets personalizados (Bitrate/NVENC).
* **🚀 Aceleração por Hardware:** Suporte a NVIDIA (NVENC) com fallback automático para CPU (`libx264`).
* **⚡ Cópia de Áudio:** Opção para copiar áudio sem reencode para máxima performance.
* **📊 Encoder em Tempo Real:** Indicador visual do encoder ativo (NVENC/CPU) na interface.
* **📦 Conversão em Lote:** Processamento de múltiplos arquivos via Drag & Drop ou seleção de arquivo com configuração individual de legendas.
* **⚡ Alta Performance:** Otimizado com cache de I/O e processamento eficiente de logs.
* **📊 Interface Moderna:** Suporte a **Drag & Drop**, log detalhado e barra de progresso.
* **💻 Multiplataforma:** Compatível com Windows, Linux e macOS*.

> \* *A aceleração por hardware é aplicada automaticamente apenas em GPUs NVIDIA.*

---

## 🧠 Como funciona a aceleração por hardware

O aplicativo detecta automaticamente o hardware disponível para otimizar a velocidade:

1.  **Detecção de GPU:** O sistema verifica se há uma GPU NVIDIA compatível.
2.  **Uso de NVENC:** Se detectada, o app utiliza o encoder de hardware para conversões ultrarrápidas.
3.  **Fallback para CPU:** Caso não haja GPU NVIDIA, a conversão é feita automaticamente via CPU (libx264), garantindo que o processo nunca falhe.

---

## 📦 Requisitos

* **Python 3.9+**
* **FFmpeg:** Instalado no sistema ou permitido o download automático (funcionalidade disponível para Windows).
* **Bibliotecas:** PySide6.

---

## ▶️ Executando o projeto

Para rodar o projeto localmente, siga os passos abaixo:

```bash
# Instale a interface gráfica
pip install PySide6

# Execute a aplicação
python HardSubForge.py

```

*Nota: No Windows, o aplicativo tentará baixar o FFmpeg automaticamente caso não o encontre no PATH.*

---

## ⚙️ Especificações Técnicas

### 🗂️ Formatos Suportados

| Tipo | Extensões |
| --- | --- |
| **Vídeo** | `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv` |
| **Legendas** | `.srt`, `.ass`, `.ssa` |

### 📁 Arquivos Gerados

Os vídeos convertidos são salvos no mesmo diretório do arquivo original seguindo o padrão:
`nome_do_video@converted.mp4`

---

## 🧪 Status do Projeto

* ✅ Estável para uso diário.
* ✅ Focado em simplicidade e estabilidade.
* ⚠️ Suporte a AMD/VAAPI não implementado (usa CPU automaticamente nestes casos).

---

## 🤝 Contribuições

Contribuições são muito bem-vindas!

1. Faça um Fork do projeto.
2. Crie uma branch para sua modificação (`git checkout -b feature/nova-funcionalidade`).
3. Envie um Pull Request.

Para mais detalhes, veja o arquivo `CONTRIBUTING.md`.

---

## 📄 Licença

Este projeto é distribuído sob a licença **MIT**. Sinta-se livre para usar, modificar e distribuir conforme desejar.

```
