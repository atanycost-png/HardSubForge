🎬 HardSub Converter Pro

HardSub Converter Pro é uma aplicação desktop poderosa e intuitiva para conversão de vídeos com legendas embutidas (hardcoded). O software combina a flexibilidade do FFmpeg com uma interface moderna, oferecendo controle total sobre qualidade, trilhas de áudio e marcas d'água.
✨ Funcionalidades

    📝 Legendas Hardcoded: Suporte nativo para formatos .srt, .ass e .ssa.

    🏷️ Branding Personalizado: Adicione textos ou marcas d'água com controle total de posição e tamanho.

    🎧 Gestão de Áudio: Selecione faixas específicas em arquivos multi-áudio.

    🚀 Alta Performance: Suporte a aceleração por hardware NVIDIA NVENC com fallback inteligente para CPU.

    🎚️ Presets Flexíveis: Editor de presets integrado (bitrate, presets NVENC) e salvamento automático em config.json.

    🖱️ Experiência Moderna: Interface limpa com suporte a Drag & Drop e barra de progresso em tempo real.

    💻 Multiplataforma: Compatível com Windows, Linux e macOS.

🧠 Inteligência de Processamento

O HardSub Converter Pro foi desenhado para ser eficiente sem exigir esforço do usuário:

    Detecção Automática: O sistema verifica a presença de drivers NVIDIA.

    Codificação: * Com GPU NVIDIA: Utiliza o encoder h264_nvenc para velocidade máxima.

        Sem GPU/Outros: Utiliza o encoder libx264 (CPU) garantindo compatibilidade universal.

    Metadados: Opção para preservar informações originais do arquivo.

📦 Requisitos & Instalação
Pré-requisitos

    Python: Versão 3.9 ou superior.

    FFmpeg: Deve estar no PATH do sistema (No Windows, o app oferece download automático).

Instalação

    Clone o repositório:
    Bash

git clone https://github.com/seu-usuario/hardsub-converter-pro.git
cd hardsub-converter-pro

Instale as dependências:
Bash

pip install PySide6

Inicie a aplicação:
Bash

    python conversor2.py

🛠️ Especificações Técnicas
Categoria	Suportados
Formatos de Vídeo	.mp4, .mkv, .avi, .mov, .wmv, .flv
Formatos de Legenda	.srt, .ass, .ssa
Presets	Alta, Padrão, Personalizado e Manual
Saída	nome_do_arquivo@converted.mp4
🧪 Status do Projeto

    [x] Interface Base (PySide6)

    [x] Integração FFmpeg

    [x] Suporte NVIDIA NVENC

    [ ] Suporte AMD (AMF/VAAPI) - Em planejamento

    [ ] Conversão em lote (Batch processing) - Em planejamento

🤝 Contribuições

Contribuições tornam a comunidade open-source um lugar incrível para aprender e criar.

    Faça um Fork do projeto.

    Crie uma Branch para sua feature (git checkout -b feature/NovaFeature).

    Dê um Commit nas suas alterações (git commit -m 'Add: Nova Feature').

    Faça um Push para a Branch (git push origin feature/NovaFeature).

    Abra um Pull Request.

📄 Licença

Distribuído sob a licença MIT. Veja LICENSE para mais informações.

    Nota: A aceleração por hardware (NVENC) requer drivers atualizados da NVIDIA instalados no sistema host.
