import pygame as gm
import random as rd
import time
from linear_agent import LinearAgent  # importa a IA

# --- pygame setup ---
gm.init()
screen = gm.display.set_mode((1280, 720))
clock = gm.time.Clock()
running = True
dt = 0

# --- posição inicial dos jogadores ---
player1_pos = gm.Vector2(screen.get_width() / 3, screen.get_height() / 2)  # jogador humano
player2_pos = gm.Vector2(2 * screen.get_width() / 3, screen.get_height() / 2)  # IA

# IA para controlar o player2 (entrada = dx, dy)
agent = LinearAgent(n_features=2, lr=0.01)
agent.load()  # tenta carregar pesos salvos no JSON

# --- configuração do jogo ---
escolha = rd.choice([1, 2])  # quem começa com a roda
bolinha_raio = 40
roda_raio = 50
tempo_invulneravel = 1000  # em ms
invulneravel_ate = 0

# --- timer do jogo ---
time_start = time.time()
time_end = 15  # duração da partida
font = gm.font.SysFont("Arial", 36)
title_font = gm.font.SysFont("Arial", 48, bold=True)


def limitar_posicao(pos, raio, screen):
    """Garante que a bolinha fique dentro dos limites da tela."""
    pos.x = max(raio, min(screen.get_width() - raio, pos.x))
    pos.y = max(raio, min(screen.get_height() - raio, pos.y))
    return pos


# --- loop principal ---
while running:
    for event in gm.event.get():
        if event.type == gm.QUIT:
            running = False

    screen.fill("white")
    keys = gm.key.get_pressed()

    # --- Player1 controlado por WASD (humano) ---
    move1 = gm.Vector2(0, 0)
    if keys[gm.K_w]:
        move1.y -= 300 * dt
    if keys[gm.K_s]:
        move1.y += 300 * dt
    if keys[gm.K_a]:
        move1.x -= 300 * dt
    if keys[gm.K_d]:
        move1.x += 300 * dt
    player1_pos += move1

    # --- Player2 controlado pela IA ---
    dx = player1_pos.x - player2_pos.x
    dy = player1_pos.y - player2_pos.y
    move_ai = agent.decide_action([dx, dy]) * 300 * dt
    player2_pos += gm.Vector2(move_ai[0], move_ai[1])

    # --- limitar posições dentro da tela ---
    player1_pos = limitar_posicao(player1_pos, bolinha_raio, screen)
    player2_pos = limitar_posicao(player2_pos, bolinha_raio, screen)

    # --- colisão entre players ---
    if player1_pos.distance_to(player2_pos) <= bolinha_raio * 2:
        agora = gm.time.get_ticks()
        if agora > invulneravel_ate:  # só troca se não estiver invulnerável
            escolha = 2 if escolha == 1 else 1
            invulneravel_ate = agora + tempo_invulneravel

            # Treinar IA → recompensa positiva por encostar no player1
            agent.update([dx, dy], 1)
            agent.save()

        # empurrar players para não sobrepor
        overlap = bolinha_raio * 2 - player1_pos.distance_to(player2_pos)
        if player1_pos != player2_pos:
            direction = (player1_pos - player2_pos).normalize()
            player1_pos += direction * (overlap / 2)
            player2_pos -= direction * (overlap / 2)

    # --- desenhar círculo preto em volta do jogador que tem a roda ---
    if escolha == 1:
        gm.draw.circle(screen, "black", player1_pos, roda_raio, 5)
    else:
        gm.draw.circle(screen, "black", player2_pos, roda_raio, 5)

    # --- desenhar jogadores ---
    gm.draw.circle(screen, "red", player1_pos, bolinha_raio)   # Player1 (humano)
    gm.draw.circle(screen, "blue", player2_pos, bolinha_raio)  # Player2 (IA)

    # --- TIMER ---
    elapsed = time.time() - time_start
    remaining = max(0, time_end - elapsed)
    timer_text = font.render(f"Tempo: {remaining:.1f}s", True, (0, 0, 0))
    screen.blit(timer_text, (20, 70))

    # --- título do jogo ---
    title_text = title_font.render("Batalha das Bolinhas", True, (0, 0, 0))
    screen.blit(title_text, (screen.get_width()//2 - title_text.get_width()//2, 10))

    # --- condição de fim de jogo ---
    if elapsed >= time_end:
        if escolha == 1:  # azul venceu
            print("A bolinha azul (IA) ganhou")
        else:  # vermelho venceu
            print("A bolinha vermelha (Humano) ganhou")

        # Se a IA perdeu → aplica uma punição
        if escolha != 1:
            agent.update([dx, dy], -1)
            agent.save()

        print("\nO tempo acabou!")
        running = False

    gm.display.flip()
    dt = clock.tick(60) / 1000

gm.quit()
