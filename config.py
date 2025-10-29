"""
Arquivo de Configuração (constantes.py)

Armazena todas as constantes globais, caminhos de arquivos,
cores, e dados estáticos (como o layout do labirinto)
para o jogo Pac-Man.
"""

import pygame
from pathlib import Path

# --- Inicialização Básica (só para ter os tipos, se necessário) ---
# O init() real será chamado em main.py
pygame.font.init()

# --- Constantes Globais de Jogo ---
TAM_CELULA = 30
COLUNAS = 32
LINHAS_LABIRINTO = 15
LARGURA = COLUNAS * TAM_CELULA
ALTURA = (LINHAS_LABIRINTO + 3) * TAM_CELULA

FPS = 60

# --- Caminhos de Arquivos e Pastas ---
ARQUIVO_USUARIOS = "data/usuarios.json"
ARQUIVO_REWARDS = "data/rewards_data.json"
ARQUIVO_AVALIACOES = "data/avaliacoes.json"

MUSICA_LABIRINTO = "assets/sounds/Musica-Labirinto.mp3"
MUSICA_GAME_OVER = "assets/sounds/Musica-Derrota.mp3"

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
ANIM32_DIR = ASSETS_DIR / "anim32"
CENTROS48_DIR = ASSETS_DIR / "centros48"
CENTROS_DIR = ASSETS_DIR / "centros"

# --- Cores ---
PRETO = (0, 0, 0)
AZUL_PAREDE = (0, 0, 139)
AMARELO = (255, 223, 0)
BRANCO = (255, 255, 255)
VERMELHO = (200, 0, 0)
VERDE_CONTINUAR = (0, 150, 0)
CINZA = (105, 105, 105)
ROXO = (128, 0, 128)
CINZA_ESCURO = (40, 40, 40)
VERMELHO_CRISE = (178, 34, 34)

COR_MOEDA = (220, 30, 30)
COR_ALIMENTO = AMARELO
COR_LIVRO = (135, 206, 250)
COR_TIJOLO = (176, 96, 52)
COR_ESCOLA = (65, 105, 225)
COR_HOSPITAL = (220, 20, 60)
COR_MERCADO = (34, 139, 34)
COR_MORADIA = (160, 82, 45)

COR_FUNDO_UI = (10, 10, 30)
COR_INPUT_INATIVO = (100, 100, 100)
COR_INPUT_ATIVO = (200, 200, 200)
COR_BOTAO = (0, 100, 0)
COR_BOTAO_VOLTAR = (150, 0, 0)

COR_OURO = (255, 215, 0)
COR_PRATA = (192, 192, 192)
COR_BRONZE = (205, 127, 50)
COR_REWARD = (0, 200, 255)

# --- Layout do Labirinto ---
LABIRINTO_LAYOUT = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,1,0,0,0,1],
    [1,0,1,0,0,0,0,1,1,1,1,0,1,0,1,1,1,1,0,1,0,1,1,1,1,0,0,0,0,1,0,1],
    [1,0,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,1,0,1],
    [1,0,0,0,0,0,1,0,1,1,1,0,1,1,0,1,1,0,1,1,0,1,1,1,1,0,1,0,0,0,0,1],
    [1,1,1,0,1,1,1,0,0,0,1,0,0,1,0,0,0,0,1,0,0,1,0,0,0,0,1,1,1,0,1,1],
    [1,0,0,0,0,0,0,0,1,0,1,1,0,1,1,0,0,1,1,0,1,1,0,1,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,1,0,1,1,1,1,1,0,0,1,1,1,1,1,0,1,0,0,0,0,0,0,0,1],
    [1,1,1,0,1,1,1,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,1,1,1,0,1,1,1],
    [1,0,0,0,0,0,1,0,1,1,1,0,1,0,0,0,0,0,0,1,0,1,1,1,1,0,1,0,0,0,0,1],
    [1,0,1,1,1,0,1,0,0,0,1,0,1,1,1,0,0,1,1,1,0,1,0,0,0,0,1,0,1,1,0,1],
    [1,0,0,0,1,0,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,0,0,0,0,1],
    [1,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

# (Otimização: Pré-calcula as posições livres como um frozenset imutável)
MAPA_POSICOES_LIVRES = frozenset(
    (x, y) for y, linha in enumerate(LABIRINTO_LAYOUT) 
    for x, celula in enumerate(linha) if celula == 0
)

# --- Textos Estáticos ---
QUESTOES_AVALIACAO = [
    ("Usabilidade do produto", [
        "Quao facil e utilizar o sistema pela primeira vez?",
        "Quao rapida e a realizacao de atividades no sistema?",
        "Quao agradavel e a utilizacao do sistema?"
    ]),
    ("Qualidade geral do produto", [
        "As cores usadas sao adequadas?",
        "As fontes dos textos sao legiveis?",
        "O tamanho dos botoes, figuras, etc. e adequado?",
        "Os itens abordados foram concluidos de modo satisfatorio?"
    ])
]

MENSAGENS_GAME_OVER = {
    "Desemprego": "O fantasma do Desemprego te perseguiu implacavelmente, deixando seus sonhos de prosperidade em ruinas. A falta de oportunidades se tornou uma armadilha sem saida...",
    "Desigualdade": "A sombra da Desigualdade te engoliu por completo, criando um abismo intransponivel entre voce e uma vida digna. A injustica social mostrou sua face mais cruel...",
    "Falta de Acesso": "A barreira da Falta de Acesso se ergueu como um muro intransponivel, bloqueando todos os caminhos que levam ao progresso. A exclusao social te consumiu...",
    "Crise Economica": "A tempestade da Crise Economica devastou todos os seus esforcos, transformando esperancas em desespero. O sistema financeiro te esmagou sem piedade..."
}