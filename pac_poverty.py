import pygame
import sys
import random
import math
import json

# --- Inicialização do Pygame ---
pygame.init()

# --- Constantes Globais ---
LARGURA, ALTURA = 600, 720
TAM_CELULA = 30
COLUNAS = LARGURA // TAM_CELULA
LINHAS_LABIRINTO = 18
FPS = 15
ARQUIVO_USUARIOS = "usuarios.json"

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pac-Man - A Missão Comunitária")
clock = pygame.time.Clock()

# --- Cores ---
PRETO = (0, 0, 0)
AZUL_PAREDE = (0, 0, 139)
AMARELO = (255, 223, 0)
BRANCO = (255, 255, 255)
VERMELHO = (200, 0, 0)
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

# --- Classes do Jogo (sem alterações) ---
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
        if self.dir_x != 0 or self.dir_y != 0:
            prox_x, prox_y = self.x + self.dir_x, self.y + self.dir_y
            if self.pode_ir(prox_x, prox_y): self.vel_x, self.vel_y = self.dir_x, self.dir_y
        prox_x, prox_y = self.x + self.vel_x, self.y + self.vel_y
        if self.pode_ir(prox_x, prox_y): self.x, self.y = prox_x, prox_y
        else: self.vel_x, self.vel_y = 0, 0
    def pode_ir(self, x, y):
        return 0 <= x < COLUNAS and 0 <= y < LINHAS_LABIRINTO and labirinto[y][x] != 1
    def coletar(self, recursos):
        if len(self.inventario) < self.capacidade_inventario:
            for recurso in recursos[:]:
                if recurso['x'] == self.x and recurso['y'] == self.y:
                    self.inventario.append(recurso['tipo']); recursos.remove(recurso); break
    def desenhar(self, surface):
        centro = (self.x * TAM_CELULA + TAM_CELULA//2, self.y * TAM_CELULA + TAM_CELULA//2)
        raio = TAM_CELULA//2 - 3
        direcao_atual = self.vel_x if self.vel_x != 0 else self.dir_x
        if direcao_atual == -1: angulo_central = math.pi
        elif direcao_atual == 1: angulo_central = 0
        elif self.vel_y == -1 or self.dir_y == -1: angulo_central = math.pi/2
        elif self.vel_y == 1 or self.dir_y == 1: angulo_central = -math.pi/2
        else: angulo_central = 0
        max_abertura = math.radians(45); min_abertura = math.radians(5)
        t = abs(self.boca_frames_total - 2 * (self.boca_frame % self.boca_frames_total)) / self.boca_frames_total
        abertura = min_abertura + (max_abertura - min_abertura) * t
        inicio = angulo_central + abertura; fim = angulo_central - abertura
        pygame.draw.circle(surface, AMARELO, centro, raio)
        if self.vel_x != 0 or self.vel_y != 0:
            p1 = centro; p2 = (centro[0] + math.cos(inicio) * raio, centro[1] - math.sin(inicio) * raio)
            p3 = (centro[0] + math.cos(fim) * raio, centro[1] - math.sin(fim) * raio)
            pygame.draw.polygon(surface, PRETO, [p1, p2, p3])
        self.boca_frame += 1

class Inimigo:
    def __init__(self, x, y, cor, nome):
        self.x, self.y = x, y; self.cor = cor; self.nome = nome
        self.vel = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.invisivel = (nome == "Falta de Acesso"); self.visivel = True
        self.timer_invisibilidade = 0; self.tempo_para_trocar = random.randint(30, 60)
    def mover(self):
        if self.invisivel:
            self.timer_invisibilidade += 1
            if self.timer_invisibilidade > self.tempo_para_trocar:
                self.visivel = not self.visivel; self.timer_invisibilidade = 0
                self.tempo_para_trocar = random.randint(20, 50)
        prox_x, prox_y = self.x + self.vel[0], self.y + self.vel[1]
        if self.pode_ir(prox_x, prox_y): self.x, self.y = prox_x, prox_y
        else:
            opcoes = []
            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                if (dx, dy) != (-self.vel[0], -self.vel[1]) and self.pode_ir(self.x + dx, self.y + dy):
                    opcoes.append((dx, dy))
            if not opcoes: opcoes.append((-self.vel[0], -self.vel[1]))
            self.vel = random.choice(opcoes)
    def pode_ir(self, x, y):
        return 0 <= x < COLUNAS and 0 <= y < LINHAS_LABIRINTO and labirinto[y][x] != 1
    def desenhar(self, surface):
        if not self.visivel: return
        centro = (self.x * TAM_CELULA + TAM_CELULA//2, self.y * TAM_CELULA + TAM_CELULA//2)
        raio = TAM_CELULA//2 - 4
        pygame.draw.circle(surface, self.cor, centro, raio)
        olho_esq_x = centro[0] - raio/2.5; olho_dir_x = centro[0] + raio/2.5
        olho_y = centro[1] - raio/3
        pygame.draw.circle(surface, BRANCO, (olho_esq_x, olho_y), 4); pygame.draw.circle(surface, BRANCO, (olho_dir_x, olho_y), 4)
        pygame.draw.circle(surface, PRETO, (olho_esq_x, olho_y), 2); pygame.draw.circle(surface, PRETO, (olho_dir_x, olho_y), 2)

class CentroComunitario:
    def __init__(self, x, y, nome, cor, recurso_necessario):
        self.x, self.y, self.nome, self.cor, self.recurso_necessario = x, y, nome, cor, recurso_necessario
        self.nivel_atual = 0; self.nivel_max = 5
    def desenhar(self, surface):
        px, py = self.x * TAM_CELULA, self.y * TAM_CELULA
        pygame.draw.rect(surface, self.cor, (px + 2, py + 2, TAM_CELULA - 4, TAM_CELULA - 4), border_radius=4)
        largura_barra = TAM_CELULA - 8; altura_barra = 5
        progresso = (self.nivel_atual / self.nivel_max) * largura_barra
        pygame.draw.rect(surface, PRETO, (px + 4, py + TAM_CELULA - 12, largura_barra, altura_barra))
        pygame.draw.rect(surface, AMARELO, (px + 4, py + TAM_CELULA - 12, progresso, altura_barra))
    def receber_entrega(self, inventario_jogador):
        recursos_entregues = 0
        for item in inventario_jogador[:]:
            if item == self.recurso_necessario:
                inventario_jogador.remove(item); recursos_entregues += 1
        if recursos_entregues > 0 and self.nivel_atual < self.nivel_max:
            self.nivel_atual += recursos_entregues
            if self.nivel_atual > self.nivel_max: self.nivel_atual = self.nivel_max
            return recursos_entregues * 20
        return 0

# --- Funções de Gerenciamento de Usuários ---
def carregar_usuarios():
    try:
        with open(ARQUIVO_USUARIOS, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, 'w') as f:
        json.dump(usuarios, f, indent=4)

# --- Funções de Desenho da UI ---
def desenhar_texto(surface, texto, pos, fonte, cor=BRANCO):
    render = fonte.render(texto, True, cor)
    rect = render.get_rect(center=pos)
    surface.blit(render, rect)

def desenhar_tela_inicial(surface, rects):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo = pygame.font.SysFont(None, 50)
    fonte_botao = pygame.font.SysFont(None, 40)
    desenhar_texto(surface, "Pac-Man - A Missão Comunitária", (LARGURA/2, 150), fonte_titulo, AMARELO)
    pygame.draw.rect(surface, COR_BOTAO, rects['logar'])
    desenhar_texto(surface, "Logar", rects['logar'].center, fonte_botao)
    pygame.draw.rect(surface, COR_BOTAO, rects['cadastrar'])
    desenhar_texto(surface, "Cadastrar", rects['cadastrar'].center, fonte_botao)

def desenhar_tela_formulario(surface, titulo, nick, senha, campo_ativo, rects, mensagem_erro=""):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo = pygame.font.SysFont(None, 50)
    fonte_label = pygame.font.SysFont(None, 36)
    fonte_input = pygame.font.SysFont(None, 32)
    fonte_erro = pygame.font.SysFont(None, 28)

    desenhar_texto(surface, titulo, (LARGURA/2, 100), fonte_titulo, AMARELO)

    label_nick = fonte_label.render("Nick:", True, BRANCO)
    surface.blit(label_nick, (rects['nick'].x, rects['nick'].y - 30))
    cor_nick = COR_INPUT_ATIVO if campo_ativo == 'nick' else COR_INPUT_INATIVO
    pygame.draw.rect(surface, cor_nick, rects['nick'], 2)
    texto_nick = fonte_input.render(nick, True, BRANCO)
    surface.blit(texto_nick, (rects['nick'].x + 10, rects['nick'].y + 10))

    label_senha = fonte_label.render("Senha:", True, BRANCO)
    surface.blit(label_senha, (rects['senha'].x, rects['senha'].y - 30))
    cor_senha = COR_INPUT_ATIVO if campo_ativo == 'senha' else COR_INPUT_INATIVO
    pygame.draw.rect(surface, cor_senha, rects['senha'], 2)
    texto_senha = fonte_input.render('*' * len(senha), True, BRANCO)
    surface.blit(texto_senha, (rects['senha'].x + 10, rects['senha'].y + 10))
    
    pygame.draw.rect(surface, COR_BOTAO, rects['confirmar'])
    desenhar_texto(surface, titulo, rects['confirmar'].center, fonte_label)
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['voltar'])
    desenhar_texto(surface, "Voltar", rects['voltar'].center, fonte_label)

    if mensagem_erro:
        desenhar_texto(surface, mensagem_erro, (LARGURA/2, 530), fonte_erro, VERMELHO)

# --- Funções do Jogo ---
def desenhar_labirinto(surface):
    for y, linha in enumerate(labirinto):
        for x, celula in enumerate(linha):
            if celula == 1:
                pygame.draw.rect(surface, AZUL_PAREDE, (x*TAM_CELULA, y*TAM_CELULA, TAM_CELULA, TAM_CELULA))

def desenhar_recursos(surface, recursos):
    recurso_map = {'Moeda':(COR_MOEDA,'c'),'Alimento':(COR_ALIMENTO,'q'),'Livro':(COR_LIVRO,'r'),'Tijolo':(COR_TIJOLO,'t')}
    for r in recursos:
        info = recurso_map[r['tipo']]; px, py = r['x']*TAM_CELULA, r['y']*TAM_CELULA
        centro = (px + TAM_CELULA//2, py + TAM_CELULA//2)
        if info[1] == 'c': pygame.draw.circle(surface, info[0], centro, 6)
        elif info[1] == 'q': pygame.draw.rect(surface, info[0], (px+10, py+10, 10, 10))
        elif info[1] == 'r': pygame.draw.rect(surface, info[0], (px+8, py+12, 14, 8))
        elif info[1] == 't': pygame.draw.rect(surface, info[0], (px+7, py+10, 16, 10))

def desenhar_hud(surface, jogador, centros, pontos):
    base_y = LINHAS_LABIRINTO * TAM_CELULA
    pygame.draw.rect(surface, COR_FUNDO_UI, (0, base_y, LARGURA, ALTURA - base_y))
    fonte = pygame.font.SysFont(None, 28)
    texto_inv = fonte.render("Inventário:", True, BRANCO); surface.blit(texto_inv, (10, base_y + 10))
    cor_map = {'Moeda':COR_MOEDA,'Alimento':COR_ALIMENTO,'Livro':COR_LIVRO,'Tijolo':COR_TIJOLO}
    for i, item in enumerate(jogador.inventario):
        pygame.draw.rect(surface, cor_map[item], (120 + i * 25, base_y + 12, 20, 20))
    for i in range(jogador.capacidade_inventario):
        pygame.draw.rect(surface, BRANCO, (120 + i * 25, base_y + 12, 20, 20), 1)
    texto_centros = fonte.render("Desenvolvimento Comunitário:", True, BRANCO); surface.blit(texto_centros, (10, base_y + 50))
    for i, centro in enumerate(centros):
        texto_c = fonte.render(f"{centro.nome}:", True, centro.cor); surface.blit(texto_c, (30, base_y+80+i*25))
        prog = (centro.nivel_atual/centro.nivel_max); pygame.draw.rect(surface,PRETO,(130,base_y+82+i*25,100,15))
        pygame.draw.rect(surface,AMARELO,(130,base_y+82+i*25,100*prog,15))
    texto_pontos = fonte.render(f"Pontos: {pontos}", True, BRANCO); surface.blit(texto_pontos, (LARGURA-150,base_y+10))

# --- Loop Principal e Lógica de Estados ---
def main():
    rodando = True
    estado_jogo = 'tela_inicial' # tela_inicial, tela_login, tela_cadastro, jogo
    jogo_iniciado = False
    
    nick_usuario, senha_usuario = "", ""
    campo_ativo = 'nick'
    mensagem_erro = ""

    usuarios = carregar_usuarios()

    # Retângulos da UI
    rects_inicial = {
        'logar': pygame.Rect(LARGURA/2 - 125, 250, 250, 60),
        'cadastrar': pygame.Rect(LARGURA/2 - 125, 350, 250, 60)
    }
    rects_formulario = {
        'nick': pygame.Rect(LARGURA/2 - 150, 200, 300, 40),
        'senha': pygame.Rect(LARGURA/2 - 150, 300, 300, 40),
        'confirmar': pygame.Rect(LARGURA/2 - 125, 400, 250, 50),
        'voltar': pygame.Rect(LARGURA/2 - 75, 470, 150, 40)
    }

    # Variáveis do Jogo (serão inicializadas quando o jogo começar)
    player, inimigos, centros_comunitarios, recursos, pontos = None, [], [], [], 0

    while rodando:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                rodando = False

        if estado_jogo == 'tela_inicial':
            for evento in eventos:
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if rects_inicial['logar'].collidepoint(evento.pos):
                        estado_jogo = 'tela_login'; mensagem_erro = ""
                        nick_usuario, senha_usuario = "", ""; campo_ativo = 'nick'
                    elif rects_inicial['cadastrar'].collidepoint(evento.pos):
                        estado_jogo = 'tela_cadastro'; mensagem_erro = ""
                        nick_usuario, senha_usuario = "", ""; campo_ativo = 'nick'
            desenhar_tela_inicial(tela, rects_inicial)

        elif estado_jogo in ['tela_login', 'tela_cadastro']:
            titulo = "Logar" if estado_jogo == 'tela_login' else "Cadastrar"
            for evento in eventos:
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    mensagem_erro = ""
                    if rects_formulario['nick'].collidepoint(evento.pos): campo_ativo = 'nick'
                    elif rects_formulario['senha'].collidepoint(evento.pos): campo_ativo = 'senha'
                    elif rects_formulario['voltar'].collidepoint(evento.pos): estado_jogo = 'tela_inicial'
                    elif rects_formulario['confirmar'].collidepoint(evento.pos):
                        if estado_jogo == 'tela_login':
                            if nick_usuario in usuarios and usuarios[nick_usuario] == senha_usuario:
                                estado_jogo = 'jogo'
                            else: mensagem_erro = "Nick ou senha inválidos."
                        else: # Tela de Cadastro
                            if not nick_usuario or not senha_usuario:
                                mensagem_erro = "Os campos não podem estar vazios."
                            elif nick_usuario in usuarios:
                                mensagem_erro = "Este nick já está em uso."
                            else:
                                usuarios[nick_usuario] = senha_usuario
                                salvar_usuarios(usuarios)
                                estado_jogo = 'jogo'

                if evento.type == pygame.KEYDOWN:
                    if campo_ativo == 'nick':
                        if evento.key == pygame.K_BACKSPACE: nick_usuario = nick_usuario[:-1]
                        elif evento.key == pygame.K_TAB: campo_ativo = 'senha'
                        else: nick_usuario += evento.unicode
                    elif campo_ativo == 'senha':
                        if evento.key == pygame.K_BACKSPACE: senha_usuario = senha_usuario[:-1]
                        elif evento.key == pygame.K_TAB: campo_ativo = 'nick'
                        elif evento.key == pygame.K_RETURN: rects_formulario['confirmar'].centerx +=1 # Truque para ativar o botão
                        else: senha_usuario += evento.unicode
            
            desenhar_tela_formulario(tela, titulo, nick_usuario, senha_usuario, campo_ativo, rects_formulario, mensagem_erro)

        elif estado_jogo == 'jogo':
            if not jogo_iniciado:
                player = Player(1, 1); pontos = 0
                inimigos = [Inimigo(18,1,CINZA,"Desemprego"), Inimigo(1,16,ROXO,"Desigualdade"),
                            Inimigo(18,16,CINZA_ESCURO,"Falta de Acesso"), Inimigo(9,8,VERMELHO_CRISE,"Crise Econômica")]
                centros_comunitarios = [CentroComunitario(1,9,"Moradia",COR_MORADIA,"Tijolo"), CentroComunitario(18,9,"Mercado",COR_MERCADO,"Alimento"),
                                        CentroComunitario(9,1,"Escola",COR_ESCOLA,"Livro"), CentroComunitario(9,16,"Hospital",COR_HOSPITAL,"Moeda")]
                recursos = []
                tipos_recursos = ['Moeda', 'Alimento', 'Livro', 'Tijolo']
                for y in range(LINHAS_LABIRINTO):
                    for x in range(COLUNAS):
                        if labirinto[y][x] == 0 and random.random() < 0.4:
                            is_pos_free = (x,y) != (1,1) and not any(c.x==x and c.y==y for c in centros_comunitarios)
                            if is_pos_free: recursos.append({'x':x,'y':y,'tipo':random.choice(tipos_recursos)})
                jogo_iniciado = True

            for evento in eventos:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_LEFT: player.dir_x, player.dir_y = -1, 0
                    elif evento.key == pygame.K_RIGHT: player.dir_x, player.dir_y = 1, 0
                    elif evento.key == pygame.K_UP: player.dir_x, player.dir_y = 0, -1
                    elif evento.key == pygame.K_DOWN: player.dir_x, player.dir_y = 0, 1
            
            player.mover()
            player.coletar(recursos)
            
            for inimigo in inimigos:
                inimigo.mover()
                if inimigo.x == player.x and inimigo.y == player.y and inimigo.visivel:
                    fonte_fim = pygame.font.SysFont(None, 40)
                    tela.fill(PRETO)
                    desenhar_texto(tela, f"Superado por: {inimigo.nome}", (LARGURA/2, ALTURA/2-20), fonte_fim, VERMELHO)
                    desenhar_texto(tela, f"Pontos: {pontos}", (LARGURA/2, ALTURA/2+20), fonte_fim)
                    pygame.display.flip(); pygame.time.wait(3000)
                    rodando = False

            for centro in centros_comunitarios:
                if player.x == centro.x and player.y == centro.y:
                    pontos += centro.receber_entrega(player.inventario)
            
            tela.fill(PRETO)
            desenhar_labirinto(tela); desenhar_recursos(tela, recursos)
            for centro in centros_comunitarios: centro.desenhar(tela)
            player.desenhar(tela)
            for inimigo in inimigos: inimigo.desenhar(tela)
            desenhar_hud(tela, player, centros_comunitarios, pontos)

            if all(c.nivel_atual >= c.nivel_max for c in centros_comunitarios):
                fonte_fim = pygame.font.SysFont(None, 36)
                tela.fill(PRETO)
                desenhar_texto(tela, "Parabéns! A comunidade prosperou!", (LARGURA/2, ALTURA/2-20), fonte_fim, (120,255,120))
                desenhar_texto(tela, f"Pontuação Final: {pontos}", (LARGURA/2, ALTURA/2+20), fonte_fim)
                pygame.display.flip(); pygame.time.wait(4000)
                rodando = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()