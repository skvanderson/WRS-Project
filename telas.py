"""
Arquivo de Telas (ui.py)

Contém todas as funções responsáveis por desenhar os diferentes
estados do jogo (menus, UI, HUD, telas de vitória/derrota).
"""

import pygame
import math
from typing import Dict, List, Tuple

# Importa constantes e dados
from config import *

# Importa entidades (para tipos) e assets
from entidades import Player, CentroComunitario
from assets import carregar_item

# --- Funções de Desenho de Texto (Helpers) ---

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

# --- Helpers de Layout de UI ---

def construir_layout_avaliacao(questoes_avaliacao, fonte_pergunta, largura_texto):
    layout = []
    perguntas = []
    y_cursor = 120  # Aumentado de 90 para 120 para dar mais espaco apos a legenda
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
    # Centralizar botoes melhor e dar mais espaco
    confirmar = pygame.Rect(LARGURA//2 - 100, ALTURA - 80, 200, 50)
    voltar = pygame.Rect(50, ALTURA - 80, 150, 50)
    return {"opcoes": opcoes, "confirmar": confirmar, "voltar": voltar}


# --- Funções de Desenho de Tela (Estados) ---

def desenhar_tela_inicial(surface, rects):
    surface.fill((5, 5, 5))
    fonte_logo = pygame.font.SysFont("bahnschrift", 68, bold=True)
    fonte_logo_small = pygame.font.SysFont("bahnschrift", 30)
    fonte_botao = pygame.font.SysFont(None, 34)
    fonte_legenda = pygame.font.SysFont(None, 26)

    # Ícone e texto lado a lado, centralizados como grupo
    y_logo = 130
    raio_pac = 46
    ponta_boca = 60
    espacamento = 20
    render_logo = fonte_logo.render("PACMAN", True, COR_OURO)
    logo_rect = render_logo.get_rect()
    
    largura_icone = raio_pac + ponta_boca  # da borda esquerda do círculo até a ponta da boca
    largura_grupo = largura_icone + espacamento + logo_rect.width
    x_inicio = (LARGURA - largura_grupo) // 2

    pac_center = (x_inicio + raio_pac, y_logo)
    pygame.draw.circle(surface, AMARELO, pac_center, raio_pac)
    pygame.draw.polygon(surface, (5, 5, 5), [pac_center, (pac_center[0] + ponta_boca, pac_center[1] - 32), (pac_center[0] + ponta_boca, pac_center[1] + 32)])
    pygame.draw.circle(surface, (25, 25, 25), (pac_center[0] + 12, pac_center[1] - 16), 6)

    logo_rect.centery = y_logo
    logo_rect.left = x_inicio + largura_icone + espacamento
    surface.blit(render_logo, logo_rect)
    
    render_sub = fonte_logo_small.render("MISSAO COMUNITARIA", True, BRANCO)
    sub_rect = render_sub.get_rect()
    sub_rect.left = logo_rect.left
    sub_rect.top = logo_rect.bottom + 5
    surface.blit(render_sub, sub_rect)
    
    # Botões principais (Logar e Cadastrar)
    for nome, rect in (("Logar", rects['logar']), ("Cadastrar", rects['cadastrar'])):
        botao_rect = rect.inflate(60, 10)
        pygame.draw.rect(surface, (12, 12, 12), botao_rect, border_radius=8)
        pygame.draw.rect(surface, COR_OURO, botao_rect, width=2, border_radius=8)
        pygame.draw.rect(surface, (250, 210, 0), rect, border_radius=8)
        pygame.draw.rect(surface, (5, 5, 5), rect, width=2, border_radius=8)
        desenhar_texto(surface, nome, rect.center, fonte_botao, (0, 0, 0))
    
    # Botão "Entrar sem cadastro" (estilo diferente, mais discreto)
    rect_sem_cadastro = rects['sem_cadastro']
    pygame.draw.rect(surface, (30, 30, 30), rect_sem_cadastro, border_radius=6)
    pygame.draw.rect(surface, (100, 100, 100), rect_sem_cadastro, width=1, border_radius=6)
    fonte_sem_cadastro = pygame.font.SysFont(None, 26)
    desenhar_texto(surface, "Entrar sem cadastro", rect_sem_cadastro.center, fonte_sem_cadastro, (180, 180, 180))

def desenhar_tela_formulario(surface, titulo, nick, senha, campo_ativo, rects, msg_erro=""):
    surface.fill((5, 5, 5))

    fonte_logo = pygame.font.SysFont("bahnschrift", 52, bold=True)
    fonte_logo_small = pygame.font.SysFont("bahnschrift", 26)
    fonte_titulo = pygame.font.SysFont(None, 40)
    fonte_label = pygame.font.SysFont(None, 24)
    fonte_input = pygame.font.SysFont(None, 30)
    fonte_msg = pygame.font.SysFont(None, 24)

    # Ícone e texto lado a lado, centralizados como grupo (formulário)
    y_logo = 110
    raio_pac = 36
    ponta_boca = 48
    espacamento = 18
    render_logo = fonte_logo.render("PACMAN", True, COR_OURO)
    logo_rect = render_logo.get_rect()
    
    largura_icone = raio_pac + ponta_boca
    largura_grupo = largura_icone + espacamento + logo_rect.width
    x_inicio = (LARGURA - largura_grupo) // 2

    pac_center = (x_inicio + raio_pac, y_logo)
    pygame.draw.circle(surface, AMARELO, pac_center, raio_pac)
    pygame.draw.polygon(surface, (5, 5, 5), [pac_center, (pac_center[0] + ponta_boca, pac_center[1] - 24), (pac_center[0] + ponta_boca, pac_center[1] + 24)])
    pygame.draw.circle(surface, (20, 20, 20), (pac_center[0] + 8, pac_center[1] - 12), 5)

    logo_rect.centery = y_logo
    logo_rect.left = x_inicio + largura_icone + espacamento
    surface.blit(render_logo, logo_rect)
    
    render_sub = fonte_logo_small.render("MISSAO COMUNITARIA", True, BRANCO)
    sub_rect = render_sub.get_rect()
    sub_rect.left = logo_rect.left
    sub_rect.top = logo_rect.bottom + 5
    surface.blit(render_sub, sub_rect)

    painel = pygame.Rect(LARGURA//2 - 240, 190, 480, 340)
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

        # Texto do campo (centralizado)
        if valor:
            texto = "*" * len(valor) if ocultar else valor
            cor_texto = BRANCO
        else:
            texto = "Password" if ocultar else "Login"
            cor_texto = (120, 120, 150)

        texto_render = fonte_input.render(texto, True, cor_texto)
        texto_rect = texto_render.get_rect(center=rect.center)
        surface.blit(texto_render, texto_rect)

        # Cursor piscando (apenas no campo ativo)
        if campo_ativo == campo_id:
            t = pygame.time.get_ticks()
            if (t // 500) % 2 == 0:  # pisca a cada ~500ms
                # Quando houver texto, o cursor acompanha o final do texto;
                # se vazio (placeholder), fica centralizado.
                if valor:
                    cursor_x = texto_rect.right + 3
                else:
                    cursor_x = rect.centerx
                cursor_top = rect.y + 8
                cursor_bottom = rect.bottom - 8
                pygame.draw.line(surface, COR_OURO, (cursor_x, cursor_top), (cursor_x, cursor_bottom), 2)

    confirmar_rect = rects['confirmar'].inflate(0, 20)
    pygame.draw.rect(surface, COR_OURO, confirmar_rect)
    pygame.draw.rect(surface, (0, 0, 0), confirmar_rect, width=2)
    desenhar_texto(surface, titulo, confirmar_rect.center, fonte_input, (0, 0, 0))

    voltar_rect = rects['voltar']
    pygame.draw.rect(surface, (40, 40, 40), voltar_rect, border_radius=4)
    pygame.draw.rect(surface, (150, 150, 150), voltar_rect, width=2, border_radius=4)
    desenhar_texto(surface, "Voltar", voltar_rect.center, fonte_input, BRANCO)

    # Mensagem de erro destacada logo abaixo do segundo campo
    if msg_erro:
        erro_rect_base = rects['senha'].inflate(0, 12)
        desenhar_texto(surface, msg_erro, (painel.centerx, erro_rect_base.bottom + 18), fonte_msg, (255, 120, 120))
    # Mensagens de ajuda na base do painel
    mensagem = msg_erro if msg_erro else "Create an account para salvar seu progresso."
    cor_msg = (255, 120, 120) if msg_erro else (160, 160, 160)
    desenhar_texto(surface, mensagem, (painel.centerx, painel.bottom + 35), fonte_msg, cor_msg)
    if not msg_erro:
        desenhar_texto(surface, "Already a member? Use o mesmo formulario para logar.", (painel.centerx, painel.bottom + 65), fonte_msg, CINZA)

def desenhar_tela_dificuldade(surface, rects, username=""):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo, fonte_botao = pygame.font.SysFont(None, 50), pygame.font.SysFont(None, 38)
    fonte_usuario = pygame.font.SysFont(None, 24)
    fonte_deslogar = pygame.font.SysFont(None, 28)
    
    desenhar_texto(surface, "Selecione o Nível de Dificuldade", (LARGURA / 2, 80), fonte_titulo, AMARELO)
    
    # Mostrar usuário logado no canto superior esquerdo com borda
    if username:
        card_usuario = pygame.Rect(20, 20, 200, 40)
        pygame.draw.rect(surface, (40, 40, 60), card_usuario, border_radius=6)
        pygame.draw.rect(surface, COR_REWARD, card_usuario, width=2, border_radius=6)
        desenhar_texto(surface, f"Usuário: {username}", card_usuario.center, fonte_usuario, BRANCO)
    
    # Botão deslogar no canto superior direito
    pygame.draw.rect(surface, (150, 50, 50), rects['deslogar'], border_radius=6)
    pygame.draw.rect(surface, (200, 80, 80), rects['deslogar'], width=2, border_radius=6)
    desenhar_texto(surface, "Deslogar", rects['deslogar'].center, fonte_deslogar, BRANCO)
    
    pygame.draw.rect(surface, (0, 150, 0), rects['easy']); desenhar_texto(surface, "Missão Tranquila", rects['easy'].center, fonte_botao)
    pygame.draw.rect(surface, (200, 150, 0), rects['default']); desenhar_texto(surface, "Ritmo da Comunidade", rects['default'].center, fonte_botao)
    pygame.draw.rect(surface, (150, 0, 0), rects['hard']); desenhar_texto(surface, "Resgate Intenso", rects['hard'].center, fonte_botao)
    pygame.draw.rect(surface, COR_BOTAO, rects['instrucoes']); desenhar_texto(surface, "Instruções", rects['instrucoes'].center, fonte_botao)
    pygame.draw.rect(surface, COR_OURO, rects['rewards']); desenhar_texto(surface, "Recompensas", rects['rewards'].center, fonte_botao)
    pygame.draw.rect(surface, COR_REWARD, rects['ranking']); desenhar_texto(surface, "Ranking", rects['ranking'].center, fonte_botao)
    pygame.draw.rect(surface, COR_BOTAO, rects['avaliacao']); desenhar_texto(surface, "Avaliação", rects['avaliacao'].center, fonte_botao)

def desenhar_tela_rewards(surface, rewards_system, username, rects):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo = pygame.font.SysFont("bahnschrift", 40, bold=True)
    fonte_secao = pygame.font.SysFont("bahnschrift", 30)
    fonte_media = pygame.font.SysFont(None, 26)
    fonte_pequena = pygame.font.SysFont(None, 24)
    
    user_data = rewards_system.obter_usuario_rewards(username)
    
    # Título
    desenhar_texto(surface, "RECOMPENSAS", (LARGURA/2, 35), fonte_titulo, COR_OURO)
    
    # Card do Jogador
    y_pos = 75
    desenhar_texto(surface, f"{username} - Nível {user_data['nivel']}", (LARGURA/2, y_pos), fonte_media, BRANCO)
    
    # Barra de Progresso XP
    xp_atual, xp_necessario, percentual = rewards_system.obter_progresso_nivel(username)
    y_pos += 30
    barra_rect = pygame.Rect(LARGURA//2 - 200, y_pos, 400, 20)
    pygame.draw.rect(surface, (40, 40, 60), barra_rect, border_radius=10)
    
    # Preenchimento da barra
    if percentual > 0:
        largura_preenchida = int((400 * percentual) / 100)
        barra_preenchida = pygame.Rect(LARGURA//2 - 200, y_pos, largura_preenchida, 20)
        pygame.draw.rect(surface, COR_OURO, barra_preenchida, border_radius=10)
    
    pygame.draw.rect(surface, BRANCO, barra_rect, width=2, border_radius=10)
    texto_xp = f"{xp_atual}/{xp_necessario} XP ({int(percentual)}%)"
    desenhar_texto(surface, texto_xp, (LARGURA/2, y_pos + 28), fonte_pequena, CINZA)
    
    # Títulos das seções
    y_pos += 60
    desenhar_texto(surface, "TAREFAS DIARIAS", (LARGURA/4, y_pos), fonte_secao, COR_OURO)
    desenhar_texto(surface, "CONQUISTAS", (3*LARGURA/4, y_pos), fonte_secao, COR_OURO)
    
    y_pos += 35
    tarefas = user_data.get("tarefas_diarias", rewards_system.daily_tasks)
    pontos_diarios = 0
    pontos_diarios_ganhos = 0
    
    # Tarefas Diárias - coluna esquerda
    y_tarefa = y_pos
    for task_id, task_data in rewards_system.daily_tasks.items():
        tarefa_user = tarefas.get(task_id, task_data)
        concluida = tarefa_user.get("concluida", False)
        pontos_diarios += task_data["pontos"]
        if concluida:
            pontos_diarios_ganhos += task_data["pontos"]
        
        # Card da tarefa
        largura_card = LARGURA//2 - 60
        card_tarefa = pygame.Rect(40, y_tarefa, largura_card, 32)
        cor_fundo = (50, 80, 50) if concluida else (50, 50, 70)
        pygame.draw.rect(surface, cor_fundo, card_tarefa, border_radius=6)
        cor_borda = COR_OURO if concluida else (100, 100, 130)
        pygame.draw.rect(surface, cor_borda, card_tarefa, width=2, border_radius=6)
        
        # Status
        status = "[OK]" if concluida else "[ ]"
        
        # Nome da tarefa
        nome_tarefa = task_data.get('nome', task_data['descricao'][:15])
        texto_completo = f"{status} {nome_tarefa}"
        desenhar_texto(surface, texto_completo, (50, y_tarefa + 16), fonte_pequena, BRANCO, "topleft")
        
        # Pontos à direita
        cor_pontos = COR_OURO if concluida else CINZA
        desenhar_texto(surface, f"{task_data['pontos']}", (40 + largura_card - 10, y_tarefa + 16), fonte_pequena, cor_pontos, "topright")
        
        y_tarefa += 36
    
    # Total de pontos diários
    desenhar_texto(surface, f"Total: {pontos_diarios_ganhos}/{pontos_diarios}", 
                  (LARGURA/4, y_tarefa + 8), fonte_media, COR_OURO)
    
    # Conquistas - coluna direita
    conquistas = user_data.get("conquistas", {})
    y_conquista = y_pos
    
    for achievement_id, achievement_data in rewards_system.achievements.items():
        user_achievement = conquistas.get(achievement_id, {"desbloqueada": False})
        desbloqueada = user_achievement.get("desbloqueada", False)
        
        # Card da conquista
        largura_card = LARGURA//2 - 60
        card_conquista = pygame.Rect(LARGURA//2 + 20, y_conquista, largura_card, 32)
        cor_fundo = (80, 50, 50) if desbloqueada else (50, 50, 70)
        pygame.draw.rect(surface, cor_fundo, card_conquista, border_radius=6)
        cor_borda = COR_OURO if desbloqueada else (100, 100, 130)
        pygame.draw.rect(surface, cor_borda, card_conquista, width=2, border_radius=6)
        
        # Status
        status = "[*]" if desbloqueada else "[-]"
        nome = achievement_data['nome']
        
        texto_completo = f"{status} {nome}"
        desenhar_texto(surface, texto_completo, (LARGURA//2 + 30, y_conquista + 16), fonte_pequena, BRANCO, "topleft")
        
        # Pontos à direita
        cor_pontos = COR_OURO if desbloqueada else CINZA
        desenhar_texto(surface, f"{achievement_data['pontos']}", (LARGURA//2 + 20 + largura_card - 10, y_conquista + 16), fonte_pequena, cor_pontos, "topright")
        
        y_conquista += 36
    
    # Botão Voltar
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['voltar_rewards'], border_radius=8)
    pygame.draw.rect(surface, BRANCO, rects['voltar_rewards'], width=2, border_radius=8)
    desenhar_texto(surface, "Voltar", rects['voltar_rewards'].center, fonte_media, BRANCO)

def desenhar_tela_ranking(surface, rewards_system, rects):
    surface.fill(COR_FUNDO_UI)
    fonte_titulo, fonte_media, fonte_pequena = pygame.font.SysFont(None, 45), pygame.font.SysFont(None, 32), pygame.font.SysFont(None, 28)
    desenhar_texto(surface, "Ranking de Jogadores", (LARGURA/2, 50), fonte_titulo, COR_OURO)
    ranking = rewards_system.obter_ranking(10)
    y_offset = 120
    for i, (username, pontos) in enumerate(ranking):
        cor = [COR_OURO, COR_PRATA, COR_BRONZE][i] if i < 3 else BRANCO
        numero = f"{i+1}."
        texto = f"{numero} {username}: {pontos} pontos"
        desenhar_texto(surface, texto, (LARGURA/2, y_offset), fonte_pequena, cor); y_offset += 30
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['voltar_ranking']); desenhar_texto(surface, "Voltar", rects['voltar_ranking'].center, fonte_media)

def desenhar_tela_game_over(surface, rects, nome_inimigo):
    surface.fill((5, 5, 5))
    fonte_logo = pygame.font.SysFont("bahnschrift", 52, bold=True)
    fonte_logo_small = pygame.font.SysFont("bahnschrift", 26)
    fonte_titulo = pygame.font.SysFont(None, 50)
    fonte_mensagem = pygame.font.SysFont(None, 26)
    fonte_botao = pygame.font.SysFont(None, 34)

    logo_x = LARGURA // 2 - 220
    
    # --- CORREÇÃO DE ALINHAMENTO (TELA GAME OVER) ---
    
    # 1. Desenha o ícone Pac-Man
    pac_center = (logo_x, 110)
    pygame.draw.circle(surface, AMARELO, pac_center, 40)
    pygame.draw.polygon(surface, (5, 5, 5), [pac_center, (pac_center[0] + 58, pac_center[1] - 28), (pac_center[0] + 58, pac_center[1] + 28)])
    pygame.draw.circle(surface, (20, 20, 20), (pac_center[0] + 10, pac_center[1] - 12), 5)

    # 2. Renderiza o texto "PACMAN"
    render_logo = fonte_logo.render("PACMAN", True, COR_OURO)
    logo_rect = render_logo.get_rect()
    
    # 3. Alinha o centro Y do texto ao centro Y do ícone
    logo_rect.centery = pac_center[1]
    
    # 4. Posiciona o texto à direita do ícone
    logo_rect.left = pac_center[0] + 65 # Espaçamento horizontal
    
    # 5. Desenha o texto (blit)
    surface.blit(render_logo, logo_rect)
    
    # 6. Renderiza e alinha o subtítulo
    render_sub = fonte_logo_small.render("MISSAO COMUNITARIA", True, BRANCO)
    sub_rect = render_sub.get_rect()
    
    # Alinha ao 'left' do título principal e abaixo dele
    sub_rect.left = logo_rect.left
    sub_rect.top = logo_rect.bottom + 5
    surface.blit(render_sub, sub_rect)
    
    # --- FIM DA CORREÇÃO ---

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
    desenhar_texto(surface, "Nao", rects['nao'].center, fonte_botao, BRANCO)

def desenhar_tela_vitoria(surface, rects, pontos_finais, pontos_bonus):
    surface.fill(COR_FUNDO_UI)
    fonte_grande = pygame.font.SysFont(None, 60)
    fonte_media = pygame.font.SysFont(None, 45)
    fonte_pontos = pygame.font.SysFont(None, 50)
    
    desenhar_texto(surface, "Parabens!", (LARGURA/2, 100), fonte_grande, AMARELO)
    desenhar_texto(surface, "A comunidade prosperou!", (LARGURA/2, 160), fonte_media, (120, 255, 120))
    
    desenhar_texto(surface, f"Pontuacao Final: {pontos_finais}", (LARGURA/2, 240), fonte_pontos, BRANCO)
    desenhar_texto(surface, f"Pontos de Recompensa: +{pontos_bonus}", (LARGURA/2, 290), fonte_pontos, COR_OURO)
    
    desenhar_texto(surface, "Deseja continuar?", (LARGURA/2, 380), fonte_media, BRANCO)
    
    pygame.draw.rect(surface, VERDE_CONTINUAR, rects['sim'])
    desenhar_texto(surface, "Sim", rects['sim'].center, fonte_media)
    
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['nao'])
    desenhar_texto(surface, "Nao", rects['nao'].center, fonte_media)

def desenhar_tela_avaliacao(surface, layout_avaliacao, perguntas_layout, rects, respostas, mensagem, medias_gerais=None):
    """
    Desenha a tela de avaliação.
    (Implementação da Sugestão #2 - Médias)
    Agora aceita 'medias_gerais' para exibir a média de notas.
    """
    surface.fill(COR_FUNDO_UI)
    fonte_titulo = pygame.font.SysFont(None, 46)
    fonte_secao = pygame.font.SysFont(None, 30)
    fonte_pergunta = pygame.font.SysFont(None, 24)
    fonte_opcao = pygame.font.SysFont(None, 24)
    fonte_media = pygame.font.SysFont(None, 20)
    fonte_mensagem = pygame.font.SysFont(None, 24)

    desenhar_texto(surface, "Avaliação do Produto", (LARGURA/2, 50), fonte_titulo, AMARELO)
    
    texto_legenda = fonte_media.render("Avalie de 1 (ruim) a 5 (excelente).", True, BRANCO)
    legenda_rect = texto_legenda.get_rect(centerx=LARGURA/2, y=85)
    surface.blit(texto_legenda, legenda_rect)

    for item in layout_avaliacao:
        if item["tipo"] == "header":
            desenhar_texto(surface, item["categoria"], (LARGURA/2, item["y"]), fonte_secao, COR_OURO)
        elif item["tipo"] == "pergunta":
            x_texto, y_linha = 50, item["y_texto"]
            for linha in item["linhas"]:
                render = fonte_pergunta.render(linha, True, BRANCO)
                surface.blit(render, (x_texto, y_linha))
                y_linha += fonte_pergunta.get_linesize()

            # Botoes de avaliacao
            for nota in range(1, 6):
                rect = rects['opcoes'][(item['indice'], nota)]
                selecionado = respostas.get(item['indice']) == nota
                cor_fundo = COR_REWARD if selecionado else COR_FUNDO_UI
                cor_borda = COR_OURO if selecionado else BRANCO
                pygame.draw.rect(surface, cor_fundo, rect, border_radius=6)
                pygame.draw.rect(surface, cor_borda, rect, width=2, border_radius=6)
                numero = fonte_opcao.render(str(nota), True, BRANCO)
                surface.blit(numero, numero.get_rect(center=rect.center))

            # --- SEÇÃO MODIFICADA (Sugestão #2) ---
            # Mostra a nota selecionada pelo usuário OU a média geral
            pos_base_y = rects['opcoes'][(item['indice'], 3)].centery
            pos_base_x = rects['opcoes'][(item['indice'], 5)].right + 35
            
            # --- LINHA CORRIGIDA (Bug Pylance) ---
            # 1. Mostrar a nota que o usuário está selecionando AGORA
            if item['indice'] in respostas:
                nota_selecionada = respostas[item['indice']]
                texto_nota = fonte_media.render(f"Sua Nota: {nota_selecionada}", True, COR_OURO) # Estava 'COR,'
                nota_rect = texto_nota.get_rect(midleft=(pos_base_x, pos_base_y - 8))
                surface.blit(texto_nota, nota_rect)
            # --- FIM DA CORREÇÃO ---
            
            # 2. Mostrar a média geral (se houver)
            if medias_gerais:
                media_da_pergunta = medias_gerais[item['indice']]
                if media_da_pergunta > 0:
                    texto_media = fonte_media.render(f"Média: {media_da_pergunta:.1f}", True, CINZA)
                else:
                    texto_media = fonte_media.render("Sem média", True, CINZA)
                
                # Ajusta a posição Y se a "Sua Nota" também estiver sendo mostrada
                pos_y_media = pos_base_y + 8 if item['indice'] in respostas else pos_base_y
                media_rect = texto_media.get_rect(midleft=(pos_base_x, pos_y_media))
                surface.blit(texto_media, media_rect)
            # --- FIM DA SEÇÃO MODIFICADA ---

    # Botoes
    pygame.draw.rect(surface, COR_BOTAO, rects['confirmar'], border_radius=8)
    pygame.draw.rect(surface, BRANCO, rects['confirmar'], width=2, border_radius=8)
    desenhar_texto(surface, "Enviar avaliacao", rects['confirmar'].center, fonte_secao, BRANCO)
    
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['voltar'], border_radius=8)
    pygame.draw.rect(surface, BRANCO, rects['voltar'], width=2, border_radius=8)
    desenhar_texto(surface, "Voltar", rects['voltar'].center, fonte_secao, BRANCO)

    # Mensagem de erro/sucesso
    if mensagem:
        cor_msg = VERMELHO if "Selecione" in mensagem else COR_OURO
        # Posiciona a mensagem de forma mais inteligente (acima dos botões)
        y_mensagem = rects['confirmar'].top - 40
        desenhar_texto(surface, mensagem, (LARGURA/2, y_mensagem), fonte_mensagem, cor_msg)

def desenhar_popup(surface, titulo, mensagem):
    """Renderiza um pop-up translucido na tela atual."""
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
    desenhar_texto(surface, "Movimento:", (x_align, y_pos), fonte_texto, AMARELO, "topleft")
    y_pos += 25
    desenhar_texto(surface, "Use as Setas ou W, A, S, D para mover continuamente.", (x_align, y_pos), fonte_texto_menor, BRANCO, "topleft")
    y_pos += 25
    desenhar_texto(surface, "O Pac-Man continuará se movendo na direção escolhida até encontrar uma parede.", (x_align, y_pos), fonte_texto_menor, BRANCO, "topleft")
    y_pos += 40
    desenhar_texto(surface, "Inventário:", (x_align, y_pos), fonte_texto, AMARELO, "topleft")
    y_pos += 25
    desenhar_texto(surface, "Pressione [H] para descartar o último item coletado.", (x_align, y_pos), fonte_texto_menor, BRANCO, "topleft")
    y_pos += 40
    desenhar_texto(surface, "Pausa:", (x_align, y_pos), fonte_texto, AMARELO, "topleft")
    y_pos += 25
    desenhar_texto(surface, "Pressione [P] para pausar ou retomar o jogo.", (x_align, y_pos), fonte_texto_menor, BRANCO, "topleft")
    pygame.draw.rect(surface, COR_BOTAO_VOLTAR, rects['voltar']); desenhar_texto(surface, "Voltar", rects['voltar'].center, fonte_subtitulo)


# --- Funções de Desenho do Jogo (Labirinto, HUD) ---

def desenhar_labirinto(surface):
    for y,linha in enumerate(LABIRINTO_LAYOUT):
        for x,celula in enumerate(linha):
            if celula == 1: pygame.draw.rect(surface,AZUL_PAREDE,(x*TAM_CELULA, y*TAM_CELULA,TAM_CELULA,TAM_CELULA))

def desenhar_recursos(surface, recursos):
    tamanho_item = (24, 24)
    # Cache simples para não recarregar imagens 60x por segundo
    if not hasattr(desenhar_recursos, "_cache"):
        desenhar_recursos._cache = {
            'Moeda': carregar_item('moeda', tamanho_item), 
            'Alimento': carregar_item('alimento', tamanho_item), 
            'Livro': carregar_item('livro', tamanho_item), 
            'Tijolo': carregar_item('tijolo', tamanho_item) 
        }
    cache = desenhar_recursos._cache

    for r in recursos:
        centro = (r['x']*TAM_CELULA + TAM_CELULA//2, r['y']*TAM_CELULA + TAM_CELULA//2)
        img = cache.get(r['tipo'])
        if img: surface.blit(img, img.get_rect(center=centro))

def desenhar_rotulos_coleta(surface, centros, player, alcance=3):
    fonte = pygame.font.SysFont(None, 22)
    tem_item = player.inventario[0] if player.inventario else None
    for centro in centros:
        distancia = abs(player.grid_x - centro.x) + abs(player.grid_y - centro.y)
        # Mostra o rótulo se o jogador estiver perto OU se tiver o item certo
        if distancia > alcance and centro.recurso_necessario != tem_item: 
            continue
        
        texto = f"Entregar {centro.recurso_necessario}"
        render = fonte.render(texto, True, BRANCO)
        padding_x, padding_y = 10, 6
        largura = render.get_width() + padding_x * 2
        altura = render.get_height() + padding_y * 2
        label_surface = pygame.Surface((largura, altura), pygame.SRCALPHA)
        label_surface.fill((0, 0, 0, 200))
        pygame.draw.rect(label_surface, COR_OURO, label_surface.get_rect(), width=1, border_radius=6)
        label_surface.blit(render, render.get_rect(center=label_surface.get_rect().center))
        
        # Calcular posição com ajuste para não sair da tela
        pos_x = centro.x * TAM_CELULA + TAM_CELULA // 2 - largura // 2
        pos_y = centro.y * TAM_CELULA - altura - 6
        
        # Ajustar se estiver saindo pela esquerda
        if pos_x < 5:
            pos_x = 5
        # Ajustar se estiver saindo pela direita
        elif pos_x + largura > LARGURA - 5:
            pos_x = LARGURA - largura - 5
        
        # Ajustar se estiver saindo pelo topo
        if pos_y < 5:
            pos_y = centro.y * TAM_CELULA + TAM_CELULA + 6  # Coloca abaixo do centro
        
        surface.blit(label_surface, (pos_x, pos_y))
        
        # Desenha "halo" de destaque se for o alvo correto
        if centro.recurso_necessario == tem_item:
            halo_surface = pygame.Surface((TAM_CELULA*2, TAM_CELULA*2), pygame.SRCALPHA)
            intensidade = 80 + int(40 * (1 + math.sin(pygame.time.get_ticks() / 250)))
            pygame.draw.circle(halo_surface, (*COR_OURO, intensidade), (halo_surface.get_width()//2, halo_surface.get_height()//2), TAM_CELULA, width=4)
            target_pos = (centro.x * TAM_CELULA + TAM_CELULA//2 - halo_surface.get_width()//2,
                          centro.y * TAM_CELULA + TAM_CELULA//2 - halo_surface.get_height()//2)
            surface.blit(halo_surface, target_pos, special_flags=pygame.BLEND_RGBA_ADD)

# --- CORREÇÃO 3 (Função Incompleta) ---
# Esta é a função `desenhar_hud` completa, que foi cortada na resposta anterior
def desenhar_hud(surface, jogador, centros, pontos):
    base_y = LINHAS_LABIRINTO * TAM_CELULA
    pygame.draw.rect(surface, COR_FUNDO_UI, (0, base_y, LARGURA, ALTURA - base_y))
    fonte, fonte_instrucao = pygame.font.SysFont(None, 28), pygame.font.SysFont(None, 24)
    surface.blit(fonte.render("Inventario:", True, BRANCO), (40, base_y + 15))
    mapa_cor={'Moeda':COR_MOEDA,'Alimento':COR_ALIMENTO,'Livro':COR_LIVRO,'Tijolo':COR_TIJOLO}
    for i in range(jogador.capacidade_inventario):
        pygame.draw.rect(surface,BRANCO,(40+i*30,base_y+40,25,25),1)
        if i < len(jogador.inventario): pygame.draw.rect(surface,mapa_cor[jogador.inventario[i]],(40+i*30,base_y+40,25,25))
    surface.blit(fonte_instrucao.render("Pressione [H] para Descartar", True, BRANCO), (40, base_y + 75))
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

def desenhar_popup_sem_cadastro(surface):
    """Desenha um popup informativo sobre entrar sem cadastro"""
    # Overlay escuro
    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    # Card do popup
    largura_popup = 500
    altura_popup = 250
    x_popup = LARGURA // 2 - largura_popup // 2
    y_popup = ALTURA // 2 - altura_popup // 2
    
    popup_rect = pygame.Rect(x_popup, y_popup, largura_popup, altura_popup)
    pygame.draw.rect(surface, (25, 25, 25), popup_rect, border_radius=12)
    pygame.draw.rect(surface, COR_OURO, popup_rect, width=3, border_radius=12)
    
    # Título
    fonte_titulo = pygame.font.SysFont("bahnschrift", 32, bold=True)
    titulo = fonte_titulo.render("Modo Visitante", True, COR_OURO)
    titulo_rect = titulo.get_rect(center=(LARGURA // 2, y_popup + 40))
    surface.blit(titulo, titulo_rect)
    
    # Mensagem
    fonte_msg = pygame.font.SysFont(None, 26)
    mensagens = [
        "Você está entrando como visitante.",
        "",
        "Sua pontuação NÃO será incluída",
        "no ranking."
    ]
    
    y_texto = y_popup + 85
    for msg in mensagens:
        texto = fonte_msg.render(msg, True, BRANCO)
        texto_rect = texto.get_rect(center=(LARGURA // 2, y_texto))
        surface.blit(texto, texto_rect)
        y_texto += 32
    
    # Botão OK
    rect_ok = pygame.Rect(LARGURA//2 - 60, ALTURA//2 + 80, 120, 40)
    pygame.draw.rect(surface, (250, 210, 0), rect_ok, border_radius=8)
    pygame.draw.rect(surface, (5, 5, 5), rect_ok, width=2, border_radius=8)
    fonte_botao = pygame.font.SysFont(None, 32)
    texto_ok = fonte_botao.render("OK", True, (0, 0, 0))
    texto_ok_rect = texto_ok.get_rect(center=rect_ok.center)
    surface.blit(texto_ok, texto_ok_rect)

def desenhar_popup_controles(surface):
    """Desenha um popup informativo sobre os controles do jogo"""
    # Overlay escuro
    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    # Card do popup
    largura_popup = 550
    altura_popup = 280
    x_popup = LARGURA // 2 - largura_popup // 2
    y_popup = ALTURA // 2 - altura_popup // 2
    
    popup_rect = pygame.Rect(x_popup, y_popup, largura_popup, altura_popup)
    pygame.draw.rect(surface, (25, 25, 25), popup_rect, border_radius=12)
    pygame.draw.rect(surface, COR_OURO, popup_rect, width=3, border_radius=12)
    
    # Título
    fonte_titulo = pygame.font.SysFont("bahnschrift", 32, bold=True)
    titulo = fonte_titulo.render("Controles do Jogo", True, COR_OURO)
    titulo_rect = titulo.get_rect(center=(LARGURA // 2, y_popup + 35))
    surface.blit(titulo, titulo_rect)
    
    # Mensagem
    fonte_msg = pygame.font.SysFont(None, 26)
    mensagens = [
        "Você pode jogar usando:",
        "",
        "Setas do Teclado (↑ ↓ ← →)",
        "OU",
        "Teclas WASD (W A S D)"
    ]
    
    y_texto = y_popup + 85
    for msg in mensagens:
        if msg == "OU":
            cor = COR_OURO
            fonte_ou = pygame.font.SysFont(None, 24, bold=True)
            texto = fonte_ou.render(msg, True, cor)
        else:
            cor = BRANCO
            texto = fonte_msg.render(msg, True, cor)
        texto_rect = texto.get_rect(center=(LARGURA // 2, y_texto))
        surface.blit(texto, texto_rect)
        y_texto += 32
    
    # Instrução para fechar
    fonte_dica = pygame.font.SysFont(None, 22)
    dica = fonte_dica.render("Clique em qualquer lugar para fechar", True, CINZA)
    dica_rect = dica.get_rect(center=(LARGURA // 2, y_popup + altura_popup - 30))
    surface.blit(dica, dica_rect)
# --- FIM DA CORREÇÃO 3 ---