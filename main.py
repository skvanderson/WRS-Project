import pygame

# Inicializa o pygame
pygame.init()

# Define o tamanho da tela
largura_tela = 1280
altura_tela = 720
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("Pac-Man: Trabalho teste")

# Carrega a imagem original (virada para a direita)
player_img_original = pygame.image.load('pacman.png')
player_largura = 30 # Tamanho do Pac-Man
player_altura = 30 # Tamanho do Pac-Man
player_img_original = pygame.transform.scale(player_img_original, (player_largura, player_altura))

# Cria as versões para cada direção a partir da original
player_img_direita = player_img_original
player_img_esquerda = pygame.transform.flip(player_img_original, True, False)
player_img_cima = pygame.transform.rotate(player_img_original, 90)
player_img_baixo = pygame.transform.rotate(player_img_original, -90)

# Define a imagem atual do jogador (começa virado para a direita)
player_img_atual = player_img_direita

# Cria um retangulo para controlar a posição e colisão do jogador
player_rect = player_img_atual.get_rect()
player_rect.center = (largura_tela / 2, altura_tela / 2) # Posição inicial

# Cores
COR_PRETA = (0, 0, 0)

# Velocidade do jogador
velocidade = 2

# Loop principal do jogo
rodando = True
while rodando:
    # Verifica os eventos (cliques, teclado)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # Lógica de movimento
    teclas = pygame.key.get_pressed()
    
    if teclas[pygame.K_LEFT]:
        player_rect.x -= velocidade
        player_img_atual = player_img_esquerda
    if teclas[pygame.K_RIGHT]:
        player_rect.x += velocidade
        player_img_atual = player_img_direita
    if teclas[pygame.K_UP]:
        player_rect.y -= velocidade
        player_img_atual = player_img_cima
    if teclas[pygame.K_DOWN]:
        player_rect.y += velocidade
        player_img_atual = player_img_baixo

    # Lógica para prender o jogador nas bordas da tela
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > largura_tela:
        player_rect.right = largura_tela
    if player_rect.top < 0:
        player_rect.top = 0
    if player_rect.bottom > altura_tela:
        player_rect.bottom = altura_tela

    # Pinta o fundo da tela de preto
    tela.fill(COR_PRETA)

    # Desenha a imagem do jogador na tela
    tela.blit(player_img_atual, player_rect)

    # Atualiza a tela para mostrar o que foi desenhado
    pygame.display.flip()

# Finaliza o pygame
pygame.quit()