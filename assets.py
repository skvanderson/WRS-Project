"""
Arquivo de Assets (recursos.py)

Responsável por carregar, processar e preparar todos os
recursos visuais (imagens, spritesheets) do jogo.
Fornece fallbacks (placeholders) caso os assets não sejam encontrados.
"""

import pygame
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Importa constantes necessárias
from config import (
    BASE_DIR, ASSETS_DIR, ANIM32_DIR, CENTROS48_DIR, CENTROS_DIR,
    AMARELO, VERMELHO_CRISE, CINZA, ROXO,
    COR_MOEDA, COR_ALIMENTO, COR_LIVRO, COR_TIJOLO
)

# =======================
#   FUNÇÕES DE BASE
# =======================

def _segura_surface(tamanho: Tuple[int,int], cor=(255,0,0), shape="circle") -> pygame.Surface:
    """Cria um placeholder (Surface) caso um asset falhe em carregar."""
    surf = pygame.Surface(tamanho, pygame.SRCALPHA)
    cx, cy = tamanho[0]//2, tamanho[1]//2
    if shape == "circle":
        pygame.draw.circle(surf, cor, (cx, cy), min(cx, cy)-2)
    else:
        pygame.draw.rect(surf, cor, (2,2,tamanho[0]-4,tamanho[1]-4), border_radius=4)
    return surf

def aplicar_cor_surface(surface: pygame.Surface, cor: Tuple[int,int,int]) -> pygame.Surface:
    """Retorna uma copia da surface original com a cor RGB substituida, mantendo a transparencia."""
    recolorida = surface.copy()
    recolorida.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    recolorida.fill((*cor, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return recolorida

def _resolve_asset_path(relative) -> Path:
    """Resolve um caminho relativo para um caminho absoluto baseado no BASE_DIR."""
    path_obj = Path(relative)
    if path_obj.is_absolute():
        return path_obj
    return BASE_DIR / path_obj

def _load_image(path: Path) -> Optional[pygame.Surface]:
    """Carrega uma imagem de forma segura, retornando None em caso de falha."""
    resolved = _resolve_asset_path(path)
    if not resolved.exists():
        # print(f"[ASSET_WARN] Arquivo nao encontrado: {resolved}")
        return None
    try:
        return pygame.image.load(str(resolved)).convert_alpha()
    except Exception as e:
        print(f"[ASSET_ERROR] Erro ao carregar imagem {resolved}: {e}")
        return None

# =======================
#   CARREGADORES DE SPRITES
# =======================

def cortar_spritesheet(path:str, frame_w:int, frame_h:int, num_frames:int=None, escala:Tuple[int,int]=None) -> List[pygame.Surface]:
    """Corta um spritesheet em uma lista de frames."""
    sheet = _load_image(path)
    if sheet is None:
        return []
    sw, sh = sheet.get_size()
    cols, rows = sw // frame_w, sh // frame_h
    frames = []
    count = cols * rows if num_frames is None else min(num_frames, cols*rows)
    
    for i in range(count):
        c, r = i % cols, i // cols
        rect = pygame.Rect(c*frame_w, r*frame_h, frame_w, frame_h)
        try:
            frame = sheet.subsurface(rect).copy()
            if escala:
                frame = pygame.transform.smoothscale(frame, escala)
            frames.append(frame)
        except ValueError as e:
            print(f"[ASSET_WARN] Erro ao cortar subsurface em {path}: {e}")
            break
    return frames

def carregar_sequencia_pasta(pasta, base: str, num_frames: int, tamanho: Tuple[int,int]) -> List[pygame.Surface]:
    """Carrega uma sequência de imagens de uma pasta (ex: anim_0.png, anim_1.png)."""
    frames = []
    pasta_path = _resolve_asset_path(pasta)
    for i in range(num_frames):
        arq = pasta_path / f"{base}_{i}.png"
        img = _load_image(arq)
        if img:
            img = pygame.transform.smoothscale(img, tamanho)
            frames.append(img)
    return frames

def carregar_pacman_frames(tamanho=(32,32)) -> Dict[str, List[pygame.Surface]]:
    """Carrega os frames do Pac-Man, com múltiplos fallbacks."""
    # 1. Tentar spritesheet
    sheet_path = ASSETS_DIR / "pacman" / "pacman_sheet.png"
    sheet_frames = cortar_spritesheet(sheet_path, 32, 32, escala=tamanho)
    if sheet_frames and len(sheet_frames) >= 16:
        def take(a, b): return sheet_frames[a:b]
        direita = take(0,4)
        esquerda = take(4,8)
        cima = take(8,12)
        baixo = take(12,16)
        return {"direita":direita, "esquerda":esquerda, "cima":cima, "baixo":baixo}

    # 2. Tentar sequência de pasta (usando a de 32x32 como base)
    seq_dir = ANIM32_DIR / "pacman"
    direita = carregar_sequencia_pasta(seq_dir, "pacman_right", 4, tamanho)
    if direita:
        esquerda = [pygame.transform.flip(f, True, False) for f in direita]
        cima = [pygame.transform.rotate(f, 90) for f in direita]
        baixo = [pygame.transform.rotate(f, -90) for f in direita]
        return {"direita":direita, "esquerda":esquerda, "cima":cima, "baixo":baixo}

    # 3. Fallback: Placeholder
    print("[ASSET_WARN] Frames do Pac-Man nao encontrados. Usando placeholder.")
    base = _segura_surface(tamanho, AMARELO, "circle")
    return {"direita":[base], "esquerda":[base], "cima":[base], "baixo":[base]}

def carregar_fantasma_frames(nome_interno:str, tamanho=(48,48), invisivel=False) -> List[pygame.Surface]:
    """Carrega os frames dos fantasmas, com múltiplos fallbacks."""
    # 1. Tentar spritesheet (48x48)
    map_sheet = {
        "Desemprego": "desemprego.png",
        "Desigualdade": "desigualdade.png",
        "Falta de Acesso": "falta_acesso_visible.png" if not invisivel else "falta_acesso_invisivel.png",
        "Crise Economica": "crise_economica.png",
    }
    sheet_key = map_sheet.get(nome_interno)
    if sheet_key:
        path = ASSETS_DIR / 'ghosts' / sheet_key
        frames = cortar_spritesheet(path, 48, 48, escala=tamanho)
        if frames: return frames if len(frames) >= 2 else frames*2
    
    # 2. Tentar sequência de pasta (32x32)
    pasta_map = {
        "Desemprego": (ANIM32_DIR / "ghost_desemprego", "ghost_desemprego"),
        "Crise Economica": (ANIM32_DIR / "ghost_crise_economica", "ghost_crise_economica"),
        "Desigualdade": (ANIM32_DIR / "ghost_desigualdade_small", "ghost_desigualdade_small"),
        "Falta de Acesso": (ANIM32_DIR / ("ghost_falta_acesso_visible" if not invisivel else "ghost_falta_acesso_invisivel"),
                            "ghost_falta_acesso_visible" if not invisivel else "ghost_falta_acesso_invisivel")
    }
    pasta, base = pasta_map.get(nome_interno, (None, None))
    if pasta:
        seq = carregar_sequencia_pasta(pasta, base, 2, tamanho)
        if seq: return seq

    # 3. Fallback: Placeholder
    print(f"[ASSET_WARN] Frames para '{nome_interno}' (invisivel={invisivel}) nao encontrados. Usando placeholder.")
    cor = ROXO if nome_interno=="Desigualdade" else (VERMELHO_CRISE if nome_interno=="Crise Economica" else CINZA)
    if invisivel: cor = (120,120,120,120)
    return [_segura_surface(tamanho, cor, "circle"), _segura_surface(tamanho, cor, "circle")]

def carregar_item(nome: str, tamanho: Tuple[int, int]) -> pygame.Surface:
    """Carrega a imagem de um item/recurso, com fallback."""
    nome_lower = nome.lower()
    # Mapeamento para nomes de arquivos inconsistentes
    nome_arquivo_map = {
        "moeda": "moeda",
        "alimento": "alimento",
        "livro": "livro",
        "tijolo": "tijolos" # Nome do arquivo é 'tijolos.png'
    }
    nome_arquivo = nome_arquivo_map.get(nome_lower, nome_lower)

    caminhos = [
        ANIM32_DIR / "itens" / f"item_{nome_arquivo}.png", 
        ASSETS_DIR / "items" / f"{nome_arquivo}.png"
    ]
    
    for arq in caminhos:
        img = _load_image(arq)
        if img is not None:
            img = pygame.transform.smoothscale(img, tamanho)
            # Aplica cor por cima da textura para diferenciar
            if nome_lower == "moeda":
                return aplicar_cor_surface(img, COR_MOEDA)
            if nome_lower == "alimento":
                return aplicar_cor_surface(img, COR_ALIMENTO)
            return img
            
    # Fallback: Placeholder
    print(f"[ASSET_WARN] Imagem para item '{nome}' nao encontrada. Usando placeholder.")
    cor_padrao = {
        "moeda": COR_MOEDA,
        "alimento": COR_ALIMENTO,
        "livro": COR_LIVRO,
        "tijolo": COR_TIJOLO
    }.get(nome_lower, COR_ALIMENTO)
    return _segura_surface(tamanho, cor_padrao, "circle")

def carregar_centro(prefixo: str, tamanho: Tuple[int, int]) -> List[pygame.Surface]:
    """Carrega os 3 frames de animação de um centro comunitário."""
    tentativas = [
        [CENTROS48_DIR / f"{prefixo}_{i}.png" for i in range(3)],
        [CENTROS_DIR / f"{prefixo}_{i}.png" for i in range(3)]
    ]
    for lista in tentativas:
        imgs = [_load_image(arq) for arq in lista]
        if all(imgs):
            return [pygame.transform.smoothscale(img, tamanho) for img in imgs]
            
    # Fallback: Placeholder
    print(f"[ASSET_WARN] Frames para centro '{prefixo}' nao encontrados. Usando placeholder.")
    cor_map = {"escola": (0,0,255), "hospital": (255,0,0), "mercado": (0,255,0), "moradia": (160,82,45)}
    return [_segura_surface(tamanho, cor_map.get(prefixo, (0,255,0)), "rect") for _ in range(3)]