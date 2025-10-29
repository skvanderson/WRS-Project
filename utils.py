"""
Arquivo de Utilitários (ferramentas.py)

Contém várias funções de suporte e classes de sistema:
- Controle de música e som
- Carregamento e salvamento de dados (JSON)
- Sistema de Recompensas (RewardsSystem)
- Algoritmo de Pathfinding (BFS)
- Funções de ajuda para formulários de UI
- Gerenciamento de dados de avaliação
"""

import pygame
import json
import datetime
import sys
from pathlib import Path
from collections import deque
from typing import Dict, List, Tuple

# Importa constantes necessárias
from config import (
    ARQUIVO_USUARIOS, ARQUIVO_REWARDS, ARQUIVO_AVALIACOES,
    MUSICA_LABIRINTO, MUSICA_GAME_OVER,
    COLUNAS, LINHAS_LABIRINTO
)

# =======================
#   CONTROLE DE MUSICA
# =======================

def tocar_musica_labirinto():
    """Toca a musica de fundo do labirinto em loop"""
    try:
        pygame.mixer.music.load(MUSICA_LABIRINTO)
        pygame.mixer.music.set_volume(0.3)  # Volume baixo para nao atrapalhar
        pygame.mixer.music.play(-1)  # -1 = loop infinito
    except pygame.error as e:
        print(f"[ERRO] Erro ao carregar musica do labirinto: {e}")
    except Exception as e:
        print(f"[ERRO] Erro inesperado ao tocar musica do labirinto: {e}")

def tocar_musica_game_over():
    """Toca a musica de game over uma vez, comecando em 5 segundos"""
    try:
        pygame.mixer.music.load(MUSICA_GAME_OVER)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(0, start=5.0)  # 0 = tocar uma vez, start=5.0 = comecar em 5 segundos
    except pygame.error as e:
        print(f"[ERRO] Erro ao carregar musica de game over: {e}")
        print("Tentando usar musica do labirinto como fallback...")
        # Fallback: usar musica do labirinto se game over falhar
        try:
            pygame.mixer.music.load(MUSICA_LABIRINTO)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(0)
            print(f"[LOG] Usando musica do labirinto como fallback")
        except:
            pygame.mixer.music.stop()
    except Exception as e:
        print(f"[ERRO] Erro inesperado ao tocar musica de game over: {e}")
        pygame.mixer.music.stop()

def parar_musica():
    """Para a musica atual"""
    try:
        pygame.mixer.music.stop()
    except Exception as e:
        print(f"[ERRO] Erro ao parar musica: {e}")

# =======================
#   GERENCIAMENTO DE DADOS (JSON)
# =======================

def carregar_usuarios():
    try:
        with open(ARQUIVO_USUARIOS, 'r') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return {}

def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, 'w') as f: json.dump(usuarios, f, indent=4)

def carregar_avaliacoes():
    try:
        with open(ARQUIVO_AVALIACOES, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and "respostas" in data:
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {"respostas": []}

def salvar_avaliacoes(dados):
    with open(ARQUIVO_AVALIACOES, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def calcular_medias_avaliacao(dados_avaliacao, quantidade_perguntas: int):
    soma = [0] * quantidade_perguntas
    contagem = [0] * quantidade_perguntas
    for resposta in dados_avaliacao.get("respostas", []):
        notas = resposta.get("notas", [])
        for i, nota in enumerate(notas[:quantidade_perguntas]):
            if isinstance(nota, (int, float)) and 1 <= nota <= 5:
                soma[i] += nota
                contagem[i] += 1
    medias = []
    for i in range(quantidade_perguntas):
        medias.append((soma[i] / contagem[i]) if contagem[i] else 0)
    return medias, contagem

# =======================
#   SISTEMA DE RECOMPENSAS
# =======================

class RewardsSystem:
    def __init__(self):
        self.rewards_data = self.carregar_rewards()
        self.daily_tasks = {"coletar_10_recursos": {"descricao": "Colete 10 recursos", "pontos": 50, "concluida": False},"entregar_5_itens": {"descricao": "Entregue 5 itens nos centros", "pontos": 75, "concluida": False},"jogar_3_partidas": {"descricao": "Jogue 3 partidas", "pontos": 100, "concluida": False},"sobreviver_2_minutos": {"descricao": "Sobreviva por 2 minutos", "pontos": 60, "concluida": False}}
        self.achievements = {"primeira_vitoria": {"nome": "Primeira Vitoria", "descricao": "Venca uma partida", "pontos": 200, "desbloqueada": False},"colecionador": {"nome": "Colecionador", "descricao": "Colete 50 recursos", "pontos": 150, "desbloqueada": False},"construtor": {"nome": "Construtor", "descricao": "Complete 3 centros comunitarios", "pontos": 300, "desbloqueada": False},"sobrevivente": {"nome": "Sobrevivente", "descricao": "Sobreviva 5 minutos", "pontos": 250, "desbloqueada": False}}
    
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


# =======================
#   PATHFINDING (BFS)
# =======================

def encontrar_caminho(labirinto: List[List[int]], inicio: Tuple[int, int], fim: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Encontra o caminho mais curto usando Breadth-First Search (BFS)"""
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

# =======================
#   HELPERS DE UI (Formulário)
# =======================

def handle_form_input(event: pygame.event.Event, nick: str, senha: str, campo_ativo: str) -> Tuple[str, str, str]:
    """
    Função unificada para lidar com a entrada de texto nos formulários
    de login e cadastro. (Implementação da Sugestão #3 - DRY)
    """
    if event.key == pygame.K_BACKSPACE:
        if campo_ativo == 'nick':
            nick = nick[:-1]
        elif campo_ativo == 'senha':
            senha = senha[:-1]
    elif event.key == pygame.K_TAB:
        campo_ativo = 'senha' if campo_ativo == 'nick' else 'nick'
    else:
        # Garante que é um caractere digitável e limita o tamanho
        if len(event.unicode) > 0 and event.unicode.isprintable(): 
            if campo_ativo == 'nick' and len(nick) < 20: 
                nick += event.unicode
            elif campo_ativo == 'senha' and len(senha) < 20:
                senha += event.unicode
    return nick, senha, campo_ativo