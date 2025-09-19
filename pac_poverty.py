import pygame
import sys
import random
import math

pygame.init()

LARGURA, ALTURA = 600, 660
TAM_CELULA = 30
COLUNAS = LARGURA // TAM_CELULA
LINHAS = (ALTURA - 60) // TAM_CELULA
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pac-Poverty - Erradicação da Pobreza")
clock = pygame.time.Clock()
FPS = 10

PRETO = (0, 0, 0)
AZUL_PAREDE = (0, 0, 180)
AMARELO = (255, 210, 0)
BRANCO = (255, 255, 255)
VERDE = (0, 200, 0)
DOURADO = (255, 215, 0)
BRANCO_ITEM = (245, 245, 245)
CINZA = (130, 130, 130)
MARROM = (139, 69, 19)
ROXO = (148, 0, 211)
PRETO_INIMIGO = (20, 20, 20)

INIMIGO_INFO = {
    'exclusao': "Exclusão Social",
    'extrema': "Pobreza Extrema",
    'desigualdade': "Desigualdade",
    'fome': "Fome/Miséria"
}

labirinto = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1],
    [1,0,1,1,1,0,0,1,0,1,1,1,0,1,0,1,1,1,0,1],
    [1,0,0,0,1,0,0,0,0,1,0,1,0,0,0,1,0,0,0,1],
    [1,0,1,0,1,0,1,1,0,1,0,1,1,0,1,1,0,1,0,1],
    [1,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1,0,1],
    [1,0,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,0,1],
    [1,1,1,1,0,1,1,1,0,1,0,1,0,1,1,1,0,1,1,1],
    [1,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,1],
    [1,0,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

LINHAS_M = len(labirinto)
COLUNAS_M = len(labirinto[0])

player_x, player_y = 1, 1
dir_x, dir_y = 0, 0
vel_x, vel_y = 0, 0
pontos = 0
boca_frame = 0
BOCA_FRAMES = 4

inimigos = [
    {"x": 18, "y": 1, "cor": CINZA, "chave": "exclusao", "vel":[0,1]},
    {"x": 18, "y": 11, "cor": MARROM, "chave": "extrema", "vel":[0,-1]},
    {"x": 10, "y": 5, "cor": ROXO, "chave": "desigualdade", "vel":[1,0]},
    {"x": 5, "y": 9, "cor": PRETO_INIMIGO, "chave": "fome", "vel":[-1,0]}
]

def desenhar_labirinto(surface):
    for y in range(LINHAS_M):
        for x in range(COLUNAS_M):
            val = labirinto[y][x]
            px = x * TAM_CELULA
            py = y * TAM_CELULA
            if val == 1:
                pygame.draw.rect(surface, AZUL_PAREDE, (px, py, TAM_CELULA, TAM_CELULA))
            elif val == 0:
                seed = (x * 31 + y * 17) % 3
                cor = [VERDE, DOURADO, BRANCO_ITEM][seed]
                centro = (px + TAM_CELULA//2, py + TAM_CELULA//2)
                pygame.draw.circle(surface, cor, centro, 5)

def centro_celula(x, y):
    return (x * TAM_CELULA + TAM_CELULA//2, y * TAM_CELULA + TAM_CELULA//2)

def pode_ir(x, y):
    if x < 0 or y < 0 or y >= LINHAS_M or x >= COLUNAS_M:
        return False
    return labirinto[y][x] != 1

def desenhar_pacman(surface, gx, gy, boca_frame, dirx, diry):
    centro = centro_celula(gx, gy)
    raio = TAM_CELULA//2 - 3
    if dirx == -1:   angulo_central = math.pi
    elif dirx == 1:  angulo_central = 0
    elif diry == -1: angulo_central = -math.pi/2
    elif diry == 1:  angulo_central = math.pi/2
    else:            angulo_central = 0
    max_abertura = math.radians(50)
    min_abertura = math.radians(8)
    t = (boca_frame % BOCA_FRAMES) / (BOCA_FRAMES - 1) if BOCA_FRAMES > 1 else 0
    abertura = min_abertura + (max_abertura - min_abertura) * t
    inicio = angulo_central + abertura
    fim = angulo_central - abertura
    pygame.draw.circle(surface, AMARELO, centro, raio)
    p1 = centro
    p2 = (centro[0] + math.cos(inicio) * raio, centro[1] + math.sin(inicio) * raio)
    p3 = (centro[0] + math.cos(fim) * raio, centro[1] + math.sin(fim) * raio)
    pygame.draw.polygon(surface, PRETO, [p1, p2, p3])

def mover_inimigo(inimigo):
    nx = inimigo['x'] + inimigo['vel'][0]
    ny = inimigo['y'] + inimigo['vel'][1]
    if pode_ir(nx, ny):
        inimigo['x'], inimigo['y'] = nx, ny
    else:
        opcoes = []
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            if pode_ir(inimigo['x']+dx, inimigo['y']+dy):
                opcoes.append((dx,dy))
        if opcoes:
            inimigo['vel'] = list(random.choice(opcoes))
        else:
            inimigo['vel'] = [0,0]

def derrota_por_inimigo(chave):
    descricao = INIMIGO_INFO.get(chave, "um Problema Social")
    return f"Você foi derrotado pela {descricao}!"

def todos_itens_coletados():
    return all(0 not in linha for linha in labirinto)

rodando = True
while rodando:
    tela.fill(PRETO)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_LEFT:  dir_x, dir_y = -1, 0
            elif evento.key == pygame.K_RIGHT: dir_x, dir_y = 1, 0
            elif evento.key == pygame.K_UP:    dir_x, dir_y = 0, -1
            elif evento.key == pygame.K_DOWN:  dir_x, dir_y = 0, 1

    if dir_x or dir_y:
        nx, ny = player_x + dir_x, player_y + dir_y
        if pode_ir(nx, ny):
            vel_x, vel_y = dir_x, dir_y
    nx, ny = player_x + vel_x, player_y + vel_y
    if pode_ir(nx, ny):
        player_x, player_y = nx, ny
    else:
        vel_x, vel_y = 0, 0

    if labirinto[player_y][player_x] == 0:
        labirinto[player_y][player_x] = 2
        pontos += 10

    for inim in inimigos:
        mover_inimigo(inim)
        if inim['x'] == player_x and inim['y'] == player_y:
            texto_derrota = derrota_por_inimigo(inim['chave'])
            fonte = pygame.font.SysFont(None, 36)
            tela.fill(PRETO)
            render = fonte.render(texto_derrota, True, (255, 80, 80))
            subt = fonte.render(f"Pontos: {pontos}", True, (200,200,200))
            tela.blit(render, (30, ALTURA//2 - 20))
            tela.blit(subt, (30, ALTURA//2 + 20))
            pygame.display.flip()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit()

    desenhar_labirinto(tela)
    desenhar_pacman(tela, player_x, player_y, boca_frame, vel_x, vel_y)
    boca_frame = (boca_frame + 1) % BOCA_FRAMES
    for inim in inimigos:
        cx, cy = centro_celula(inim['x'], inim['y'])
        raio = TAM_CELULA//2 - 3
        pygame.draw.circle(tela, inim['cor'], (cx, cy), raio)

    fonte_hud = pygame.font.SysFont(None, 28)
    tela.blit(fonte_hud.render(f"Pontos: {pontos}", True, BRANCO), (10, ALTURA - 50))
    tela.blit(fonte_hud.render("ODS 1 - Erradicação da Pobreza", True, BRANCO), (200, ALTURA - 50))

    if todos_itens_coletados():
        fonte_v = pygame.font.SysFont(None, 36)
        tela.fill(PRETO)
        tela.blit(fonte_v.render("Parabéns! Você ajudou a combater a pobreza!", True, (120, 255, 120)), (30, ALTURA//2 - 20))
        tela.blit(fonte_v.render(f"Pontos finais: {pontos}", True, (200,200,200)), (30, ALTURA//2 + 20))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
