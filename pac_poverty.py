import pygame
import sys
import random
import math
import json
import datetime
from typing import Dict, List, Tuple

# --- Inicialização do Pygame ---
pygame.init()

# --- Constantes Globais ---
LARGURA, ALTURA = 600, 720
TAM_CELULA = 30
COLUNAS = LARGURA // TAM_CELULA
LINHAS_LABIRINTO = 18
FPS = 60
ARQUIVO_USUARIOS = "usuarios.json"
ARQUIVO_REWARDS = "rewards_data.json"

# --- Carregamento de Assets ---
def carregar_duas(pasta: str, base: str, tamanho: Tuple[int, int]) -> List[pygame.Surface]:
    """Carrega 2 frames de animação de um fantasma"""
    frames = []
    for i in range(2):
        arq = f"assets/anim32/{pasta}/{base}_{i}.png"
        try:
            img = pygame.image.load(arq).convert_alpha()
            img = pygame.transform.smoothscale(img, tamanho)
            frames.append(img)
        except:
            # Fallback para fantasma simples
            surface = pygame.Surface(tamanho, pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 0, 0), (tamanho[0]//2, tamanho[1]//2), tamanho[0]//2 - 2)
            frames.append(surface)
    return frames

def carregar_sequencia(pasta: str, base: str, num_frames: int, tamanho: Tuple[int, int]) -> List[pygame.Surface]:
    """Carrega uma sequência de frames de animação"""
    frames = []
    for i in range(num_frames):
        arq = f"assets/anim32/{pasta}/{base}_{i}.png"
        try:
            img = pygame.image.load(arq).convert_alpha()
            img = pygame.transform.smoothscale(img, tamanho)
            frames.append(img)
        except:
            # Fallback para frame simples
            surface = pygame.Surface(tamanho, pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 255, 0), (tamanho[0]//2, tamanho[1]//2), tamanho[0]//2 - 2)
            frames.append(surface)
    return frames

def carregar_item(nome: str, tamanho: Tuple[int, int]) -> pygame.Surface:
    """Carrega imagem de um item"""
    arq = f"assets/anim32/itens/item_{nome}.png"
    try:
        img = pygame.image.load(arq).convert_alpha()
        return pygame.transform.smoothscale(img, tamanho)
    except:
        # Fallback para item simples
        surface = pygame.Surface(tamanho, pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 255, 0), (tamanho[0]//2, tamanho[1]//2), tamanho[0]//2 - 2)
        return surface

def carregar_centro(prefixo: str, tamanho: Tuple[int, int]) -> List[pygame.Surface]:
    """Carrega imagens de um centro comunitário (3 níveis)"""
    imagens = []
    for i in range(3):
        arq = f"assets/centros48/{prefixo}_{i}.png"
        try:
            img = pygame.image.load(arq).convert_alpha()
            img = pygame.transform.smoothscale(img, tamanho)
            imagens.append(img)
        except:
            # Fallback para centro simples
            surface = pygame.Surface(tamanho, pygame.SRCALPHA)
            pygame.draw.rect(surface, (0, 255, 0), (2, 2, tamanho[0]-4, tamanho[1]-4), border_radius=4)
            imagens.append(surface)
    return imagens

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pac-Man - A Missão Comunitária")
clock = pygame.time.Clock()

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

COR_MOEDA = (255, 215, 0)
COR_ALIMENTO = (152, 251, 152)
COR_LIVRO = (135, 206, 250)
COR_TIJOLO = (176, 96, 52)

COR_ESCOLA = (65, 105, 225)
COR_HOSPITAL = (220, 20, 60)
COR_MERCADO = (34, 139, 34)
COR_MORADIA = (160, 82, 45)

# Cores para a UI
COR_FUNDO_UI = (10, 10, 30)
COR_INPUT_INATIVO = (100, 100, 100)
COR_INPUT_ATIVO = (200, 200, 200)
COR_BOTAO = (0, 100, 0)
COR_BOTAO_VOLTAR = (150, 0, 0)

# Cores para o sistema de recompensas
COR_OURO = (255, 215, 0)
COR_PRATA = (192, 192, 192)
COR_BRONZE = (205, 127, 50)
COR_REWARD = (0, 200, 255)

# --- Layout do Labirinto ---
labirinto = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,0,1,1,0,1,1,1,0,1,1,0,1], [1,0,1,1,0,1,0,0,0,0,0,0,0,0,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,1,1,0,1,1,0,0,0,0,0,0,0,1], [1,0,1,1,0,1,0,0,1,0,1,0,0,1,0,1,1,0,0,1],
    [1,0,0,1,0,1,1,0,1,0,1,0,1,1,0,1,0,0,0,1], [1,1,0,1,0,1,0,0,0,0,0,0,0,1,0,1,0,1,1,1],
    [1,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,1], [1,0,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,0,0,1],
    [1,0,0,0,0,1,0,1,1,1,1,1,0,1,0,0,0,0,0,1], [1,1,1,0,1,1,0,1,0,0,0,1,0,1,1,0,1,1,1,1],
    [1,0,0,0,0,0,0,1,0,1,0,1,0,0,0,0,0,0,0,1], [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,0,1],
    [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1], [1,0,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1], [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
posicoes_livres = [(x, y) for y, linha in enumerate(labirinto) for x, celula in enumerate(linha) if celula == 0]

# --- Sistema de Recompensas ---
class RewardsSystem:
    """Sistema de recompensas similar ao Microsoft Rewards"""
    
    def __init__(self):
        self.rewards_data = self.carregar_rewards()
        self.daily_tasks = {
            "coletar_10_recursos": {"descricao": "Colete 10 recursos", "pontos": 50, "concluida": False},
            "entregar_5_itens": {"descricao": "Entregue 5 itens nos centros", "pontos": 75, "concluida": False},
            "jogar_3_partidas": {"descricao": "Jogue 3 partidas", "pontos": 100, "concluida": False},
            "sobreviver_2_minutos": {"descricao": "Sobreviva por 2 minutos", "pontos": 60, "concluida": False}
        }
        self.achievements = {
            "primeira_vitoria": {"nome": "Primeira Vitória", "descricao": "Vença uma partida", "pontos": 200, "desbloqueada": False},
            "colecionador": {"nome": "Colecionador", "descricao": "Colete 50 recursos", "pontos": 150, "desbloqueada": False},
            "construtor": {"nome": "Construtor", "descricao": "Complete 3 centros comunitários", "pontos": 300, "desbloqueada": False},
            "sobrevivente": {"nome": "Sobrevivente", "descricao": "Sobreviva 5 minutos", "pontos": 250, "desbloqueada": False}
        }
    
    def carregar_rewards(self) -> Dict:
        """Carrega dados de recompensas do arquivo"""
        try:
            with open(ARQUIVO_REWARDS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def salvar_rewards(self):
        """Salva dados de recompensas no arquivo"""
        with open(ARQUIVO_REWARDS, 'w', encoding='utf-8') as f:
            json.dump(self.rewards_data, f, indent=4, ensure_ascii=False)
    
    def obter_usuario_rewards(self, username: str) -> Dict:
        """Obtém dados de recompensas de um usuário"""
        if username not in self.rewards_data:
            self.rewards_data[username] = {
                "pontos_totais": 0,
                "nivel": 1,
                "conquistas": {},
                "tarefas_diarias": {},
                "ultima_atualizacao": datetime.datetime.now().isoformat(),
                "historico_partidas": []
            }
        return self.rewards_data[username]
    
    def adicionar_pontos(self, username: str, pontos: int, origem: str = "jogo"):
        """Adiciona pontos para um usuário"""
        user_data = self.obter_usuario_rewards(username)
        user_data["pontos_totais"] += pontos
        user_data["ultima_atualizacao"] = datetime.datetime.now().isoformat()
        
        # Adiciona ao histórico
        user_data["historico_partidas"].append({
            "data": datetime.datetime.now().isoformat(),
            "pontos": pontos,
            "origem": origem
        })
        
        # Limita o histórico a 50 entradas
        if len(user_data["historico_partidas"]) > 50:
            user_data["historico_partidas"] = user_data["historico_partidas"][-50:]
        
        # Calcula nível baseado nos pontos
        user_data["nivel"] = min(100, (user_data["pontos_totais"] // 1000) + 1)
        
        self.salvar_rewards()
    
    def verificar_tarefas_diarias(self, username: str, stats: Dict):
        """Verifica e atualiza tarefas diárias"""
        user_data = self.obter_usuario_rewards(username)
        hoje = datetime.datetime.now().date().isoformat()
        
        # Reinicia tarefas se for um novo dia
        if user_data.get("ultima_tarefa_dia") != hoje:
            user_data["tarefas_diarias"] = self.daily_tasks.copy()
            user_data["ultima_tarefa_dia"] = hoje
        
        tarefas = user_data["tarefas_diarias"]
        
        # Verifica tarefas
        if stats.get("recursos_coletados", 0) >= 10 and not tarefas["coletar_10_recursos"]["concluida"]:
            tarefas["coletar_10_recursos"]["concluida"] = True
            self.adicionar_pontos(username, 50, "tarefa_diaria")
        
        if stats.get("itens_entregues", 0) >= 5 and not tarefas["entregar_5_itens"]["concluida"]:
            tarefas["entregar_5_itens"]["concluida"] = True
            self.adicionar_pontos(username, 75, "tarefa_diaria")
        
        if stats.get("partidas_jogadas", 0) >= 3 and not tarefas["jogar_3_partidas"]["concluida"]:
            tarefas["jogar_3_partidas"]["concluida"] = True
            self.adicionar_pontos(username, 100, "tarefa_diaria")
        
        if stats.get("tempo_sobrevivencia", 0) >= 120 and not tarefas["sobreviver_2_minutos"]["concluida"]:
            tarefas["sobreviver_2_minutos"]["concluida"] = True
            self.adicionar_pontos(username, 60, "tarefa_diaria")
        
        self.salvar_rewards()
    
    def verificar_conquistas(self, username: str, stats: Dict):
        """Verifica e desbloqueia conquistas"""
        user_data = self.obter_usuario_rewards(username)
        conquistas = user_data.setdefault("conquistas", {})
        
        for achievement_id, achievement in self.achievements.items():
            if achievement_id not in conquistas:
                conquistas[achievement_id] = {"desbloqueada": False, "data": None}
            
            if not conquistas[achievement_id]["desbloqueada"]:
                desbloqueou = False
                
                if achievement_id == "primeira_vitoria" and stats.get("vitorias", 0) >= 1:
                    desbloqueou = True
                elif achievement_id == "colecionador" and stats.get("recursos_coletados", 0) >= 50:
                    desbloqueou = True
                elif achievement_id == "construtor" and stats.get("centros_completos", 0) >= 3:
                    desbloqueou = True
                elif achievement_id == "sobrevivente" and stats.get("tempo_sobrevivencia", 0) >= 300:
                    desbloqueou = True
                
                if desbloqueou:
                    conquistas[achievement_id] = {
                        "desbloqueada": True,
                        "data": datetime.datetime.now().isoformat()
                    }
                    self.adicionar_pontos(username, achievement["pontos"], "conquista")
        
        self.salvar_rewards()
    
    def obter_ranking(self, limite: int = 10) -> List[Tuple[str, int]]:
        """Obtém ranking de usuários por pontos"""
        ranking = []
        for username, data in self.rewards_data.items():
            ranking.append((username, data.get("pontos_totais", 0)))
        
        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking[:limite]

# --- Classes do Jogo ---
class Player:
    def __init__(self, x, y):
        self.px, self.py = x * TAM_CELULA, y * TAM_CELULA
        self.dir_x, self.dir_y = 0, 0
        self.vel_x, self.vel_y = 0, 0
        self.velocidade = 3
        self.boca_frame = 0
        self.boca_frames_total = 4
        self.inventario = []
        self.capacidade_inventario = 5
        
        # Carregar animações do Pac-Man
        self.carregar_imagens()
        
        # Estatísticas para o sistema de recompensas
        self.stats = {
            "recursos_coletados": 0,
            "itens_entregues": 0,
            "tempo_jogado": 0,
            "inicio_partida": datetime.datetime.now()
        }
    
    def carregar_imagens(self):
        """Carrega as imagens de animação do Pac-Man"""
        tamanho_player = (32, 32)
        
        # Carrega frames para direita
        self.frames_direita = carregar_sequencia("pacman", "pacman_right", 4, tamanho_player)
        
        if self.frames_direita:
            # Cria frames para outras direções
            self.frames_esquerda = [pygame.transform.flip(f, True, False) for f in self.frames_direita]
            self.frames_cima = [pygame.transform.rotate(f, 90) for f in self.frames_direita]
            self.frames_baixo = [pygame.transform.rotate(f, -90) for f in self.frames_direita]
            
            # Define frames atuais
            self.frames_atual = self.frames_direita
            self.frame_atual = 0
            self.timer_animacao = 0
            self.tempo_por_frame = 110  # ms por frame
        else:
            # Fallback se não conseguir carregar
            self.frames_atual = None
            self.frame_atual = 0

    @property
    def grid_x(self):
        return int((self.px + TAM_CELULA // 2) / TAM_CELULA)
    @property
    def grid_y(self):
        return int((self.py + TAM_CELULA // 2) / TAM_CELULA)
    
    def reiniciar(self):
        self.px, self.py = 1 * TAM_CELULA, 1 * TAM_CELULA
        self.dir_x, self.dir_y = 0, 0
        self.vel_x, self.vel_y = 0, 0
        self.inventario.clear()
        self.stats["inicio_partida"] = datetime.datetime.now()
        if hasattr(self, 'frames_direita'):
            self.frames_atual = self.frames_direita
            self.frame_atual = 0
            self.timer_animacao = 0
    
    def atualizar_animacao(self, dt):
        """Atualiza a animação do Pac-Man"""
        if hasattr(self, 'frames_atual') and self.frames_atual:
            self.timer_animacao += dt
            if self.timer_animacao >= self.tempo_por_frame:
                self.timer_animacao = 0
                self.frame_atual = (self.frame_atual + 1) % len(self.frames_atual)
    
    def atualizar_direcao(self):
        """Atualiza os frames baseado na direção do movimento"""
        if hasattr(self, 'frames_direita') and self.frames_direita:
            if self.vel_x > 0:
                self.frames_atual = self.frames_direita
            elif self.vel_x < 0:
                self.frames_atual = self.frames_esquerda
            elif self.vel_y < 0:
                self.frames_atual = self.frames_cima
            elif self.vel_y > 0:
                self.frames_atual = self.frames_baixo

    def mover(self):
        esta_alinhado = self.px % TAM_CELULA == 0 and self.py % TAM_CELULA == 0
        if esta_alinhado:
            if self.dir_x != 0 or self.dir_y != 0:
                prox_grid_x, prox_grid_y = self.grid_x + self.dir_x, self.grid_y + self.dir_y
                if not self.colide_parede(prox_grid_x, prox_grid_y):
                    self.vel_x, self.vel_y = self.dir_x, self.dir_y
        self.px += self.vel_x * self.velocidade
        self.py += self.vel_y * self.velocidade
        if esta_alinhado:
            prox_grid_x, prox_grid_y = self.grid_x + self.vel_x, self.grid_y + self.vel_y
            if self.colide_parede(prox_grid_x, prox_grid_y):
                self.px, self.py = self.grid_x * TAM_CELULA, self.grid_y * TAM_CELULA
                self.vel_x, self.vel_y = 0, 0
        
        # Atualiza direção da animação
        self.atualizar_direcao()

    def colide_parede(self, x, y):
        return not (0 <= x < COLUNAS and 0 <= y < LINHAS_LABIRINTO and labirinto[y][x] != 1)

    def coletar(self, recursos, centros_comunitarios):
        if len(self.inventario) < self.capacidade_inventario:
            for recurso in recursos[:]:
                if recurso['x'] == self.grid_x and recurso['y'] == self.grid_y:
                    self.inventario.append(recurso['tipo'])
                    self.stats["recursos_coletados"] += 1
                    pos_ocupadas = [(r['x'], r['y']) for r in recursos] + \
                                   [(c.x, c.y) for c in centros_comunitarios] + \
                                   [(self.grid_x, self.grid_y)]
                    nova_pos = random.choice([p for p in posicoes_livres if p not in pos_ocupadas])
                    recurso['x'], recurso['y'] = nova_pos[0], nova_pos[1]
                    break
    
    def descartar_item(self):
        if self.inventario:
            self.inventario.pop()

    def desenhar(self, surface):
        centro = (self.px + TAM_CELULA//2, self.py + TAM_CELULA//2)
        
        # Tenta usar imagem do Pac-Man
        if hasattr(self, 'frames_atual') and self.frames_atual and self.frame_atual < len(self.frames_atual):
            img = self.frames_atual[self.frame_atual]
            img_rect = img.get_rect(center=centro)
            surface.blit(img, img_rect)
        else:
            # Fallback para desenho simples
            raio = TAM_CELULA//2 - 3
            direcao_atual = self.vel_x
            if direcao_atual == -1: angulo_central = math.pi
            elif direcao_atual == 1: angulo_central = 0
            elif self.vel_y == -1: angulo_central = math.pi/2
            elif self.vel_y == 1: angulo_central = -math.pi/2
            else: angulo_central = 0
            max_abertura = math.radians(45)
            min_abertura = math.radians(5)
            t = abs(self.boca_frames_total - 2 * (self.boca_frame % self.boca_frames_total)) / self.boca_frames_total
            abertura = min_abertura + (max_abertura - min_abertura) * t
            inicio, fim = angulo_central + abertura, angulo_central - abertura
            pygame.draw.circle(surface, AMARELO, centro, raio)
            if self.vel_x != 0 or self.vel_y != 0:
                p1 = centro
                p2 = (centro[0] + math.cos(inicio) * raio, centro[1] - math.sin(inicio) * raio)
                p3 = (centro[0] + math.cos(fim) * raio, centro[1] - math.sin(fim) * raio)
                pygame.draw.polygon(surface, PRETO, [p1, p2, p3])
            self.boca_frame += 1

class Inimigo:
    def __init__(self, x, y, cor, nome, dificuldade="Default"):
        self.px, self.py = x * TAM_CELULA, y * TAM_CELULA
        self.cor, self.nome = cor, nome
        self.vel_x, self.vel_y = random.choice([(1,0),(-1,0),(0,1),(-1,0)])
        self.invisivel = (nome == "Falta de Acesso")
        self.visivel = True
        self.timer_invisibilidade = 0
        self.tempo_para_trocar = random.randint(30, 60)
        self.dificuldade = dificuldade

        # Carregar imagens do fantasma
        self.carregar_imagens()

        if self.dificuldade == "Easy":
            self.velocidade = 1.5
            self.comportamento_aleatorio = 1.0 
        elif self.dificuldade == "Hard":
            self.velocidade = 2.5
            self.comportamento_aleatorio = 0.25
        else:  # Default
            self.velocidade = 2
            self.comportamento_aleatorio = 0.7
    
    def carregar_imagens(self):
        """Carrega as imagens do fantasma baseado no nome"""
        tamanho_ghost = (48, 48)
        
        # Mapeia nomes para pastas de assets
        pasta_map = {
            "Desemprego": "ghost_desemprego",
            "Crise Econômica": "ghost_crise_economica",
            "Desigualdade": "ghost_desigualdade_small",
            "Falta de Acesso": "ghost_falta_acesso_visible"
        }
        
        pasta = pasta_map.get(self.nome, "ghost_desemprego")
        self.frames = carregar_duas(pasta, pasta, tamanho_ghost)
        
        # Para "Falta de Acesso", carrega também frames invisíveis
        if self.nome == "Falta de Acesso":
            self.frames_invisivel = carregar_duas("ghost_falta_acesso_invisivel", "ghost_falta_acesso_invisivel", tamanho_ghost)
        
        if not self.frames:
            # Fallback para fantasma simples
            self.frames = [self.criar_fantasma_simples()]
    
    def criar_fantasma_simples(self):
        """Cria um fantasma simples como fallback"""
        surface = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(surface, self.cor, (24, 24), 22)
        return surface 

    @property
    def grid_x(self):
        return int((self.px + TAM_CELULA // 2) / TAM_CELULA)
    @property
    def grid_y(self):
        return int((self.py + TAM_CELULA // 2) / TAM_CELULA)

    def mover(self, player):
        if self.invisivel:
            self.timer_invisibilidade += 1
            if self.timer_invisibilidade > self.tempo_para_trocar * (FPS / 10):
                self.visivel = not self.visivel
                self.timer_invisibilidade = 0
                self.tempo_para_trocar = random.randint(20, 50)

        if self.px % TAM_CELULA == 0 and self.py % TAM_CELULA == 0:
            opcoes = []
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                if not self.colide_parede(self.grid_x + dx, self.grid_y + dy):
                    opcoes.append((dx, dy))

            if random.random() < self.comportamento_aleatorio or not opcoes:
                prox_grid_x, prox_grid_y = self.grid_x + self.vel_x, self.grid_y + self.vel_y
                if self.colide_parede(prox_grid_x, prox_grid_y):
                    if opcoes:
                        self.vel_x, self.vel_y = random.choice(opcoes)
            else:
                dist_x = player.grid_x - self.grid_x
                dist_y = player.grid_y - self.grid_y
                
                movimentos_preferidos = []
                if abs(dist_x) > abs(dist_y):
                    if dist_x > 0 and (1, 0) in opcoes:
                        movimentos_preferidos.append((1, 0))
                    elif dist_x < 0 and (-1, 0) in opcoes:
                        movimentos_preferidos.append((-1, 0))
                    if dist_y > 0 and (0, 1) in opcoes:
                        movimentos_preferidos.append((0, 1))
                    elif dist_y < 0 and (0, -1) in opcoes:
                        movimentos_preferidos.append((0, -1))
                else:
                    if dist_y > 0 and (0, 1) in opcoes:
                        movimentos_preferidos.append((0, 1))
                    elif dist_y < 0 and (0, -1) in opcoes:
                        movimentos_preferidos.append((0, -1))
                    if dist_x > 0 and (1, 0) in opcoes:
                        movimentos_preferidos.append((1, 0))
                    elif dist_x < 0 and (-1, 0) in opcoes:
                        movimentos_preferidos.append((-1, 0))

                if movimentos_preferidos:
                    self.vel_x, self.vel_y = movimentos_preferidos[0]
                elif opcoes:
                    self.vel_x, self.vel_y = random.choice(opcoes)

        self.px += self.vel_x * self.velocidade
        self.py += self.vel_y * self.velocidade

    def colide_parede(self, x, y):
        return not (0 <= x < COLUNAS and 0 <= y < LINHAS_LABIRINTO and labirinto[y][x] != 1)

    def desenhar(self, surface):
        if not self.visivel:
            return
        centro = (self.px + TAM_CELULA//2, self.py + TAM_CELULA//2)
        
        # Tenta usar imagem do fantasma
        if hasattr(self, 'frames') and self.frames:
            # Para "Falta de Acesso", usa frames invisíveis quando não visível
            if self.nome == "Falta de Acesso" and hasattr(self, 'frames_invisivel') and not self.visivel:
                frames_para_usar = self.frames_invisivel
            else:
                frames_para_usar = self.frames
            
            if frames_para_usar and len(frames_para_usar) > 0:
                # Usa o frame atual (pode ser 0 ou 1)
                frame_index = 0  # Por enquanto usa sempre o primeiro frame
                img = frames_para_usar[frame_index]
                img_rect = img.get_rect(center=centro)
                surface.blit(img, img_rect)
                return
        
        # Fallback para desenho simples
        raio = TAM_CELULA//2 - 4
        pygame.draw.circle(surface, self.cor, centro, raio)
        olho_esq_x, olho_dir_x = centro[0] - raio/2.5, centro[0] + raio/2.5
        olho_y = centro[1] - raio/3
        pygame.draw.circle(surface, BRANCO, (olho_esq_x, olho_y), 4)
        pygame.draw.circle(surface, BRANCO, (olho_dir_x, olho_y), 4)
        pygame.draw.circle(surface, PRETO, (olho_esq_x, olho_y), 2)
        pygame.draw.circle(surface, PRETO, (olho_dir_x, olho_y), 2)


class CentroComunitario:
    def __init__(self, x, y, nome, cor, recurso_necessario):
        self.x = x
        self.y = y
        self.nome = nome
        self.cor = cor
        self.recurso_necessario = recurso_necessario
        self.nivel_atual = 0
        self.nivel_max = 5
        
        # Carregar imagens do centro
        self.carregar_imagens()
    
    def carregar_imagens(self):
        """Carrega as imagens do centro comunitário baseado no nome"""
        tamanho_centro = (48, 48)
        
        # Mapeia nomes para prefixos de arquivos
        prefixo_map = {
            "Escola": "escola",
            "Hospital": "hospital", 
            "Mercado": "mercado",
            "Moradia": "moradia"
        }
        
        prefixo = prefixo_map.get(self.nome, "escola")
        self.frames = carregar_centro(prefixo, tamanho_centro)
        
        if not self.frames:
            # Fallback para desenho simples
            self.frames = [self.criar_centro_simples()]
    
    def criar_centro_simples(self):
        """Cria um centro simples como fallback"""
        surface = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.cor, (2, 2, 44, 44), border_radius=4)
        return surface
    def desenhar(self, surface):
        px, py = self.x * TAM_CELULA, self.y * TAM_CELULA
        
        # Desenha a imagem do centro baseada no nível
        if hasattr(self, 'frames') and self.frames:
            nivel_index = min(self.nivel_atual // 2, len(self.frames) - 1)  # 0-2 baseado no nível
            img = self.frames[nivel_index]
            # Centraliza a imagem na célula
            img_rect = img.get_rect(center=(px + TAM_CELULA//2, py + TAM_CELULA//2))
            surface.blit(img, img_rect)
        else:
            # Fallback para desenho simples
            pygame.draw.rect(surface, self.cor, (px+2, py+2, TAM_CELULA-4, TAM_CELULA-4), border_radius=4)
        
        # Desenha barra de progresso
        largura_barra = TAM_CELULA - 8
        altura_barra = 5
        progresso = (self.nivel_atual / self.nivel_max) * largura_barra
        pygame.draw.rect(surface, PRETO, (px+4, py+TAM_CELULA-12, largura_barra, altura_barra))
        pygame.draw.rect(surface, AMARELO, (px+4, py+TAM_CELULA-12, progresso, altura_barra))
    def receber_entrega(self, inventario_jogador, player_stats=None):
        recursos_entregues = 0
        for item in inventario_jogador[:]:
            if item == self.recurso_necessario:
                inventario_jogador.remove(item)
                recursos_entregues += 1
                if player_stats:
                    player_stats["itens_entregues"] += 1
        
        if recursos_entregues > 0 and self.nivel_atual < self.nivel_max:
            self.nivel_atual += recursos_entregues
            if self.nivel_atual > self.nivel_max:
                self.nivel_atual = self.nivel_max
            return recursos_entregues * 20
        return 0

# --- Funções de Gerenciamento de Usuários e UI ---
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

# <-- NOVA FUNÇÃO para desenhar texto com quebra de linha automática
def desenhar_texto_quebra_linha(surface, texto, pos, largura_maxima, fonte, cor=BRANCO):
    palavras = texto.split(' ')
    linha_atual = ""
    linhas_renderizadas = []

    for palavra in palavras:
        palavra_teste = f" {palavra}"
        linha_teste = linha_atual + palavra_teste
        
        # Verifica se a linha atual está vazia para não adicionar espaço no início
        if linha_atual == "":
             linha_teste = palavra

        tamanho_linha_teste = fonte.size(linha_teste)

        if tamanho_linha_teste[0] <= largura_maxima:
            linha_atual = linha_teste
        else:
            linhas_renderizadas.append(linha_atual)
            linha_atual = palavra
    
    linhas_renderizadas.append(linha_atual)

    altura_total_texto = len(linhas_renderizadas) * fonte.get_linesize()
    y_inicial = pos[1] - (altura_total_texto / 2)

    for i, linha in enumerate(linhas_renderizadas):
        render_linha = fonte.render(linha, True, cor)
        rect_linha = render_linha.get_rect(center=(pos[0], y_inicial + i * fonte.get_linesize()))
        surface.blit(render_linha, rect_linha)
# <-- FIM DA NOVA FUNÇÃO

def desenhar_tela_inicial(surface, rects):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo = pygame.font.SysFont(None, 50); fonte_botao = pygame.font.SysFont(None, 40)
    desenhar_texto(surface, "Pac-Man - A Missão Comunitária", (LARGURA/2, 150), fonte_titulo, AMARELO)
    pygame.draw.rect(surface, COR_BOTAO, rects['logar']); desenhar_texto(surface, "Logar", rects['logar'].center, fonte_botao)
    pygame.draw.rect(surface, COR_BOTAO, rects['cadastrar']); desenhar_texto(surface, "Cadastrar", rects['cadastrar'].center, fonte_botao)

def desenhar_tela_formulario(surface, titulo, nick, senha, campo_ativo, rects, msg_erro=""):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo=pygame.font.SysFont(None,50); fonte_label=pygame.font.SysFont(None,36)
    fonte_input=pygame.font.SysFont(None,32); fonte_erro=pygame.font.SysFont(None,28)
    desenhar_texto(surface, titulo, (LARGURA/2, 100), fonte_titulo, AMARELO)
    label_nick = fonte_label.render("Nick:", True, BRANCO); surface.blit(label_nick, (rects['nick'].x, rects['nick'].y-30))
    cor_nick = COR_INPUT_ATIVO if campo_ativo=='nick' else COR_INPUT_INATIVO; pygame.draw.rect(surface,cor_nick,rects['nick'],2)
    texto_nick = fonte_input.render(nick,True,BRANCO); surface.blit(texto_nick, (rects['nick'].x+10, rects['nick'].y+10))
    label_senha=fonte_label.render("Senha:",True,BRANCO); surface.blit(label_senha, (rects['senha'].x, rects['senha'].y-30))
    cor_senha=COR_INPUT_ATIVO if campo_ativo=='senha' else COR_INPUT_INATIVO; pygame.draw.rect(surface,cor_senha,rects['senha'],2)
    texto_senha=fonte_input.render('*'*len(senha),True,BRANCO); surface.blit(texto_senha,(rects['senha'].x+10,rects['senha'].y+10))
    pygame.draw.rect(surface,COR_BOTAO,rects['confirmar']); desenhar_texto(surface,titulo,rects['confirmar'].center,fonte_label)
    pygame.draw.rect(surface,COR_BOTAO_VOLTAR,rects['voltar']); desenhar_texto(surface,"Voltar",rects['voltar'].center,fonte_label)
    if msg_erro: desenhar_texto(surface, msg_erro, (LARGURA/2, 530), fonte_erro, VERMELHO)

def desenhar_tela_dificuldade(surface, rects):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo = pygame.font.SysFont(None, 50)
    fonte_botao = pygame.font.SysFont(None, 40)
    desenhar_texto(surface, "Select Difficulty", (LARGURA / 2, 150), fonte_titulo, AMARELO)
    pygame.draw.rect(surface, (0, 150, 0), rects['easy'])
    desenhar_texto(surface, "Easy", rects['easy'].center, fonte_botao)
    pygame.draw.rect(surface, (200, 150, 0), rects['default'])
    desenhar_texto(surface, "Default", rects['default'].center, fonte_botao)
    pygame.draw.rect(surface, (150, 0, 0), rects['hard'])
    desenhar_texto(surface, "Hard", rects['hard'].center, fonte_botao)
    pygame.draw.rect(surface, COR_OURO, rects['rewards'])
    desenhar_texto(surface, "Recompensas", rects['rewards'].center, fonte_botao)
    pygame.draw.rect(surface, COR_REWARD, rects['ranking'])
    desenhar_texto(surface, "Ranking", rects['ranking'].center, fonte_botao)

def desenhar_tela_rewards(surface, rewards_system, username, rects):
    """Desenha a tela do sistema de recompensas"""
    surface.fill(COR_FUNDO_UI)
    fonte_titulo = pygame.font.SysFont(None, 50)
    fonte_media = pygame.font.SysFont(None, 36)
    fonte_pequena = pygame.font.SysFont(None, 28)
    
    user_data = rewards_system.obter_usuario_rewards(username)
    
    # Título
    desenhar_texto(surface, "Sistema de Recompensas", (LARGURA/2, 50), fonte_titulo, COR_OURO)
    
    # Informações do usuário
    desenhar_texto(surface, f"Usuário: {username}", (LARGURA/2, 100), fonte_media, BRANCO)
    desenhar_texto(surface, f"Pontos Totais: {user_data['pontos_totais']}", (LARGURA/2, 130), fonte_media, COR_OURO)
    desenhar_texto(surface, f"Nível: {user_data['nivel']}", (LARGURA/2, 160), fonte_media, COR_REWARD)
    
    # Tarefas diárias
    desenhar_texto(surface, "Tarefas Diárias", (LARGURA/2, 200), fonte_media, COR_OURO)
    y_offset = 230
    tarefas = user_data.get("tarefas_diarias", rewards_system.daily_tasks)
    
    for task_id, task_data in tarefas.items():
        cor = COR_OURO if task_data.get("concluida", False) else CINZA
        status = "✓" if task_data.get("concluida", False) else "○"
        texto = f"{status} {task_data['descricao']} - {task_data['pontos']} pts"
        desenhar_texto(surface, texto, (50, y_offset), fonte_pequena, cor)
        y_offset += 25
    
    # Conquistas
    desenhar_texto(surface, "Conquistas", (LARGURA/2, y_offset + 20), fonte_media, COR_OURO)
    y_offset += 50
    conquistas = user_data.get("conquistas", {})
    
    for achievement_id, achievement_data in rewards_system.achievements.items():
        user_achievement = conquistas.get(achievement_id, {"desbloqueada": False})
        if user_achievement.get("desbloqueada", False):
            cor = COR_OURO
            status = "🏆"
        else:
            cor = CINZA
            status = "🔒"
        
        texto = f"{status} {achievement_data['nome']} - {achievement_data['pontos']} pts"
        desenhar_texto(surface, texto, (50, y_offset), fonte_pequena, cor)
        y_offset += 25
    
    # Botões
    pygame.draw.rect(surface, COR_BOTAO, rects['voltar_rewards'])
    desenhar_texto(surface, "Voltar", rects['voltar_rewards'].center, fonte_media)

def desenhar_tela_ranking(surface, rewards_system, rects):
    """Desenha a tela de ranking"""
    surface.fill(COR_FUNDO_UI)
    fonte_titulo = pygame.font.SysFont(None, 50)
    fonte_media = pygame.font.SysFont(None, 36)
    fonte_pequena = pygame.font.SysFont(None, 28)
    
    desenhar_texto(surface, "Ranking de Jogadores", (LARGURA/2, 50), fonte_titulo, COR_OURO)
    
    ranking = rewards_system.obter_ranking(10)
    y_offset = 100
    
    for i, (username, pontos) in enumerate(ranking, 1):
        if i == 1:
            cor = COR_OURO
            medalha = "🥇"
        elif i == 2:
            cor = COR_PRATA
            medalha = "🥈"
        elif i == 3:
            cor = COR_BRONZE
            medalha = "🥉"
        else:
            cor = BRANCO
            medalha = f"{i}°"
        
        texto = f"{medalha} {username}: {pontos} pontos"
        desenhar_texto(surface, texto, (LARGURA/2, y_offset), fonte_pequena, cor)
        y_offset += 30
    
    # Botões
    pygame.draw.rect(surface, COR_BOTAO, rects['voltar_ranking'])
    desenhar_texto(surface, "Voltar", rects['voltar_ranking'].center, fonte_media)

MENSAGENS_GAME_OVER = {
    "Desemprego": "O Desemprego paralisou seus planos e te deixou sem recursos para continuar a missão.",
    "Desigualdade": "A Desigualdade bloqueou seu caminho para o progresso e o desenvolvimento da comunidade.",
    "Falta de Acesso": "A Falta de Acesso a oportunidades essenciais te deixou para trás e sem chances de vencer.",
    "Crise Econômica": "A Crise Econômica consumiu todos os seus esforços e os investimentos feitos na comunidade."
}

def desenhar_tela_game_over(surface, rects, nome_inimigo):
    surface.fill(COR_FUNDO_UI)
    fonte_grande = pygame.font.SysFont(None, 60)
    fonte_media = pygame.font.SysFont(None, 40)
    fonte_mensagem = pygame.font.SysFont(None, 36)

    mensagem = MENSAGENS_GAME_OVER.get(nome_inimigo, f"Você foi superado por: {nome_inimigo}")

    desenhar_texto(surface, "A Missão Falhou", (LARGURA/2, 120), fonte_grande, AMARELO)
    
    # <-- ALTERAÇÃO: Chamada da nova função de texto com quebra de linha
    largura_max_texto = LARGURA - 80 # Define uma margem de 40px de cada lado
    desenhar_texto_quebra_linha(surface, mensagem, (LARGURA/2, 220), largura_max_texto, fonte_mensagem, VERMELHO_CRISE)
    
    desenhar_texto(surface, "Deseja tentar novamente?", (LARGURA/2, 320), fonte_media)
    pygame.draw.rect(surface, VERDE_CONTINUAR, rects['sim']); desenhar_texto(surface, "Sim", rects['sim'].center, fonte_media)
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['nao']); desenhar_texto(surface, "Não", rects['nao'].center, fonte_media)
# <-- FIM DA ALTERAÇÃO

# --- Funções do Jogo ---
def desenhar_labirinto(surface):
    for y,linha in enumerate(labirinto):
        for x,celula in enumerate(linha):
            if celula == 1: pygame.draw.rect(surface,AZUL_PAREDE,(x*TAM_CELULA, y*TAM_CELULA,TAM_CELULA,TAM_CELULA))

def desenhar_recursos(surface, recursos):
    # Carrega imagens dos itens
    itens_imagens = {
        'Moeda': carregar_item('moeda', (24, 24)),
        'Alimento': carregar_item('alimento', (24, 24)),
        'Livro': carregar_item('livro', (24, 24)),
        'Tijolo': carregar_item('tijolos', (24, 24))
    }
    
    for r in recursos:
        px, py = r['x']*TAM_CELULA, r['y']*TAM_CELULA
        centro = (px + TAM_CELULA//2, py + TAM_CELULA//2)
        
        # Tenta usar imagem do item
        if r['tipo'] in itens_imagens:
            img = itens_imagens[r['tipo']]
            img_rect = img.get_rect(center=centro)
            surface.blit(img, img_rect)
        else:
            # Fallback para desenho simples
            mapa = {'Moeda':(COR_MOEDA,'c'),'Alimento':(COR_ALIMENTO,'q'),'Livro':(COR_LIVRO,'r'),'Tijolo':(COR_TIJOLO,'t')}
            info = mapa[r['tipo']]
            if info[1]=='c': pygame.draw.circle(surface,info[0],centro,6)
            elif info[1]=='q': pygame.draw.rect(surface,info[0],(px+10,py+10,10,10))
            elif info[1]=='r': pygame.draw.rect(surface,info[0],(px+8,py+12,14,8))
            elif info[1]=='t': pygame.draw.rect(surface,info[0],(px+7,py+10,16,10))

def desenhar_hud(surface, jogador, centros, pontos):
    base_y = LINHAS_LABIRINTO * TAM_CELULA
    pygame.draw.rect(surface, COR_FUNDO_UI, (0, base_y, LARGURA, ALTURA - base_y))
    fonte = pygame.font.SysFont(None, 28)
    fonte_instrucao = pygame.font.SysFont(None, 24)
    texto_inv = fonte.render("Inventário:", True, BRANCO); surface.blit(texto_inv, (10, base_y+10))
    mapa_cor={'Moeda':COR_MOEDA,'Alimento':COR_ALIMENTO,'Livro':COR_LIVRO,'Tijolo':COR_TIJOLO}
    for i,item in enumerate(jogador.inventario): pygame.draw.rect(surface,mapa_cor[item],(120+i*25,base_y+12,20,20))
    for i in range(jogador.capacidade_inventario): pygame.draw.rect(surface,BRANCO,(120+i*25,base_y+12,20,20),1)
    texto_c=fonte.render("Desenvolvimento Comunitário:",True,BRANCO); surface.blit(texto_c,(10,base_y+50))
    for i,centro in enumerate(centros):
        texto_c=fonte.render(f"{centro.nome}:",True,centro.cor); surface.blit(texto_c,(30,base_y+80+i*25))
        prog=(centro.nivel_atual/centro.nivel_max); pygame.draw.rect(surface,PRETO,(130,base_y+82+i*25,100,15))
        pygame.draw.rect(surface,AMARELO,(130,base_y+82+i*25,100*prog,15))
    texto_p=fonte.render(f"Pontos: {pontos}",True,BRANCO); surface.blit(texto_p,(LARGURA-150,base_y+10))
    texto_instrucao = fonte_instrucao.render("Pressione [D] para Descartar o último item", True, CINZA)
    surface.blit(texto_instrucao, (LARGURA - 260, ALTURA - 25))


# --- Loop Principal e Lógica de Estados ---
def main():
    rodando = True
    estado_jogo = 'tela_inicial'
    nick_usuario, senha_usuario, campo_ativo, mensagem_erro = "", "", 'nick', ""
    usuarios = carregar_usuarios()
    dificuldade_selecionada = "Default"
    
    # Inicializar sistema de recompensas
    rewards_system = RewardsSystem()

    rects_inicial = {'logar':pygame.Rect(LARGURA/2-125,250,250,60),'cadastrar':pygame.Rect(LARGURA/2-125,350,250,60)}
    rects_form = {'nick':pygame.Rect(LARGURA/2-150,200,300,40),'senha':pygame.Rect(LARGURA/2-150,300,300,40),
                  'confirmar':pygame.Rect(LARGURA/2-125,400,250,50),'voltar':pygame.Rect(LARGURA/2-75,470,150,40)}
    rects_game_over = {'sim':pygame.Rect(LARGURA/2-150,370,100,50),'nao':pygame.Rect(LARGURA/2+50,370,100,50)}
    
    rects_dificuldade = {'easy': pygame.Rect(LARGURA/2 - 125, 220, 250, 60),
                         'default': pygame.Rect(LARGURA/2 - 125, 300, 250, 60),
                         'hard': pygame.Rect(LARGURA/2 - 125, 380, 250, 60),
                         'rewards': pygame.Rect(LARGURA/2 - 125, 460, 250, 60),
                         'ranking': pygame.Rect(LARGURA/2 - 125, 540, 250, 60)}
    
    rects_rewards = {'voltar_rewards': pygame.Rect(LARGURA/2 - 75, 650, 150, 40)}
    rects_ranking = {'voltar_ranking': pygame.Rect(LARGURA/2 - 75, 650, 150, 40)}

    player, inimigos, centros, recursos, pontos = None, [], [], [], 0
    inimigo_colisor = None
    posicoes_iniciais_inimigos = [(18,1),(1,16),(18,16),(9,8)]
    tempo_inicio_partida = 0
    
    def reiniciar_posicoes(dificuldade):
        nonlocal player, inimigos
        if player:
            player.reiniciar()
            
        nomes=["Desemprego","Desigualdade","Falta de Acesso","Crise Econômica"]
        cores=[CINZA,ROXO,CINZA_ESCURO,VERMELHO_CRISE]
        inimigos.clear()
        for i,pos in enumerate(posicoes_iniciais_inimigos):
            inimigos.append(Inimigo(pos[0], pos[1], cores[i], nomes[i], dificuldade))
    
    def inicializar_novo_jogo(dificuldade):
        nonlocal pontos, centros, recursos, player, tempo_inicio_partida
        pontos = 0
        tempo_inicio_partida = datetime.datetime.now()
        player = Player(1, 1)
        centros = [CentroComunitario(1,9,"Moradia",COR_MORADIA,"Tijolo"), CentroComunitario(18,9,"Mercado",COR_MERCADO,"Alimento"),
                   CentroComunitario(9,1,"Escola",COR_ESCOLA,"Livro"), CentroComunitario(9,16,"Hospital",COR_HOSPITAL,"Moeda")]
        recursos = []
        tipos_recursos = ['Moeda','Alimento','Livro','Tijolo']
        pos_ocupadas = [(c.x, c.y) for c in centros] + [(player.grid_x, player.grid_y)]
        
        for tipo in tipos_recursos:
            for _ in range(4):
                pos = random.choice([p for p in posicoes_livres if p not in pos_ocupadas])
                recursos.append({'x':pos[0], 'y':pos[1], 'tipo':tipo})
                pos_ocupadas.append(pos)
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
                            if nick_usuario in usuarios and usuarios[nick_usuario] == senha_usuario:
                                estado_jogo = 'tela_dificuldade'
                            else: mensagem_erro = "Nick ou senha inválidos."
                        else: 
                            if not nick_usuario or not senha_usuario: mensagem_erro="Os campos não podem estar vazios."
                            elif nick_usuario in usuarios: mensagem_erro="Este nick já está em uso."
                            else:
                                usuarios[nick_usuario]=senha_usuario; salvar_usuarios(usuarios)
                                estado_jogo = 'tela_dificuldade'
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN or e.key == pygame.K_KP_ENTER:
                        if estado_jogo == 'tela_login':
                            if nick_usuario in usuarios and usuarios[nick_usuario] == senha_usuario:
                                estado_jogo = 'tela_dificuldade'
                            else: mensagem_erro = "Nick ou senha inválidos."
                        else: 
                            if not nick_usuario or not senha_usuario: mensagem_erro="Os campos não podem estar vazios."
                            elif nick_usuario in usuarios: mensagem_erro="Este nick já está em uso."
                            else:
                                usuarios[nick_usuario]=senha_usuario; salvar_usuarios(usuarios)
                                estado_jogo = 'tela_dificuldade'
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
                    if rects_dificuldade['easy'].collidepoint(e.pos):
                        dificuldade_selecionada = "Easy"
                        inicializar_novo_jogo(dificuldade_selecionada)
                        estado_jogo = 'jogo'
                    elif rects_dificuldade['default'].collidepoint(e.pos):
                        dificuldade_selecionada = "Default"
                        inicializar_novo_jogo(dificuldade_selecionada)
                        estado_jogo = 'jogo'
                    elif rects_dificuldade['hard'].collidepoint(e.pos):
                        dificuldade_selecionada = "Hard"
                        inicializar_novo_jogo(dificuldade_selecionada)
                        estado_jogo = 'jogo'
                    elif rects_dificuldade['rewards'].collidepoint(e.pos):
                        estado_jogo = 'tela_rewards'
                    elif rects_dificuldade['ranking'].collidepoint(e.pos):
                        estado_jogo = 'tela_ranking'
            desenhar_tela_dificuldade(tela, rects_dificuldade)
        
        elif estado_jogo == 'tela_rewards':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if rects_rewards['voltar_rewards'].collidepoint(e.pos):
                        estado_jogo = 'tela_dificuldade'
            desenhar_tela_rewards(tela, rewards_system, nick_usuario, rects_rewards)
        
        elif estado_jogo == 'tela_ranking':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if rects_ranking['voltar_ranking'].collidepoint(e.pos):
                        estado_jogo = 'tela_dificuldade'
            desenhar_tela_ranking(tela, rewards_system, rects_ranking)

        elif estado_jogo == 'tela_game_over':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if rects_game_over['sim'].collidepoint(e.pos):
                        reiniciar_posicoes(dificuldade_selecionada)
                        estado_jogo = 'jogo'
                    elif rects_game_over['nao'].collidepoint(e.pos):
                        # Processar estatísticas finais e adicionar pontos
                        if player:
                            tempo_decorrido = (datetime.datetime.now() - tempo_inicio_partida).total_seconds()
                            player.stats["tempo_jogado"] = tempo_decorrido
                            player.stats["tempo_sobrevivencia"] = tempo_decorrido
                            
                            # Adicionar pontos baseados na performance
                            pontos_base = pontos
                            rewards_system.adicionar_pontos(nick_usuario, pontos_base, "partida")
                            
                            # Verificar tarefas diárias e conquistas
                            rewards_system.verificar_tarefas_diarias(nick_usuario, player.stats)
                            rewards_system.verificar_conquistas(nick_usuario, player.stats)
                        
                        estado_jogo = 'tela_inicial'
            desenhar_tela_game_over(tela, rects_game_over, inimigo_colisor.nome)

        elif estado_jogo == 'jogo':
            for e in eventos:
                if e.type == pygame.KEYDOWN:
                    if e.key==pygame.K_LEFT: player.dir_x,player.dir_y=-1,0
                    elif e.key==pygame.K_RIGHT: player.dir_x,player.dir_y=1,0
                    elif e.key==pygame.K_UP: player.dir_x,player.dir_y=0,-1
                    elif e.key==pygame.K_DOWN: player.dir_x,player.dir_y=0,1
                    elif e.key == pygame.K_d:
                        player.descartar_item()
            
            # Atualiza animações
            dt = clock.get_time()
            player.atualizar_animacao(dt)
            
            player.mover(); player.coletar(recursos, centros)
            for inimigo in inimigos:
                inimigo.mover(player) 
                if inimigo.grid_x==player.grid_x and inimigo.grid_y==player.grid_y and inimigo.visivel:
                    inimigo_colisor = inimigo; estado_jogo = 'tela_game_over'
            for centro in centros:
                if player.grid_x==centro.x and player.grid_y==centro.y:
                    pontos += centro.receber_entrega(player.inventario, player.stats)
            
            tela.fill(PRETO); desenhar_labirinto(tela); desenhar_recursos(tela, recursos)
            for centro in centros: centro.desenhar(tela)
            player.desenhar(tela)
            for inimigo in inimigos: inimigo.desenhar(tela)
            desenhar_hud(tela, player, centros, pontos)

            if all(c.nivel_atual >= c.nivel_max for c in centros):
                # Vitória! Processar recompensas
                tempo_decorrido = (datetime.datetime.now() - tempo_inicio_partida).total_seconds()
                player.stats["tempo_jogado"] = tempo_decorrido
                player.stats["vitorias"] = 1
                player.stats["centros_completos"] = len([c for c in centros if c.nivel_atual >= c.nivel_max])
                
                # Pontos extras por vitória
                pontos_vitoria = pontos + 500
                rewards_system.adicionar_pontos(nick_usuario, pontos_vitoria, "vitoria")
                
                # Verificar conquistas
                rewards_system.verificar_conquistas(nick_usuario, player.stats)
                
                fonte_fim=pygame.font.SysFont(None,36); tela.fill(PRETO)
                desenhar_texto(tela,"Parabéns! A comunidade prosperou!",(LARGURA/2,ALTURA/2-20),fonte_fim,(120,255,120))
                desenhar_texto(tela,f"Pontuação Final: {pontos}",(LARGURA/2,ALTURA/2+20),fonte_fim)
                desenhar_texto(tela,f"Pontos de Recompensa: +500",(LARGURA/2,ALTURA/2+50),fonte_fim,COR_OURO)
                pygame.display.flip(); pygame.time.wait(4000)
                rodando = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()