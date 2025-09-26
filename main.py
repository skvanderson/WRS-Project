import pygame, os, sys, random

# Inicializa o pygame
pygame.init()

# Define o tamanho da tela
largura_tela = 1280
altura_tela = 720
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("Pac-Man: Trabalho teste")

# Cores
COR_PRETA = (0, 0, 0)
COR_BRANCA = (255, 255, 255)
COR_CINZA = (200, 200, 200)
COR_AVISO = (255, 120, 120)

# FPS alvo
fps_alvo = 60
clock = pygame.time.Clock()

# Velocidade do jogador (pixels/segundo)
velocidade = 180

# Tamanho do Pac-Man
player_largura = 30
player_altura = 30

# Pastas de assets
pasta_anim = os.path.join("assets", "anim32")
pasta_centros = os.path.join("assets", "centros48")

# Funções simples
def carregar_sequencia(pasta, prefixo, qtd, tamanho):
    imagens = []
    for i in range(qtd):
        arq = os.path.join(pasta_anim, pasta, f"{prefixo}_{i}.png")
        if os.path.exists(arq):
            img = pygame.image.load(arq).convert_alpha()
            img = pygame.transform.smoothscale(img, tamanho)
            imagens.append(img)
    return imagens

def carregar_duas(pasta, base, tamanho):
    imgs = []
    for i in range(2):
        arq = os.path.join(pasta_anim, pasta, f"{base}_{i}.png")
        if os.path.exists(arq):
            img = pygame.image.load(arq).convert_alpha()
            img = pygame.transform.smoothscale(img, tamanho)
            imgs.append(img)
    return imgs

def carregar_item(nome_arquivo):
    arq = os.path.join(pasta_anim, "itens", nome_arquivo + ".png")
    if not os.path.exists(arq): return None
    img = pygame.image.load(arq).convert_alpha()
    return pygame.transform.smoothscale(img, (24, 24))

def carregar_centro(prefixo, tamanho):
    imagens = []
    for i in range(3):
        arq = os.path.join(pasta_centros, f"{prefixo}_{i}.png")
        if os.path.exists(arq):
            img = pygame.image.load(arq).convert_alpha()
            img = pygame.transform.smoothscale(img, tamanho)
            imagens.append(img)
    return imagens

def limitar_na_tela(recto):
    if recto.left < 0: recto.left = 0
    if recto.right > largura_tela: recto.right = largura_tela
    if recto.top < 0: recto.top = 0
    if recto.bottom > altura_tela: recto.bottom = altura_tela

def distancia(a, b):
    return ((a[0]-b[0])**2 + (a[1]-b[1])**2) ** 0.5

# JOGADOR (frames do nosso Pac-Man) 
player_frames_direita = carregar_sequencia("pacman", "pacman_right", 4, (player_largura, player_altura))
if not player_frames_direita:
    print("Faltam os frames em assets/anim32/pacman/pacman_right_0..3.png")
    pygame.quit(); sys.exit(1)

player_frames_esquerda = [pygame.transform.flip(f, True, False) for f in player_frames_direita]
player_frames_cima     = [pygame.transform.rotate(f, 90) for f in player_frames_direita]
player_frames_baixo    = [pygame.transform.rotate(f, -90) for f in player_frames_direita]

player_img_direita  = player_frames_direita
player_img_esquerda = player_frames_esquerda
player_img_cima     = player_frames_cima
player_img_baixo    = player_frames_baixo

player_frame_indice = 0
player_img_direita_atual = player_img_direita
player_img_atual = player_img_direita[player_frame_indice]
player_rect = player_img_atual.get_rect()
player_rect.center = (largura_tela / 2, altura_tela / 2)

# Temporizador de animação do jogador (ms por frame)
tempo_anim_player_ms = 110
timer_anim_player = 0

# FANTASMAS (2 frames, aleatórios) 
vel_des = 60
vel_cri = 90
vel_dsg = 110
vel_fal = 90

tempo_anim_ghost_ms = 220
timer_anim_ghost = 0
indice_ghost = 0

tam_ghost = (48, 48)
g_des = carregar_duas("ghost_desemprego", "ghost_desemprego", tam_ghost)
g_cri = carregar_duas("ghost_crise_economica", "ghost_crise_economica", tam_ghost)
g_dsg = carregar_duas("ghost_desigualdade_small", "ghost_desigualdade_small", tam_ghost)
g_fv  = carregar_duas("ghost_falta_acesso_visible", "ghost_falta_acesso_visible", tam_ghost)
g_fi  = carregar_duas("ghost_falta_acesso_invisivel", "ghost_falta_acesso_invisivel", tam_ghost)

def novo_fantasma(nome, frames, vel_px, x=None, y=None):
    if not frames: return None
    if x is None: x = random.randint(120, largura_tela-120)
    if y is None: y = random.randint(120, altura_tela-120)
    ang = random.uniform(0, 360)
    v = pygame.Vector2(1,0).rotate(ang) * vel_px
    rect = frames[0].get_rect(center=(x,y))
    return {
        "nome": nome,
        "frames": frames,
        "rect": rect,
        "vel": v,
        "troca_dir_ms": random.randint(800, 1800),
        "timer_dir": 0
    }

# ITENS E INVENTÁRIO 
itens_png = {
    "moeda": carregar_item("item_moeda"),
    "alimento": carregar_item("item_alimento"),
    "livro": carregar_item("item_livro"),
    "tijolos": carregar_item("item_tijolos"),
}
itens_no_cenario = []
inventario = []
inventario_limite = 5
coleta_dist = 26
pontos = 0
spawn_item_ms = 1200
timer_spawn_item = 0
max_itens_no_cenario = 12

def spawn_item():
    tipos = [k for k, v in itens_png.items() if v]
    if not tipos: return
    tipo = random.choice(tipos)
    x = random.randint(80, largura_tela-80)
    y = random.randint(120, altura_tela-80)
    itens_no_cenario.append({"tipo": tipo, "pos": pygame.Vector2(x,y)})

# CENTROS (3 frames, depósito) 
centros = (
    {"nome":"Escola",   "pos": (320, 520), "aceita":"livro",   "dir":"escola"},
    {"nome":"Hospital", "pos": (540, 520), "aceita":"alimento","dir":"hospital"},
    {"nome":"Mercado",  "pos": (760, 520), "aceita":"moeda",   "dir":"mercado"},
    {"nome":"Moradia",  "pos": (980, 520), "aceita":"tijolos", "dir":"moradia"},
)
centros_imgs = {c["dir"]: carregar_centro(c["dir"], (48,48)) for c in centros}
deposito_dist = 40

tempo_anim_centro_ms = 180
timer_anim_centro = 0
indice_centro = 0

# HUD
fonte = pygame.font.SysFont(None, 22)
fonte_aviso = pygame.font.SysFont(None, 36)

# Aviso de colisão + reinício
aviso_texto = ""
aviso_timer = 0
tempo_aviso_ms = 800  # mostra aviso por 0.8s antes de reiniciar

# função para reiniciar o jogo 
def reiniciar_jogo():
    global player_rect, player_frame_indice, player_img_direita_atual, player_img_atual
    global itens_no_cenario, inventario, pontos
    global fantasmas, timer_anim_player, timer_anim_ghost, indice_ghost
    global timer_anim_centro, indice_centro, timer_spawn_item

    # jogador
    player_frame_indice = 0
    player_img_direita_atual = player_img_direita
    player_img_atual = player_img_direita[player_frame_indice]
    player_rect = player_img_atual.get_rect()
    player_rect.center = (largura_tela / 2, altura_tela / 2)

    # itens/inventário/pontos
    itens_no_cenario = []
    inventario = []
    pontos = 0
    timer_spawn_item = 0

    # timers de animação
    timer_anim_player = 0
    timer_anim_ghost = 0
    indice_ghost = 0
    timer_anim_centro = 0
    indice_centro = 0

    # recria os fantasmas
    fantasmas = []
    f1 = novo_fantasma("Desemprego",       g_des, vel_des, 260, 220)
    f2 = novo_fantasma("Crise Econômica",  g_cri, vel_cri, 1020, 220)
    f3 = novo_fantasma("Desigualdade A",   g_dsg, vel_dsg, 520, 240)
    f4 = novo_fantasma("Desigualdade B",   g_dsg, vel_dsg, 560, 260)
    f5 = novo_fantasma("Falta de Acesso",  g_fv,  vel_fal, 760, 220)
    for f in (f1,f2,f3,f4,f5):
        if f: fantasmas.append(f)

# cria o estado inicial chamando a função uma vez
fantasmas = []
reiniciar_jogo()

# Loop principal do jogo
rodando = True
while rodando:
    dt = clock.tick(fps_alvo)
    dt_s = dt / 1000.0

    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # Lógica de movimento
    teclas = pygame.key.get_pressed()
    move_x = 0.0
    move_y = 0.0

    if teclas[pygame.K_LEFT]:
        move_x -= velocidade * dt_s
        player_img_direita_atual = player_img_esquerda
    if teclas[pygame.K_RIGHT]:
        move_x += velocidade * dt_s
        player_img_direita_atual = player_img_direita
    if teclas[pygame.K_UP]:
        move_y -= velocidade * dt_s
        player_img_direita_atual = player_img_cima
    if teclas[pygame.K_DOWN]:
        move_y += velocidade * dt_s
        player_img_direita_atual = player_img_baixo

    # animação do jogador
    if move_x or move_y:
        timer_anim_player += dt
        if timer_anim_player >= tempo_anim_player_ms:
            timer_anim_player = 0
            player_frame_indice = (player_frame_indice + 1) % len(player_img_direita)
    else:
        timer_anim_player = 0
        player_frame_indice = 0
    player_img_atual = player_img_direita_atual[player_frame_indice]

    # Atualiza posição do jogador
    player_rect.x += int(round(move_x))
    player_rect.y += int(round(move_y))
    limitar_na_tela(player_rect)

    # Itens: spawn e coleta
    timer_spawn_item += dt
    if timer_spawn_item >= spawn_item_ms and len(itens_no_cenario) < max_itens_no_cenario:
        spawn_item()
        timer_spawn_item = 0

    for it in itens_no_cenario[:]:
        if distancia(player_rect.center, (it["pos"].x, it["pos"].y)) <= coleta_dist and len(inventario) < inventario_limite:
            inventario.append(it["tipo"])
            itens_no_cenario.remove(it)
            pontos += 10

    # Depósito nos centros
    for c in centros:
        cx, cy = c["pos"]
        if distancia(player_rect.center, (cx, cy)) <= deposito_dist and inventario:
            tipo_aceito = c["aceita"]
            quantos = sum(1 for x in inventario if x == tipo_aceito)
            if quantos:
                inventario = [x for x in inventario if x != tipo_aceito]
                pontos += 100 * quantos

    # Fantasmas: animação e movimento
    timer_anim_ghost += dt
    if timer_anim_ghost >= tempo_anim_ghost_ms:
        timer_anim_ghost = 0
        indice_ghost = (indice_ghost + 1) % 2

    for f in fantasmas:
        # Falta de Acesso: alterna visibilidade a cada 400ms usando o próprio timer_dir
        if f["nome"].startswith("Falta") and g_fi:
            f["timer_dir"] += dt
            if f["timer_dir"] >= 400:
                f["timer_dir"] = 0
                f["frames"] = g_fi if (f["frames"] is g_fv) else g_fv

        # troca de direção
        f["timer_dir"] += dt
        if f["timer_dir"] >= f["troca_dir_ms"]:
            f["timer_dir"] = 0
            f["troca_dir_ms"] = random.randint(800, 1800)
            ang = random.uniform(0, 360)
            vel_mod = f["vel"].length()
            f["vel"] = pygame.Vector2(1,0).rotate(ang) * vel_mod

        # move por dt
        f["rect"].x += int(round(f["vel"].x * dt_s))
        f["rect"].y += int(round(f["vel"].y * dt_s))
        if f["rect"].left < 0 or f["rect"].right > largura_tela: f["vel"].x *= -1
        if f["rect"].top < 0 or f["rect"].bottom > altura_tela: f["vel"].y *= -1
        f["rect"].clamp_ip(pygame.Rect(0,0,largura_tela,altura_tela))

    # Colisão com fantasmas → aviso + reinício
    pegou = None
    for f in fantasmas:
        if distancia(player_rect.center, f["rect"].center) <= 24:
            pegou = f["nome"]
            break
    if pegou and aviso_timer == 0:
        aviso_texto = f"A barreira {pegou} te pegou! Reiniciando..."
        aviso_timer = tempo_aviso_ms

    # Se está contando aviso, ao terminar reinicia o jogo
    if aviso_timer > 0:
        aviso_timer -= dt
        if aviso_timer <= 0:
            reiniciar_jogo()
            aviso_texto = ""
            aviso_timer = 0

    # animação dos centros
    timer_anim_centro += dt
    if timer_anim_centro >= tempo_anim_centro_ms:
        timer_anim_centro = 0
        indice_centro = (indice_centro + 1) % 3

    # Pinta o fundo
    tela.fill(COR_PRETA)

    # Desenha Centros
    for c in centros:
        seq = centros_imgs.get(c["dir"], [])
        if seq:
            imgc = seq[indice_centro % len(seq)]
            tela.blit(imgc, imgc.get_rect(center=c["pos"]))

    # Desenha Itens
    for it in itens_no_cenario:
        ic = itens_png.get(it["tipo"])
        if ic:
            tela.blit(ic, ic.get_rect(center=(int(it["pos"].x), int(it["pos"].y))))

    # Desenha o jogador
    tela.blit(player_img_atual, player_rect)

    # Desenha Fantasmas
    for f in fantasmas:
        fr = f["frames"][indice_ghost % len(f["frames"])]
        tela.blit(fr, fr.get_rect(center=f["rect"].center))

    # HUD
    hud_pontos = fonte.render(f"Pontos: {pontos}", True, COR_BRANCA)
    hud_inv = fonte.render(f"Inventário ({len(inventario)}/{inventario_limite})", True, COR_CINZA)
    tela.blit(hud_pontos, (16, 12))
    tela.blit(hud_inv, (16, 40))
    xhud = 16
    for item in inventario:
        ic = itens_png.get(item)
        if ic:
            tela.blit(ic, (xhud, 66))
            xhud += 28

    # Aviso de colisão (centralizado no topo)
    if aviso_timer > 0 and aviso_texto:
        msg = fonte_aviso.render(aviso_texto, True, COR_AVISO)
        tela.blit(msg, msg.get_rect(center=(largura_tela//2, 80)))

    # Atualiza a tela
    pygame.display.flip()

# Finaliza o pygame
pygame.quit()
