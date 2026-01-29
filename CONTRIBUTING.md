# Contribuindo com o HardSubForge

Obrigado pelo interesse em contribuir com o HardSubForge! Este documento fornece diretrizes para contribuir com o projeto.

## Estrutura do Projeto

O HardSubForge possui uma arquitetura modular organizada da seguinte forma:

```
HardSubForge/
├── config/           # Gerenciamento de configurações
├── ffmpeg/           # Wrapper para FFmpeg
├── presets/          # Definições de presets de qualidade
├── ui/               # Interface do usuário (PySide6)
├── utils/            # Funções auxiliares
├── workers/          # Threads de processamento
└── main.py           # Ponto de entrada da aplicação
```

## Desenvolvimento

### Pré-requisitos

- Python 3.9+
- FFmpeg instalado e disponível no PATH
- Bibliotecas do requirements.txt

### Configuração do Ambiente

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/HardSubForge.git
cd HardSubForge

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python main.py
```

## Padrões de Código

- Siga o PEP 8 para estilo de código
- Use type hints quando apropriado
- Adicione docstrings em funções e classes públicas
- Mantenha os módulos pequenos e focados

## Como Contribuir

1. Faça um Fork do projeto
2. Crie uma branch para sua funcionalidade (`git checkout -b feature/nova-funcionalidade`)
3. Faça suas modificações
4. Teste as alterações
5. Faça o commit das mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
6. Faça o push para a branch (`git push origin feature/nova-funcionalidade`)
7. Abra um Pull Request

## Funcionalidades Disponíveis

### Atual (v3.0.0)
- Arquitetura modular
- Presets otimizados para Mixdrop e Byse.sx
- Legendas hardcoded (.srt, .ass, .ssa)
- Watermark customizável
- Seleção de faixas de áudio
- Aceleração NVIDIA NVENC
- Presets customizados

### Planejado
- Suporte a legendas embutidas do vídeo
- Processamento em lote
- Suporte a mais formatos de saída

## Reportando Bugs

Ao reportar bugs, inclua:
- Versão do HardSubForge
- Sistema operacional
- Descrição detalhada do problema
- Passos para reproduzir
- Logs relevantes (se aplicável)

## Solicitando Funcionalidades

Abra uma issue com a tag "enhancement" e descreva:
- Qual funcionalidade você gostaria de ver
- Por que ela seria útil
- Como você imagina que funcione

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a licença MIT do projeto.
