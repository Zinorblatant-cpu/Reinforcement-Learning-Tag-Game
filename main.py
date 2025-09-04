import pygame as gm
import random as rd
import time
from linear_agent import LinearAgent
from AggressiveAgent import AggressiveAgent

# --- pygame setup ---
gm.init()
screen = gm.display.set_mode((1200, 700))
clock = gm.time.Clock()

# --- Carregar imagem do mapa ---
try:
    map_image = gm.image.load("mapa.png").convert()
except Exception as e:
    print(f"Erro ao carregar imagem: {e}")
    gm.quit()
    exit()

# Centralizar imagem
offset_x = (screen.get_width() - map_image.get_width()) // 2
offset_y = (screen.get_height() - map_image.get_height()) // 2

# --- configurações ---
bolinha_raio = 30
roda_raio = 40

# --- criar IAs ---
agent1 = AggressiveAgent(n_features=2, lr=0.001)
agent1.load()
agent2 = LinearAgent(n_features=2, lr=0.001)
agent2.load()

# --- funções ---
def limitar_posicao(pos, raio, screen):
    pos.x = max(raio, min(screen.get_width() - raio, pos.x))
    pos.y = max(raio, min(screen.get_height() - raio, pos.y))
    return pos

def colisao_imagem(pos, image, offset_x, offset_y):
    x = int(pos.x - offset_x)
    y = int(pos.y - offset_y)
    if x < 0 or x >= image.get_width() or y < 0 or y >= image.get_height():
        return True
    pixel = image.get_at((x, y))
    return pixel[0] < 128 and pixel[1] < 128 and pixel[2] < 128  # preto = parede

# --- função principal ---
def jogar_partida(time_end=15, treinar=True):
    # Tenta encontrar posições iniciais válidas (fora das paredes)
    max_tentativas = 100
    player1_pos = None
    player2_pos = None

    for _ in range(max_tentativas):
        x = rd.randint(offset_x + bolinha_raio, offset_x + map_image.get_width() - bolinha_raio)
        y = rd.randint(offset_y + bolinha_raio, offset_y + map_image.get_height() - bolinha_raio)
        pos = gm.Vector2(x, y)

        if not colisao_imagem(pos, map_image, offset_x, offset_y):
            if player1_pos is None:
                player1_pos = pos
            elif player2_pos is None:
                player2_pos = pos
                break
    else:
        print("Não foi possível encontrar posições válidas. Usando posições padrão.")
        player1_pos = gm.Vector2(200, 200)
        player2_pos = gm.Vector2(700, 600)

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
        if escolha == 1:
            dx1 = -(player2_pos.x - player1_pos.x)  # fugir
            dy1 = -(player2_pos.y - player1_pos.y)
        else:
            dx1 = player2_pos.x - player1_pos.x   # perseguir
            dy1 = player2_pos.y - player1_pos.y

        action1 = agent1.decide_action([dx1, dy1])
        move1 = gm.Vector2(action1[0], action1[1]) * 200 * dt
        nova_pos1 = player1_pos + move1
        if not colisao_imagem(nova_pos1, map_image, offset_x, offset_y):
            player1_pos = nova_pos1

        # --- IA Player2 ---
        if escolha == 2:
            dx2 = -(player1_pos.x - player2_pos.x)
            dy2 = -(player1_pos.y - player2_pos.y)
        else:
            dx2 = player1_pos.x - player2_pos.x
            dy2 = player1_pos.y - player2_pos.y

        action2 = agent2.decide_action([dx2, dy2])
        move2 = gm.Vector2(action2[0], action2[1]) * 200 * dt
        nova_pos2 = player2_pos + move2
        if not colisao_imagem(nova_pos2, map_image, offset_x, offset_y):
            player2_pos = nova_pos2

        # --- limitar posições ---
        player1_pos = limitar_posicao(player1_pos, bolinha_raio, screen)
        player2_pos = limitar_posicao(player2_pos, bolinha_raio, screen)

        # --- colisão entre jogadores ---
        if player1_pos.distance_to(player2_pos) <= bolinha_raio * 2:
            agora = gm.time.get_ticks()
            if agora > invulneravel_ate:
                # Recalcular as direções ANTES de atualizar
                dx1_atual = player2_pos.x - player1_pos.x
                dy1_atual = player2_pos.y - player1_pos.y
                dx2_atual = player1_pos.x - player2_pos.x
                dy2_atual = player1_pos.y - player2_pos.y

                escolha = 2 if escolha == 1 else 1
                invulneravel_ate = agora + tempo_invulneravel

                if escolha == 1:
                    agent1.update([dx1_atual, dy1_atual], 1)
                    agent2.update([dx2_atual, dy2_atual], 0)
                else:
                    agent1.update([dx1_atual, dy1_atual], 0)
                    agent2.update([dx2_atual, dy2_atual], 1)

            overlap = bolinha_raio * 2 - player1_pos.distance_to(player2_pos)
            if player1_pos != player2_pos:
                direction = (player1_pos - player2_pos).normalize()
                player1_pos += direction * (overlap / 2)
                player2_pos -= direction * (overlap / 2)

        # --- desenhar tudo ---
        screen.fill("white")
        screen.blit(map_image, (offset_x, offset_y))
        gm.draw.circle(screen, "red", player1_pos, bolinha_raio)
        gm.draw.circle(screen, "blue", player2_pos, bolinha_raio)
        if escolha == 1:
            gm.draw.circle(screen, "black", player1_pos, roda_raio, 5)
        else:
            gm.draw.circle(screen, "black", player2_pos, roda_raio, 5)
        gm.display.flip()

        elapsed = time.time() - time_start
        if elapsed >= time_end:
            running = False
        dt = clock.tick(60) / 1000

    agent1.save()
    agent2.save()
    return escolha

# --- rodar múltiplas partidas ---
num_partidas = 10
vitorias_player1 = 0
vitorias_player2 = 0

for i in range(num_partidas):
    vencedor = jogar_partida(time_end=5)
    if vencedor == 1:
        vitorias_player1 += 1
    else:
        vitorias_player2 += 1
    print(f"Partida {i+1} terminou. Placar: {vitorias_player1} x {vitorias_player2}")

print("Treino concluído!")
gm.quit()