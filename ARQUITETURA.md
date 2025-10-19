# Arquitetura do Sistema - Pac-Man: A Missão Comunitária

## 📐 Visão Geral da Arquitetura

O sistema foi desenvolvido seguindo uma arquitetura modular e orientada a objetos, com separação clara de responsabilidades.

## 🏗️ Estrutura do Sistema

### 1. Camada de Apresentação (UI)
```
┌─────────────────────────────────────┐
│           Interface do Usuário       │
├─────────────────────────────────────┤
│ • Tela Inicial (Login/Cadastro)     │
│ • Seleção de Dificuldade            │
│ • Sistema de Recompensas            │
│ • Ranking de Jogadores              │
│ • HUD do Jogo                       │
│ • Tela de Game Over                 │
└─────────────────────────────────────┘
```

### 2. Camada de Lógica de Negócio
```
┌─────────────────────────────────────┐
│          Classes Principais         │
├─────────────────────────────────────┤
│ • Player (Jogador)                  │
│ • Inimigo (Fantasma)                │
│ • CentroComunitario                 │
│ • RewardsSystem                     │
└─────────────────────────────────────┘
```

### 3. Camada de Dados
```
┌─────────────────────────────────────┐
│         Persistência de Dados       │
├─────────────────────────────────────┤
│ • usuarios.json                     │
│ • rewards_data.json                 │
└─────────────────────────────────────┘
```

## 🔄 Fluxo de Dados

### Fluxo Principal do Jogo
1. **Inicialização** → Carregamento de dados de usuários e recompensas
2. **Autenticação** → Validação de credenciais
3. **Seleção de Dificuldade** → Configuração do jogo
4. **Loop Principal** → Execução do jogo
5. **Processamento de Resultados** → Atualização de estatísticas e recompensas

### Fluxo do Sistema de Recompensas
1. **Coleta de Estatísticas** → Durante o jogo
2. **Verificação de Tarefas** → Após cada ação
3. **Verificação de Conquistas** → No final da partida
4. **Atualização de Pontos** → Persistência no arquivo
5. **Atualização de Ranking** → Recálculo da classificação

## 🎯 Padrões de Design Utilizados

### 1. Observer Pattern
- Sistema de recompensas observa as ações do jogador
- Atualizações automáticas de tarefas e conquistas

### 2. State Pattern
- Diferentes estados do jogo (menu, jogo, game over)
- Transições controladas entre estados

### 3. Strategy Pattern
- Diferentes comportamentos de inimigos baseados na dificuldade
- Algoritmos de movimento adaptativos

## 📊 Estrutura de Dados

### Player Stats
```json
{
  "recursos_coletados": 0,
  "itens_entregues": 0,
  "tempo_jogado": 0,
  "inicio_partida": "timestamp"
}
```

### Rewards Data
```json
{
  "username": {
    "pontos_totais": 0,
    "nivel": 1,
    "conquistas": {},
    "tarefas_diarias": {},
    "ultima_atualizacao": "timestamp",
    "historico_partidas": []
  }
}
```

## 🔧 Componentes Técnicos

### Gerenciamento de Estados
- **Estados**: tela_inicial, tela_login, tela_cadastro, tela_dificuldade, jogo, tela_game_over, tela_rewards, tela_ranking
- **Transições**: Controladas por eventos de mouse e teclado
- **Persistência**: Dados salvos automaticamente

### Sistema de Recompensas
- **Tarefas Diárias**: Resetadas automaticamente a cada dia
- **Conquistas**: Desbloqueadas baseadas em estatísticas
- **Ranking**: Atualizado em tempo real
- **Níveis**: Calculados dinamicamente

### Tratamento de Erros
- **Validação de Input**: Verificação de campos obrigatórios
- **Manipulação de Arquivos**: Tratamento de arquivos não encontrados
- **Recuperação de Dados**: Inicialização com dados padrão

## 🎨 Renderização

### Pipeline de Renderização
1. **Background** → Preenchimento da tela
2. **Labirinto** → Desenho das paredes
3. **Recursos** → Coletáveis espalhados
4. **Centros** → Prédios comunitários
5. **Personagens** → Player e inimigos
6. **HUD** → Interface sobreposta
7. **UI** → Menus e telas

### Otimizações
- **Double Buffering**: Pygame gerencia automaticamente
- **Sprites**: Elementos gráficos simples para performance
- **Culling**: Renderização apenas de elementos visíveis

## 🔒 Segurança e Validação

### Validação de Dados
- **Usuários**: Verificação de campos obrigatórios
- **Senhas**: Armazenamento simples (sem criptografia)
- **Estatísticas**: Validação de valores numéricos
- **Arquivos**: Verificação de integridade JSON

### Tratamento de Exceções
- **FileNotFoundError**: Criação automática de arquivos
- **JSONDecodeError**: Inicialização com dados padrão
- **KeyError**: Verificação de existência de chaves

## 📈 Métricas e Monitoramento

### Estatísticas Coletadas
- **Performance**: Tempo de jogo, recursos coletados
- **Engajamento**: Frequência de jogos, tarefas completadas
- **Progresso**: Níveis alcançados, conquistas desbloqueadas

### Logs de Sistema
- **Histórico de Partidas**: Últimas 50 partidas por usuário
- **Atualizações**: Timestamps de modificações
- **Erros**: Tratamento silencioso com fallbacks

## 🚀 Extensibilidade

### Pontos de Extensão
- **Novos Tipos de Recursos**: Adição fácil de novos coletáveis
- **Novas Conquistas**: Sistema flexível para adicionar objetivos
- **Novas Dificuldades**: Configuração de parâmetros de jogo
- **Novos Centros**: Expansão do mapa comunitário

### APIs Internas
- **RewardsSystem**: Interface clara para adicionar pontos
- **Player**: Métodos para atualizar estatísticas
- **CentroComunitario**: Sistema de entrega extensível

## 🔄 Manutenibilidade

### Princípios Aplicados
- **DRY (Don't Repeat Yourself)**: Funções reutilizáveis
- **SOLID**: Responsabilidades bem definidas
- **Clean Code**: Código legível e bem documentado
- **Separation of Concerns**: Camadas bem separadas

### Testabilidade
- **Métodos Públicos**: Interface clara para testes
- **Dependências Injetadas**: Facilita mocking
- **Estados Isolados**: Cada componente é independente

---

Esta arquitetura garante um sistema robusto, extensível e de fácil manutenção, seguindo as melhores práticas de desenvolvimento de software.

