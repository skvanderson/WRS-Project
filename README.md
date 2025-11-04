# WRS-Project: Pac-Man - A Missão Comunitária

## 📋 Descrição

Um jogo estilo Pac-Man com tema social que aborda questões de pobreza e desigualdade, onde o jogador deve coletar recursos e entregá-los em centros comunitários para desenvolver a comunidade.

## 🎮 Funcionalidades

### Sistema de Jogo
- **Jogabilidade**: Movimento contínuo com setas do teclado ou WASD
- **Objetivo**: Coletar recursos (Moedas, Alimentos, Livros, Tijolos) e entregá-los nos centros comunitários
- **Inimigos**: Desemprego, Desigualdade, Falta de Acesso e Crise Econômica
- **Dificuldades**: Easy, Default, Hard
- **Inventário**: Capacidade limitada de 5 itens
- **Pausa**: Sistema de pausa durante o jogo

### Sistema de Recompensas (Similar ao Microsoft Rewards)
- **Pontos**: Sistema de pontuação baseado em performance
- **Níveis**: Progressão baseada em pontos acumulados
- **Tarefas Diárias**: 
  - Coletar 10 recursos (50 pontos)
  - Entregar 5 itens (75 pontos)
  - Jogar 3 partidas (100 pontos)
  - Sobreviver 2 minutos (60 pontos)
- 
**Conquistas**:
  - 🏆 Primeira Vitória (200 pontos)
  - 🏆 Colecionador - Coletar 50 recursos ao longo do tempo (150 pontos)
  - 🏆 Construtor - Completar todos os 4 centros em uma partida (300 pontos)
  - 🏆 Sobrevivente - Sobreviver 5 minutos em uma partida (250 pontos)
- **Ranking**: Sistema de classificação entre jogadores

### Sistema de Avaliação
- **Feedback do Usuário**: Sistema de avaliação com perguntas sobre usabilidade e qualidade
- **Médias**: Visualização de médias gerais e pessoais de avaliações
- **Histórico**: Registro de todas as avaliações realizadas

### Interface
- **Tela Inicial**: Login/Cadastro de usuários ou modo visitante
- **Modo Visitante**: Permite jogar sem cadastro (sem ranking)
- **Seleção de Dificuldade**: Com acesso ao sistema de recompensas, ranking e avaliação
- **Tela de Recompensas**: Visualização de pontos, tarefas e conquistas
- **Ranking**: Lista dos melhores jogadores
- **Avaliação**: Tela dedicada para feedback do produto
- **HUD**: Interface com inventário, progresso dos centros e instruções
- **Popups Informativos**: Controles e informações adicionais

## 🚀 Como Executar

### Pré-requisitos
- Python 3.12+
- Pygame 2.5+

### Instalação
```bash
# Instalar pygame (se não estiver instalado)
pip install pygame

# Executar o jogo
python main.py
```

## 🎯 Controles

- **Setas do Teclado (↑ ↓ ← →)** ou **WASD (W A S D)**: Movimentação contínua do personagem
- **H**: Descartar último item do inventário
- **P**: Pausar/Retomar o jogo
- **Mouse**: Navegação nos menus

## 🏗️ Estrutura do Projeto

```
WRS-Project/
├── main.py                # Arquivo principal do jogo (orquestra tudo)
├── config.py              # Constantes, configurações e layouts
├── entidades.py           # Classes: Player, Inimigo, CentroComunitario
├── telas.py               # Funções de desenho de UI e menus
├── utils.py               # Utilitários, sistema de recompensas e avaliação
├── assets.py              # Carregamento e processamento de recursos visuais
├── data/
│   ├── usuarios.json      # Base de dados de usuários
│   ├── rewards_data.json  # Base de dados de recompensas (criado automaticamente)
│   └── avaliacoes.json    # Base de dados de avaliações (criado automaticamente)
├── assets/
│   ├── sounds/            # Músicas e efeitos sonoros
│   ├── anim32/            # Sprites de animação 32x32
│   ├── centros48/         # Sprites de centros 48x48
│   └── centros/           # Imagens dos centros
└── README.md              # Este arquivo
```

## 🎨 Características Técnicas

### Arquitetura Modular
- **Separação de Responsabilidades**: Código organizado em módulos específicos
- **Manutenibilidade**: Fácil manutenção e expansão do código
- **Reutilização**: Componentes reutilizáveis entre diferentes partes do jogo

### Melhorias de Qualidade de Código
- **PEP 8**: Código formatado seguindo padrões Python
- **Type Hints**: Tipagem estática para melhor legibilidade
- **Tratamento de Erros**: Validações robustas e tratamento de exceções
- **Estrutura Modular**: Classes bem organizadas e separação de responsabilidades
- **Documentação**: Docstrings e comentários explicativos

### Classes Principais
- **Player**: Jogador com sistema de estatísticas e animações
- **Inimigo**: Inimigos com diferentes comportamentos baseados na dificuldade
- **CentroComunitario**: Centros que recebem recursos com sistema de progresso
- **RewardsSystem**: Sistema completo de recompensas e progressão

### Recursos Visuais
- **Labirinto**: Layout fixo com paredes azuis
- **Personagens**: Pac-Man amarelo com animação de boca (múltiplas direções)
- **Inimigos**: Fantasmas coloridos com olhos e animações
- **Recursos**: Diferentes formas e cores para cada tipo
- **Centros**: Prédios com barras de progresso animadas

## 🏆 Sistema de Pontuação

### Pontos por Ação
- **Entrega de recurso**: 20 pontos por item
- **Vitória**: 500 pontos extras
- **Tarefas diárias**: 50-100 pontos
- **Conquistas**: 150-300 pontos

### Progressão
- **Nível**: Calculado baseado em pontos totais (1000 pontos = nível 2)
- **Ranking**: Classificação global entre todos os jogadores

## 📊 Sistema de Avaliação

### Características
- **Perguntas Categorizadas**: Usabilidade e qualidade geral do produto
- **Escala de 1-5**: Avaliação de 1 (ruim) a 5 (excelente)
- **Médias em Tempo Real**: Visualização de médias gerais e pessoais
- **Histórico Completo**: Todas as avaliações são armazenadas com timestamp

## 🐛 Correções e Melhorias Implementadas

- ✅ Refatoração completa para arquitetura modular
- ✅ Melhoria na formatação do código (PEP 8)
- ✅ Correção de quebras de linha em mensagens longas
- ✅ Adição de sistema de recompensas completo
- ✅ Implementação de tarefas diárias
- ✅ Sistema de conquistas
- ✅ Ranking de jogadores
- ✅ Sistema de avaliação do produto
- ✅ Modo visitante (jogar sem cadastro)
- ✅ Popups informativos de controles
- ✅ Sistema de pausa durante o jogo
- ✅ Controles melhorados (WASD + setas)
- ✅ Melhor tratamento de erros
- ✅ Validações robustas
- ✅ Sistema de médias na avaliação

## 🎯 Objetivos Educacionais

O jogo visa conscientizar sobre:
- **Pobreza**: Representada pela coleta de recursos básicos
- **Desigualdade**: Diferentes tipos de recursos necessários
- **Acesso**: Barreiras representadas pelos inimigos
- **Comunidade**: Trabalho coletivo para o desenvolvimento

## 📝 Notas de Desenvolvimento

- O sistema de recompensas é similar ao Microsoft Rewards, incentivando o engajamento diário
- As conquistas são baseadas em marcos de progressão significativos
- O ranking promove competição saudável entre jogadores
- As tarefas diárias garantem que os jogadores retornem regularmente
- O sistema de avaliação permite feedback contínuo dos usuários
- O modo visitante permite que novos jogadores experimentem o jogo antes de se cadastrarem

## 🔧 Tecnologias Utilizadas

- **Python 3.12+**: Linguagem de programação
- **Pygame 2.5+**: Biblioteca para desenvolvimento de jogos
- **JSON**: Armazenamento de dados de usuários, recompensas e avaliações
- **datetime**: Controle de tempo para tarefas diárias e histórico
- **Pathlib**: Gerenciamento de caminhos de arquivos

---

**Desenvolvido para fins educacionais e de conscientização social.**
