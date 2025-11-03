"""
Arquivo de Entidades (classes.py)

Define as classes principais do jogo (sprites e objetos interativos):
- Player
- Inimigo
- CentroComunitario
"""

import pygame
import random
import datetime
from typing import Dict, List, Tuple, Optional

# Importa constantes e layouts
from config import (
    TAM_CELULA, COLUNAS, LINHAS_LABIRINTO, LABIRINTO_LAYOUT, FPS,
    AMARELO, 
    # --- CORREÇÃO ADICIONADA AQUI ---
    PRETO, CINZA, ROXO, VERMELHO_CRISE 
    # --- FIM DA CORREÇÃO ---
)

# Importa carregadores de assets
from assets import (
    carregar_pacman_frames, carregar_fantasma_frames, carregar_centro
)

# --- Classes do Jogo ---

class Player:
    def __init__(self, x, y):
        self.px, self.py = x * TAM_CELULA, y * TAM_CELULA
        self.dir_x, self.dir_y, self.vel_x, self.vel_y = 0, 0, 0, 0
        self.velocidade = 3
        self.inventario, self.capacidade_inventario = [], 5
        self.caminho = []
        self.stats = {
            "recursos_coletados": 0,
            "itens_entregues": 0,
            "tempo_jogado": 0,
            "tempo_sobrevivencia": 0,
            "partidas_jogadas": 0,
            "vitorias": 0,
            "centros_completos": 0,
            "inicio_partida": datetime.datetime.now()
        }
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
        # Resetar stats da partida (mas manter estrutura)
        self.stats["recursos_coletados"] = 0
        self.stats["itens_entregues"] = 0
        self.stats["tempo_jogado"] = 0
        self.stats["tempo_sobrevivencia"] = 0
        self.stats["partidas_jogadas"] = 0
        self.stats["vitorias"] = 0
        self.stats["centros_completos"] = 0
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
        
        # Sistema de movimento contínuo (estilo Pac-Man original)
        if esta_alinhado:
            # Movimento contínuo por teclado
            if self.dir_x != 0 or self.dir_y != 0:
                # Tenta mudar para a nova direção solicitada
                prox_grid_x, prox_grid_y = self.grid_x + self.dir_x, self.grid_y + self.dir_y
                if not self.colide_parede(prox_grid_x, prox_grid_y): 
                    self.vel_x, self.vel_y = self.dir_x, self.dir_y
            # Se não pode ir na nova direção, continua na direção atual
            elif self.vel_x == 0 and self.vel_y == 0:
                # Está parado e tentando ir em direção bloqueada
                pass
            
            # Verifica se pode continuar na direção atual
            if self.vel_x != 0 or self.vel_y != 0:
                prox_grid_x, prox_grid_y = self.grid_x + self.vel_x, self.grid_y + self.vel_y
                if self.colide_parede(prox_grid_x, prox_grid_y):
                    # Para se encontrar uma parede na direção atual
                    self.px, self.py = self.grid_x * TAM_CELULA, self.grid_y * TAM_CELULA
                    self.vel_x, self.vel_y = 0, 0
        
        # Move o jogador
        self.px += self.vel_x * self.velocidade
        self.py += self.vel_y * self.velocidade
        
        self.atualizar_direcao()
        
    def colide_parede(self, x, y): return not (0 <= x < COLUNAS and 0 <= y < LINHAS_LABIRINTO and LABIRINTO_LAYOUT[y][x] != 1)
    
    def coletar(self, recursos: List[Dict]) -> Optional[Tuple[int, int]]:
        """
        Tenta coletar um recurso.
        (Implementação da Sugestão #4 - Otimização)
        Retorna a posição (x, y) do recurso coletado se for bem-sucedido,
        para que o game loop possa adicionar a posição de volta ao 
        conjunto de posições livres.
        """
        if len(self.inventario) < self.capacidade_inventario:
            for recurso in recursos[:]:
                if recurso['x'] == self.grid_x and recurso['y'] == self.grid_y:
                    self.inventario.append(recurso['tipo'])
                    self.stats["recursos_coletados"] += 1
                    recursos.remove(recurso)
                    return (recurso['x'], recurso['y']) # Retorna a posição liberada
        return None # Nada foi coletado

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
    
    def mover(self, player: Player):
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
        return not (0 <= x < COLUNAS and 0 <= y < LINHAS_LABIRINTO and LABIRINTO_LAYOUT[y][x] != 1)

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
        self.efeitos = [] # Lista para efeitos visuais
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
        
        # Desenha o sprite animado
        if self.frames and self.frames[self.anim_index]:
            frame = self.frames[self.anim_index]
            img_rect = frame.get_rect(center=(px + TAM_CELULA//2, py + TAM_CELULA//2))
            surface.blit(frame, img_rect)
        else: # Fallback
            pygame.draw.rect(surface, self.cor, (px+2, py+2, TAM_CELULA-4, TAM_CELULA-4), border_radius=4)
        
        # Barra de progresso
        largura_barra, altura_barra = TAM_CELULA - 8, 5
        progresso = (self.nivel_atual / self.nivel_max) * largura_barra
        # AQUI É ONDE O 'PRETO' É USADO
        pygame.draw.rect(surface, PRETO, (px+4, py+TAM_CELULA-12, largura_barra, altura_barra))
        pygame.draw.rect(surface, AMARELO, (px+4, py+TAM_CELULA-12, progresso, altura_barra))

        # Desenha efeitos (ex: brilho ao entregar)
        for efeito in list(self.efeitos):
            efeito["tempo"] -= 1
            if efeito["tempo"] <= 0:
                self.efeitos.remove(efeito)
                continue
            intensidade = max(30, 200 * efeito["tempo"] / efeito["duracao"])
            raio = TAM_CELULA + (efeito["duracao"] - efeito["tempo"]) * 2
            glow = pygame.Surface((raio*2, raio*2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 223, 0, int(intensidade)), (raio, raio), raio, width=4)
            surface.blit(glow, (px + TAM_CELULA//2 - raio, py + TAM_CELULA//2 - raio), special_flags=pygame.BLEND_RGBA_ADD)

    def receber_entrega(self, inventario_jogador, player_stats=None):
        recursos_entregues = sum(1 for item in inventario_jogador if item == self.recurso_necessario)
        if recursos_entregues > 0 and self.nivel_atual < self.nivel_max:
            inventario_jogador[:] = [item for item in inventario_jogador if item != self.recurso_necessario]
            self.nivel_atual = min(self.nivel_max, self.nivel_atual + recursos_entregues)
            if player_stats: player_stats["itens_entregues"] += recursos_entregues
            self.efeitos.append({"tempo": 30, "duracao": 30}) 
            return recursos_entregues * 20
        return 0