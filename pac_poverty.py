import pygame
import sys
import random
import math

# --- Inicialização do Pygame ---
pygame.init()

# --- Constantes do Jogo ---
LARGURA, ALTURA = 600, 720  # Aumentei a altura para caber o novo HUD
TAM_CELULA = 30
COLUNAS = LARGURA // TAM_CELULA
LINHAS_LABIRINTO = 18
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pac-Man - A Missão Comunitária")
clock = pygame.time.Clock()
FPS = 10

# --- Cores ---
PRETO = (0, 0, 0)
AZUL_PAREDE = (0, 0, 139)
AMARELO = (255, 223, 0)
BRANCO = (255, 255, 255)
CINZA = (105, 105, 105) # Desemprego
ROXO = (128, 0, 128)   # Desigualdade
CINZA_ESCURO = (40, 40, 40) # Falta de Acesso
VERMELHO_CRISE = (178, 34, 34) # Crise Econômica

# Cores dos Recursos
COR_MOEDA = (255, 215, 0)
COR_ALIMENTO = (152, 251, 152)
COR_LIVRO = (135, 206, 250)
COR_TIJOLO = (176, 96, 52)

# Cores dos Centros Comunitários
COR_ESCOLA = (65, 105, 225)
COR_HOSPITAL = (220, 20, 60)
COR_MERCADO = (34, 139, 34)
COR_MORADIA = (160, 82, 45)

# --- Layout do Labirinto (0: caminho, 1: parede) ---
labirinto = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,0,1,1,0,1,1,1,0,1,1,0,1],
    [1,0,1,1,0,1,0,0,0,0,0,0,0,0,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,1,1,0,1,1,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,0,1,0,1,0,0,1,0,1,1,0,0,1],
    [1,0,0,1,0,1,1,0,1,0,1,0,1,1,0,1,0,0,0,1],
    [1,1,0,1,0,1,0,0,0,0,0,0,0,1,0,1,0,1,1,1],
    [1,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,0,0,1],
    [1,0,0,0,0,1,0,1,1,1,1,1,0,1,0,0,0,0,0,1],
    [1,1,1,0,1,1,0,1,0,0,0,1,0,1,1,0,1,1,1,1],
    [1,0,0,0,0,0,0,1,0,1,0,1,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,0,1],
    [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# --- Classes do Jogo ---

class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.dir_x, self.dir_y = 0, 0
        self.vel_x, self.vel_y = 0, 0
        self.boca_frame = 0
        self.boca_frames_total = 4
        self.inventario = []
        self.capacidade_inventario = 5

    def mover(self):
        # Tenta aplicar a direção desejada à velocidade
        if self.dir_x != 0 or self.dir_y != 0:
            prox_x, prox_y = self.x + self.dir_x, self.y + self.dir_y
            if self.pode_ir(prox_x, prox_y):
                self.vel_x, self.vel_y = self.dir_x, self.dir_y

        # Move o jogador com base na velocidade atual
        prox_x, prox_y = self.x + self.vel_x, self.y + self.vel_y
        if self.pode_ir(prox_x, prox_y):
            self.x, self.y = prox_x, prox_y
        else:
            # Para se bater na parede
            self.vel_x, self.vel_y = 0, 0
    
    def pode_ir(self, x, y):
        if 0 <= x < COLUNAS and 0 <= y < LINHAS_LABIRINTO:
            return labirinto[y][x] != 1
        return False

    def coletar(self, recursos):
        if len(self.inventario) < self.capacidade_inventario:
            for recurso in recursos[:]: # Itera sobre uma cópia
                if recurso['x'] == self.x and recurso['y'] == self.y:
                    self.inventario.append(recurso['tipo'])
                    recursos.remove(recurso)
                    # print(f"Coletou {recurso['tipo']}. Inventário: {self.inventario}")
                    break
    
    def desenhar(self, surface):
        centro = (self.x * TAM_CELULA + TAM_CELULA//2, self.y * TAM_CELULA + TAM_CELULA//2)
        raio = TAM_CELULA//2 - 3
        
        # Lógica da boca
        direcao_atual = self.vel_x if self.vel_x != 0 else self.dir_x
        if direcao_atual == -1: angulo_central = math.pi
        elif direcao_atual == 1: angulo_central = 0
        elif self.vel_y == -1 or self.dir_y == -1: angulo_central = math.pi/2
        elif self.vel_y == 1 or self.dir_y == 1: angulo_central = -math.pi/2
        else: angulo_central = 0

        max_abertura = math.radians(45)
        min_abertura = math.radians(5)
        t = abs(self.boca_frames_total - 2 * (self.boca_frame % self.boca_frames_total)) / self.boca_frames_total
        abertura = min_abertura + (max_abertura - min_abertura) * t
        
        inicio = angulo_central + abertura
        fim = angulo_central - abertura
        
        pygame.draw.circle(surface, AMARELO, centro, raio)
        
        # Desenha a boca como um polígono preto
        if self.vel_x != 0 or self.vel_y != 0:
            p1 = centro
            p2 = (centro[0] + math.cos(inicio) * raio, centro[1] - math.sin(inicio) * raio)
            p3 = (centro[0] + math.cos(fim) * raio, centro[1] - math.sin(fim) * raio)
            pygame.draw.polygon(surface, PRETO, [p1, p2, p3])
        
        self.boca_frame += 1

class Inimigo:
    def __init__(self, x, y, cor, nome):
        self.x, self.y = x, y
        self.cor = cor
        self.nome = nome
        self.vel = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        # Habilidade especial: Invisibilidade
        self.invisivel = (nome == "Falta de Acesso")
        self.visivel = True
        self.timer_invisibilidade = 0
        self.tempo_para_trocar = random.randint(30, 60) # frames

    def mover(self):
        if self.invisivel:
            self.timer_invisibilidade += 1
            if self.timer_invisibilidade > self.tempo_para_trocar:
                self.visivel = not self.visivel
                self.timer_invisibilidade = 0
                self.tempo_para_trocar = random.randint(20, 50)


        prox_x, prox_y = self.x + self.vel[0], self.y + self.vel[1]
        
        if self.pode_ir(prox_x, prox_y):
            self.x, self.y = prox_x, prox_y
        else:
            opcoes = []
            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                # Não voltar pelo mesmo caminho, a menos que seja a única opção
                if (dx, dy) != (-self.vel[0], -self.vel[1]):
                    if self.pode_ir(self.x + dx, self.y + dy):
                        opcoes.append((dx, dy))
            
            if not opcoes: # Se estiver num beco sem saída
                opcoes.append((-self.vel[0], -self.vel[1]))

            self.vel = random.choice(opcoes)

    def pode_ir(self, x, y):
        if 0 <= x < COLUNAS and 0 <= y < LINHAS_LABIRINTO:
            return labirinto[y][x] != 1
        return False
    
    def desenhar(self, surface):
        if not self.visivel:
            return
        centro = (self.x * TAM_CELULA + TAM_CELULA//2, self.y * TAM_CELULA + TAM_CELULA//2)
        raio = TAM_CELULA//2 - 4
        pygame.draw.circle(surface, self.cor, centro, raio)
        # Olhos
        olho_esq_x = centro[0] - raio/2.5
        olho_dir_x = centro[0] + raio/2.5
        olho_y = centro[1] - raio/3
        pygame.draw.circle(surface, BRANCO, (olho_esq_x, olho_y), 4)
        pygame.draw.circle(surface, BRANCO, (olho_dir_x, olho_y), 4)
        pygame.draw.circle(surface, PRETO, (olho_esq_x, olho_y), 2)
        pygame.draw.circle(surface, PRETO, (olho_dir_x, olho_y), 2)

class CentroComunitario:
    def __init__(self, x, y, nome, cor, recurso_necessario):
        self.x, self.y = x, y
        self.nome = nome
        self.cor = cor
        self.recurso_necessario = recurso_necessario
        self.nivel_atual = 0
        self.nivel_max = 5
        self.entregas_para_upar = 3

    def desenhar(self, surface):
        px, py = self.x * TAM_CELULA, self.y * TAM_CELULA
        # Base
        pygame.draw.rect(surface, self.cor, (px + 2, py + 2, TAM_CELULA - 4, TAM_CELULA - 4), border_radius=4)
        # Barra de progresso
        largura_barra = TAM_CELULA - 8
        altura_barra = 5
        progresso = (self.nivel_atual / self.nivel_max) * largura_barra
        pygame.draw.rect(surface, PRETO, (px + 4, py + TAM_CELULA - 12, largura_barra, altura_barra))
        pygame.draw.rect(surface, AMARELO, (px + 4, py + TAM_CELULA - 12, progresso, altura_barra))

    def receber_entrega(self, inventario_jogador):
        recursos_entregues = 0
        for item in inventario_jogador[:]:
            if item == self.recurso_necessario:
                inventario_jogador.remove(item)
                recursos_entregues += 1
        
        if recursos_entregues > 0 and self.nivel_atual < self.nivel_max:
            self.nivel_atual += recursos_entregues
            if self.nivel_atual > self.nivel_max:
                self.nivel_atual = self.nivel_max
            return recursos_entregues * 20 # Pontos por entrega
        return 0

# --- Funções Auxiliares ---

def desenhar_labirinto(surface):
    for y in range(LINHAS_LABIRINTO):
        for x in range(COLUNAS):
            if labirinto[y][x] == 1:
                pygame.draw.rect(surface, AZUL_PAREDE, (x * TAM_CELULA, y * TAM_CELULA, TAM_CELULA, TAM_CELULA))

def desenhar_recursos(surface, recursos):
    recurso_map = {
        'Moeda': {'cor': COR_MOEDA, 'forma': 'circulo'},
        'Alimento': {'cor': COR_ALIMENTO, 'forma': 'quadrado'},
        'Livro': {'cor': COR_LIVRO, 'forma': 'retangulo'},
        'Tijolo': {'cor': COR_TIJOLO, 'forma': 'tijolo'}
    }
    for r in recursos:
        info = recurso_map[r['tipo']]
        px, py = r['x'] * TAM_CELULA, r['y'] * TAM_CELULA
        centro = (px + TAM_CELULA//2, py + TAM_CELULA//2)
        if info['forma'] == 'circulo':
            pygame.draw.circle(surface, info['cor'], centro, 6)
        elif info['forma'] == 'quadrado':
            pygame.draw.rect(surface, info['cor'], (px + 10, py + 10, 10, 10))
        elif info['forma'] == 'retangulo':
            pygame.draw.rect(surface, info['cor'], (px + 8, py + 12, 14, 8))
        elif info['forma'] == 'tijolo':
            pygame.draw.rect(surface, info['cor'], (px + 7, py + 10, 16, 10))

def desenhar_hud(surface, jogador, centros):
    base_y = LINHAS_LABIRINTO * TAM_CELULA
    pygame.draw.rect(surface, (10,10,30), (0, base_y, LARGURA, ALTURA - base_y))

    fonte = pygame.font.SysFont(None, 28)
    # Inventário
    texto_inv = fonte.render("Inventário:", True, BRANCO)
    surface.blit(texto_inv, (10, base_y + 10))
    for i, item in enumerate(jogador.inventario):
        cor_item = {
            'Moeda': COR_MOEDA, 'Alimento': COR_ALIMENTO, 
            'Livro': COR_LIVRO, 'Tijolo': COR_TIJOLO
        }[item]
        pygame.draw.rect(surface, cor_item, (120 + i * 25, base_y + 12, 20, 20))
    for i in range(jogador.capacidade_inventario):
        pygame.draw.rect(surface, BRANCO, (120 + i * 25, base_y + 12, 20, 20), 1)

    # Status dos Centros
    texto_centros = fonte.render("Desenvolvimento Comunitário:", True, BRANCO)
    surface.blit(texto_centros, (10, base_y + 50))
    for i, centro in enumerate(centros):
        texto_centro = fonte.render(f"{centro.nome}:", True, centro.cor)
        surface.blit(texto_centro, (30, base_y + 80 + i * 25))
        # Barra de progresso
        progresso = (centro.nivel_atual / centro.nivel_max)
        pygame.draw.rect(surface, PRETO, (130, base_y + 82 + i * 25, 100, 15))
        pygame.draw.rect(surface, AMARELO, (130, base_y + 82 + i * 25, 100 * progresso, 15))

    # Pontos
    texto_pontos = fonte.render(f"Pontos: {pontos}", True, BRANCO)
    surface.blit(texto_pontos, (LARGURA - 150, base_y + 10))

def verificar_vitoria(centros):
    return all(c.nivel_atual >= c.nivel_max for c in centros)

# --- Configuração Inicial do Jogo ---
player = Player(1, 1)
pontos = 0

inimigos = [
    Inimigo(18, 1, CINZA, "Desemprego"),
    Inimigo(1, 16, ROXO, "Desigualdade"),
    Inimigo(18, 16, CINZA_ESCURO, "Falta de Acesso"),
    Inimigo(9, 8, VERMELHO_CRISE, "Crise Econômica")
]

centros_comunitarios = [
    CentroComunitario(1, 9, "Moradia", COR_MORADIA, "Tijolo"),
    CentroComunitario(18, 9, "Mercado", COR_MERCADO, "Alimento"),
    CentroComunitario(9, 1, "Escola", COR_ESCOLA, "Livro"),
    CentroComunitario(9, 16, "Hospital", COR_HOSPITAL, "Moeda")
]

recursos = []
tipos_recursos = ['Moeda', 'Alimento', 'Livro', 'Tijolo']
for y in range(LINHAS_LABIRINTO):
    for x in range(COLUNAS):
        if labirinto[y][x] == 0 and random.random() < 0.4: # 40% de chance de ter um recurso
            # Evita gerar recursos em cima do jogador e dos centros
            if (x,y) != (1,1) and not any(c.x == x and c.y == y for c in centros_comunitarios):
                recursos.append({'x': x, 'y': y, 'tipo': random.choice(tipos_recursos)})


# --- Loop Principal do Jogo ---
rodando = True
while rodando:
    # --- Eventos ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_LEFT:  player.dir_x, player.dir_y = -1, 0
            elif evento.key == pygame.K_RIGHT: player.dir_x, player.dir_y = 1, 0
            elif evento.key == pygame.K_UP:    player.dir_x, player.dir_y = 0, -1
            elif evento.key == pygame.K_DOWN:  player.dir_x, player.dir_y = 0, 1

    # --- Lógica de Atualização ---
    player.mover()
    player.coletar(recursos)
    
    for inimigo in inimigos:
        inimigo.mover()
        # Colisão com o jogador
        if inimigo.x == player.x and inimigo.y == player.y and inimigo.visivel:
            fonte_fim = pygame.font.SysFont(None, 40)
            tela.fill(PRETO)
            texto_derrota = fonte_fim.render(f"Você foi superado por: {inimigo.nome}", True, (255, 80, 80))
            texto_pontos = fonte_fim.render(f"Pontos: {pontos}", True, BRANCO)
            tela.blit(texto_derrota, (LARGURA/2 - texto_derrota.get_width()/2, ALTURA/2 - 40))
            tela.blit(texto_pontos, (LARGURA/2 - texto_pontos.get_width()/2, ALTURA/2 + 10))
            pygame.display.flip()
            pygame.time.wait(3000)
            rodando = False

    # Entrega de recursos nos centros
    for centro in centros_comunitarios:
        if player.x == centro.x and player.y == centro.y:
            pontos_ganhos = centro.receber_entrega(player.inventario)
            pontos += pontos_ganhos

    # --- Lógica de Desenho ---
    tela.fill(PRETO)
    desenhar_labirinto(tela)
    desenhar_recursos(tela, recursos)
    
    for centro in centros_comunitarios:
        centro.desenhar(tela)
        
    player.desenhar(tela)

    for inimigo in inimigos:
        inimigo.desenhar(tela)
        
    desenhar_hud(tela, player, centros_comunitarios)

    # --- Condição de Vitória ---
    if verificar_vitoria(centros_comunitarios):
        fonte_fim = pygame.font.SysFont(None, 36)
        tela.fill(PRETO)
        v_texto1 = fonte_fim.render("Parabéns! A comunidade prosperou!", True, (120, 255, 120))
        v_texto2 = fonte_fim.render(f"Pontuação Final: {pontos}", True, BRANCO)
        tela.blit(v_texto1, (LARGURA/2 - v_texto1.get_width()/2, ALTURA/2 - 40))
        tela.blit(v_texto2, (LARGURA/2 - v_texto2.get_width()/2, ALTURA/2 + 10))
        pygame.display.flip()
        pygame.time.wait(4000)
        rodando = False

    # --- Atualização da Tela ---
    pygame.display.flip()
    clock.tick(FPS)

# --- Fim do Jogo ---
pygame.quit()
sys.exit()