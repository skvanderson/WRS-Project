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
        # Tarefas diárias com ícones e metadados
        self.daily_tasks = {
            "coletar_10_recursos": {
                "icone": "🎯",
                "nome": "Coletor",
                "descricao": "Colete 10 recursos",
                "requisito": 10,
                "stat_key": "recursos_coletados",
                "pontos": 50,
                "concluida": False
            },
            "entregar_5_itens": {
                "icone": "📦",
                "nome": "Entregador",
                "descricao": "Entregue 5 itens nos centros",
                "requisito": 5,
                "stat_key": "itens_entregues",
                "pontos": 75,
                "concluida": False
            },
            "jogar_3_partidas": {
                "icone": "🎮",
                "nome": "Jogador",
                "descricao": "Jogue 3 partidas",
                "requisito": 3,
                "stat_key": "partidas_jogadas",
                "pontos": 100,
                "concluida": False
            },
            "sobreviver_2_minutos": {
                "icone": "⏱️",
                "nome": "Sobrevivente",
                "descricao": "Sobreviva por 2 minutos",
                "requisito": 120,
                "stat_key": "tempo_sobrevivencia",
                "pontos": 60,
                "concluida": False
            }
        }
        # Conquistas permanentes com ícones e descrições detalhadas
        self.achievements = {
            "primeira_vitoria": {
                "icone": "🏆",
                "nome": "Primeira Vitoria",
                "descricao": "Venca uma partida",
                "requisito": 1,
                "stat_key": "vitorias",
                "pontos": 200,
                "desbloqueada": False
            },
            "colecionador": {
                "icone": "💎",
                "nome": "Colecionador",
                "descricao": "Colete 50 recursos ao longo do tempo",
                "requisito": 50,
                "stat_key": "recursos_coletados_total",
                "pontos": 150,
                "desbloqueada": False
            },
            "construtor": {
                "icone": "🏗️",
                "nome": "Construtor",
                "descricao": "Complete todos os centros comunitarios em uma partida",
                "requisito": 4,
                "stat_key": "centros_completos",
                "pontos": 300,
                "desbloqueada": False
            },
            "sobrevivente": {
                "icone": "🛡️",
                "nome": "Sobrevivente",
                "descricao": "Sobreviva por 5 minutos em uma partida",
                "requisito": 300,
                "stat_key": "tempo_sobrevivencia",
                "pontos": 250,
                "desbloqueada": False
            }
        }
        # Notificações pendentes
        self.notificacoes = []
    
    def carregar_rewards(self) -> Dict:
        try:
            with open(ARQUIVO_REWARDS, 'r', encoding='utf-8') as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): return {}
    
    def salvar_rewards(self):
        with open(ARQUIVO_REWARDS, 'w', encoding='utf-8') as f: json.dump(self.rewards_data, f, indent=4, ensure_ascii=False)
    
    def obter_usuario_rewards(self, username: str) -> Dict:
        if username not in self.rewards_data:
            self.rewards_data[username] = {
                "pontos_totais": 0,
                "nivel": 1,
                "conquistas": {},
                "tarefas_diarias": {},
                "stats_acumuladas": {  # Novo: stats que persistem
                    "partidas_jogadas": 0,
                    "vitorias": 0,
                    "derrotas": 0,
                    "recursos_coletados_total": 0,
                    "itens_entregues_total": 0,
                    "tempo_jogado_total": 0
                },
                "ultima_atualizacao": datetime.datetime.now().isoformat(),
                "historico_partidas": []
            }
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
        stats_acum = user_data.get("stats_acumuladas", {})
        
        # Tarefa: Coletar 10 recursos (da partida atual)
        if stats.get("recursos_coletados", 0) >= 10 and not tarefas["coletar_10_recursos"]["concluida"]: 
            tarefas["coletar_10_recursos"]["concluida"] = True
            self.adicionar_pontos(username, 50, "tarefa_diaria")
        
        # Tarefa: Entregar 5 itens (da partida atual)
        if stats.get("itens_entregues", 0) >= 5 and not tarefas["entregar_5_itens"]["concluida"]: 
            tarefas["entregar_5_itens"]["concluida"] = True
            self.adicionar_pontos(username, 75, "tarefa_diaria")
        
        # Tarefa: Jogar 3 partidas (usa stats acumuladas)
        partidas_acumuladas = stats_acum.get("partidas_jogadas", 0)
        if partidas_acumuladas >= 3 and not tarefas["jogar_3_partidas"]["concluida"]: 
            tarefas["jogar_3_partidas"]["concluida"] = True
            self.adicionar_pontos(username, 100, "tarefa_diaria")
        
        # Tarefa: Sobreviver 2 minutos (da partida atual)
        if stats.get("tempo_sobrevivencia", 0) >= 120 and not tarefas["sobreviver_2_minutos"]["concluida"]: 
            tarefas["sobreviver_2_minutos"]["concluida"] = True
            self.adicionar_pontos(username, 60, "tarefa_diaria")
        
        self.salvar_rewards()
    
    def verificar_conquistas(self, username: str, stats: Dict):
        user_data = self.obter_usuario_rewards(username)
        conquistas = user_data.setdefault("conquistas", {})
        stats_acum = user_data.get("stats_acumuladas", {})
        
        for achievement_id, achievement in self.achievements.items():
            if achievement_id not in conquistas: 
                conquistas[achievement_id] = {"desbloqueada": False, "data": None}
            if not conquistas[achievement_id]["desbloqueada"]:
                desbloqueou = False
                
                # Primeira Vitória: verifica stats da partida atual
                if achievement_id == "primeira_vitoria" and stats.get("vitorias", 0) >= 1: 
                    desbloqueou = True
                
                # Colecionador: usa stats acumuladas (50 recursos ao longo do tempo)
                elif achievement_id == "colecionador": 
                    recursos_total = stats_acum.get("recursos_coletados_total", 0)
                    if recursos_total >= 50:
                        desbloqueou = True
                
                # Construtor: completa todos os 4 centros em uma partida
                elif achievement_id == "construtor" and stats.get("centros_completos", 0) >= 4: 
                    desbloqueou = True
                
                # Sobrevivente: 5 minutos em uma partida
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
        # Filtra visitantes e ordena por pontos
        ranking = [(u, d.get("pontos_totais", 0)) for u, d in self.rewards_data.items() if u != "Visitante"]
        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking[:limite]
    
    def obter_progresso_nivel(self, username: str) -> Tuple[int, int, float]:
        """Retorna (xp_atual, xp_proximo_nivel, percentual)"""
        user_data = self.obter_usuario_rewards(username)
        pontos = user_data["pontos_totais"]
        nivel_atual = user_data["nivel"]
        
        xp_nivel_atual = (nivel_atual - 1) * 1000
        xp_proximo_nivel = nivel_atual * 1000
        xp_atual_no_nivel = pontos - xp_nivel_atual
        xp_necessario_nivel = 1000
        
        percentual = (xp_atual_no_nivel / xp_necessario_nivel) * 100
        return (xp_atual_no_nivel, xp_necessario_nivel, percentual)
    
    def obter_progresso_tarefa(self, username: str, task_id: str, stats: Dict) -> Tuple[int, int]:
        """Retorna (progresso_atual, requisito_total)"""
        if task_id not in self.daily_tasks:
            return (0, 0)
        
        tarefa = self.daily_tasks[task_id]
        stat_key = tarefa.get("stat_key", "")
        requisito = tarefa.get("requisito", 0)
        progresso = stats.get(stat_key, 0)
        
        return (min(progresso, requisito), requisito)
    
    def obter_progresso_conquista(self, username: str, achievement_id: str, stats: Dict) -> Tuple[int, int]:
        """Retorna (progresso_atual, requisito_total)"""
        if achievement_id not in self.achievements:
            return (0, 0)
        
        conquista = self.achievements[achievement_id]
        stat_key = conquista.get("stat_key", "")
        requisito = conquista.get("requisito", 0)
        
        # Para conquistas acumuladas, usa stats_acumuladas
        user_data = self.obter_usuario_rewards(username)
        stats_acum = user_data.get("stats_acumuladas", {})
        
        if stat_key in stats_acum:
            progresso = stats_acum.get(stat_key, 0)
        else:
            progresso = stats.get(stat_key, 0)
        
        return (min(progresso, requisito), requisito)
    
    def atualizar_stats_acumuladas(self, username: str, stats: Dict, vitoria: bool = False):
        """Atualiza estatísticas acumuladas do jogador"""
        user_data = self.obter_usuario_rewards(username)
        stats_acum = user_data.setdefault("stats_acumuladas", {})
        
        # Incrementa contadores
        stats_acum["partidas_jogadas"] = stats_acum.get("partidas_jogadas", 0) + 1
        if vitoria:
            stats_acum["vitorias"] = stats_acum.get("vitorias", 0) + 1
        else:
            stats_acum["derrotas"] = stats_acum.get("derrotas", 0) + 1
        
        # Acumula valores
        stats_acum["recursos_coletados_total"] = stats_acum.get("recursos_coletados_total", 0) + stats.get("recursos_coletados", 0)
        stats_acum["itens_entregues_total"] = stats_acum.get("itens_entregues_total", 0) + stats.get("itens_entregues", 0)
        stats_acum["tempo_jogado_total"] = stats_acum.get("tempo_jogado_total", 0) + stats.get("tempo_jogado", 0)
        
        self.salvar_rewards()
    
    def adicionar_notificacao(self, tipo: str, titulo: str, mensagem: str, pontos: int = 0):
        """Adiciona uma notificação para ser exibida"""
        self.notificacoes.append({
            "tipo": tipo,  # "pontos", "tarefa", "conquista", "nivel"
            "titulo": titulo,
            "mensagem": mensagem,
            "pontos": pontos,
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    def obter_notificacoes(self) -> List[Dict]:
        """Retorna e limpa as notificações pendentes"""
        notifs = self.notificacoes.copy()
        self.notificacoes.clear()
        return notifs


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