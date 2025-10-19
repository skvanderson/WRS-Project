# WRS-Project: Pac-Man - A Missão Comunitária

## 📋 Descrição

Um jogo estilo Pac-Man com tema social que aborda questões de pobreza e desigualdade, onde o jogador deve coletar recursos e entregá-los em centros comunitários para desenvolver a comunidade.

## 🎮 Funcionalidades

### Sistema de Jogo
- **Jogabilidade**: Movimento com setas do teclado
- **Objetivo**: Coletar recursos (Moedas, Alimentos, Livros, Tijolos) e entregá-los nos centros comunitários
- **Inimigos**: Desemprego, Desigualdade, Falta de Acesso e Crise Econômica
- **Dificuldades**: Easy, Default, Hard
- **Inventário**: Capacidade limitada de 5 itens

### Sistema de Recompensas (Similar ao Microsoft Rewards)
- **Pontos**: Sistema de pontuação baseado em performance
- **Níveis**: Progressão baseada em pontos acumulados
- **Tarefas Diárias**: 
  - Coletar 10 recursos (50 pontos)
  - Entregar 5 itens (75 pontos)
  - Jogar 3 partidas (100 pontos)
  - Sobreviver 2 minutos (60 pontos)
- **Conquistas**:
  - 🏆 Primeira Vitória (200 pontos)
  - 🏆 Colecionador - Coletar 50 recursos (150 pontos)
  - 🏆 Construtor - Completar 3 centros (300 pontos)
  - 🏆 Sobrevivente - Sobreviver 5 minutos (250 pontos)
- **Ranking**: Sistema de classificação entre jogadores

### Interface
- **Tela Inicial**: Login/Cadastro de usuários
- **Seleção de Dificuldade**: Com acesso ao sistema de recompensas
- **Tela de Recompensas**: Visualização de pontos, tarefas e conquistas
- **Ranking**: Lista dos melhores jogadores
- **HUD**: Interface com inventário, progresso dos centros e instruções

## 🚀 Como Executar

### Pré-requisitos
- Python 3.7+
- Pygame 2.0+

### Instalação
```bash
# Instalar pygame (se não estiver instalado)
pip install pygame

# Executar o jogo
python pac_poverty.py
```

## 🎯 Controles

- **Setas**: Movimentação do personagem
- **D**: Descartar último item do inventário
- **Mouse**: Navegação nos menus

## 🏗️ Estrutura do Projeto

```
WRS-Project/
├── pac_poverty.py          # Arquivo principal do jogo
├── usuarios.json           # Base de dados de usuários
├── rewards_data.json       # Base de dados de recompensas (criado automaticamente)
└── README.md              # Este arquivo
```

## 🎨 Características Técnicas

### Melhorias de Qualidade de Código
- **PEP 8**: Código formatado seguindo padrões Python
- **Type Hints**: Tipagem estática para melhor legibilidade
- **Tratamento de Erros**: Validações robustas e tratamento de exceções
- **Estrutura Modular**: Classes bem organizadas e separação de responsabilidades
- **Documentação**: Docstrings e comentários explicativos

### Classes Principais
- **Player**: Jogador com sistema de estatísticas
- **Inimigo**: Inimigos com diferentes comportamentos baseados na dificuldade
- **CentroComunitario**: Centros que recebem recursos
- **RewardsSystem**: Sistema completo de recompensas

### Recursos Visuais
- **Labirinto**: Layout fixo com paredes azuis
- **Personagens**: Pac-Man amarelo com animação de boca
- **Inimigos**: Fantasmas coloridos com olhos
- **Recursos**: Diferentes formas e cores para cada tipo
- **Centros**: Prédios com barras de progresso

## 🏆 Sistema de Pontuação

### Pontos por Ação
- **Entrega de recurso**: 20 pontos por item
- **Vitória**: 500 pontos extras
- **Tarefas diárias**: 50-100 pontos
- **Conquistas**: 150-300 pontos

### Progressão
- **Nível**: Calculado baseado em pontos totais (1000 pontos = nível 2)
- **Ranking**: Classificação global entre todos os jogadores

## 🐛 Correções Implementadas

- ✅ Melhoria na formatação do código (PEP 8)
- ✅ Correção de quebras de linha em mensagens longas
- ✅ Adição de sistema de recompensas completo
- ✅ Implementação de tarefas diárias
- ✅ Sistema de conquistas
- ✅ Ranking de jogadores
- ✅ Melhor tratamento de erros
- ✅ Validações robustas

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

## 🔧 Tecnologias Utilizadas

- **Python 3.12+**: Linguagem de programação
- **Pygame 2.5+**: Biblioteca para desenvolvimento de jogos
- **JSON**: Armazenamento de dados de usuários e recompensas
- **datetime**: Controle de tempo para tarefas diárias

---

**Desenvolvido para fins educacionais e de conscientização social.**