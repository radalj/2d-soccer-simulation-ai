import time
from threading import Thread

from runner.models import Ball, Map
from runner.models.score_board import ScoreBoard
from runner.settings import BALL_RADIUS, SCREEN_HEIGHT, SCREEN_WIDTH, GRASS_COLOR as GC
import pygame as pg
from runner.utils import init_players, get_info, reverse_information
from team1.team1 import play as red_play
from team2.team2 import play as blue_play


def red_fire(red_players, blue_players, red_score, blue_score, ball, time_passed):
    global red_decisions
    red_decisions = red_play(red_players, blue_players, red_score, blue_score, ball, time_passed)


def blue_fire(red_players, blue_players, red_score, blue_score, ball, time_passed):
    global blue_decisions
    blue_decisions = blue_play(red_players, blue_players, red_score, blue_score, ball, time_passed)


if __name__ == "__main__":
    ''' INIT OBJECTS AND VARS '''
    red_players = []
    blue_players = []
    init_players(red_players, blue_players)
    ball = Ball(x=0, y=0, speed=0, direction=-1, radius=BALL_RADIUS)
    score_board = ScoreBoard(red_score=0, blue_score=0, cycle_number=0)
    the_map = Map(red_players=red_players, blue_players=blue_players, ball=ball, score_board=score_board)
    ''' INIT PYGAME '''
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill(GC)
    the_map.show(screen=screen)
    pg.display.update()
    done = False
    pause = False
    while not done:
        # events: pause and quit
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p:
                    pause = not pause
                    print('pause')
                if event.key == pg.K_ESCAPE:
                    done = True
            if event.type == pg.QUIT:
                done = True
        if pause:
            continue

        red_decisions = []
        blue_decisions = []
        red_players_info, blue_players_info, ball_info = get_info(the_map.red_players, the_map.blue_players,
                                                                  the_map.ball)
        red_thread = Thread(target=red_fire, args=(
            red_players_info, blue_players_info, the_map.score_board.red_score, the_map.score_board.blue_score,
            ball_info, the_map.score_board.cycle_number))
        red_players_info, blue_players_info, ball_info = reverse_information(red_players_info, blue_players_info,
                                                                             ball_info)
        blue_thread = Thread(target=blue_fire, args=(
            red_players_info, blue_players_info, the_map.score_board.red_score, the_map.score_board.blue_score,
            ball_info, the_map.score_board.cycle_number))
        blue_thread.start()
        red_thread.start()
        for i in range(5):
            time.sleep(0.1)
            if len(blue_decisions) != 0 and len(red_decisions) != 0:
                break
        the_map.perform_decisions(red_decisions, blue_decisions)
        the_map.ball.move()
        screen.fill(GC)
        the_map.show(screen=screen)
        pg.display.update()
        the_map.check_if_scored()
        the_map.check_if_the_bus_is_parked()
        the_map.check_if_ball_is_crowded()
        the_map.score_board.cycle_number += 1
        if the_map.score_board.cycle_number > 500:
            done = True
