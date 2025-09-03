import pygame as gm
import random as rd
import time
from linear_agent import LinearAgent
from AggressiveAgent import AggressiveAgent

# --- pygame setup ---
gm.init()
screen = gm.display.set_mode((1280, 720))
clock = gm.time.Clock()

# --- configuração do jogo ---
bolinha_raio = 40
roda_raio = 50

# --- criar IAs ---
agent1 = AggressiveAgent(n_features=2, lr=0.01)
agent1.load()
agent2 = LinearAgent(n_features=2, lr=0.01)
agent2.load()

def limitar_posicao(pos, raio, screen):
    """Garante que a bolinha fique dentro dos limites da tela."""
    pos.x = max(raio, min(screen.get_width() - raio, pos.x))
    pos.y = max(raio, min(screen.get_height() - raio, pos.y))
    return pos

def jogar_partida(time_end=15, treinar=True):
    # --- inicialização ---
    player1_pos = gm.Vector2(screen.get_width() / 3, screen.get_height() / 2)
    player2_pos = gm.Vector2(2 * screen.get_width() / 3, screen.get_height() / 2)

    escolha = rd.choice([1, 2])
    tempo_invulneravel = 1000  # ms
    invulneravel_ate = 0

    time_start = time.time()
    dt = 0
    running = True

    while running:
        for event in gm.event.get():
            if event.type == gm.QUIT:
                running = False

        # --- IA Player1 ---
        if escolha == 1:  # player1 tem a roda → perseguir
            dx1 = player2_pos.x - player1_pos.x
            dy1 = player2_pos.y - player1_pos.y
        else:  # fugir
            dx1 = player1_pos.x - player2_pos.x
            dy1 = player1_pos.y - player2_pos.y
        move1 = agent1.decide_action([dx1, dy1]) * 300 * dt
        player1_pos += gm.Vector2(move1[0], move1[1])

        # --- IA Player2 ---
        if escolha == 2:  # player2 tem a roda → perseguir
            dx2 = player1_pos.x - player2_pos.x
            dy2 = player1_pos.y - player2_pos.y
        else:  # fugir
            dx2 = player2_pos.x - player1_pos.x
            dy2 = player2_pos.y - player1_pos.y
        move2 = agent2.decide_action([dx2, dy2]) * 300 * dt
        player2_pos += gm.Vector2(move2[0], move2[1])

        # --- limitar posições ---
        player1_pos = limitar_posicao(player1_pos, bolinha_raio, screen)
        player2_pos = limitar_posicao(player2_pos, bolinha_raio, screen)

        # --- colisão e atualização de recompensas ---
        if player1_pos.distance_to(player2_pos) <= bolinha_raio * 2:
            agora = gm.time.get_ticks()
            if agora > invulneravel_ate:
                escolha = 2 if escolha == 1 else 1
                invulneravel_ate = agora + tempo_invulneravel

                # Atualiza recompensas sem destruir pesos
                if escolha == 1:
                    agent1.update([dx1, dy1], 1)  # quem ganhou recebe +1
                    agent2.update([dx2, dy2], 0)  # quem perdeu recebe 0
                else:
                    agent1.update([dx1, dy1], 0)
                    agent2.update([dx2, dy2], 1)

            # empurrar para não sobrepor
            overlap = bolinha_raio * 2 - player1_pos.distance_to(player2_pos)
            if player1_pos != player2_pos:
                direction = (player1_pos - player2_pos).normalize()
                player1_pos += direction * (overlap / 2)
                player2_pos -= direction * (overlap / 2)

        # --- desenhar jogadores e roda ---
        screen.fill("white")
        gm.draw.circle(screen, "red", player1_pos, bolinha_raio)
        gm.draw.circle(screen, "blue", player2_pos, bolinha_raio)
        if escolha == 1:
            gm.draw.circle(screen, "black", player1_pos, roda_raio, 5)
        else:
            gm.draw.circle(screen, "black", player2_pos, roda_raio, 5)
        gm.display.flip()

        # --- atualizar tempo ---
        elapsed = time.time() - time_start
        if elapsed >= time_end:
            running = False
        dt = clock.tick(60) / 1000
        
    agent1.save()
    agent2.save()

    return escolha  # retorna vencedor

# --- rodar múltiplas partidas ---
num_partidas = 100
vitorias_player1 = 0
vitorias_player2 = 0

for i in range(num_partidas):
    vencedor = jogar_partida(time_end=5)  # partidas curtas
    if vencedor == 1:
        vitorias_player1 += 1
    else:
        vitorias_player2 += 1
    print(f"Partida {i+1} terminou. Placar: {vitorias_player1} x {vitorias_player2}")

print("Treino concluído!")
gm.quit()
