import pygame
import sys
import random
import math
import json
import datetime
from pathlib import Path
from collections import deque
from typing import Dict, List, Tuple

# --- Inicializacao do Pygame ---
pygame.init()
pygame.mixer.init()

# --- Constantes Globais ---
TAM_CELULA = 30
COLUNAS = 32
LINHAS_LABIRINTO = 15
LARGURA = COLUNAS * TAM_CELULA
ALTURA = (LINHAS_LABIRINTO + 3) * TAM_CELULA

FPS = 60
ARQUIVO_USUARIOS = "usuarios.json"
ARQUIVO_REWARDS = "rewards_data.json"
ARQUIVO_AVALIACOES = "avaliacoes.json"
MUSICA_LABIRINTO = "assets/sounds/Musica-Labirinto.mp3"
MUSICA_GAME_OVER = "assets/sounds/Musica-Derrota.mp3"
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
ANIM32_DIR = ASSETS_DIR / "anim32"
CENTROS48_DIR = ASSETS_DIR / "centros48"
CENTROS_DIR = ASSETS_DIR / "centros"

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pac-Man - A Missao Comunitaria")
clock = pygame.time.Clock()

# --- Cores ---
PRETO, AZUL_PAREDE, AMARELO, BRANCO = (0,0,0), (0,0,139), (255,223,0), (255,255,255)
VERMELHO, VERDE_CONTINUAR, CINZA, ROXO = (200,0,0), (0,150,0), (105,105,105), (128,0,128)
CINZA_ESCURO, VERMELHO_CRISE = (40,40,40), (178,34,34)
COR_MOEDA, COR_ALIMENTO, COR_LIVRO, COR_TIJOLO = (220,30,30), AMARELO, (135,206,250), (176,96,52)
COR_ESCOLA, COR_HOSPITAL, COR_MERCADO, COR_MORADIA = (65,105,225), (220,20,60), (34,139,34), (160,82,45)
COR_FUNDO_UI, COR_INPUT_INATIVO, COR_INPUT_ATIVO = (10,10,30), (100,100,100), (200,200,200)
COR_BOTAO, COR_BOTAO_VOLTAR = (0,100,0), (150,0,0)
COR_OURO, COR_PRATA, COR_BRONZE, COR_REWARD = (255,215,0), (192,192,192), (205,127,50), (0,200,255)

QUESTOES_AVALIACAO = [
    ("Usabilidade do produto", [
        "QuÃ£o fÃ¡cil Ã© utilizar o sistema pela primeira vez?",
        "QuÃ£o rÃ¡pida Ã© a realizaÃ§Ã£o de atividades no sistema?",
        "QuÃ£o agradÃ¡vel Ã© a utilizaÃ§Ã£o do sistema?"
    ]),
    ("Qualidade geral do produto", [
        "As cores usadas sÃ£o adequadas?",
        "As fontes dos textos sÃ£o legÃ­veis?",
        "O tamanho dos botÃµes, figuras, etc. Ã© adequado?",
        "Os itens abordados foram concluÃ­dos de modo satisfatÃ³rio?"
    ])
]

# =======================
#   CONTROLE DE MÃšSICA
# =======================

def tocar_musica_labirinto():
    """Toca a mÃºsica de fundo do labirinto em loop"""
    try:
        pygame.mixer.music.load(MUSICA_LABIRINTO)
        pygame.mixer.music.set_volume(0.3)  # Volume baixo para nÃ£o atrapalhar
        pygame.mixer.music.play(-1)  # -1 = loop infinito
        # print(f"ðŸŽµ MÃºsica do labirinto iniciada: {MUSICA_LABIRINTO}")
    except pygame.error as e:
        print(f"âŒ Erro ao carregar mÃºsica do labirinto: {e}")
    except Exception as e:
        print(f"âŒ Erro inesperado ao tocar mÃºsica do labirinto: {e}")

def tocar_musica_game_over():
    """Toca a mÃºsica de game over uma vez, comeÃ§ando em 5 segundos"""
    try:
        pygame.mixer.music.load(MUSICA_GAME_OVER)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(0, start=5.0)  # 0 = tocar uma vez, start=5.0 = comeÃ§ar em 5 segundos
        # print(f"ðŸŽµ MÃºsica de game over iniciada (5s): {MUSICA_GAME_OVER}")
    except pygame.error as e:
        print(f"âŒ Erro ao carregar mÃºsica de game over: {e}")
        print("â„¹ï¸  Tentando usar mÃºsica do labirinto como fallback...")
        # Fallback: usar mÃºsica do labirinto se game over falhar
        try:
            pygame.mixer.music.load(MUSICA_LABIRINTO)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(0)
            print(f"ðŸŽµ Usando mÃºsica do labirinto como fallback")
        except:
            pygame.mixer.music.stop()
    except Exception as e:
        print(f"âŒ Erro inesperado ao tocar mÃºsica de game over: {e}")
        pygame.mixer.music.stop()

def parar_musica():
    """Para a mÃºsica atual"""
    try:
        pygame.mixer.music.stop()
        # print("ðŸ”‡ MÃºsica parada")
    except Exception as e:
        print(f"âŒ Erro ao parar mÃºsica: {e}")

# =======================
#   LOADING DE ASSETS
# =======================

def _segura_surface(tamanho: Tuple[int,int], cor=(255,0,0), shape="circle") -> pygame.Surface:
    surf = pygame.Surface(tamanho, pygame.SRCALPHA)
    cx, cy = tamanho[0]//2, tamanho[1]//2
    if shape == "circle":
        pygame.draw.circle(surf, cor, (cx, cy), min(cx, cy)-2)
    else:
        pygame.draw.rect(surf, cor, (2,2,tamanho[0]-4,tamanho[1]-4), border_radius=4)
    return surf

def aplicar_cor_surface(surface: pygame.Surface, cor: Tuple[int,int,int]) -> pygame.Surface:
    """Retorna uma cÃ³pia da surface original com a cor RGB substituÃ­da, mantendo a transparÃªncia."""
    recolorida = surface.copy()
    recolorida.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    recolorida.fill((*cor, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return recolorida

def _resolve_asset_path(relative) -> Path:
    path_obj = Path(relative)
    if path_obj.is_absolute():
        return path_obj
    return BASE_DIR / path_obj

def _load_image(path: Path) -> pygame.Surface | None:
    resolved = _resolve_asset_path(path)
    if not resolved.exists():
        return None
    try:
        return pygame.image.load(str(resolved)).convert_alpha()
    except Exception:
        return None

def cortar_spritesheet(path:str, frame_w:int, frame_h:int, num_frames:int=None, escala:Tuple[int,int]=None) -> List[pygame.Surface]:
    sheet = _load_image(path)
    if sheet is None:
        return []
    sw, sh = sheet.get_size()
    cols, rows = sw // frame_w, sh // frame_h
    frames = []
    count = cols * rows if num_frames is None else min(num_frames, cols*rows)
    for i in range(count):
        c, r = i % cols, i // cols
        rect = pygame.Rect(c*frame_w, r*frame_h, frame_w, frame_h)
        frame = sheet.subsurface(rect).copy()
        if escala:
            frame = pygame.transform.smoothscale(frame, escala)
        frames.append(frame)
    return frames

def carregar_sequencia_pasta(pasta, base: str, num_frames: int, tamanho: Tuple[int,int]) -> List[pygame.Surface]:
    frames = []
    pasta_path = _resolve_asset_path(pasta)
    for i in range(num_frames):
        arq = pasta_path / f"{base}_{i}.png"
        img = _load_image(arq)
        if img:
            img = pygame.transform.smoothscale(img, tamanho)
            frames.append(img)
    return frames

def carregar_pacman_frames(tamanho=(32,32)) -> Dict[str, List[pygame.Surface]]:
    sheet_path = ASSETS_DIR / "pacman" / "pacman_sheet.png"
    sheet_frames = cortar_spritesheet(sheet_path, 32, 32, escala=tamanho)
    if sheet_frames:
        def take(a, b): return sheet_frames[a:b] if len(sheet_frames)>=b else []
        direita = take(0,4) or sheet_frames[:4]
        esquerda = take(4,8) or [pygame.transform.flip(f, True, False) for f in direita]
        cima = take(8,12) or [pygame.transform.rotate(f, 90) for f in direita]
        baixo = take(12,16) or [pygame.transform.rotate(f, -90) for f in direita]
        return {"direita":direita, "esquerda":esquerda, "cima":cima, "baixo":baixo}
    seq_dir = ANIM32_DIR / "pacman"
    direita = carregar_sequencia_pasta(seq_dir, "pacman_right", 4, tamanho)
    if direita:
        esquerda = [pygame.transform.flip(f, True, False) for f in direita]
        cima = [pygame.transform.rotate(f, 90) for f in direita]
        baixo = [pygame.transform.rotate(f, -90) for f in direita]
        return {"direita":direita, "esquerda":esquerda, "cima":cima, "baixo":baixo}
    base = _segura_surface(tamanho, AMARELO, "circle")
    return {"direita":[base], "esquerda":[base], "cima":[base], "baixo":[base]}

def carregar_fantasma_frames(nome_interno:str, tamanho=(48,48), invisivel=False) -> List[pygame.Surface]:
    map_sheet = {
        "Desemprego": "desemprego.png",
        "Desigualdade": "desigualdade.png",
        "Falta de Acesso": "falta_acesso_visible.png" if not invisivel else "falta_acesso_invisivel.png",
        "Crise Economica": "crise_economica.png",
    }
    sheet_key = map_sheet.get(nome_interno)
    if sheet_key:
        path = ASSETS_DIR / 'ghosts' / sheet_key
        frames = cortar_spritesheet(path, 48, 48, escala=tamanho)
        if frames: return frames if len(frames) >= 2 else frames*2
    
    pasta_map = {
        "Desemprego": (ANIM32_DIR / "ghost_desemprego", "ghost_desemprego"),
        "Crise Economica": (ANIM32_DIR / "ghost_crise_economica", "ghost_crise_economica"),
        "Desigualdade": (ANIM32_DIR / "ghost_desigualdade_small", "ghost_desigualdade_small"),
        "Falta de Acesso": (ANIM32_DIR / ("ghost_falta_acesso_visible" if not invisivel else "ghost_falta_acesso_invisivel"),
                              "ghost_falta_acesso_visible" if not invisivel else "ghost_falta_acesso_invisivel")
    }
    pasta, base = pasta_map.get(nome_interno, (None, None))
    if pasta:
        seq = carregar_sequencia_pasta(pasta, base, 2, tamanho)
        if seq: return seq
    cor = ROXO if nome_interno=="Desigualdade" else (VERMELHO_CRISE if nome_interno=="Crise Economica" else CINZA)
    if invisivel: cor = (120,120,120,120)
    return [_segura_surface(tamanho, cor, "circle"), _segura_surface(tamanho, cor, "circle")]

def carregar_item(nome: str, tamanho: Tuple[int, int]) -> pygame.Surface:
    nome_lower = nome.lower()
    caminhos = [ANIM32_DIR / "itens" / f"item_{nome}.png", ASSETS_DIR / "items" / f"{nome_lower}.png"]
    for arq in caminhos:
        img = _load_image(arq)
        if img is not None:
            img = pygame.transform.smoothscale(img, tamanho)
            if nome_lower == "moeda":
                return aplicar_cor_surface(img, COR_MOEDA)
            if nome_lower == "alimento":
                return aplicar_cor_surface(img, COR_ALIMENTO)
            return img
    cor_padrao = {
        "moeda": COR_MOEDA,
        "alimento": COR_ALIMENTO,
        "livro": COR_LIVRO,
        "tijolo": COR_TIJOLO
    }.get(nome_lower, COR_ALIMENTO)
    return _segura_surface(tamanho, cor_padrao, "circle")

def carregar_centro(prefixo: str, tamanho: Tuple[int, int]) -> List[pygame.Surface]:
    tentativas = [
        [CENTROS48_DIR / f"{prefixo}_{i}.png" for i in range(3)],
        [CENTROS_DIR / f"{prefixo}_{i}.png" for i in range(3)]
    ]
    for lista in tentativas:
        imgs = [_load_image(arq) for arq in lista]
        if all(imgs):
            return [pygame.transform.smoothscale(img, tamanho) for img in imgs]
    return [_segura_surface(tamanho, (0,255,0), "rect") for _ in range(3)]

# --- Layout do Labirinto ---
labirinto = [
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
posicoes_livres = [(x, y) for y, linha in enumerate(labirinto) for x, celula in enumerate(linha) if celula == 0]

# --- Sistema de Recompensas ---
class RewardsSystem:
    # ... (cÃ³digo da classe RewardsSystem intacto) ...
    def __init__(self):
        self.rewards_data = self.carregar_rewards()
        self.daily_tasks = {"coletar_10_recursos": {"descricao": "Colete 10 recursos", "pontos": 50, "concluida": False},"entregar_5_itens": {"descricao": "Entregue 5 itens nos centros", "pontos": 75, "concluida": False},"jogar_3_partidas": {"descricao": "Jogue 3 partidas", "pontos": 100, "concluida": False},"sobreviver_2_minutos": {"descricao": "Sobreviva por 2 minutos", "pontos": 60, "concluida": False}}
        self.achievements = {"primeira_vitoria": {"nome": "Primeira Vitoria", "descricao": "Venca uma partida", "pontos": 200, "desbloqueada": False},"colecionador": {"nome": "Colecionador", "descricao": "Colete 50 recursos", "pontos": 150, "desbloqueada": False},"construtor": {"nome": "Construtor", "descricao": "Complete 3 centros comunitarios", "pontos": 300, "desbloqueada": False},"sobrevivente": {"nome": "Sobrevivente", "descricao": "Sobreviva 5 minutos", "pontos": 250, "desbloqueada": False}}
    def carregar_rewards(self) -> Dict:
        try:
            with open(ARQUIVO_REWARDS, 'r', encoding='utf-8') as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): return {}
    def salvar_rewards(self):
        with open(ARQUIVO_REWARDS, 'w', encoding='utf-8') as f: json.dump(self.rewards_data, f, indent=4, ensure_ascii=False)
    def obter_usuario_rewards(self, username: str) -> Dict:
        if username not in self.rewards_data: self.rewards_data[username] = {"pontos_totais": 0,"nivel": 1,"conquistas": {},"tarefas_diarias": {},"ultima_atualizacao": datetime.datetime.now().isoformat(),"historico_partidas": []}
        return self.rewards_data[username]
    def adicionar_pontos(self, username: str, pontos: int, origem: str = "jogo"):
        user_data = self.obter_usuario_rewards(username)
        user_data["pontos_totais"] += pontos
        user_data["ultima_atualizacao"] = datetime.datetime.now().isoformat()
        user_data["historico_partidas"].append({"data": datetime.datetime.now().isoformat(),"pontos": pontos,"origem": origem})
        if len(user_data["historico_partidas"]) > 50: user_data["historico_partidas"] = user_data["historico_partidas"][-50:]
        user_data["nivel"] = min(100, (user_data["pontos_totais"] // 1000) + 1)
        self.salvar_rewards()
    def verificar_tarefas_diarias(self, username: str, stats: Dict):
        user_data = self.obter_usuario_rewards(username)
        hoje = datetime.datetime.now().date().isoformat()
        if user_data.get("ultima_tarefa_dia") != hoje: user_data["tarefas_diarias"] = {k:v.copy() for k,v in self.daily_tasks.items()}; user_data["ultima_tarefa_dia"] = hoje
        tarefas = user_data["tarefas_diarias"]
        if stats.get("recursos_coletados", 0) >= 10 and not tarefas["coletar_10_recursos"]["concluida"]: tarefas["coletar_10_recursos"]["concluida"] = True; self.adicionar_pontos(username, 50, "tarefa_diaria")
        if stats.get("itens_entregues", 0) >= 5 and not tarefas["entregar_5_itens"]["concluida"]: tarefas["entregar_5_itens"]["concluida"] = True; self.adicionar_pontos(username, 75, "tarefa_diaria")
        if stats.get("partidas_jogadas", 0) >= 3 and not tarefas["jogar_3_partidas"]["concluida"]: tarefas["jogar_3_partidas"]["concluida"] = True; self.adicionar_pontos(username, 100, "tarefa_diaria")
        if stats.get("tempo_sobrevivencia", 0) >= 120 and not tarefas["sobreviver_2_minutos"]["concluida"]: tarefas["sobreviver_2_minutos"]["concluida"] = True; self.adicionar_pontos(username, 60, "tarefa_diaria")
        self.salvar_rewards()
    def verificar_conquistas(self, username: str, stats: Dict):
        user_data = self.obter_usuario_rewards(username)
        conquistas = user_data.setdefault("conquistas", {})
        for achievement_id, achievement in self.achievements.items():
            if achievement_id not in conquistas: conquistas[achievement_id] = {"desbloqueada": False, "data": None}
            if not conquistas[achievement_id]["desbloqueada"]:
                desbloqueou = False
                if achievement_id == "primeira_vitoria" and stats.get("vitorias", 0) >= 1: desbloqueou = True
                elif achievement_id == "colecionador" and stats.get("recursos_coletados", 0) >= 50: desbloqueou = True
                elif achievement_id == "construtor" and stats.get("centros_completos", 0) >= 3: desbloqueou = True
                elif achievement_id == "sobrevivente" and stats.get("tempo_sobrevivencia", 0) >= 300: desbloqueou = True
                if desbloqueou: conquistas[achievement_id] = {"desbloqueada": True,"data": datetime.datetime.now().isoformat()}; self.adicionar_pontos(username, achievement["pontos"], "conquista")
        self.salvar_rewards()
    def obter_ranking(self, limite: int = 10) -> List[Tuple[str, int]]:
        ranking = [(u, d.get("pontos_totais", 0)) for u, d in self.rewards_data.items()]; ranking.sort(key=lambda x: x[1], reverse=True); return ranking[:limite]

# --- Pathfinding ---
def encontrar_caminho(labirinto: List[List[int]], inicio: Tuple[int, int], fim: Tuple[int, int]) -> List[Tuple[int, int]]:
    if labirinto[fim[1]][fim[0]] == 1: return []
    fila = deque([[inicio]])
    visitados = {inicio}
    while fila:
        caminho = fila.popleft()
        x, y = caminho[-1]
        if (x, y) == fim: return caminho
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            prox_x, prox_y = x + dx, y + dy
            if (0 <= prox_x < COLUNAS and 0 <= prox_y < LINHAS_LABIRINTO and
                    labirinto[prox_y][prox_x] == 0 and (prox_x, prox_y) not in visitados):
                novo_caminho = list(caminho)
                novo_caminho.append((prox_x, prox_y))
                fila.append(novo_caminho)
                visitados.add((prox_x, prox_y))
    return []

# --- Classes do Jogo ---
class Player:
    def __init__(self, x, y):
        self.px, self.py = x * TAM_CELULA, y * TAM_CELULA
        self.dir_x, self.dir_y, self.vel_x, self.vel_y = 0, 0, 0, 0
        self.velocidade = 3
        self.inventario, self.capacidade_inventario = [], 5
        self.caminho = []
        self.stats = {"recursos_coletados": 0,"itens_entregues": 0,"tempo_jogado": 0, "inicio_partida": datetime.datetime.now()}
        self.carregar_imagens()

    def carregar_imagens(self):
        imgs = carregar_pacman_frames((32,32))
        self.frames_direita = imgs["direita"]
        self.frames_esquerda = imgs["esquerda"]
        self.frames_cima = imgs["cima"]
        self.frames_baixo = imgs["baixo"]
        self.frames_atual, self.frame_atual, self.timer_animacao, self.tempo_por_frame = self.frames_direita, 0, 0, 110

    @property
    def grid_x(self): return int((self.px + TAM_CELULA // 2) / TAM_CELULA)
    @property
    def grid_y(self): return int((self.py + TAM_CELULA // 2) / TAM_CELULA)

    def reiniciar(self):
        self.px, self.py = 1 * TAM_CELULA, 1 * TAM_CELULA
        self.dir_x, self.dir_y, self.vel_x, self.vel_y = 0, 0, 0, 0
        self.inventario.clear()
        self.caminho.clear()
        self.stats["inicio_partida"] = datetime.datetime.now()
        if hasattr(self, 'frames_direita'): self.frames_atual, self.frame_atual, self.timer_animacao = self.frames_direita, 0, 0

    def atualizar_animacao(self, dt):
        if self.frames_atual:
            self.timer_animacao += dt
            if self.timer_animacao >= self.tempo_por_frame:
                self.timer_animacao = 0
                self.frame_atual = (self.frame_atual + 1) % len(self.frames_atual)

    def atualizar_direcao(self):
            if self.vel_x > 0: self.frames_atual = self.frames_direita
            elif self.vel_x < 0: self.frames_atual = self.frames_esquerda
            elif self.vel_y < 0: self.frames_atual = self.frames_cima
            elif self.vel_y > 0: self.frames_atual = self.frames_baixo
            
    def mover(self):
        esta_alinhado = self.px % TAM_CELULA == 0 and self.py % TAM_CELULA == 0
        if esta_alinhado:
            if self.caminho:
                if (self.grid_x, self.grid_y) == self.caminho[0]: self.caminho.pop(0)
                if self.caminho:
                    proximo_ponto = self.caminho[0]
                    self.vel_x = proximo_ponto[0] - self.grid_x
                    self.vel_y = proximo_ponto[1] - self.grid_y
                else: self.vel_x, self.vel_y = 0, 0
            else:
                if self.dir_x != 0 or self.dir_y != 0:
                    prox_grid_x, prox_grid_y = self.grid_x + self.dir_x, self.grid_y + self.dir_y
                    if not self.colide_parede(prox_grid_x, prox_grid_y): 
                        self.vel_x, self.vel_y = self.dir_x, self.dir_y
        self.px += self.vel_x * self.velocidade
        self.py += self.vel_y * self.velocidade
        if esta_alinhado:
            prox_grid_x, prox_grid_y = self.grid_x + self.vel_x, self.grid_y + self.vel_y
            if self.colide_parede(prox_grid_x, prox_grid_y):
                self.px, self.py, self.vel_x, self.vel_y = self.grid_x * TAM_CELULA, self.grid_y * TAM_CELULA, 0, 0
                self.caminho.clear()
        self.atualizar_direcao()
        
    def colide_parede(self, x, y): return not (0 <= x < COLUNAS and 0 <= y < LINHAS_LABIRINTO and labirinto[y][x] != 1)
    
    def coletar(self, recursos):
        if len(self.inventario) < self.capacidade_inventario:
            for recurso in recursos[:]:
                if recurso['x'] == self.grid_x and recurso['y'] == self.grid_y:
                    self.inventario.append(recurso['tipo'])
                    self.stats["recursos_coletados"] += 1
                    recursos.remove(recurso)
                    break

    def descartar_item(self):
        if self.inventario: self.inventario.pop()

    def desenhar(self, surface):
        centro = (self.px + TAM_CELULA//2, self.py + TAM_CELULA//2)
        if self.frames_atual and self.frames_atual[self.frame_atual]:
            img = self.frames_atual[self.frame_atual]
            rect = img.get_rect(center=centro)
            surface.blit(img, rect)
        else:
            pygame.draw.circle(surface, AMARELO, centro, TAM_CELULA//2 - 3)

class Inimigo:
    id_counter = 0

    def __init__(self, x, y, cor, nome, dificuldade="Default", *, is_clone=False, parent_id=None):
        self.px, self.py = x * TAM_CELULA, y * TAM_CELULA
        self.cor, self.nome = cor, nome
        self.vel_x, self.vel_y = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.invisivel = (nome == "Falta de Acesso")
        self.visivel = True
        self.timer_invisibilidade, self.tempo_para_trocar = 0, random.randint(30, 60)
        self.dificuldade = dificuldade
        self.is_clone = is_clone
        self.parent_id = parent_id
        self.id = Inimigo.id_counter
        Inimigo.id_counter += 1

        if self.dificuldade == "Easy": self.velocidade, self.comportamento_aleatorio = 1.5, 1.0
        elif self.dificuldade == "Hard": self.velocidade, self.comportamento_aleatorio = 2.5, 0.25
        else: self.velocidade, self.comportamento_aleatorio = 2.0, 0.7

        self.frames = carregar_fantasma_frames(self.nome, (48, 48), invisivel=False)
        self.frames_invisivel = carregar_fantasma_frames(self.nome, (48, 48), invisivel=True) if self.invisivel else None

        self.pode_dividir = (self.nome == "Crise Economica" and not self.is_clone)
        self.split_cooldown_ms = random.randint(5500, 9000) if self.pode_dividir else 0
        self.split_elapsed_ms = 0
        self.split_duration_ms = random.randint(2000, 3800) if self.pode_dividir else 0
        self.split_active = False
        self.split_active_elapsed_ms = 0
        self.clone_ids: List[int] = []

    @property
    def grid_x(self): return int((self.px + TAM_CELULA // 2) / TAM_CELULA)
    @property
    def grid_y(self): return int((self.py + TAM_CELULA // 2) / TAM_CELULA)
    
    def mover(self, player):
        if self.invisivel:
            self.timer_invisibilidade += 1
            if self.timer_invisibilidade > self.tempo_para_trocar * (FPS / 10):
                self.visivel = not self.visivel; self.timer_invisibilidade = 0; self.tempo_para_trocar = random.randint(20, 50)
        if self.px % TAM_CELULA == 0 and self.py % TAM_CELULA == 0:
            opcoes = []
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                if not self.colide_parede(self.grid_x + dx, self.grid_y + dy): opcoes.append((dx, dy))
            
            if len(opcoes) > 1:
                reverso = (-self.vel_x, -self.vel_y)
                if reverso in opcoes:
                    opcoes.remove(reverso)

            if random.random() < self.comportamento_aleatorio or not opcoes:
                    if opcoes: self.vel_x, self.vel_y = random.choice(opcoes)
            else:
                dist_x, dist_y = player.grid_x - self.grid_x, player.grid_y - self.grid_y
                movimentos_preferidos = []
                if abs(dist_x) > abs(dist_y):
                    if dist_x > 0 and (1, 0) in opcoes: movimentos_preferidos.append((1, 0))
                    elif dist_x < 0 and (-1, 0) in opcoes: movimentos_preferidos.append((-1, 0))
                    if dist_y > 0 and (0, 1) in opcoes: movimentos_preferidos.append((0, 1))
                    elif dist_y < 0 and (0, -1) in opcoes: movimentos_preferidos.append((0, -1))
                else:
                    if dist_y > 0 and (0, 1) in opcoes: movimentos_preferidos.append((0, 1))
                    elif dist_y < 0 and (0, -1) in opcoes: movimentos_preferidos.append((0, -1))
                    if dist_x > 0 and (1, 0) in opcoes: movimentos_preferidos.append((1, 0))
                    elif dist_x < 0 and (-1, 0) in opcoes: movimentos_preferidos.append((-1, 0))
                
                if movimentos_preferidos: self.vel_x, self.vel_y = movimentos_preferidos[0]
                elif opcoes: self.vel_x, self.vel_y = random.choice(opcoes)
        
        self.px += self.vel_x * self.velocidade
        self.py += self.vel_y * self.velocidade

    def _escolher_direcao_clone(self):
        direcoes = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        atual = (self.vel_x, self.vel_y)
        if atual in direcoes: direcoes.remove(atual)
        return random.choice(direcoes) if direcoes else (0,0)

    def _criar_clone(self):
        clone = Inimigo(self.grid_x, self.grid_y, self.cor, self.nome, self.dificuldade, is_clone=True, parent_id=self.id)
        clone.px, clone.py = self.px, self.py
        clone.vel_x, clone.vel_y = self._escolher_direcao_clone()
        return clone

    def atualizar_divisao(self, dt_ms, novos_inimigos, remover_ids):
        if not self.pode_dividir: return
        if not self.split_active:
            self.split_elapsed_ms += dt_ms
            if self.split_elapsed_ms >= self.split_cooldown_ms:
                self.split_elapsed_ms = 0; self.split_active = True; self.split_active_elapsed_ms = 0
                novo_clone = self._criar_clone()
                novos_inimigos.append(novo_clone)
                self.clone_ids = [novo_clone.id]
        else:
            self.split_active_elapsed_ms += dt_ms
            if self.split_active_elapsed_ms >= self.split_duration_ms:
                if self.clone_ids: remover_ids.extend(self.clone_ids)
                self.clone_ids = []; self.split_active = False
                self.split_cooldown_ms = random.randint(5500, 9000)
                self.split_duration_ms = random.randint(2000, 3800)

    def colide_parede(self, x, y):
        return not (0 <= x < COLUNAS and 0 <= y < LINHAS_LABIRINTO and labirinto[y][x] != 1)

    def desenhar(self, surface):
        frames_para_usar = self.frames
        if self.invisivel and not self.visivel:
            frames_para_usar = self.frames_invisivel or self.frames
        
        if not frames_para_usar:
            if not self.visivel: return
            centro = (self.px + TAM_CELULA // 2, self.py + TAM_CELULA // 2)
            pygame.draw.circle(surface, self.cor, centro, TAM_CELULA // 2 - 4)
            return

        frame_index = int(pygame.time.get_ticks() / 300) % len(frames_para_usar)
        img = frames_para_usar[frame_index]
        rect = img.get_rect(center=(self.px + TAM_CELULA // 2, self.py + TAM_CELULA // 2))
        
        render_img = img
        if self.is_clone or (not self.visivel and self.invisivel):
            render_img = img.copy()
            alpha = 120 if (not self.visivel and self.invisivel) else 200
            render_img.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
        
        surface.blit(render_img, rect)

class CentroComunitario:
    def __init__(self, x, y, nome, cor, recurso_necessario):
        self.x, self.y, self.nome, self.cor = x, y, nome, cor
        self.recurso_necessario = recurso_necessario
        self.nivel_atual, self.nivel_max = 0, 5
        self.anim_index, self.anim_timer, self.anim_interval_ms = 0, 0, 220
        self.carregar_imagens()
    def carregar_imagens(self):
        tamanho_centro = (48, 48)
        prefixo_map = {"Escola": "escola","Hospital": "hospital", "Mercado": "mercado","Moradia": "moradia"}
        prefixo = prefixo_map.get(self.nome, "escola")
        self.frames = carregar_centro(prefixo, tamanho_centro)
    def atualizar_animacao(self, dt_ms):
        if not self.frames: return
        self.anim_timer += dt_ms
        if self.anim_timer >= self.anim_interval_ms:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(self.frames)
        self.efeitos = []
    def desenhar(self, surface):
        px, py = self.x * TAM_CELULA, self.y * TAM_CELULA
        if self.frames and self.frames[self.anim_index]:
            frame = self.frames[self.anim_index]
            img_rect = frame.get_rect(center=(px + TAM_CELULA//2, py + TAM_CELULA//2))
            surface.blit(frame, img_rect)
        else: pygame.draw.rect(surface, self.cor, (px+2, py+2, TAM_CELULA-4, TAM_CELULA-4), border_radius=4)
        largura_barra, altura_barra = TAM_CELULA - 8, 5
        progresso = (self.nivel_atual / self.nivel_max) * largura_barra
        pygame.draw.rect(surface, PRETO, (px+4, py+TAM_CELULA-12, largura_barra, altura_barra))
        pygame.draw.rect(surface, AMARELO, (px+4, py+TAM_CELULA-12, progresso, altura_barra))
        for efeito in list(self.efeitos):
            efeito["tempo"] -= 1
            if efeito["tempo"] <= 0:
                self.efeitos.remove(efeito)
                continue
            intensidade = max(30, 200 * efeito["tempo"] / efeito["duracao"])
            raio = TAM_CELULA + (efeito["duracao"] - efeito["tempo"]) * 2
            glow = pygame.Surface((raio*2, raio*2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 223, 0, int(intensidade)), (raio, raio), raio, width=4)
            surface.blit(glow, (px + TAM_CELULA//2 - raio, py + TAM_CELULA//2 - raio), special_flags=pygame.BLEND_RGBA_ADD)
    def receber_entrega(self, inventario_jogador, player_stats=None):
        recursos_entregues = sum(1 for item in inventario_jogador if item == self.recurso_necessario)
        if recursos_entregues > 0 and self.nivel_atual < self.nivel_max:
            inventario_jogador[:] = [item for item in inventario_jogador if item != self.recurso_necessario]
            self.nivel_atual = min(self.nivel_max, self.nivel_atual + recursos_entregues)
            if player_stats: player_stats["itens_entregues"] += recursos_entregues
            self.efeitos.append({"tempo": 30, "duracao": 30})
            return recursos_entregues * 20
        return 0

# --- FunÃ§Ãµes de UI e Jogo ---
def carregar_usuarios():
    try:
        with open(ARQUIVO_USUARIOS, 'r') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return {}
def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, 'w') as f: json.dump(usuarios, f, indent=4)
def desenhar_texto(surface, texto, pos, fonte, cor=BRANCO, alinhamento="center"):
    render = fonte.render(texto, True, cor)
    rect = render.get_rect()
    if alinhamento == "center":
        rect.center = pos
    elif alinhamento == "topleft":
        rect.topleft = pos
    surface.blit(render, rect)

def desenhar_texto_quebra_linha(surface, texto, pos, largura_maxima, fonte, cor=BRANCO):
    palavras = texto.split(' ')
    linha_atual, linhas_renderizadas = "", []
    for palavra in palavras:
        palavra_teste = f" {palavra}" if linha_atual else palavra
        if fonte.size(linha_atual + palavra_teste)[0] <= largura_maxima:
            linha_atual += palavra_teste
        else:
            linhas_renderizadas.append(linha_atual); linha_atual = palavra
    linhas_renderizadas.append(linha_atual)
    y_inicial = pos[1]
    for i, linha in enumerate(linhas_renderizadas):
        render_linha = fonte.render(linha, True, cor)
        rect_linha = render_linha.get_rect(center=(pos[0], y_inicial + i * fonte.get_linesize()))
        surface.blit(render_linha, rect_linha)

def quebrar_texto_em_linhas(texto: str, fonte: pygame.font.Font, largura_maxima: int) -> List[str]:
    palavras = texto.split(' ')
    linha_atual, linhas = "", []
    for palavra in palavras:
        linha_teste = f"{linha_atual} {palavra}".strip()
        if fonte.size(linha_teste)[0] <= largura_maxima:
            linha_atual = linha_teste
        else:
            if linha_atual: linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual: linhas.append(linha_atual)
    return linhas

def carregar_avaliacoes():
    try:
        with open(ARQUIVO_AVALIACOES, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and "respostas" in data:
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {"respostas": []}

def salvar_avaliacoes(dados):
    with open(ARQUIVO_AVALIACOES, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def calcular_medias_avaliacao(dados_avaliacao, quantidade_perguntas: int):
    soma = [0] * quantidade_perguntas
    contagem = [0] * quantidade_perguntas
    for resposta in dados_avaliacao.get("respostas", []):
        notas = resposta.get("notas", [])
        for i, nota in enumerate(notas[:quantidade_perguntas]):
            if isinstance(nota, (int, float)) and 1 <= nota <= 5:
                soma[i] += nota
                contagem[i] += 1
    medias = []
    for i in range(quantidade_perguntas):
        medias.append((soma[i] / contagem[i]) if contagem[i] else 0)
    return medias, contagem

def construir_layout_avaliacao(questoes_avaliacao, fonte_pergunta, largura_texto):
    layout = []
    perguntas = []
    y_cursor = 120  # Aumentado de 90 para 120 para dar mais espaÃ§o apÃ³s a legenda
    for categoria, perguntas_categoria in questoes_avaliacao:
        layout.append({"tipo": "header", "categoria": categoria, "y": y_cursor})
        y_cursor += fonte_pergunta.get_linesize() + 10  # Aumentado de 4 para 10
        for texto in perguntas_categoria:
            linhas = quebrar_texto_em_linhas(texto, fonte_pergunta, largura_texto)
            altura_texto = max(fonte_pergunta.get_linesize(), len(linhas) * fonte_pergunta.get_linesize())
            entrada = {
                "tipo": "pergunta",
                "categoria": categoria,
                "texto": texto,
                "linhas": linhas,
                "y_texto": y_cursor,
                "altura_texto": altura_texto,
                "indice": len(perguntas)
            }
            layout.append(entrada)
            perguntas.append(entrada)
            y_cursor += altura_texto + 18
    return layout, perguntas

def gerar_rects_avaliacao(perguntas_layout, largura_coluna_direita=350):
    opcoes = {}
    tamanho_opcao = 32
    espaco_opcao = 18
    x_inicio = LARGURA - largura_coluna_direita
    for pergunta in perguntas_layout:
        y_opcao = pergunta['y_texto'] + pergunta['altura_texto'] // 2 - tamanho_opcao // 2
        for nota in range(1, 6):
            opcoes[(pergunta['indice'], nota)] = pygame.Rect(
                x_inicio + (nota - 1) * (tamanho_opcao + espaco_opcao),
                y_opcao,
                tamanho_opcao,
                tamanho_opcao
            )
    # Centralizar botÃµes melhor e dar mais espaÃ§o
    confirmar = pygame.Rect(LARGURA//2 - 100, ALTURA - 80, 200, 50)
    voltar = pygame.Rect(50, ALTURA - 80, 150, 50)
    return {"opcoes": opcoes, "confirmar": confirmar, "voltar": voltar}

def desenhar_tela_inicial(surface, rects):
    surface.fill((5, 5, 5))
    fonte_logo = pygame.font.SysFont("bahnschrift", 68, bold=True)
    fonte_logo_small = pygame.font.SysFont("bahnschrift", 30)
    fonte_botao = pygame.font.SysFont(None, 34)
    fonte_legenda = pygame.font.SysFont(None, 26)

    logo_x = LARGURA // 2 - 160
    pac_center = (logo_x, 150)
    pygame.draw.circle(surface, AMARELO, pac_center, 46)
    pygame.draw.polygon(surface, (5, 5, 5), [pac_center, (pac_center[0] + 60, pac_center[1] - 32), (pac_center[0] + 60, pac_center[1] + 32)])
    pygame.draw.circle(surface, (25, 25, 25), (pac_center[0] + 12, pac_center[1] - 16), 6)
    desenhar_texto(surface, "PACMAN", (pac_center[0] + 220, 120), fonte_logo, COR_OURO)
    desenhar_texto(surface, "MISSÃƒO COMUNITÃRIA", (pac_center[0] + 220, 165), fonte_logo_small, BRANCO)
    legenda_y = rects['cadastrar'].bottom + 40
    desenhar_texto(surface, "Prepare-se para entrar na missÃ£o ou criar seu acesso.", (LARGURA/2, legenda_y), fonte_legenda, BRANCO)

    for nome, rect in (("Logar", rects['logar']), ("Cadastrar", rects['cadastrar'])):
        botao_rect = rect.inflate(60, 10)
        pygame.draw.rect(surface, (12, 12, 12), botao_rect, border_radius=8)
        pygame.draw.rect(surface, COR_OURO, botao_rect, width=2, border_radius=8)
        pygame.draw.rect(surface, (250, 210, 0), rect, border_radius=8)
        pygame.draw.rect(surface, (5, 5, 5), rect, width=2, border_radius=8)
        desenhar_texto(surface, nome, rect.center, fonte_botao, (0, 0, 0))

def desenhar_tela_formulario(surface, titulo, nick, senha, campo_ativo, rects, msg_erro=""):
    surface.fill((5, 5, 5))

    fonte_logo = pygame.font.SysFont("bahnschrift", 52, bold=True)
    fonte_logo_small = pygame.font.SysFont("bahnschrift", 26)
    fonte_titulo = pygame.font.SysFont(None, 40)
    fonte_label = pygame.font.SysFont(None, 24)
    fonte_input = pygame.font.SysFont(None, 30)
    fonte_msg = pygame.font.SysFont(None, 24)

    logo_x = LARGURA // 2 - 150
    pac_center = (logo_x, 90)
    pygame.draw.circle(surface, AMARELO, pac_center, 36)
    pygame.draw.polygon(surface, (5, 5, 5), [pac_center, (pac_center[0] + 48, pac_center[1] - 24), (pac_center[0] + 48, pac_center[1] + 24)])
    pygame.draw.circle(surface, (20, 20, 20), (pac_center[0] + 8, pac_center[1] - 12), 5)
    desenhar_texto(surface, "PACMAN", (pac_center[0] + 180, 70), fonte_logo, COR_OURO)
    desenhar_texto(surface, "MISSÃƒO COMUNITÃRIA", (pac_center[0] + 180, 105), fonte_logo_small, BRANCO)

    painel = pygame.Rect(LARGURA//2 - 240, 150, 480, 340)
    sombra = painel.copy(); sombra.inflate_ip(8, 8); sombra.move_ip(6, 6)
    pygame.draw.rect(surface, (0, 0, 0), sombra, border_radius=6)
    pygame.draw.rect(surface, (10, 10, 10), painel, border_radius=6)
    pygame.draw.rect(surface, COR_OURO, painel, width=3, border_radius=6)

    titulo_card = "Log in to the system" if titulo.lower().startswith("log") else "Create an account"
    desenhar_texto(surface, titulo_card, (painel.centerx, painel.y + 45), fonte_titulo, BRANCO)

    campos = [
        ("nick", "Login*", nick, False),
        ("senha", "Password*", senha, True)
    ]
    for campo_id, label, valor, ocultar in campos:
        rect = rects[campo_id].inflate(0, 12)
        cor_borda = COR_OURO if campo_ativo == campo_id else (120, 120, 120)
        pygame.draw.rect(surface, (8, 8, 8), rect, border_radius=4)
        pygame.draw.rect(surface, cor_borda, rect, width=2, border_radius=4)
        surface.blit(fonte_label.render(label, True, COR_OURO if campo_ativo == campo_id else CINZA), (rect.x, rect.y - 22))
        if valor:
            texto = "*" * len(valor) if ocultar else valor
            cor_texto = BRANCO
        else:
            texto = "Password" if ocultar else "Login"
            cor_texto = (120, 120, 150)
        surface.blit(fonte_input.render(texto, True, cor_texto), (rect.x + 10, rect.y + 8))

    confirmar_rect = rects['confirmar'].inflate(0, 20)
    pygame.draw.rect(surface, COR_OURO, confirmar_rect)
    pygame.draw.rect(surface, (0, 0, 0), confirmar_rect, width=2)
    desenhar_texto(surface, titulo, confirmar_rect.center, fonte_input, (0, 0, 0))

    voltar_rect = rects['voltar']
    pygame.draw.rect(surface, (40, 40, 40), voltar_rect, border_radius=4)
    pygame.draw.rect(surface, (150, 150, 150), voltar_rect, width=2, border_radius=4)
    desenhar_texto(surface, "Voltar", voltar_rect.center, fonte_input, BRANCO)

    mensagem = msg_erro if msg_erro else "Create an account para salvar seu progresso."
    cor_msg = (255, 120, 120) if msg_erro else (160, 160, 160)
    desenhar_texto(surface, mensagem, (painel.centerx, painel.bottom + 35), fonte_msg, cor_msg)
    if not msg_erro:
        desenhar_texto(surface, "Already a member? Use o mesmo formulÃ¡rio para logar.", (painel.centerx, painel.bottom + 65), fonte_msg, CINZA)
def desenhar_tela_dificuldade(surface, rects):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo, fonte_botao = pygame.font.SysFont(None, 50), pygame.font.SysFont(None, 38)
    desenhar_texto(surface, "Escolha o Desafio da MissÃ£o", (LARGURA / 2, 80), fonte_titulo, AMARELO)
    pygame.draw.rect(surface, (0, 150, 0), rects['easy']); desenhar_texto(surface, "MissÃ£o Tranquila", rects['easy'].center, fonte_botao)
    pygame.draw.rect(surface, (200, 150, 0), rects['default']); desenhar_texto(surface, "Ritmo da Comunidade", rects['default'].center, fonte_botao)
    pygame.draw.rect(surface, (150, 0, 0), rects['hard']); desenhar_texto(surface, "Resgate Intenso", rects['hard'].center, fonte_botao)
    pygame.draw.rect(surface, COR_BOTAO, rects['instrucoes']); desenhar_texto(surface, "InstruÃ§Ãµes", rects['instrucoes'].center, fonte_botao)
    pygame.draw.rect(surface, COR_OURO, rects['rewards']); desenhar_texto(surface, "Recompensas", rects['rewards'].center, fonte_botao)
    pygame.draw.rect(surface, COR_REWARD, rects['ranking']); desenhar_texto(surface, "Ranking", rects['ranking'].center, fonte_botao)
    pygame.draw.rect(surface, COR_BOTAO, rects['avaliacao']); desenhar_texto(surface, "AvaliaÃ§Ã£o", rects['avaliacao'].center, fonte_botao)
def desenhar_tela_rewards(surface, rewards_system, username, rects):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo, fonte_media, fonte_pequena = pygame.font.SysFont(None, 45), pygame.font.SysFont(None, 32), pygame.font.SysFont(None, 26)
    user_data = rewards_system.obter_usuario_rewards(username)
    desenhar_texto(surface, "Sistema de Recompensas", (LARGURA/2, 50), fonte_titulo, COR_OURO)
    desenhar_texto(surface, f"UsuÃ¡rio: {username}", (LARGURA/2, 100), fonte_media, BRANCO)
    desenhar_texto(surface, f"Pontos Totais: {user_data['pontos_totais']}", (LARGURA/2, 130), fonte_media, COR_OURO)
    desenhar_texto(surface, f"NÃ­vel: {user_data['nivel']}", (LARGURA/2, 160), fonte_media, COR_REWARD)
    desenhar_texto(surface, "Tarefas DiÃ¡rias", (LARGURA/2, 200), fonte_media, COR_OURO)
    y_offset = 230
    tarefas = user_data.get("tarefas_diarias", rewards_system.daily_tasks)
    for task_data in tarefas.values():
        cor = COR_OURO if task_data.get("concluida") else CINZA
        texto = f"{task_data['descricao']} - {task_data['pontos']} pts"
        desenhar_texto(surface, texto, (LARGURA/2, y_offset), fonte_pequena, cor); y_offset += 25
    desenhar_texto(surface, "Conquistas", (LARGURA/2, y_offset + 20), fonte_media, COR_OURO)
    y_offset += 50
    conquistas = user_data.get("conquistas", {})
    for achievement_id, achievement_data in rewards_system.achievements.items():
        user_achievement = conquistas.get(achievement_id, {"desbloqueada": False})
        cor = COR_OURO if user_achievement.get("desbloqueada") else CINZA
        texto = f"{achievement_data['nome']} - {achievement_data['pontos']} pts"
        desenhar_texto(surface, texto, (LARGURA/2, y_offset), fonte_pequena, cor); y_offset += 25
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['voltar_rewards']); desenhar_texto(surface, "Voltar", rects['voltar_rewards'].center, fonte_media)
def desenhar_tela_ranking(surface, rewards_system, rects):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo, fonte_media, fonte_pequena = pygame.font.SysFont(None, 45), pygame.font.SysFont(None, 32), pygame.font.SysFont(None, 28)
    desenhar_texto(surface, "Ranking de Jogadores", (LARGURA/2, 50), fonte_titulo, COR_OURO)
    ranking = rewards_system.obter_ranking(10)
    y_offset = 120
    for i, (username, pontos) in enumerate(ranking):
        cor = [COR_OURO, COR_PRATA, COR_BRONZE][i] if i < 3 else BRANCO
        medalha = ["ðŸ¥‡", "ðŸ¥ˆ", "ðŸ¥‰"][i] if i < 3 else f"{i+1}Âº"
        texto = f"{medalha} {username}: {pontos} pontos"
        desenhar_texto(surface, texto, (LARGURA/2, y_offset), fonte_pequena, cor); y_offset += 30
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['voltar_ranking']); desenhar_texto(surface, "Voltar", rects['voltar_ranking'].center, fonte_media)
MENSAGENS_GAME_OVER = {
    "Desemprego": "O fantasma do Desemprego te perseguiu implacavelmente, deixando seus sonhos de prosperidade em ruÃ­nas. A falta de oportunidades se tornou uma armadilha sem saÃ­da...",
    "Desigualdade": "A sombra da Desigualdade te engoliu por completo, criando um abismo intransponÃ­vel entre vocÃª e uma vida digna. A injustiÃ§a social mostrou sua face mais cruel...",
    "Falta de Acesso": "A barreira da Falta de Acesso se ergueu como um muro intransponÃ­vel, bloqueando todos os caminhos que levam ao progresso. A exclusÃ£o social te consumiu...",
    "Crise EconÃ´mica": "A tempestade da Crise EconÃ´mica devastou todos os seus esforÃ§os, transformando esperanÃ§as em desespero. O sistema financeiro te esmagou sem piedade..."
}
def desenhar_tela_game_over(surface, rects, nome_inimigo):
    surface.fill((5, 5, 5))
    fonte_logo = pygame.font.SysFont("bahnschrift", 52, bold=True)
    fonte_logo_small = pygame.font.SysFont("bahnschrift", 26)
    fonte_titulo = pygame.font.SysFont(None, 50)
    fonte_mensagem = pygame.font.SysFont(None, 26)
    fonte_botao = pygame.font.SysFont(None, 34)

    logo_x = LARGURA // 2 - 220
    pac_center = (logo_x, 110)
    pygame.draw.circle(surface, AMARELO, pac_center, 40)
    pygame.draw.polygon(surface, (5, 5, 5), [pac_center, (pac_center[0] + 58, pac_center[1] - 28), (pac_center[0] + 58, pac_center[1] + 28)])
    pygame.draw.circle(surface, (20, 20, 20), (pac_center[0] + 10, pac_center[1] - 12), 5)
    desenhar_texto(surface, "PACMAN", (pac_center[0] + 210, 90), fonte_logo, COR_OURO)
    desenhar_texto(surface, "MISSÃO COMUNITÁRIA", (pac_center[0] + 210, 125), fonte_logo_small, BRANCO)

    card_rect = pygame.Rect(LARGURA//2 - 270, 160, 540, 300)
    pygame.draw.rect(surface, (0, 0, 0), card_rect.inflate(12, 12), border_radius=10)
    pygame.draw.rect(surface, (14, 14, 32), card_rect, border_radius=10)
    pygame.draw.rect(surface, COR_OURO, card_rect, width=2, border_radius=10)

    titulo = "A Missão Falhou"
    mensagem = MENSAGENS_GAME_OVER.get(nome_inimigo, f"Você foi superado por: {nome_inimigo}")
    desenhar_texto(surface, titulo, (card_rect.centerx, card_rect.y + 50), fonte_titulo, AMARELO)
    desenhar_texto_quebra_linha(surface, mensagem, (card_rect.centerx, card_rect.y + 130), card_rect.width - 80, fonte_mensagem, (255, 150, 150))
    desenhar_texto(surface, "Deseja tentar novamente?", (card_rect.centerx, card_rect.bottom - 70), fonte_titulo, BRANCO)

    pygame.draw.rect(surface, COR_OURO, rects['sim'], border_radius=10)
    pygame.draw.rect(surface, (0, 0, 0), rects['sim'], width=2, border_radius=10)
    desenhar_texto(surface, "Sim", rects['sim'].center, fonte_botao, (0, 0, 0))

    pygame.draw.rect(surface, (40, 40, 40), rects['nao'], border_radius=10)
    pygame.draw.rect(surface, (200, 80, 80), rects['nao'], width=2, border_radius=10)
    desenhar_texto(surface, "Não", rects['nao'].center, fonte_botao, BRANCO)
# ### FUNÃ‡ÃƒO NOVA ADICIONADA ###
def desenhar_tela_vitoria(surface, rects, pontos_finais, pontos_bonus):
    surface.fill(COR_FUNDO_UI)
    fonte_grande = pygame.font.SysFont(None, 60)
    fonte_media = pygame.font.SysFont(None, 45)
    fonte_pontos = pygame.font.SysFont(None, 50)
    
    desenhar_texto(surface, "ParabÃ©ns!", (LARGURA/2, 100), fonte_grande, AMARELO)
    desenhar_texto(surface, "A comunidade prosperou!", (LARGURA/2, 160), fonte_media, (120, 255, 120))
    
    desenhar_texto(surface, f"PontuaÃ§Ã£o Final: {pontos_finais}", (LARGURA/2, 240), fonte_pontos, BRANCO)
    desenhar_texto(surface, f"Pontos de Recompensa: +{pontos_bonus}", (LARGURA/2, 290), fonte_pontos, COR_OURO)
    
    desenhar_texto(surface, "Deseja continuar?", (LARGURA/2, 380), fonte_media, BRANCO)
    
    pygame.draw.rect(surface, VERDE_CONTINUAR, rects['sim'])
    desenhar_texto(surface, "Sim", rects['sim'].center, fonte_media)
    
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['nao'])
    desenhar_texto(surface, "NÃ£o", rects['nao'].center, fonte_media)

def desenhar_tela_avaliacao(surface, layout_avaliacao, perguntas_layout, rects, respostas, dados_avaliacao, mensagem):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo = pygame.font.SysFont(None, 46)
    fonte_secao = pygame.font.SysFont(None, 30)
    fonte_pergunta = pygame.font.SysFont(None, 24)
    fonte_opcao = pygame.font.SysFont(None, 24)
    fonte_media = pygame.font.SysFont(None, 20)
    fonte_mensagem = pygame.font.SysFont(None, 24)

    # TÃ­tulo centralizado
    desenhar_texto(surface, "AvaliaÃ§Ã£o do Produto", (LARGURA/2, 50), fonte_titulo, AMARELO)
    
    # Legenda centralizada com mais espaÃ§o
    texto_legenda = fonte_media.render("Avalie de 1 (ruim) a 5 (excelente).", True, BRANCO)
    legenda_rect = texto_legenda.get_rect()
    legenda_rect.centerx = LARGURA // 2
    legenda_rect.y = 85  # Ajustado de 80 para 85
    surface.blit(texto_legenda, legenda_rect)

    for item in layout_avaliacao:
        if item["tipo"] == "header":
            desenhar_texto(surface, item["categoria"], (LARGURA/2, item["y"]), fonte_secao, COR_OURO)
        elif item["tipo"] == "pergunta":
            # Texto da pergunta alinhado Ã  esquerda com margem consistente
            x_texto = 50
            y_linha = item["y_texto"]
            for linha in item["linhas"]:
                render = fonte_pergunta.render(linha, True, BRANCO)
                surface.blit(render, (x_texto, y_linha))
                y_linha += fonte_pergunta.get_linesize()

            # BotÃµes de avaliaÃ§Ã£o
            for nota in range(1, 6):
                rect = rects['opcoes'][(item['indice'], nota)]
                selecionado = respostas.get(item['indice']) == nota
                cor_fundo = COR_REWARD if selecionado else COR_FUNDO_UI
                cor_borda = COR_OURO if selecionado else BRANCO
                pygame.draw.rect(surface, cor_fundo, rect, border_radius=6)
                pygame.draw.rect(surface, cor_borda, rect, width=2, border_radius=6)
                numero = fonte_opcao.render(str(nota), True, BRANCO)
                surface.blit(numero, numero.get_rect(center=rect.center))

            # Mostrar a nota selecionada pelo usuÃ¡rio
            if item['indice'] in respostas:
                nota_selecionada = respostas[item['indice']]
                texto_media = fonte_media.render(f"Nota: {nota_selecionada}", True, COR_OURO)
            else:
                # Quando esta pergunta nÃ£o foi respondida, nÃ£o mostrar nada
                texto_media = fonte_media.render("", True, CINZA)
            
            # Posicionar o texto da mÃ©dia com mais espaÃ§o para evitar corte
            media_rect = texto_media.get_rect()
            media_rect.midleft = (rects['opcoes'][(item['indice'], 5)].right + 35, rects['opcoes'][(item['indice'], 3)].centery)
            
            # Verificar se o texto nÃ£o vai sair da tela
            if media_rect.right > LARGURA - 20:
                media_rect.right = LARGURA - 20
            
            surface.blit(texto_media, media_rect)

    # BotÃµes com melhor posicionamento e estilo
    pygame.draw.rect(surface, COR_BOTAO, rects['confirmar'], border_radius=8)
    pygame.draw.rect(surface, BRANCO, rects['confirmar'], width=2, border_radius=8)
    desenhar_texto(surface, "Enviar avaliaÃ§Ã£o", rects['confirmar'].center, fonte_secao, BRANCO)
    
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['voltar'], border_radius=8)
    pygame.draw.rect(surface, BRANCO, rects['voltar'], width=2, border_radius=8)
    desenhar_texto(surface, "Voltar", rects['voltar'].center, fonte_secao, BRANCO)

    # Mensagem centralizada - posicionada bem acima dos botÃµes
    if mensagem:
        cor_msg = VERMELHO if "Selecione" in mensagem else COR_OURO
        # Posicionar a mensagem bem acima, no meio da tela
        y_mensagem = ALTURA // 2 - 50
        desenhar_texto(surface, mensagem, (LARGURA/2, y_mensagem), fonte_mensagem, cor_msg)

def desenhar_popup(surface, titulo, mensagem):
    """Renderiza um pop-up translÃºcido na tela atual."""
    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((5, 5, 15, 180))
    surface.blit(overlay, (0, 0))

    largura_popup, altura_popup = 480, 210
    popup_rect = pygame.Rect(0, 0, largura_popup, altura_popup)
    popup_rect.center = (LARGURA // 2, ALTURA // 2)

    pygame.draw.rect(surface, (12, 12, 35), popup_rect, border_radius=16)
    pygame.draw.rect(surface, COR_OURO, popup_rect, width=2, border_radius=16)

    fonte_titulo = pygame.font.SysFont(None, 36)
    fonte_texto = pygame.font.SysFont(None, 26)
    fonte_dica = pygame.font.SysFont(None, 22)

    desenhar_texto(surface, titulo or "Mensagem", (popup_rect.centerx, popup_rect.y + 40), fonte_titulo, AMARELO)
    desenhar_texto_quebra_linha(surface, mensagem, (popup_rect.centerx, popup_rect.centery), popup_rect.width - 60, fonte_texto, BRANCO)

    dica = fonte_dica.render("Clique para fechar ou aguarde alguns segundos.", True, CINZA)
    surface.blit(dica, dica.get_rect(center=(popup_rect.centerx, popup_rect.bottom - 30)))
def desenhar_labirinto(surface):
    for y,linha in enumerate(labirinto):
        for x,celula in enumerate(linha):
            if celula == 1: pygame.draw.rect(surface,AZUL_PAREDE,(x*TAM_CELULA, y*TAM_CELULA,TAM_CELULA,TAM_CELULA))
def desenhar_recursos(surface, recursos):
    tamanho_item = (24, 24)
    cache = getattr(desenhar_recursos, "_cache", {})
    if not cache:
        cache["imagens"] = { 'Moeda': carregar_item('moeda', tamanho_item), 'Alimento': carregar_item('alimento', tamanho_item), 'Livro': carregar_item('livro', tamanho_item), 'Tijolo': carregar_item('tijolos', tamanho_item) }
        desenhar_recursos._cache = cache
    for r in recursos:
        centro = (r['x']*TAM_CELULA + TAM_CELULA//2, r['y']*TAM_CELULA + TAM_CELULA//2)
        img = cache["imagens"].get(r['tipo'])
        if img: surface.blit(img, img.get_rect(center=centro))
def desenhar_rotulos_coleta(surface, centros, player, alcance=3):
    fonte = pygame.font.SysFont(None, 22)
    tem_item = player.inventario[0] if player.inventario else None
    for centro in centros:
        distancia = abs(player.grid_x - centro.x) + abs(player.grid_y - centro.y)
        if distancia > alcance and centro.recurso_necessario != tem_item: continue
        texto = f"Entregar {centro.recurso_necessario}"
        render = fonte.render(texto, True, BRANCO)
        padding_x, padding_y = 10, 6
        largura = render.get_width() + padding_x * 2
        altura = render.get_height() + padding_y * 2
        label_surface = pygame.Surface((largura, altura), pygame.SRCALPHA)
        label_surface.fill((0, 0, 0, 200))
        pygame.draw.rect(label_surface, COR_OURO, label_surface.get_rect(), width=1, border_radius=6)
        label_surface.blit(render, render.get_rect(center=label_surface.get_rect().center))
        pos_x = centro.x * TAM_CELULA + TAM_CELULA // 2 - largura // 2
        pos_y = centro.y * TAM_CELULA - altura - 6
        surface.blit(label_surface, (pos_x, pos_y))
        halo_surface = pygame.Surface((TAM_CELULA*2, TAM_CELULA*2), pygame.SRCALPHA)
        intensidade = 80 + int(40 * (1 + math.sin(pygame.time.get_ticks() / 250)))
        pygame.draw.circle(halo_surface, (*COR_OURO, intensidade), (halo_surface.get_width()//2, halo_surface.get_height()//2), TAM_CELULA, width=4)
        target_pos = (centro.x * TAM_CELULA + TAM_CELULA//2 - halo_surface.get_width()//2,
                      centro.y * TAM_CELULA + TAM_CELULA//2 - halo_surface.get_height()//2)
        surface.blit(halo_surface, target_pos, special_flags=pygame.BLEND_RGBA_ADD)
def desenhar_hud(surface, jogador, centros, pontos):
    base_y = LINHAS_LABIRINTO * TAM_CELULA
    pygame.draw.rect(surface, COR_FUNDO_UI, (0, base_y, LARGURA, ALTURA - base_y))
    fonte, fonte_instrucao = pygame.font.SysFont(None, 28), pygame.font.SysFont(None, 24)
    surface.blit(fonte.render("InventÃ¡rio:", True, BRANCO), (40, base_y + 15))
    mapa_cor={'Moeda':COR_MOEDA,'Alimento':COR_ALIMENTO,'Livro':COR_LIVRO,'Tijolo':COR_TIJOLO}
    for i in range(jogador.capacidade_inventario):
        pygame.draw.rect(surface,BRANCO,(40+i*30,base_y+40,25,25),1)
        if i < len(jogador.inventario): pygame.draw.rect(surface,mapa_cor[jogador.inventario[i]],(40+i*30,base_y+40,25,25))
    surface.blit(fonte_instrucao.render("Pressione [H] para Descartar", True, BRANCO), (40, base_y + 75))
    surface.blit(fonte.render("Desenvolvimento ComunitÃ¡rio",True,BRANCO), (LARGURA/2, base_y+10))
    centros_esquerda, centros_direita = centros[:2], centros[2:]
    for i, centro in enumerate(centros_esquerda):
        pos_x, pos_y = 320, base_y + 40 + i * 25
        surface.blit(fonte.render(f"{centro.nome}:",True,centro.cor), (pos_x, pos_y))
        prog=(centro.nivel_atual/centro.nivel_max)
        pygame.draw.rect(surface,PRETO,(pos_x + 90, pos_y+2, 100, 12)); pygame.draw.rect(surface,AMARELO,(pos_x + 90, pos_y+2, 100*prog, 12))
    for i, centro in enumerate(centros_direita):
        pos_x, pos_y = LARGURA/2 + 100, base_y + 40 + i * 25
        surface.blit(fonte.render(f"{centro.nome}:",True,centro.cor), (pos_x, pos_y))
        prog=(centro.nivel_atual/centro.nivel_max)
        pygame.draw.rect(surface,PRETO,(pos_x + 90, pos_y+2, 100, 12)); pygame.draw.rect(surface,AMARELO,(pos_x + 90, pos_y+2, 100*prog, 12))
    surface.blit(fonte.render(f"Pontos: {pontos}",True,BRANCO), (LARGURA-150,base_y+10))

def desenhar_tela_instrucoes(surface, rects):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo = pygame.font.SysFont(None, 50)
    fonte_subtitulo = pygame.font.SysFont(None, 38)
    fonte_texto = pygame.font.SysFont(None, 30)
    fonte_texto_menor = pygame.font.SysFont(None, 28)
    y_pos = 50
    desenhar_texto(surface, "InstruÃ§Ãµes do Jogo", (LARGURA/2, y_pos), fonte_titulo, AMARELO)
    y_pos += 60
    desenhar_texto(surface, "Objetivo", (LARGURA/2, y_pos), fonte_subtitulo, COR_REWARD)
    y_pos += 45
    texto_objetivo = "Seu objetivo Ã© reconstruir a comunidade! Para isso, colete os recursos e entregue-os nos Centros ComunitÃ¡rios correspondentes. VenÃ§a a partida completando o desenvolvimento de todos os centros."
    desenhar_texto_quebra_linha(surface, texto_objetivo, (LARGURA/2, y_pos), LARGURA - 150, fonte_texto, BRANCO)
    y_pos += 90
    desenhar_texto(surface, "Controles", (LARGURA/2, y_pos), fonte_subtitulo, COR_REWARD)
    y_pos += 40
    x_align = 150
    desenhar_texto(surface, "Teclado (Passo-a-passo):", (x_align, y_pos), fonte_texto, AMARELO, "topleft")
    y_pos += 25
    desenhar_texto(surface, "Use as Setas ou W, A, S, D para mover um quadrado por vez.", (x_align, y_pos), fonte_texto_menor, BRANCO, "topleft")
    y_pos += 40
    desenhar_texto(surface, "Mouse (Caminho AutomÃ¡tico):", (x_align, y_pos), fonte_texto, AMARELO, "topleft")
    y_pos += 25
    desenhar_texto(surface, "Clique em qualquer lugar do labirinto para o Pac-Man ir atÃ© lÃ¡.", (x_align, y_pos), fonte_texto_menor, BRANCO, "topleft")
    y_pos += 40
    desenhar_texto(surface, "InventÃ¡rio:", (x_align, y_pos), fonte_texto, AMARELO, "topleft")
    y_pos += 25
    desenhar_texto(surface, "Pressione [H] para descartar o Ãºltimo item coletado.", (x_align, y_pos), fonte_texto_menor, BRANCO, "topleft")
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['voltar']); desenhar_texto(surface, "Voltar", rects['voltar'].center, fonte_subtitulo)


# --- Loop Principal e LÃ³gica de Estados ---
def main():
    rodando = True
    estado_jogo = 'tela_inicial'
    nick_usuario, senha_usuario, campo_ativo, mensagem_erro = "", "", 'nick', ""
    usuarios = carregar_usuarios()
    dificuldade_selecionada = "Default"
    rewards_system = RewardsSystem()
    avaliacoes_dados = carregar_avaliacoes()
    fonte_layout_avaliacao = pygame.font.SysFont(None, 24)
    layout_avaliacao, perguntas_avaliacao = construir_layout_avaliacao(QUESTOES_AVALIACAO, fonte_layout_avaliacao, 520)
    rects_avaliacao = gerar_rects_avaliacao(perguntas_avaliacao)
    respostas_avaliacao = {}
    mensagem_avaliacao = ""
    popup_avaliacao = {"mensagem": "", "titulo": "", "ativo": False, "expira": 0}

    rects_inicial = {'logar':pygame.Rect(LARGURA/2-150,230,300,70),'cadastrar':pygame.Rect(LARGURA/2-150,320,300,70)}
    rects_form = {'nick':pygame.Rect(LARGURA/2-200,180,400,40),'senha':pygame.Rect(LARGURA/2-200,280,400,40), 'confirmar':pygame.Rect(LARGURA/2-150,380,300,60),'voltar':pygame.Rect(LARGURA/2-100,460,200,50)}
    rects_game_over = {'sim':pygame.Rect(LARGURA/2-180,420,150,70),'nao':pygame.Rect(LARGURA/2+30,420,150,70)}
    # ### NOVO RECT ADICIONADO ###
    rects_vitoria = {'sim': pygame.Rect(LARGURA/2-180, 420, 150, 70), 'nao': pygame.Rect(LARGURA/2+30, 420, 150, 70)}
    
    rects_dificuldade = {
        'easy': pygame.Rect(LARGURA/2-150, 150, 300, 45),
        'default': pygame.Rect(LARGURA/2-150, 205, 300, 45),
        'hard': pygame.Rect(LARGURA/2-150, 260, 300, 45),
        'instrucoes': pygame.Rect(LARGURA/2-150, 315, 300, 45),
        'rewards': pygame.Rect(LARGURA/2-150, 370, 300, 45),
        'ranking': pygame.Rect(LARGURA/2-150, 425, 300, 45),
        'avaliacao': pygame.Rect(LARGURA/2-150, 480, 300, 45)
    }
    rects_instrucoes = {'voltar': pygame.Rect(LARGURA/2-100, ALTURA-60, 200, 50)}
    
    rects_rewards = {'voltar_rewards': pygame.Rect(LARGURA/2-100, 480, 200, 50)}
    rects_ranking = {'voltar_ranking': pygame.Rect(LARGURA/2-100, 480, 200, 50)}

    player, inimigos, centros, recursos, pontos, inimigo_colisor = None, [], [], [], 0, None
    # ### NOVAS VARIÃVEIS PARA A PONTUAÃ‡ÃƒO FINAL ###
    pontos_finais, pontos_bonus_vitoria = 0, 0
    posicoes_iniciais_inimigos = [(30, 1), (1, 13), (30, 13), (15, 7)]
    tempo_inicio_partida = 0
    musica_labirinto_tocando = False
    
    tipos_recursos_padrao = ['Moeda', 'Alimento', 'Livro', 'Tijolo']
    tempo_spawn_recursos_ms = 900
    timer_spawn_recursos = 0
    max_recursos_no_cenario = 60
    def reiniciar_posicoes(dificuldade):
        nonlocal player, inimigos
        if player: player.reiniciar()
        nomes, cores = ["Desemprego","Desigualdade","Falta de Acesso","Crise Economica"], [CINZA,ROXO,CINZA_ESCURO,VERMELHO_CRISE]
        inimigos.clear()
        Inimigo.id_counter = 0
        for i,pos in enumerate(posicoes_iniciais_inimigos):
            inimigos.append(Inimigo(pos[0], pos[1], cores[i], nomes[i], dificuldade))
    
    def inicializar_novo_jogo(dificuldade):
        nonlocal pontos, centros, recursos, player, tempo_inicio_partida, timer_spawn_recursos
        pontos, tempo_inicio_partida = 0, datetime.datetime.now()
        player = Player(1, 1)
        centros = [CentroComunitario(1, 7, "Moradia", COR_MORADIA, "Tijolo"), CentroComunitario(30, 7, "Mercado", COR_MERCADO, "Alimento"), CentroComunitario(15, 1, "Escola", COR_ESCOLA, "Livro"), CentroComunitario(15, 13, "Hospital", COR_HOSPITAL, "Moeda")]
        recursos = []
        timer_spawn_recursos = 0
        pos_ocupadas = [(c.x, c.y) for c in centros] + [(player.grid_x, player.grid_y)]
        for tipo in tipos_recursos_padrao:
            for _ in range(6):
                pos = random.choice([p for p in posicoes_livres if p not in pos_ocupadas])
                recursos.append({'x':pos[0], 'y':pos[1], 'tipo':tipo}); pos_ocupadas.append(pos)
        reiniciar_posicoes(dificuldade)
        
    def spawn_recurso():
        nonlocal recursos
        if len(recursos) >= max_recursos_no_cenario: return
        ocupados = {(c.x, c.y) for c in centros}
        ocupados.update((r['x'], r['y']) for r in recursos)
        if player: ocupados.add((player.grid_x, player.grid_y))
        livres = [p for p in posicoes_livres if p not in ocupados]
        if not livres: return
        quantidade_por_spawn = 2
        for _ in range(quantidade_por_spawn):
            if len(recursos) >= max_recursos_no_cenario or not livres: break
            pos = random.choice(livres)
            livres.remove(pos)
            tipo = random.choice(tipos_recursos_padrao)
            recursos.append({'x': pos[0], 'y': pos[1], 'tipo': tipo})

    while rodando:
        eventos = pygame.event.get()
        for e in eventos:
            if e.type == pygame.QUIT: rodando = False
        tempo_atual = pygame.time.get_ticks()
        if popup_avaliacao["ativo"] and tempo_atual >= popup_avaliacao["expira"]:
            popup_avaliacao["ativo"] = False

        if estado_jogo == 'tela_inicial':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if rects_inicial['logar'].collidepoint(e.pos):
                        estado_jogo='tela_login'; mensagem_erro,nick_usuario,senha_usuario="","",""; campo_ativo='nick'
                    elif rects_inicial['cadastrar'].collidepoint(e.pos):
                        estado_jogo='tela_cadastro'; mensagem_erro,nick_usuario,senha_usuario="","",""; campo_ativo='nick'
            desenhar_tela_inicial(tela, rects_inicial)

        elif estado_jogo in ['tela_login', 'tela_cadastro']:
            # ... (cÃ³digo do formulÃ¡rio intacto) ...
            titulo = "Logar" if estado_jogo == 'tela_login' else "Cadastrar"
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    mensagem_erro="";
                    if rects_form['nick'].collidepoint(e.pos): campo_ativo='nick'
                    elif rects_form['senha'].collidepoint(e.pos): campo_ativo='senha'
                    elif rects_form['voltar'].collidepoint(e.pos): estado_jogo='tela_inicial'
                    elif rects_form['confirmar'].collidepoint(e.pos):
                        if estado_jogo == 'tela_login':
                            if nick_usuario in usuarios and usuarios[nick_usuario] == senha_usuario: estado_jogo = 'tela_dificuldade'
                            else: mensagem_erro = "Nick ou senha invÃ¡lidos."
                        else: 
                            if not nick_usuario or not senha_usuario: mensagem_erro="Os campos nÃ£o podem estar vazios."
                            elif nick_usuario in usuarios: mensagem_erro="Este nick jÃ¡ estÃ¡ em uso."
                            else: usuarios[nick_usuario]=senha_usuario; salvar_usuarios(usuarios); estado_jogo = 'tela_dificuldade'
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN or e.key == pygame.K_KP_ENTER:
                        if estado_jogo == 'tela_login':
                            if nick_usuario in usuarios and usuarios[nick_usuario] == senha_usuario: estado_jogo = 'tela_dificuldade'
                            else: mensagem_erro = "Nick ou senha invÃ¡lidos."
                        else: 
                            if not nick_usuario or not senha_usuario: mensagem_erro="Os campos nÃ£o podem estar vazios."
                            elif nick_usuario in usuarios: mensagem_erro="Este nick jÃ¡ estÃ¡ em uso."
                            else: usuarios[nick_usuario]=senha_usuario; salvar_usuarios(usuarios); estado_jogo = 'tela_dificuldade'
                    elif campo_ativo=='nick':
                        if e.key==pygame.K_BACKSPACE: nick_usuario=nick_usuario[:-1]
                        elif e.key==pygame.K_TAB: campo_ativo='senha'
                        else: nick_usuario+=e.unicode
                    elif campo_ativo=='senha':
                        if e.key==pygame.K_BACKSPACE: senha_usuario=senha_usuario[:-1]
                        elif e.key==pygame.K_TAB: campo_ativo='nick'
                        else: senha_usuario+=e.unicode
            desenhar_tela_formulario(tela, titulo, nick_usuario, senha_usuario, campo_ativo, rects_form, mensagem_erro)

        elif estado_jogo == 'tela_dificuldade':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    dificuldade_foi_escolhida = False
                    if rects_dificuldade['easy'].collidepoint(e.pos): dificuldade_selecionada, dificuldade_foi_escolhida = "Easy", True
                    elif rects_dificuldade['default'].collidepoint(e.pos): dificuldade_selecionada, dificuldade_foi_escolhida = "Default", True
                    elif rects_dificuldade['hard'].collidepoint(e.pos): dificuldade_selecionada, dificuldade_foi_escolhida = "Hard", True
                    elif rects_dificuldade['instrucoes'].collidepoint(e.pos): estado_jogo = 'tela_instrucoes'
                    elif rects_dificuldade['rewards'].collidepoint(e.pos): estado_jogo = 'tela_rewards'
                    elif rects_dificuldade['ranking'].collidepoint(e.pos): estado_jogo = 'tela_ranking'
                    elif rects_dificuldade['avaliacao'].collidepoint(e.pos):
                        estado_jogo = 'tela_avaliacao'
                        mensagem_avaliacao = ""
                        popup_avaliacao["ativo"] = False
                        respostas_avaliacao.clear()  # Limpar respostas ao entrar na tela
                        avaliacoes_dados = carregar_avaliacoes()  # Recarregar dados atualizados
                    if dificuldade_foi_escolhida: inicializar_novo_jogo(dificuldade_selecionada); estado_jogo = 'jogo'
            desenhar_tela_dificuldade(tela, rects_dificuldade)

        elif estado_jogo == 'tela_instrucoes':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if rects_instrucoes['voltar'].collidepoint(e.pos):
                        estado_jogo = 'tela_dificuldade'
            desenhar_tela_instrucoes(tela, rects_instrucoes)

        elif estado_jogo == 'tela_avaliacao':
            for e in eventos:
                if popup_avaliacao["ativo"]:
                    if e.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN): popup_avaliacao["ativo"] = False
                    continue
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if rects_avaliacao['voltar'].collidepoint(e.pos):
                        estado_jogo = 'tela_dificuldade'
                        mensagem_avaliacao = ""
                        popup_avaliacao["ativo"] = False
                        respostas_avaliacao.clear()  # Limpar respostas ao voltar
                    elif rects_avaliacao['confirmar'].collidepoint(e.pos):
                        if len(respostas_avaliacao) < len(perguntas_avaliacao):
                            mensagem_avaliacao = "Selecione uma nota para cada pergunta."
                        else:
                            notas_ordenadas = [respostas_avaliacao[i] for i in range(len(perguntas_avaliacao))]
                            avaliacoes_dados["respostas"].append({
                                "usuario": nick_usuario or "Convidado",
                                "timestamp": datetime.datetime.now().isoformat(),
                                "notas": notas_ordenadas
                            })
                            salvar_avaliacoes(avaliacoes_dados)
                            respostas_avaliacao.clear()
                            mensagem_avaliacao = "AvaliaÃ§Ã£o registrada! Obrigado pelo feedback."
                            # Recarregar dados de avaliaÃ§Ã£o para atualizar as mÃ©dias
                            avaliacoes_dados = carregar_avaliacoes()
                            popup_avaliacao.update({
                                "mensagem": mensagem_avaliacao,
                                "titulo": "Feedback recebido",
                                "ativo": True,
                                "expira": pygame.time.get_ticks() + 3500
                            })
                    else:
                        for (indice, nota), rect in rects_avaliacao['opcoes'].items():
                            if rect.collidepoint(e.pos):
                                respostas_avaliacao[indice] = nota
                                mensagem_avaliacao = ""  # Limpar mensagem ao selecionar uma nota
                                break
            desenhar_tela_avaliacao(tela, layout_avaliacao, perguntas_avaliacao, rects_avaliacao, respostas_avaliacao, avaliacoes_dados, mensagem_avaliacao)
            if popup_avaliacao["ativo"]:
                desenhar_popup(tela, popup_avaliacao["titulo"], popup_avaliacao["mensagem"])

        elif estado_jogo == 'tela_rewards':
            # ... (cÃ³digo da tela de recompensas intacto) ...
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and rects_rewards['voltar_rewards'].collidepoint(e.pos): estado_jogo = 'tela_dificuldade'
            desenhar_tela_rewards(tela, rewards_system, nick_usuario, rects_rewards)
        
        elif estado_jogo == 'tela_ranking':
            # ... (cÃ³digo da tela de ranking intacto) ...
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and rects_ranking['voltar_ranking'].collidepoint(e.pos): estado_jogo = 'tela_dificuldade'
            desenhar_tela_ranking(tela, rewards_system, rects_ranking)

        # ### NOVO ESTADO DE JOGO ADICIONADO ###
        elif estado_jogo == 'tela_vitoria':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if rects_vitoria['sim'].collidepoint(e.pos):
                        # Volta para a tela de dificuldade para um novo jogo
                        estado_jogo = 'tela_dificuldade'
                    elif rects_vitoria['nao'].collidepoint(e.pos):
                        # Fecha o jogo
                        rodando = False
            desenhar_tela_vitoria(tela, rects_vitoria, pontos_finais, pontos_bonus_vitoria)

        elif estado_jogo == 'tela_game_over':
            # ... (cÃ³digo da tela de game over intacto) ...
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if rects_game_over['sim'].collidepoint(e.pos):
                        parar_musica()  # Para a mÃºsica de game over
                        musica_labirinto_tocando = False  # Reset flag para tocar mÃºsica do labirinto novamente
                        inicializar_novo_jogo(dificuldade_selecionada)
                        estado_jogo = 'jogo'
                    elif rects_game_over['nao'].collidepoint(e.pos):
                        if player:
                            tempo_decorrido = (datetime.datetime.now() - tempo_inicio_partida).total_seconds()
                            player.stats["tempo_jogado"], player.stats["tempo_sobrevivencia"] = tempo_decorrido, tempo_decorrido
                            rewards_system.adicionar_pontos(nick_usuario, pontos, "partida")
                            rewards_system.verificar_tarefas_diarias(nick_usuario, player.stats)
                            rewards_system.verificar_conquistas(nick_usuario, player.stats)
                        parar_musica()  # Para a mÃºsica de game over
                        musica_labirinto_tocando = False  # Reset flag
                        estado_jogo = 'tela_inicial'
            desenhar_tela_game_over(tela, rects_game_over, inimigo_colisor.nome if inimigo_colisor else "um inimigo")

        elif estado_jogo == 'jogo':
            dt = clock.get_time()
            
            # Toca mÃºsica do labirinto se ainda nÃ£o estiver tocando
            if not musica_labirinto_tocando:
                # print("ðŸŽ® Iniciando mÃºsica do labirinto...")
                tocar_musica_labirinto()
                musica_labirinto_tocando = True
            
            for e in eventos:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_h: player.descartar_item() # ### ALTERADO ###
                    elif player.px % TAM_CELULA == 0 and player.py % TAM_CELULA == 0:
                        target_x, target_y = player.grid_x, player.grid_y
                        if e.key in [pygame.K_LEFT, pygame.K_a]: target_x -= 1
                        elif e.key in [pygame.K_RIGHT, pygame.K_d]: target_x += 1 # ### ALTERADO ###
                        elif e.key in [pygame.K_UP, pygame.K_w]: target_y -= 1
                        elif e.key in [pygame.K_DOWN, pygame.K_s]: target_y += 1
                        if not player.colide_parede(target_x, target_y):
                            player.caminho = [(player.grid_x, player.grid_y), (target_x, target_y)]
                            player.dir_x, player.dir_y = 0,0
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                        mouse_x, mouse_y = e.pos
                        grid_x, grid_y = mouse_x // TAM_CELULA, mouse_y // TAM_CELULA
                        if 0 <= grid_x < COLUNAS and 0 <= grid_y < LINHAS_LABIRINTO:
                            if player.px % TAM_CELULA == 0 and player.py % TAM_CELULA == 0:
                                caminho = encontrar_caminho(labirinto, (player.grid_x, player.grid_y), (grid_x, grid_y))
                            if caminho: player.caminho = caminho; player.dir_x, player.dir_y = 0, 0
            
            player.atualizar_animacao(dt)
            player.mover(); player.coletar(recursos)
            
            timer_spawn_recursos += dt
            if timer_spawn_recursos >= tempo_spawn_recursos_ms:
                timer_spawn_recursos = 0
                spawn_recurso()
            
            novos_inimigos, remover_ids = [], []
            for inimigo in list(inimigos):
                inimigo.mover(player) 
                inimigo.atualizar_divisao(dt, novos_inimigos, remover_ids)
                if inimigo.grid_x == player.grid_x and inimigo.grid_y == player.grid_y and inimigo.visivel:
                    inimigo_colisor = inimigo
                    parar_musica()  # Para a mÃºsica do labirinto
                    tocar_musica_game_over()  # Toca mÃºsica de game over
                    musica_labirinto_tocando = False  # Reset flag
                    estado_jogo = 'tela_game_over'
            
            if novos_inimigos: inimigos.extend(novos_inimigos)
            if remover_ids: inimigos[:] = [ini for ini in inimigos if ini.id not in remover_ids]
            
            for centro in centros:
                centro.atualizar_animacao(dt)
                if player.grid_x == centro.x and player.grid_y == centro.y:
                    pontos += centro.receber_entrega(player.inventario, player.stats)
            
            tela.fill(PRETO); desenhar_labirinto(tela); desenhar_recursos(tela, recursos)
            for centro in centros: centro.desenhar(tela)
            desenhar_rotulos_coleta(tela, centros, player)
            player.desenhar(tela)
            for inimigo in inimigos: inimigo.desenhar(tela)
            desenhar_hud(tela, player, centros, pontos)

            # ### BLOCO DE VITÃ“RIA MODIFICADO ###
            if all(c.nivel_atual >= c.nivel_max for c in centros):
                tempo_decorrido = (datetime.datetime.now() - tempo_inicio_partida).total_seconds()
                player.stats["tempo_jogado"] = tempo_decorrido
                player.stats["vitorias"] = 1
                player.stats["centros_completos"] = len(centros)
                
                # Armazena os pontos para a tela de vitÃ³ria
                pontos_finais = pontos
                pontos_bonus_vitoria = 500
                pontos_totais_vitoria = pontos_finais + pontos_bonus_vitoria

                # Adiciona pontos ao sistema de recompensas
                rewards_system.adicionar_pontos(nick_usuario, pontos_totais_vitoria, "vitoria")
                rewards_system.verificar_conquistas(nick_usuario, player.stats)
                
                # Para a mÃºsica e muda para a tela de vitÃ³ria
                parar_musica()
                musica_labirinto_tocando = False
                estado_jogo = 'tela_vitoria'

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()