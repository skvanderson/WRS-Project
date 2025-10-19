import pygame
import sys
import random
import math
import json
import datetime
from collections import deque
from typing import Dict, List, Tuple

# --- Inicialização do Pygame ---
pygame.init()

# --- Constantes Globais ---
TAM_CELULA = 30
COLUNAS = 32
LINHAS_LABIRINTO = 15 
LARGURA = COLUNAS * TAM_CELULA
ALTURA = (LINHAS_LABIRINTO + 3) * TAM_CELULA

FPS = 60
ARQUIVO_USUARIOS = "usuarios.json"
ARQUIVO_REWARDS = "rewards_data.json"

# --- Carregamento de Assets ---
def carregar_duas(pasta: str, base: str, tamanho: Tuple[int, int]) -> List[pygame.Surface]:
    frames = []
    for i in range(2):
        arq = f"assets/anim32/{pasta}/{base}_{i}.png"
        try:
            img = pygame.image.load(arq).convert_alpha()
            img = pygame.transform.smoothscale(img, tamanho)
            frames.append(img)
        except:
            surface = pygame.Surface(tamanho, pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 0, 0), (tamanho[0]//2, tamanho[1]//2), tamanho[0]//2 - 2)
            frames.append(surface)
    return frames

def carregar_sequencia(pasta: str, base: str, num_frames: int, tamanho: Tuple[int, int]) -> List[pygame.Surface]:
    frames = []
    for i in range(num_frames):
        arq = f"assets/anim32/{pasta}/{base}_{i}.png"
        try:
            img = pygame.image.load(arq).convert_alpha()
            img = pygame.transform.smoothscale(img, tamanho)
            frames.append(img)
        except:
            surface = pygame.Surface(tamanho, pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 255, 0), (tamanho[0]//2, tamanho[1]//2), tamanho[0]//2 - 2)
            frames.append(surface)
    return frames

def carregar_item(nome: str, tamanho: Tuple[int, int]) -> pygame.Surface:
    arq = f"assets/anim32/itens/item_{nome}.png"
    try:
        img = pygame.image.load(arq).convert_alpha()
        return pygame.transform.smoothscale(img, tamanho)
    except:
        surface = pygame.Surface(tamanho, pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 255, 0), (tamanho[0]//2, tamanho[1]//2), tamanho[0]//2 - 2)
        return surface

def carregar_centro(prefixo: str, tamanho: Tuple[int, int]) -> List[pygame.Surface]:
    imagens = []
    for i in range(3):
        arq = f"assets/centros48/{prefixo}_{i}.png"
        try:
            img = pygame.image.load(arq).convert_alpha()
            img = pygame.transform.smoothscale(img, tamanho)
            imagens.append(img)
        except:
            surface = pygame.Surface(tamanho, pygame.SRCALPHA)
            pygame.draw.rect(surface, (0, 255, 0), (2, 2, tamanho[0]-4, tamanho[1]-4), border_radius=4)
            imagens.append(surface)
    return imagens

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pac-Man - A Missão Comunitária")
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
        self.achievements = {"primeira_vitoria": {"nome": "Primeira Vitória", "descricao": "Vença uma partida", "pontos": 200, "desbloqueada": False},"colecionador": {"nome": "Colecionador", "descricao": "Colete 50 recursos", "pontos": 150, "desbloqueada": False},"construtor": {"nome": "Construtor", "descricao": "Complete 3 centros comunitários", "pontos": 300, "desbloqueada": False},"sobrevivente": {"nome": "Sobrevivente", "descricao": "Sobreviva 5 minutos", "pontos": 250, "desbloqueada": False}}
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
        self.carregar_imagens()
        self.stats = {"recursos_coletados": 0,"itens_entregues": 0,"tempo_jogado": 0, "inicio_partida": datetime.datetime.now()}
    def carregar_imagens(self):
        tamanho_player = (32, 32)
        self.frames_direita = carregar_sequencia("pacman", "pacman_right", 4, tamanho_player)
        if self.frames_direita:
            self.frames_esquerda = [pygame.transform.flip(f, True, False) for f in self.frames_direita]
            self.frames_cima = [pygame.transform.rotate(f, 90) for f in self.frames_direita]
            self.frames_baixo = [pygame.transform.rotate(f, -90) for f in self.frames_direita]
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
        if hasattr(self, 'frames_atual') and self.frames_atual:
            self.timer_animacao += dt
            if self.timer_animacao >= self.tempo_por_frame: self.timer_animacao, self.frame_atual = 0, (self.frame_atual + 1) % len(self.frames_atual)
    def atualizar_direcao(self):
        if hasattr(self, 'frames_direita') and self.frames_direita:
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
            else: # Mantém a lógica do teclado se não houver caminho
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
    def coletar(self, recursos, centros_comunitarios):
        if len(self.inventario) < self.capacidade_inventario:
            for recurso in recursos[:]:
                if recurso['x'] == self.grid_x and recurso['y'] == self.grid_y:
                    self.inventario.append(recurso['tipo'])
                    self.stats["recursos_coletados"] += 1
                    pos_ocupadas = [(r['x'], r['y']) for r in recursos] + [(c.x, c.y) for c in centros_comunitarios] + [(self.grid_x, self.grid_y)]
                    nova_pos = random.choice([p for p in posicoes_livres if p not in pos_ocupadas])
                    recurso['x'], recurso['y'] = nova_pos[0], nova_pos[1]
                    break
    def descartar_item(self):
        if self.inventario: self.inventario.pop()
    def desenhar(self, surface):
        centro = (self.px + TAM_CELULA//2, self.py + TAM_CELULA//2)
        if hasattr(self, 'frames_atual') and self.frames_atual:
            img_rect = self.frames_atual[self.frame_atual].get_rect(center=centro)
            surface.blit(self.frames_atual[self.frame_atual], img_rect)
        else:
            pygame.draw.circle(surface, AMARELO, centro, TAM_CELULA//2 - 3)

class Inimigo:
    def __init__(self, x, y, cor, nome, dificuldade="Default"):
        self.px, self.py = x * TAM_CELULA, y * TAM_CELULA
        self.cor, self.nome = cor, nome
        self.vel_x, self.vel_y = random.choice([(1,0),(-1,0),(0,1),(-1,0)])
        self.invisivel = (nome == "Falta de Acesso")
        self.visivel = True
        self.timer_invisibilidade, self.tempo_para_trocar = 0, random.randint(30, 60)
        self.dificuldade = dificuldade
        self.carregar_imagens()
        if self.dificuldade == "Easy": self.velocidade, self.comportamento_aleatorio = 1.5, 1.0
        elif self.dificuldade == "Hard": self.velocidade, self.comportamento_aleatorio = 2.5, 0.25
        else: self.velocidade, self.comportamento_aleatorio = 2.0, 0.7
    def carregar_imagens(self):
        tamanho_ghost = (48, 48)
        pasta_map = {"Desemprego": "ghost_desemprego", "Crise Econômica": "ghost_crise_economica", "Desigualdade": "ghost_desigualdade_small", "Falta de Acesso": "ghost_falta_acesso_visible"}
        pasta = pasta_map.get(self.nome, "ghost_desemprego")
        self.frames = carregar_duas(pasta, pasta, tamanho_ghost)
        if self.nome == "Falta de Acesso": self.frames_invisivel = carregar_duas("ghost_falta_acesso_invisivel", "ghost_falta_acesso_invisivel", tamanho_ghost)
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
            if random.random() < self.comportamento_aleatorio or not opcoes:
                prox_grid_x, prox_grid_y = self.grid_x + self.vel_x, self.grid_y + self.vel_y
                if self.colide_parede(prox_grid_x, prox_grid_y):
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
    def colide_parede(self, x, y): return not (0 <= x < COLUNAS and 0 <= y < LINHAS_LABIRINTO and labirinto[y][x] != 1)
    def desenhar(self, surface):
        if not self.visivel: return
        centro = (self.px + TAM_CELULA//2, self.py + TAM_CELULA//2)
        if hasattr(self, 'frames') and self.frames:
            frames_para_usar = self.frames_invisivel if self.nome == "Falta de Acesso" and hasattr(self, 'frames_invisivel') and not self.visivel else self.frames
            if frames_para_usar:
                frame_index = int(pygame.time.get_ticks() / 300) % len(frames_para_usar)
                img_rect = frames_para_usar[frame_index].get_rect(center=centro)
                surface.blit(frames_para_usar[frame_index], img_rect)
        else: pygame.draw.circle(surface, self.cor, centro, TAM_CELULA//2 - 4)
class CentroComunitario:
    def __init__(self, x, y, nome, cor, recurso_necessario):
        self.x, self.y, self.nome, self.cor = x, y, nome, cor
        self.recurso_necessario = recurso_necessario
        self.nivel_atual, self.nivel_max = 0, 5
        self.carregar_imagens()
    def carregar_imagens(self):
        tamanho_centro = (48, 48)
        prefixo_map = {"Escola": "escola","Hospital": "hospital", "Mercado": "mercado","Moradia": "moradia"}
        prefixo = prefixo_map.get(self.nome, "escola")
        self.frames = carregar_centro(prefixo, tamanho_centro)
    def desenhar(self, surface):
        px, py = self.x * TAM_CELULA, self.y * TAM_CELULA
        if hasattr(self, 'frames') and self.frames:
            nivel_index = min(self.nivel_atual // 2, len(self.frames) - 1)
            img_rect = self.frames[nivel_index].get_rect(center=(px + TAM_CELULA//2, py + TAM_CELULA//2))
            surface.blit(self.frames[nivel_index], img_rect)
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
def desenhar_texto(surface, texto, pos, fonte, cor=BRANCO):
    render = fonte.render(texto, True, cor)
    rect = render.get_rect(center=pos)
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
    y_inicial = pos[1] - (len(linhas_renderizadas) * fonte.get_linesize() / 2)
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
    fonte_titulo, fonte_label, fonte_input, fonte_erro = pygame.font.SysFont(None, 50), pygame.font.SysFont(None, 36), pygame.font.SysFont(None, 32), pygame.font.SysFont(None, 28)
    desenhar_texto(surface, titulo, (LARGURA/2, 100), fonte_titulo, AMARELO)
    surface.blit(fonte_label.render("Nick:", True, BRANCO), (rects['nick'].x, rects['nick'].y-40))
    pygame.draw.rect(surface,COR_INPUT_ATIVO if campo_ativo=='nick' else COR_INPUT_INATIVO,rects['nick'],2)
    surface.blit(fonte_input.render(nick,True,BRANCO), (rects['nick'].x+10, rects['nick'].y+10))
    surface.blit(fonte_label.render("Senha:",True,BRANCO), (rects['senha'].x, rects['senha'].y-40))
    pygame.draw.rect(surface,COR_INPUT_ATIVO if campo_ativo=='senha' else COR_INPUT_INATIVO,rects['senha'],2)
    surface.blit(fonte_input.render('*'*len(senha),True,BRANCO),(rects['senha'].x+10,rects['senha'].y+10))
    pygame.draw.rect(surface,COR_BOTAO,rects['confirmar']); desenhar_texto(surface,titulo,rects['confirmar'].center,fonte_label)
    pygame.draw.rect(surface,COR_BOTAO_VOLTAR,rects['voltar']); desenhar_texto(surface,"Voltar",rects['voltar'].center,fonte_label)
    if msg_erro: desenhar_texto(surface, msg_erro, (LARGURA/2, 500), fonte_erro, VERMELHO)
def desenhar_tela_dificuldade(surface, rects):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo, fonte_botao = pygame.font.SysFont(None, 50), pygame.font.SysFont(None, 38)
    desenhar_texto(surface, "Select Difficulty", (LARGURA / 2, 100), fonte_titulo, AMARELO)
    pygame.draw.rect(surface, (0, 150, 0), rects['easy']); desenhar_texto(surface, "Easy", rects['easy'].center, fonte_botao)
    pygame.draw.rect(surface, (200, 150, 0), rects['default']); desenhar_texto(surface, "Default", rects['default'].center, fonte_botao)
    pygame.draw.rect(surface, (150, 0, 0), rects['hard']); desenhar_texto(surface, "Hard", rects['hard'].center, fonte_botao)
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
        cor, status = (COR_OURO, "✓") if task_data.get("concluida") else (CINZA, "○")
        texto = f"{status} {task_data['descricao']} - {task_data['pontos']} pts"
        desenhar_texto(surface, texto, (LARGURA/2, y_offset), fonte_pequena, cor); y_offset += 25
    desenhar_texto(surface, "Conquistas", (LARGURA/2, y_offset + 20), fonte_media, COR_OURO)
    y_offset += 50
    conquistas = user_data.get("conquistas", {})
    for achievement_id, achievement_data in rewards_system.achievements.items():
        user_achievement = conquistas.get(achievement_id, {"desbloqueada": False})
        cor, status = (COR_OURO, "🏆") if user_achievement.get("desbloqueada") else (CINZA, "🔒")
        texto = f"{status} {achievement_data['nome']} - {achievement_data['pontos']} pts"
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
MENSAGENS_GAME_OVER = { "Desemprego": "O Desemprego paralisou seus planos...", "Desigualdade": "A Desigualdade bloqueou seu caminho...", "Falta de Acesso": "A Falta de Acesso a oportunidades te deixou para trás...", "Crise Econômica": "A Crise Econômica consumiu todos os seus esforços..." }
def desenhar_tela_game_over(surface, rects, nome_inimigo):
    surface.fill(COR_FUNDO_UI)
    fonte_grande, fonte_media, fonte_mensagem = pygame.font.SysFont(None, 60), pygame.font.SysFont(None, 45), pygame.font.SysFont(None, 32)
    mensagem = MENSAGENS_GAME_OVER.get(nome_inimigo, f"Você foi superado por: {nome_inimigo}")
    desenhar_texto(surface, "A Missão Falhou", (LARGURA/2, 150), fonte_grande, AMARELO)
    desenhar_texto_quebra_linha(surface, mensagem, (LARGURA/2, 250), LARGURA - 200, fonte_mensagem, VERMELHO_CRISE)
    desenhar_texto(surface, "Deseja tentar novamente?", (LARGURA/2, 350), fonte_media)
    pygame.draw.rect(surface, VERDE_CONTINUAR, rects['sim']); desenhar_texto(surface, "Sim", rects['sim'].center, fonte_media)
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['nao']); desenhar_texto(surface, "Não", rects['nao'].center, fonte_media)
def desenhar_labirinto(surface):
    for y,linha in enumerate(labirinto):
        for x,celula in enumerate(linha):
            if celula == 1: pygame.draw.rect(surface,AZUL_PAREDE,(x*TAM_CELULA, y*TAM_CELULA,TAM_CELULA,TAM_CELULA))
def desenhar_recursos(surface, recursos):
    tamanho_item = (24, 24)
    itens_imagens = {'Moeda': carregar_item('moeda', tamanho_item),'Alimento': carregar_item('alimento', tamanho_item), 'Livro': carregar_item('livro', tamanho_item),'Tijolo': carregar_item('tijolos', tamanho_item)}
    for r in recursos:
        centro = (r['x']*TAM_CELULA + TAM_CELULA//2, r['y']*TAM_CELULA + TAM_CELULA//2)
        if r['tipo'] in itens_imagens: surface.blit(itens_imagens[r['tipo']], itens_imagens[r['tipo']].get_rect(center=centro))
def desenhar_hud(surface, jogador, centros, pontos):
    base_y = LINHAS_LABIRINTO * TAM_CELULA
    pygame.draw.rect(surface, COR_FUNDO_UI, (0, base_y, LARGURA, ALTURA - base_y))
    fonte, fonte_instrucao = pygame.font.SysFont(None, 28), pygame.font.SysFont(None, 24)
    
    # Inventário e Instrução
    surface.blit(fonte.render("Inventário:", True, BRANCO), (40, base_y + 15))
    mapa_cor={'Moeda':COR_MOEDA,'Alimento':COR_ALIMENTO,'Livro':COR_LIVRO,'Tijolo':COR_TIJOLO}
    for i in range(jogador.capacidade_inventario):
        pygame.draw.rect(surface,BRANCO,(40+i*30,base_y+40,25,25),1)
        if i < len(jogador.inventario): pygame.draw.rect(surface,mapa_cor[jogador.inventario[i]],(40+i*30,base_y+40,25,25))
    surface.blit(fonte_instrucao.render("Pressione [D] para Descartar", True, CINZA), (40, base_y + 75))

    # Título Central
    surface.blit(fonte.render("Desenvolvimento Comunitário",True,BRANCO), (LARGURA/2, base_y+10))
    
    # Centros Comunitários (2 na esquerda, 2 na direita)
    centros_esquerda = centros[:2]
    centros_direita = centros[2:]
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
    
    # Pontos
    surface.blit(fonte.render(f"Pontos: {pontos}",True,BRANCO), (LARGURA-150,base_y+10))
    surface.blit(fonte_instrucao.render("Pressione [D] para Descartar", True, CINZA), (LARGURA - 180, ALTURA - 25))

# --- Loop Principal e Lógica de Estados ---
def main():
    rodando = True
    estado_jogo = 'tela_inicial'
    nick_usuario, senha_usuario, campo_ativo, mensagem_erro = "", "", 'nick', ""
    usuarios = carregar_usuarios()
    dificuldade_selecionada = "Default"
    rewards_system = RewardsSystem()

    rects_inicial = {'logar':pygame.Rect(LARGURA/2-150,230,300,70),'cadastrar':pygame.Rect(LARGURA/2-150,320,300,70)}
    rects_form = {'nick':pygame.Rect(LARGURA/2-200,200,400,40),'senha':pygame.Rect(LARGURA/2-200,320,400,40), 'confirmar':pygame.Rect(LARGURA/2-150,420,300,60),'voltar':pygame.Rect(LARGURA/2-100,500,200,50)}
    rects_game_over = {'sim':pygame.Rect(LARGURA/2-180,420,150,70),'nao':pygame.Rect(LARGURA/2+30,420,150,70)}
    rects_dificuldade = {'easy': pygame.Rect(LARGURA/2-150, 180, 300, 60), 'default': pygame.Rect(LARGURA/2-150, 250, 300, 60), 'hard': pygame.Rect(LARGURA/2-150, 320, 300, 60), 'rewards': pygame.Rect(LARGURA/2-150, 390, 300, 60), 'ranking': pygame.Rect(LARGURA/2-150, 460, 300, 60)}
    rects_rewards = {'voltar_rewards': pygame.Rect(LARGURA/2-100, 480, 200, 50)}
    rects_ranking = {'voltar_ranking': pygame.Rect(LARGURA/2-100, 480, 200, 50)}

    player, inimigos, centros, recursos, pontos, inimigo_colisor = None, [], [], [], 0, None
    posicoes_iniciais_inimigos = [(30, 1), (1, 13), (30, 13), (15, 7)]
    tempo_inicio_partida = 0
    
    def reiniciar_posicoes(dificuldade):
        nonlocal player, inimigos
        if player: player.reiniciar()
        nomes, cores = ["Desemprego","Desigualdade","Falta de Acesso","Crise Econômica"], [CINZA,ROXO,CINZA_ESCURO,VERMELHO_CRISE]
        inimigos.clear()
        for i,pos in enumerate(posicoes_iniciais_inimigos): inimigos.append(Inimigo(pos[0], pos[1], cores[i], nomes[i], dificuldade))
    
    def inicializar_novo_jogo(dificuldade):
        nonlocal pontos, centros, recursos, player, tempo_inicio_partida
        pontos, tempo_inicio_partida = 0, datetime.datetime.now()
        player = Player(1, 1)
        centros = [CentroComunitario(1, 7, "Moradia", COR_MORADIA, "Tijolo"), CentroComunitario(30, 7, "Mercado", COR_MERCADO, "Alimento"), CentroComunitario(15, 1, "Escola", COR_ESCOLA, "Livro"), CentroComunitario(15, 13, "Hospital", COR_HOSPITAL, "Moeda")]
        recursos, tipos_recursos = [], ['Moeda','Alimento','Livro','Tijolo']
        pos_ocupadas = [(c.x, c.y) for c in centros] + [(player.grid_x, player.grid_y)]
        for tipo in tipos_recursos:
            for _ in range(8):
                pos = random.choice([p for p in posicoes_livres if p not in pos_ocupadas])
                recursos.append({'x':pos[0], 'y':pos[1], 'tipo':tipo}); pos_ocupadas.append(pos)
        reiniciar_posicoes(dificuldade)

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
                    elif rects_dificuldade['rewards'].collidepoint(e.pos): estado_jogo = 'tela_rewards'
                    elif rects_dificuldade['ranking'].collidepoint(e.pos): estado_jogo = 'tela_ranking'
                    if dificuldade_foi_escolhida: inicializar_novo_jogo(dificuldade_selecionada); estado_jogo = 'jogo'
            desenhar_tela_dificuldade(tela, rects_dificuldade)

        elif estado_jogo == 'tela_rewards':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and rects_rewards['voltar_rewards'].collidepoint(e.pos): estado_jogo = 'tela_dificuldade'
            desenhar_tela_rewards(tela, rewards_system, nick_usuario, rects_rewards)
        
        elif estado_jogo == 'tela_ranking':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and rects_ranking['voltar_ranking'].collidepoint(e.pos): estado_jogo = 'tela_dificuldade'
            desenhar_tela_ranking(tela, rewards_system, rects_ranking)

        elif estado_jogo == 'tela_game_over':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if rects_game_over['sim'].collidepoint(e.pos):
                        inicializar_novo_jogo(dificuldade_selecionada)
                        estado_jogo = 'jogo'
                    elif rects_game_over['nao'].collidepoint(e.pos):
                        if player:
                            tempo_decorrido = (datetime.datetime.now() - tempo_inicio_partida).total_seconds()
                            player.stats["tempo_jogado"], player.stats["tempo_sobrevivencia"] = tempo_decorrido, tempo_decorrido
                            rewards_system.adicionar_pontos(nick_usuario, pontos, "partida")
                            rewards_system.verificar_tarefas_diarias(nick_usuario, player.stats)
                            rewards_system.verificar_conquistas(nick_usuario, player.stats)
                        estado_jogo = 'tela_inicial'
            desenhar_tela_game_over(tela, rects_game_over, inimigo_colisor.nome if inimigo_colisor else "um inimigo")

        elif estado_jogo == 'jogo':
            dt = clock.get_time()
            
            for e in eventos:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_d: 
                        player.descartar_item()

                    # Lógica de movimento passo-a-passo com o teclado
                    elif player.px % TAM_CELULA == 0 and player.py % TAM_CELULA == 0: # Só aceita novo comando se estiver alinhado
                        target_x, target_y = player.grid_x, player.grid_y
                        if e.key in [pygame.K_LEFT, pygame.K_a]: target_x -= 1
                        elif e.key in [pygame.K_RIGHT]: target_x += 1
                        elif e.key in [pygame.K_UP, pygame.K_w]: target_y -= 1
                        elif e.key in [pygame.K_DOWN, pygame.K_s]: target_y += 1

                        if not player.colide_parede(target_x, target_y):
                            player.caminho = [(player.grid_x, player.grid_y), (target_x, target_y)]
                            player.dir_x, player.dir_y = 0,0 # Limpa direção antiga
                
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 1: 
                        mouse_x, mouse_y = e.pos
                        grid_x, grid_y = mouse_x // TAM_CELULA, mouse_y // TAM_CELULA
                        if 0 <= grid_x < COLUNAS and 0 <= grid_y < LINHAS_LABIRINTO:
                            if player.px % TAM_CELULA == 0 and player.py % TAM_CELULA == 0:
                                caminho = encontrar_caminho(labirinto, (player.grid_x, player.grid_y), (grid_x, grid_y))
                                if caminho:
                                    player.caminho = caminho
                                    player.dir_x, player.dir_y = 0, 0
            
            # Atualiza o estado do jogo (fora do loop de eventos)
            player.atualizar_animacao(dt)
            player.mover(); player.coletar(recursos, centros)
            for inimigo in inimigos:
                inimigo.mover(player) 
                if inimigo.grid_x==player.grid_x and inimigo.grid_y==player.grid_y and inimigo.visivel:
                    inimigo_colisor = inimigo; estado_jogo = 'tela_game_over'
            for centro in centros:
                if player.grid_x==centro.x and player.grid_y==centro.y:
                    pontos += centro.receber_entrega(player.inventario, player.stats)
            
            # Desenha tudo
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
