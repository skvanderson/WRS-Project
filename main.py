"""
Arquivo Principal (main.py)

Orquestra o jogo:
- Inicializa o Pygame
- Gerencia o loop principal do jogo (game loop)
- Controla a máquina de estados (menus, jogo, game over, etc.)
- Gerencia as entidades e a lógica de jogo
"""

import pygame
import sys
import random
import datetime
from typing import Dict, List, Tuple, Set

# --- 1. Importar Constantes e Configurações ---
from config import *

# --- 2. Importar Utilitários e Sistemas ---
from utils import (
    tocar_musica_labirinto, tocar_musica_game_over, parar_musica,
    carregar_usuarios, salvar_usuarios,
    RewardsSystem,
    encontrar_caminho,
    carregar_avaliacoes, salvar_avaliacoes, calcular_medias_avaliacao,
    handle_form_input # (Sugestão #3)
)

# --- 3. Importar Entidades do Jogo ---
from entidades import Player, Inimigo, CentroComunitario

# --- 4. Importar Funções de Desenho de UI ---
from telas import *


# --- Loop Principal e Logica de Estados ---
def main():
    # --- Inicialização do Pygame ---
    pygame.init()
    pygame.mixer.init()
    
    # Mover a criação de tela e clock para dentro do main
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Pac-Man - A Missao Comunitaria")
    clock = pygame.time.Clock()
    
    rodando = True
    estado_jogo = 'tela_inicial'
    
    # --- Variáveis de Estado (UI) ---
    nick_usuario, senha_usuario, campo_ativo, mensagem_erro = "", "", 'nick', ""
    usuarios = carregar_usuarios()
    dificuldade_selecionada = "Default"
    
    # --- Variáveis de Estado (Sistemas) ---
    rewards_system = RewardsSystem()
    avaliacoes_dados = carregar_avaliacoes()
    
    # --- Variáveis de Estado (Avaliação) ---
    fonte_layout_avaliacao = pygame.font.SysFont(None, 24)
    layout_avaliacao, perguntas_avaliacao = construir_layout_avaliacao(QUESTOES_AVALIACAO, fonte_layout_avaliacao, 520)
    rects_avaliacao = gerar_rects_avaliacao(perguntas_avaliacao)
    respostas_avaliacao = {}
    mensagem_avaliacao = ""
    popup_avaliacao = {"mensagem": "", "titulo": "", "ativo": False, "expira": 0}
    # (Sugestão #2) Variável para guardar as médias
    medias_gerais_avaliacao = [] 

    # Popup para modo sem cadastro
    popup_sem_cadastro = {"ativo": False, "expira": 0} 

    # --- Definição dos Rects dos Menus ---
    rects_inicial = {
        'logar':pygame.Rect(LARGURA/2-150,230,300,70),
        'cadastrar':pygame.Rect(LARGURA/2-150,320,300,70),
        'sem_cadastro':pygame.Rect(LARGURA/2-150,410,300,50)
    }
    
    # --- CORREÇÃO DO BUG DE SOBREPOSIÇÃO ---
    # Os valores de Y foram restaurados para os originais do seu script
    rects_form = {
        'nick':pygame.Rect(LARGURA/2-200, 230, 400, 40),
        'senha':pygame.Rect(LARGURA/2-200, 330, 400, 40),
        'confirmar':pygame.Rect(LARGURA/2-150, 430, 300, 60),
        'voltar':pygame.Rect(LARGURA/2-100, 490, 200, 50)
    }
    # --- FIM DA CORREÇÃO ---

    rects_game_over = {'sim':pygame.Rect(LARGURA/2-180, ALTURA - 140, 150, 70),'nao':pygame.Rect(LARGURA/2+30, ALTURA - 140, 150, 70)}
    rects_vitoria = {'sim': pygame.Rect(LARGURA/2-180, ALTURA - 140, 150, 70), 'nao': pygame.Rect(LARGURA/2+30, ALTURA - 140, 150, 70)}
    rects_dificuldade = {
        'easy': pygame.Rect(LARGURA/2-150, 150, 300, 45),
        'default': pygame.Rect(LARGURA/2-150, 205, 300, 45),
        'hard': pygame.Rect(LARGURA/2-150, 260, 300, 45),
        'instrucoes': pygame.Rect(LARGURA/2-150, 315, 300, 45),
        'rewards': pygame.Rect(LARGURA/2-150, 370, 300, 45),
        'ranking': pygame.Rect(LARGURA/2-150, 425, 300, 45),
        'avaliacao': pygame.Rect(LARGURA/2-150, 480, 300, 45),
        'deslogar': pygame.Rect(LARGURA - 180, 20, 160, 40)
    }
    rects_instrucoes = {'voltar': pygame.Rect(LARGURA/2-100, ALTURA-60, 200, 50)}
    rects_rewards = {'voltar_rewards': pygame.Rect(LARGURA/2-100, ALTURA-80, 200, 50)}
    rects_ranking = {'voltar_ranking': pygame.Rect(LARGURA/2-100, ALTURA-80, 200, 50)}
    rect_desistir_jogo = pygame.Rect(LARGURA - 140, LINHAS_LABIRINTO * TAM_CELULA + 45, 120, 35)

    # --- Variáveis de Estado (Jogo) ---
    player: Player | None = None
    inimigos: List[Inimigo] = []
    centros: List[CentroComunitario] = []
    recursos: List[Dict] = []
    pontos = 0
    inimigo_colisor: Inimigo | None = None
    pontos_finais, pontos_bonus_vitoria = 0, 0
    posicoes_iniciais_inimigos = [(30, 1), (1, 13), (30, 13), (15, 7)]
    tempo_inicio_partida = datetime.datetime.now()
    musica_labirinto_tocando = False
    jogo_pausado = False
    
    # --- Variáveis de Spawn ---
    tipos_recursos_padrao = ['Moeda', 'Alimento', 'Livro', 'Tijolo']
    tempo_spawn_recursos_ms = 900
    timer_spawn_recursos = 0
    max_recursos_no_cenario = 60
    # (Sugestão #4) Set dinâmico de posições livres
    posicoes_livres_dinamicas: Set[Tuple[int, int]] = set() 

    # --- Funções Aninhadas (para gerenciar o estado do jogo) ---
    
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
        nonlocal posicoes_livres_dinamicas # (Sugestão #4)
        
        pontos, tempo_inicio_partida = 0, datetime.datetime.now()
        player = Player(1, 1)
        centros = [CentroComunitario(1, 7, "Moradia", COR_MORADIA, "Tijolo"), CentroComunitario(30, 7, "Mercado", COR_MERCADO, "Alimento"), CentroComunitario(15, 1, "Escola", COR_ESCOLA, "Livro"), CentroComunitario(15, 13, "Hospital", COR_HOSPITAL, "Moeda")]
        recursos = []
        timer_spawn_recursos = 0
        
        # (Sugestão #4) Inicializa o set dinâmico a partir da constante
        posicoes_livres_dinamicas = set(MAPA_POSICOES_LIVRES) 
        
        # Remove posições ocupadas inicialmente
        posicoes_livres_dinamicas.discard((player.grid_x, player.grid_y))
        for c in centros:
            posicoes_livres_dinamicas.discard((c.x, c.y))
            
        for tipo in tipos_recursos_padrao:
            for _ in range(6):
                if not posicoes_livres_dinamicas: break
                pos = random.choice(list(posicoes_livres_dinamicas))
                recursos.append({'x':pos[0], 'y':pos[1], 'tipo':tipo})
                posicoes_livres_dinamicas.discard(pos) # Remove do set

        reiniciar_posicoes(dificuldade)
        
    def spawn_recurso():
        nonlocal recursos, posicoes_livres_dinamicas # (Sugestão #4)
        if len(recursos) >= max_recursos_no_cenario: return
        if not posicoes_livres_dinamicas: return # (Sugestão #4) Checa o set
        
        quantidade_por_spawn = 2
        for _ in range(quantidade_por_spawn):
            if len(recursos) >= max_recursos_no_cenario or not posicoes_livres_dinamicas: break
            
            # (Sugestão #4) Pega uma posição direto do set (muito rápido)
            pos = random.choice(list(posicoes_livres_dinamicas))
            posicoes_livres_dinamicas.discard(pos)
            
            tipo = random.choice(tipos_recursos_padrao)
            recursos.append({'x': pos[0], 'y': pos[1], 'tipo': tipo})

    # ==========================
    # --- INICIO DO GAME LOOP ---
    # ==========================
    while rodando:
        eventos = pygame.event.get()
        for e in eventos:
            if e.type == pygame.QUIT: rodando = False
        
        tempo_atual = pygame.time.get_ticks()
        if popup_avaliacao["ativo"] and tempo_atual >= popup_avaliacao["expira"]:
            popup_avaliacao["ativo"] = False

        # --- Maquina de Estados ---

        if estado_jogo == 'tela_inicial':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    # Se popup está ativo, verificar clique no botão OK
                    if popup_sem_cadastro["ativo"]:
                        rect_ok = pygame.Rect(LARGURA//2 - 60, ALTURA//2 + 80, 120, 40)
                        if rect_ok.collidepoint(e.pos):
                            popup_sem_cadastro["ativo"] = False
                            nick_usuario = "Visitante"
                            estado_jogo = 'tela_dificuldade'
                    else:
                        if rects_inicial['logar'].collidepoint(e.pos):
                            estado_jogo='tela_login'; mensagem_erro,nick_usuario,senha_usuario="","",""; campo_ativo='nick'
                        elif rects_inicial['cadastrar'].collidepoint(e.pos):
                            estado_jogo='tela_cadastro'; mensagem_erro,nick_usuario,senha_usuario="","",""; campo_ativo='nick'
                        elif rects_inicial['sem_cadastro'].collidepoint(e.pos):
                            popup_sem_cadastro["ativo"] = True
                            popup_sem_cadastro["expira"] = pygame.time.get_ticks() + 10000  # 10 segundos
            
            desenhar_tela_inicial(tela, rects_inicial)
            
            # Desenhar popup se ativo
            if popup_sem_cadastro["ativo"]:
                desenhar_popup_sem_cadastro(tela)
                if pygame.time.get_ticks() > popup_sem_cadastro["expira"]:
                    popup_sem_cadastro["ativo"] = False

        elif estado_jogo in ['tela_login', 'tela_cadastro']:
            titulo = "Logar" if estado_jogo == 'tela_login' else "Cadastrar"
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mensagem_erro="";
                    if rects_form['nick'].collidepoint(e.pos): campo_ativo='nick'
                    elif rects_form['senha'].collidepoint(e.pos): campo_ativo='senha'
                    elif rects_form['voltar'].collidepoint(e.pos): estado_jogo='tela_inicial'
                    elif rects_form['confirmar'].collidepoint(e.pos):
                        # (Lógica de submissão do formulário)
                        if estado_jogo == 'tela_login':
                            if nick_usuario in usuarios and usuarios[nick_usuario] == senha_usuario: estado_jogo = 'tela_dificuldade'
                            else: mensagem_erro = "Nick ou senha invalidos."
                        else: 
                            if not nick_usuario or not senha_usuario: mensagem_erro="Os campos nao podem estar vazios."
                            elif nick_usuario in usuarios: mensagem_erro="Este nick ja esta em uso."
                            else: usuarios[nick_usuario]=senha_usuario; salvar_usuarios(usuarios); estado_jogo = 'tela_dificuldade'
                
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN or e.key == pygame.K_KP_ENTER:
                        # (Lógica de submissão com Enter)
                        if estado_jogo == 'tela_login':
                            if nick_usuario in usuarios and usuarios[nick_usuario] == senha_usuario: estado_jogo = 'tela_dificuldade'
                            else: mensagem_erro = "Nick ou senha invalidos."
                        else: 
                            if not nick_usuario or not senha_usuario: mensagem_erro="Os campos nao podem estar vazios."
                            elif nick_usuario in usuarios: mensagem_erro="Este nick ja esta em uso."
                            else: usuarios[nick_usuario]=senha_usuario; salvar_usuarios(usuarios); estado_jogo = 'tela_dificuldade'
                    else:
                        # (Sugestão #3) Chama a função unificada
                        nick_usuario, senha_usuario, campo_ativo = handle_form_input(e, nick_usuario, senha_usuario, campo_ativo)
                        
            desenhar_tela_formulario(tela, titulo, nick_usuario, senha_usuario, campo_ativo, rects_form, mensagem_erro)

        elif estado_jogo == 'tela_dificuldade':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
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
                        respostas_avaliacao.clear() 
                        avaliacoes_dados = carregar_avaliacoes() 
                        # (Sugestão #2) Calcula as médias ao entrar na tela
                        medias_gerais_avaliacao, _ = calcular_medias_avaliacao(avaliacoes_dados, len(perguntas_avaliacao))
                    elif rects_dificuldade['deslogar'].collidepoint(e.pos):
                        # Deslogar: limpar usuário e voltar para tela inicial
                        nick_usuario = ""
                        estado_jogo = 'tela_inicial'
                        
                    if dificuldade_foi_escolhida: inicializar_novo_jogo(dificuldade_selecionada); estado_jogo = 'jogo'
            desenhar_tela_dificuldade(tela, rects_dificuldade, nick_usuario)

        elif estado_jogo == 'tela_instrucoes':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if rects_instrucoes['voltar'].collidepoint(e.pos):
                        estado_jogo = 'tela_dificuldade'
            desenhar_tela_instrucoes(tela, rects_instrucoes)

        elif estado_jogo == 'tela_avaliacao':
            for e in eventos:
                if popup_avaliacao["ativo"]:
                    if e.type == pygame.KEYDOWN or (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1): popup_avaliacao["ativo"] = False
                    continue
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if rects_avaliacao['voltar'].collidepoint(e.pos):
                        estado_jogo = 'tela_dificuldade'
                        mensagem_avaliacao = ""
                        popup_avaliacao["ativo"] = False
                        respostas_avaliacao.clear()
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
                            mensagem_avaliacao = "Avaliacao registrada! Obrigado pelo feedback."
                            
                            avaliacoes_dados = carregar_avaliacoes()
                            # (Sugestão #2) Recalcula as médias após salvar
                            medias_gerais_avaliacao, _ = calcular_medias_avaliacao(avaliacoes_dados, len(perguntas_avaliacao))
                            
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
                                mensagem_avaliacao = "" 
                                break
            # (Sugestão #2) Passa as médias para a função de desenho
            desenhar_tela_avaliacao(tela, layout_avaliacao, perguntas_avaliacao, rects_avaliacao, respostas_avaliacao, mensagem_avaliacao, medias_gerais_avaliacao)
            
            if popup_avaliacao["ativo"]:
                desenhar_popup(tela, popup_avaliacao["titulo"], popup_avaliacao["mensagem"])

        elif estado_jogo == 'tela_rewards':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and rects_rewards['voltar_rewards'].collidepoint(e.pos): estado_jogo = 'tela_dificuldade'
            desenhar_tela_rewards(tela, rewards_system, nick_usuario, rects_rewards)
        
        elif estado_jogo == 'tela_ranking':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and rects_ranking['voltar_ranking'].collidepoint(e.pos): estado_jogo = 'tela_dificuldade'
            desenhar_tela_ranking(tela, rewards_system, rects_ranking)

        elif estado_jogo == 'tela_vitoria':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if rects_vitoria['sim'].collidepoint(e.pos):
                        estado_jogo = 'tela_dificuldade'
                    elif rects_vitoria['nao'].collidepoint(e.pos):
                        rodando = False
            desenhar_tela_vitoria(tela, rects_vitoria, pontos_finais, pontos_bonus_vitoria)

        elif estado_jogo == 'tela_game_over':
            for e in eventos:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if rects_game_over['sim'].collidepoint(e.pos):
                        parar_musica()
                        musica_labirinto_tocando = False 
                        inicializar_novo_jogo(dificuldade_selecionada)
                        estado_jogo = 'jogo'
                    elif rects_game_over['nao'].collidepoint(e.pos):
                        if player:
                            tempo_decorrido = (datetime.datetime.now() - tempo_inicio_partida).total_seconds()
                            player.stats["tempo_jogado"], player.stats["tempo_sobrevivencia"] = tempo_decorrido, tempo_decorrido
                            # Só adiciona pontos se não for visitante
                            if nick_usuario != "Visitante":
                                rewards_system.adicionar_pontos(nick_usuario, pontos, "partida")
                                rewards_system.atualizar_stats_acumuladas(nick_usuario, player.stats, vitoria=False)
                                rewards_system.verificar_tarefas_diarias(nick_usuario, player.stats)
                                rewards_system.verificar_conquistas(nick_usuario, player.stats)
                        parar_musica()
                        musica_labirinto_tocando = False 
                        estado_jogo = 'tela_inicial' # Volta para a tela inicial, não de dificuldade
            desenhar_tela_game_over(tela, rects_game_over, inimigo_colisor.nome if inimigo_colisor else "um inimigo")

        elif estado_jogo == 'jogo':
            if not player: # Segurança: se o player não existe, não rode o jogo
                estado_jogo = 'tela_dificuldade'
                continue

            dt = clock.get_time()
            
            if not musica_labirinto_tocando:
                tocar_musica_labirinto()
                musica_labirinto_tocando = True
            
            for e in eventos:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_h and not jogo_pausado: 
                        player.descartar_item()
                    # Tecla P para pausar/despausar
                    if e.key == pygame.K_p:
                        jogo_pausado = not jogo_pausado
                        # Pausar/despausar música
                        if jogo_pausado:
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                
                # Botão desistir
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                        mouse_x, mouse_y = e.pos
                        
                        # Verificar clique no botão desistir
                        if rect_desistir_jogo.collidepoint(mouse_x, mouse_y):
                            parar_musica()
                            musica_labirinto_tocando = False
                            jogo_pausado = False
                            estado_jogo = 'tela_dificuldade'
                            continue
            
            # Se o jogo está pausado, não atualiza a lógica
            if not jogo_pausado:
                # --- Movimentação contínua por teclado (estilo Pac-Man original) ---
                teclas = pygame.key.get_pressed()
                if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                    player.dir_x, player.dir_y = -1, 0
                elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                    player.dir_x, player.dir_y = 1, 0
                elif teclas[pygame.K_UP] or teclas[pygame.K_w]:
                    player.dir_x, player.dir_y = 0, -1
                elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
                    player.dir_x, player.dir_y = 0, 1
                
                # --- Atualização de Lógica ---
                player.atualizar_animacao(dt)
                player.mover()
                
                # (Sugestão #4) Lógica de coleta modificada
                pos_liberada = player.coletar(recursos)
                if pos_liberada:
                    posicoes_livres_dinamicas.add(pos_liberada)
                
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
                        parar_musica()
                        tocar_musica_game_over()
                        musica_labirinto_tocando = False
                        jogo_pausado = False
                        estado_jogo = 'tela_game_over'
                
                if novos_inimigos: inimigos.extend(novos_inimigos)
                if remover_ids: inimigos[:] = [ini for ini in inimigos if ini.id not in remover_ids]
                
                for centro in centros:
                    centro.atualizar_animacao(dt)
                    if player.grid_x == centro.x and player.grid_y == centro.y:
                        pontos += centro.receber_entrega(player.inventario, player.stats)
            else:
                # Quando pausado, apenas animações visuais continuam
                player.atualizar_animacao(dt)
                for centro in centros:
                    centro.atualizar_animacao(dt)
            
            # --- Desenho ---
            tela.fill(PRETO)
            desenhar_labirinto(tela)
            desenhar_recursos(tela, recursos)
            for centro in centros: centro.desenhar(tela)
            desenhar_rotulos_coleta(tela, centros, player)
            player.desenhar(tela)
            for inimigo in inimigos: inimigo.desenhar(tela)
            desenhar_hud(tela, player, centros, pontos)
            
            # Desenhar botão desistir no HUD
            pygame.draw.rect(tela, (150, 50, 50), rect_desistir_jogo, border_radius=6)
            pygame.draw.rect(tela, (200, 80, 80), rect_desistir_jogo, width=2, border_radius=6)
            fonte_desistir = pygame.font.SysFont(None, 26)
            texto_desistir = fonte_desistir.render("Desistir", True, BRANCO)
            tela.blit(texto_desistir, texto_desistir.get_rect(center=rect_desistir_jogo.center))
            
            # Overlay de pausa
            if jogo_pausado:
                # Overlay semi-transparente
                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                tela.blit(overlay, (0, 0))
                
                # Mensagem de pausa
                fonte_pausa_titulo = pygame.font.SysFont("bahnschrift", 60, bold=True)
                fonte_pausa_info = pygame.font.SysFont(None, 30)
                
                texto_pausado = fonte_pausa_titulo.render("JOGO PAUSADO", True, COR_OURO)
                texto_continuar = fonte_pausa_info.render("Pressione [P] para continuar", True, BRANCO)
                
                tela.blit(texto_pausado, texto_pausado.get_rect(center=(LARGURA//2, ALTURA//2 - 30)))
                tela.blit(texto_continuar, texto_continuar.get_rect(center=(LARGURA//2, ALTURA//2 + 30)))

            # --- Verificação de Vitória ---
            if all(c.nivel_atual >= c.nivel_max for c in centros):
                tempo_decorrido = (datetime.datetime.now() - tempo_inicio_partida).total_seconds()
                player.stats["tempo_jogado"] = tempo_decorrido
                player.stats["tempo_sobrevivencia"] = tempo_decorrido
                player.stats["vitorias"] = 1
                player.stats["centros_completos"] = len(centros)
                
                pontos_finais = pontos
                pontos_bonus_vitoria = 500
                pontos_totais_vitoria = pontos_finais + pontos_bonus_vitoria

                # Só adiciona pontos se não for visitante
                if nick_usuario != "Visitante":
                    rewards_system.adicionar_pontos(nick_usuario, pontos_totais_vitoria, "vitoria")
                    rewards_system.atualizar_stats_acumuladas(nick_usuario, player.stats, vitoria=True)
                    rewards_system.verificar_tarefas_diarias(nick_usuario, player.stats)
                    rewards_system.verificar_conquistas(nick_usuario, player.stats)
                
                parar_musica()
                musica_labirinto_tocando = False
                estado_jogo = 'tela_vitoria'

        # Atualiza a tela
        pygame.display.flip()
        clock.tick(FPS)

    # --- Fim do Jogo ---
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()