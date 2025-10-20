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
COR_MOEDA, COR_ALIMENTO, COR_LIVRO, COR_TIJOLO = (255,215,0), (152,251,152), (135,206,250), (176,96,52)
COR_ESCOLA, COR_HOSPITAL, COR_MERCADO, COR_MORADIA = (65,105,225), (220,20,60), (34,139,34), (160,82,45)
COR_FUNDO_UI, COR_INPUT_INATIVO, COR_INPUT_ATIVO = (10,10,30), (100,100,100), (200,200,200)
COR_BOTAO, COR_BOTAO_VOLTAR = (0,100,0), (150,0,0)
COR_OURO, COR_PRATA, COR_BRONZE, COR_REWARD = (255,215,0), (192,192,192), (205,127,50), (0,200,255)

# =======================
#   CONTROLE DE MÚSICA
# =======================

def tocar_musica_labirinto():
    """Toca a música de fundo do labirinto em loop"""
    try:
        pygame.mixer.music.load(MUSICA_LABIRINTO)
        pygame.mixer.music.set_volume(0.3)  # Volume baixo para não atrapalhar
        pygame.mixer.music.play(-1)  # -1 = loop infinito
        # print(f"🎵 Música do labirinto iniciada: {MUSICA_LABIRINTO}")
    except pygame.error as e:
        print(f"❌ Erro ao carregar música do labirinto: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao tocar música do labirinto: {e}")

def tocar_musica_game_over():
    """Toca a música de game over uma vez, começando em 5 segundos"""
    try:
        pygame.mixer.music.load(MUSICA_GAME_OVER)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(0, start=5.0)  # 0 = tocar uma vez, start=5.0 = começar em 5 segundos
        # print(f"🎵 Música de game over iniciada (5s): {MUSICA_GAME_OVER}")
    except pygame.error as e:
        print(f"❌ Erro ao carregar música de game over: {e}")
        print("ℹ️  Tentando usar música do labirinto como fallback...")
        # Fallback: usar música do labirinto se game over falhar
        try:
            pygame.mixer.music.load(MUSICA_LABIRINTO)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(0)
            print(f"🎵 Usando música do labirinto como fallback")
        except:
            pygame.mixer.music.stop()
    except Exception as e:
        print(f"❌ Erro inesperado ao tocar música de game over: {e}")
        pygame.mixer.music.stop()

def parar_musica():
    """Para a música atual"""
    try:
        pygame.mixer.music.stop()
        # print("🔇 Música parada")
    except Exception as e:
        print(f"❌ Erro ao parar música: {e}")

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
    caminhos = [ANIM32_DIR / "itens" / f"item_{nome}.png", ASSETS_DIR / "items" / f"{nome.lower()}.png"]
    for arq in caminhos:
        img = _load_image(arq)
        if img is not None:
            return pygame.transform.smoothscale(img, tamanho)
    return _segura_surface(tamanho, (255,255,0), "circle")

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
    # ... (código da classe RewardsSystem intacto) ...
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
    def receber_entrega(self, inventario_jogador, player_stats=None):
        recursos_entregues = sum(1 for item in inventario_jogador if item == self.recurso_necessario)
        if recursos_entregues > 0 and self.nivel_atual < self.nivel_max:
            inventario_jogador[:] = [item for item in inventario_jogador if item != self.recurso_necessario]
            self.nivel_atual = min(self.nivel_max, self.nivel_atual + recursos_entregues)
            if player_stats: player_stats["itens_entregues"] += recursos_entregues
            return recursos_entregues * 20
        return 0

# --- Funções de UI e Jogo ---
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

def desenhar_tela_inicial(surface, rects):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo, fonte_botao = pygame.font.SysFont(None, 50), pygame.font.SysFont(None, 38)
    desenhar_texto(surface, "Pac-Man - A Missão Comunitária", (LARGURA/2, 130), fonte_titulo, AMARELO)
    pygame.draw.rect(surface, COR_BOTAO, rects['logar']); desenhar_texto(surface, "Logar", rects['logar'].center, fonte_botao)
    pygame.draw.rect(surface, COR_BOTAO, rects['cadastrar']); desenhar_texto(surface, "Cadastrar", rects['cadastrar'].center, fonte_botao)
def desenhar_tela_formulario(surface, titulo, nick, senha, campo_ativo, rects, msg_erro=""):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo, fonte_label, fonte_input, fonte_erro = pygame.font.SysFont(None, 50), pygame.font.SysFont(None, 36), pygame.font.SysFont(None, 32), pygame.font.SysFont(None, 32)
    desenhar_texto(surface, titulo, (LARGURA/2, 100), fonte_titulo, AMARELO)
    surface.blit(fonte_label.render("Nick:", True, BRANCO), (rects['nick'].x, rects['nick'].y-40))
    pygame.draw.rect(surface,COR_INPUT_ATIVO if campo_ativo=='nick' else COR_INPUT_INATIVO,rects['nick'],2)
    surface.blit(fonte_input.render(nick,True,BRANCO), (rects['nick'].x+10, rects['nick'].y+10))
    surface.blit(fonte_label.render("Senha:",True,BRANCO), (rects['senha'].x, rects['senha'].y-40))
    pygame.draw.rect(surface,COR_INPUT_ATIVO if campo_ativo=='senha' else COR_INPUT_INATIVO,rects['senha'],2)
    surface.blit(fonte_input.render('*'*len(senha),True,BRANCO),(rects['senha'].x+10,rects['senha'].y+10))
    # Desenha mensagem de erro logo abaixo do campo de senha
    if msg_erro: 
        desenhar_texto(surface, msg_erro, (LARGURA/2, rects['senha'].bottom + 30), fonte_erro, (255, 100, 100))  # Vermelho mais claro e visível
    
    pygame.draw.rect(surface,COR_BOTAO,rects['confirmar']); desenhar_texto(surface,titulo,rects['confirmar'].center,fonte_label)
    pygame.draw.rect(surface,COR_BOTAO_VOLTAR,rects['voltar']); desenhar_texto(surface,"Voltar",rects['voltar'].center,fonte_label)
def desenhar_tela_dificuldade(surface, rects):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo, fonte_botao = pygame.font.SysFont(None, 50), pygame.font.SysFont(None, 38)
    desenhar_texto(surface, "Select Difficulty", (LARGURA / 2, 80), fonte_titulo, AMARELO)
    pygame.draw.rect(surface, (0, 150, 0), rects['easy']); desenhar_texto(surface, "Easy", rects['easy'].center, fonte_botao)
    pygame.draw.rect(surface, (200, 150, 0), rects['default']); desenhar_texto(surface, "Default", rects['default'].center, fonte_botao)
    pygame.draw.rect(surface, (150, 0, 0), rects['hard']); desenhar_texto(surface, "Hard", rects['hard'].center, fonte_botao)
    pygame.draw.rect(surface, COR_BOTAO, rects['instrucoes']); desenhar_texto(surface, "Instruções", rects['instrucoes'].center, fonte_botao)
    pygame.draw.rect(surface, COR_OURO, rects['rewards']); desenhar_texto(surface, "Recompensas", rects['rewards'].center, fonte_botao)
    pygame.draw.rect(surface, COR_REWARD, rects['ranking']); desenhar_texto(surface, "Ranking", rects['ranking'].center, fonte_botao)
def desenhar_tela_rewards(surface, rewards_system, username, rects):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo, fonte_media, fonte_pequena = pygame.font.SysFont(None, 45), pygame.font.SysFont(None, 32), pygame.font.SysFont(None, 26)
    user_data = rewards_system.obter_usuario_rewards(username)
    desenhar_texto(surface, "Sistema de Recompensas", (LARGURA/2, 50), fonte_titulo, COR_OURO)
    desenhar_texto(surface, f"Usuário: {username}", (LARGURA/2, 100), fonte_media, BRANCO)
    desenhar_texto(surface, f"Pontos Totais: {user_data['pontos_totais']}", (LARGURA/2, 130), fonte_media, COR_OURO)
    desenhar_texto(surface, f"Nível: {user_data['nivel']}", (LARGURA/2, 160), fonte_media, COR_REWARD)
    desenhar_texto(surface, "Tarefas Diárias", (LARGURA/2, 200), fonte_media, COR_OURO)
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
        medalha = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}º"
        texto = f"{medalha} {username}: {pontos} pontos"
        desenhar_texto(surface, texto, (LARGURA/2, y_offset), fonte_pequena, cor); y_offset += 30
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['voltar_ranking']); desenhar_texto(surface, "Voltar", rects['voltar_ranking'].center, fonte_media)
MENSAGENS_GAME_OVER = {
    "Desemprego": "O fantasma do Desemprego te perseguiu implacavelmente, deixando seus sonhos de prosperidade em ruínas. A falta de oportunidades se tornou uma armadilha sem saída...",
    "Desigualdade": "A sombra da Desigualdade te engoliu por completo, criando um abismo intransponível entre você e uma vida digna. A injustiça social mostrou sua face mais cruel...",
    "Falta de Acesso": "A barreira da Falta de Acesso se ergueu como um muro intransponível, bloqueando todos os caminhos que levam ao progresso. A exclusão social te consumiu...",
    "Crise Econômica": "A tempestade da Crise Econômica devastou todos os seus esforços, transformando esperanças em desespero. O sistema financeiro te esmagou sem piedade..."
}
def desenhar_tela_game_over(surface, rects, nome_inimigo):
    surface.fill(COR_FUNDO_UI)
    fonte_grande, fonte_media, fonte_mensagem = pygame.font.SysFont(None, 60), pygame.font.SysFont(None, 45), pygame.font.SysFont(None, 28)
    mensagem = MENSAGENS_GAME_OVER.get(nome_inimigo, f"Você foi superado por: {nome_inimigo}")
    desenhar_texto(surface, "A Missão Falhou", (LARGURA/2, 120), fonte_grande, AMARELO)
    desenhar_texto_quebra_linha(surface, mensagem, (LARGURA/2, 200), LARGURA - 100, fonte_mensagem, VERMELHO_CRISE)
    desenhar_texto(surface, "Deseja tentar novamente?", (LARGURA/2, 400), fonte_media)
    pygame.draw.rect(surface, VERDE_CONTINUAR, rects['sim']); desenhar_texto(surface, "Sim", rects['sim'].center, fonte_media)
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['nao']); desenhar_texto(surface, "Não", rects['nao'].center, fonte_media)
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
def desenhar_hud(surface, jogador, centros, pontos):
    base_y = LINHAS_LABIRINTO * TAM_CELULA
    pygame.draw.rect(surface, COR_FUNDO_UI, (0, base_y, LARGURA, ALTURA - base_y))
    fonte, fonte_instrucao = pygame.font.SysFont(None, 28), pygame.font.SysFont(None, 24)
    surface.blit(fonte.render("Inventário:", True, BRANCO), (40, base_y + 15))
    mapa_cor={'Moeda':COR_MOEDA,'Alimento':COR_ALIMENTO,'Livro':COR_LIVRO,'Tijolo':COR_TIJOLO}
    for i in range(jogador.capacidade_inventario):
        pygame.draw.rect(surface,BRANCO,(40+i*30,base_y+40,25,25),1)
        if i < len(jogador.inventario): pygame.draw.rect(surface,mapa_cor[jogador.inventario[i]],(40+i*30,base_y+40,25,25))
    surface.blit(fonte_instrucao.render("Pressione [H] para Descartar", True, CINZA), (40, base_y + 75))
    surface.blit(fonte.render("Desenvolvimento Comunitário",True,BRANCO), (LARGURA/2, base_y+10))
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
    desenhar_texto(surface, "Instruções do Jogo", (LARGURA/2, y_pos), fonte_titulo, AMARELO)
    y_pos += 60
    desenhar_texto(surface, "Objetivo", (LARGURA/2, y_pos), fonte_subtitulo, COR_REWARD)
    y_pos += 45
    texto_objetivo = "Seu objetivo é reconstruir a comunidade! Para isso, colete os recursos e entregue-os nos Centros Comunitários correspondentes. Vença a partida completando o desenvolvimento de todos os centros."
    desenhar_texto_quebra_linha(surface, texto_objetivo, (LARGURA/2, y_pos), LARGURA - 150, fonte_texto, BRANCO)
    y_pos += 90
    desenhar_texto(surface, "Controles", (LARGURA/2, y_pos), fonte_subtitulo, COR_REWARD)
    y_pos += 40
    x_align = 150
    desenhar_texto(surface, "Teclado (Passo-a-passo):", (x_align, y_pos), fonte_texto, AMARELO, "topleft")
    y_pos += 25
    desenhar_texto(surface, "Use as Setas ou W, A, S, D para mover um quadrado por vez.", (x_align, y_pos), fonte_texto_menor, BRANCO, "topleft")
    y_pos += 40
    desenhar_texto(surface, "Mouse (Caminho Automático):", (x_align, y_pos), fonte_texto, AMARELO, "topleft")
    y_pos += 25
    desenhar_texto(surface, "Clique em qualquer lugar do labirinto para o Pac-Man ir até lá.", (x_align, y_pos), fonte_texto_menor, BRANCO, "topleft")
    y_pos += 40
    desenhar_texto(surface, "Inventário:", (x_align, y_pos), fonte_texto, AMARELO, "topleft")
    y_pos += 25
    desenhar_texto(surface, "Pressione [H] para descartar o último item coletado.", (x_align, y_pos), fonte_texto_menor, BRANCO, "topleft")
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['voltar']); desenhar_texto(surface, "Voltar", rects['voltar'].center, fonte_subtitulo)


# --- Loop Principal e Lógica de Estados ---
def main():
    rodando = True
    estado_jogo = 'tela_inicial'
    nick_usuario, senha_usuario, campo_ativo, mensagem_erro = "", "", 'nick', ""
    usuarios = carregar_usuarios()
    dificuldade_selecionada = "Default"
    rewards_system = RewardsSystem()

    rects_inicial = {'logar':pygame.Rect(LARGURA/2-150,230,300,70),'cadastrar':pygame.Rect(LARGURA/2-150,320,300,70)}
    rects_form = {'nick':pygame.Rect(LARGURA/2-200,180,400,40),'senha':pygame.Rect(LARGURA/2-200,280,400,40), 'confirmar':pygame.Rect(LARGURA/2-150,380,300,60),'voltar':pygame.Rect(LARGURA/2-100,460,200,50)}
    rects_game_over = {'sim':pygame.Rect(LARGURA/2-180,420,150,70),'nao':pygame.Rect(LARGURA/2+30,420,150,70)}
    
    rects_dificuldade = {
        'easy': pygame.Rect(LARGURA/2-150, 160, 300, 50), 
        'default': pygame.Rect(LARGURA/2-150, 220, 300, 50), 
        'hard': pygame.Rect(LARGURA/2-150, 280, 300, 50),
        'instrucoes': pygame.Rect(LARGURA/2-150, 340, 300, 50),
        'rewards': pygame.Rect(LARGURA/2-150, 400, 300, 50), 
        'ranking': pygame.Rect(LARGURA/2-150, 460, 300, 50)
    }
    rects_instrucoes = {'voltar': pygame.Rect(LARGURA/2-100, ALTURA-60, 200, 50)}
    
    rects_rewards = {'voltar_rewards': pygame.Rect(LARGURA/2-100, 480, 200, 50)}
    rects_ranking = {'voltar_ranking': pygame.Rect(LARGURA/2-100, 480, 200, 50)}

    player, inimigos, centros, recursos, pontos, inimigo_colisor = None, [], [], [], 0, None
    posicoes_iniciais_inimigos = [(30, 1), (1, 13), (30, 13), (15, 7)]
    tempo_inicio_partida = 0
    musica_labirinto_tocando = False
    
    tipos_recursos_padrao = ['Moeda', 'Alimento', 'Livro', 'Tijolo']
    tempo_spawn_recursos_ms = 1800
    timer_spawn_recursos = 0
    max_recursos_no_cenario = 40
    
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
            for _ in range(4):
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
        tipo = random.choice(tipos_recursos_padrao)
        pos = random.choice(livres)
        recursos.append({'x': pos[0], 'y': pos[1], 'tipo': tipo})

    while rodando:
        eventos = pygame.event.get()
        for e in eventos:
            if e.type == pygame.QUIT: rodando = False

        if estado_jogo == 'tela_inicial':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if rects_inicial['logar'].collidepoint(e.pos):
                        estado_jogo='tela_login'; mensagem_erro,nick_usuario,senha_usuario="","",""; campo_ativo='nick'
                    elif rects_inicial['cadastrar'].collidepoint(e.pos):
                        estado_jogo='tela_cadastro'; mensagem_erro,nick_usuario,senha_usuario="","",""; campo_ativo='nick'
            desenhar_tela_inicial(tela, rects_inicial)

        elif estado_jogo in ['tela_login', 'tela_cadastro']:
            # ... (código do formulário intacto) ...
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
                            else: mensagem_erro = "Nick ou senha inválidos."
                        else: 
                            if not nick_usuario or not senha_usuario: mensagem_erro="Os campos não podem estar vazios."
                            elif nick_usuario in usuarios: mensagem_erro="Este nick já está em uso."
                            else: usuarios[nick_usuario]=senha_usuario; salvar_usuarios(usuarios); estado_jogo = 'tela_dificuldade'
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN or e.key == pygame.K_KP_ENTER:
                        if estado_jogo == 'tela_login':
                            if nick_usuario in usuarios and usuarios[nick_usuario] == senha_usuario: estado_jogo = 'tela_dificuldade'
                            else: mensagem_erro = "Nick ou senha inválidos."
                        else: 
                            if not nick_usuario or not senha_usuario: mensagem_erro="Os campos não podem estar vazios."
                            elif nick_usuario in usuarios: mensagem_erro="Este nick já está em uso."
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
                    if dificuldade_foi_escolhida: inicializar_novo_jogo(dificuldade_selecionada); estado_jogo = 'jogo'
            desenhar_tela_dificuldade(tela, rects_dificuldade)

        elif estado_jogo == 'tela_instrucoes':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if rects_instrucoes['voltar'].collidepoint(e.pos):
                        estado_jogo = 'tela_dificuldade'
            desenhar_tela_instrucoes(tela, rects_instrucoes)

        elif estado_jogo == 'tela_rewards':
            # ... (código da tela de recompensas intacto) ...
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and rects_rewards['voltar_rewards'].collidepoint(e.pos): estado_jogo = 'tela_dificuldade'
            desenhar_tela_rewards(tela, rewards_system, nick_usuario, rects_rewards)
        
        elif estado_jogo == 'tela_ranking':
            # ... (código da tela de ranking intacto) ...
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and rects_ranking['voltar_ranking'].collidepoint(e.pos): estado_jogo = 'tela_dificuldade'
            desenhar_tela_ranking(tela, rewards_system, rects_ranking)

        elif estado_jogo == 'tela_game_over':
            # ... (código da tela de game over intacto) ...
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if rects_game_over['sim'].collidepoint(e.pos):
                        parar_musica()  # Para a música de game over
                        musica_labirinto_tocando = False  # Reset flag para tocar música do labirinto novamente
                        inicializar_novo_jogo(dificuldade_selecionada)
                        estado_jogo = 'jogo'
                    elif rects_game_over['nao'].collidepoint(e.pos):
                        if player:
                            tempo_decorrido = (datetime.datetime.now() - tempo_inicio_partida).total_seconds()
                            player.stats["tempo_jogado"], player.stats["tempo_sobrevivencia"] = tempo_decorrido, tempo_decorrido
                            rewards_system.adicionar_pontos(nick_usuario, pontos, "partida")
                            rewards_system.verificar_tarefas_diarias(nick_usuario, player.stats)
                            rewards_system.verificar_conquistas(nick_usuario, player.stats)
                        parar_musica()  # Para a música de game over
                        musica_labirinto_tocando = False  # Reset flag
                        estado_jogo = 'tela_inicial'
            desenhar_tela_game_over(tela, rects_game_over, inimigo_colisor.nome if inimigo_colisor else "um inimigo")

        elif estado_jogo == 'jogo':
            dt = clock.get_time()
            
            # Toca música do labirinto se ainda não estiver tocando
            if not musica_labirinto_tocando:
                # print("🎮 Iniciando música do labirinto...")
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
                    parar_musica()  # Para a música do labirinto
                    tocar_musica_game_over()  # Toca música de game over
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
            player.desenhar(tela)
            for inimigo in inimigos: inimigo.desenhar(tela)
            desenhar_hud(tela, player, centros, pontos)

            if all(c.nivel_atual >= c.nivel_max for c in centros):
                tempo_decorrido = (datetime.datetime.now() - tempo_inicio_partida).total_seconds()
                player.stats["tempo_jogado"], player.stats["vitorias"], player.stats["centros_completos"] = tempo_decorrido, 1, len(centros)
                pontos_vitoria = pontos + 500
                rewards_system.adicionar_pontos(nick_usuario, pontos_vitoria, "vitoria")
                rewards_system.verificar_conquistas(nick_usuario, player.stats)
                fonte_fim=pygame.font.SysFont(None,50)
                tela.fill(PRETO)
                desenhar_texto(tela,"Parabéns! A comunidade prosperou!",(LARGURA/2,ALTURA/2-40),fonte_fim,(120,255,120))
                desenhar_texto(tela,f"Pontuação Final: {pontos}",(LARGURA/2,ALTURA/2+10),fonte_fim)
                desenhar_texto(tela,f"Pontos de Recompensa: +500",(LARGURA/2,ALTURA/2+50),fonte_fim,COR_OURO)
                pygame.display.flip(); pygame.time.wait(4000)
                rodando = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()