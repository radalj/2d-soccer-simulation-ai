import math
import random

def move(decisions, player_number, destination, speed):
    decisions.append({
        'action': 'move',
        'player_number': player_number,
        'destination': destination,
        'speed': speed,
    })


def kick(decisions, player_number, direction, power):
    decisions.append({
        'action': 'kick',
        'player_number': player_number,
        'direction': clock_to_degree(direction),
        'power': power,
    })


def grab(decisions, player_number):
    decisions.append({
        'action': 'grab',
        'player_number': player_number
    })


def degree_to_clock(degree):
    if degree < 90:
        degree += 360
    degree = 450 - degree
    hour = degree // 30
    minute = degree % 30 // 6
    return hour + minute / 10


def clock_to_degree(clock):
    angle = int(clock // 1 * 30 + 10 * (clock % 1) * 6)
    angle = 450 - angle
    if angle >= 360:
        angle -= 360
    return angle


def get_direction(a, b):
    x = b['x'] - a['x']
    y = b['y'] - a['y']
    angle = math.degrees(math.atan2(y, x))
    return degree_to_clock(angle)


def get_distance(a, b):
    return math.hypot(a['x'] - b['x'], a['y'] - b['y'])

def pg_on_line(ap, bp, cp, er=10):
    x1, y1 = ap["x"], ap["y"]
    x2, y2 = bp["x"], bp["y"]
    x3, y3 = cp["x"], cp["y"]
    bx, kx = max(x1, x2), min(x1, x2)
    by, ky = max(y1, y2), min(y1, y2)
    if kx <= x3 <= bx and ky <= y3 <= by:
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0:
            if abs(x1-x3)<er:
                return True
            return False
        elif dy == 0:
            if abs(y1-y3)<er:
                return True
            return False
        else:
            m = dy / dx
        b = y1 - m * x1
        y = m*x3+b
        if abs(y-y3) < er:
            return True
    return False

def non_of_enemies_on_line(ap, bp, enemies, er=10):
    for i in enemies:
        if pg_on_line(ap, bp, i, er):
            return False
    return True

def sort_by_distance(players, i, not_lis):
    lis = []
    for j in range(6):
        if j != i and (j not in not_lis):
            lis.append({"n" : j, 
            "d": get_distance(players[i], players[j])})
    lis = list(sorted(lis, key=lambda x: x["d"]))
    lis = list(map(lambda x : x["n"], lis))
    return lis[:]

def search_for_good_teammate(players, enemies, i, ball, not_lis) -> (int):
    sorted_players = sort_by_distance(players, i, not_lis)
    for j in sorted_players:
        if non_of_enemies_on_line(players[i], players[j], enemies):
            return j
    return sorted_players[0]

def min_index(lis):
    m = lis[0]
    mi = 0
    for i in range(1, len(lis)):
        mm = lis[i]
        if mm < m:
            mi = i
            mm = m
    return mi

def play(red_players, blue_players, red_score, blue_score, ball, time_passed):
    decisions = []
    ######################################################################################
    red = "red"
    blue = "blue"
    white = "white"
    players = red_players
    enemies = blue_players
    enemie_goal_mean = {'x' : 484, 'y' : 0}
    enemie_goal_min  = {'x' : 484, 'y' : -90}
    enemie_goal_max  = {'x' : 484, 'y' : 90}
    ball_color = ball["owner_color"]
    ball_number = ball["owner_number"]
    ball_x = ball['x']
    ball_y = ball['y']
    ball_speed = ball["speed"]
    ball_dir = ball["direction"]
    go_poses = [ {'x' : -436, 'y' : 0},
                 {'x' : -450, 'y' : 60},
                 {'x' : -450, 'y' : -60},
                 enemie_goal_mean,
                 enemie_goal_max,
                 enemie_goal_min ]
    distances_for_players = [23]+([18]*5)
    moves = [True]*6
    distance_from_goal = 170
    # er = 10
    # firts do the defend (players 0 ~ 2)
    for i in range(3):
        p = players[i]
        px, py = p["x"], p["y"]
        if ball_x <= -300:
            if -162.5 <= ball_y <= 162.5:
                if get_distance(players[i], ball) < distances_for_players[i]:
                    if ball_color != red:
                        grab(decisions, i)
                        j = search_for_good_teammate(players, enemies, i, ball, [0, 1, 2])
                        kick(decisions, i, get_direction(players[i], players[j]), 60)
                if ball_color == red and ball_number == i:
                    j = search_for_good_teammate(players, enemies, i, ball, [0, 1, 2])
                    kick(decisions, i, get_direction(players[i], players[j]), 60)
                else:
                    speed = 18
                    if -500 <= px <= -300 and -162.5 <= py <= 162.5:
                        speed = 9
                    move(decisions, i, ball, speed)
            else:
                move(decisions, i, ball, 18)
            moves[i] = False
    # then go to the defend position !
    for i in range(3):
        if get_distance( players[i], go_poses[i] ) > 0 and moves[i]:
            move(decisions, i, go_poses[i], 18)
    # now lets attask!
    # but waht should we do?
    # go neat the goal and goal a goal?
    # do this by passing the ball?
    # attack (players 3 ~ 5)
    for i in range(4, 6):
        p = players[i]
        if ball_color != red: # we don't have the ball
            if get_distance(p, ball) < distances_for_players[i]: # we can grab the ball
                if ball_color == blue: # the ball is grabbed by enemies
                    grab(decisions, i)
                # the ball is opposite us or makes no changes so we should grab it
                elif ball_color == white:
                    if ball_speed == 0: # the ball is stopped so we had better grab it
                        grab(decisions, i)
                    # the ball is comming through us! we should stop it so we can attack later!
                    elif 0.0 <= ball_dir <= 6.0:
                        grab(decisions, i)
            else: # we can not grab the ball so we will move through it
                move(decisions, i, ball, min(get_distance(p, ball), 18))
        elif ball_number not in [3, 4, 5]: # the ball is grabbed by the defenders
            move(decisions, i, ball, min(get_distance(p, ball), 18))
            kick(decisions, ball_number, get_direction(players[ball_number], enemie_goal_mean), 60)
        else: # the ball is grabbed by attackers
            if ball_number != i: # the ball is not grabbed by us
                move(decisions, i, go_poses[i], 18)
            else: # the ball is grabbed by us
                dmean = get_distance(p, enemie_goal_mean)
                dmin  = get_distance(p, enemie_goal_min)
                dmax  = get_distance(p, enemie_goal_max)
                # its better to attack through which part of the goal
                if dmean <= distance_from_goal and non_of_enemies_on_line(p, enemie_goal_mean, enemies):
                    kick(decisions, i, get_direction(p, enemie_goal_mean), 60)
                elif dmin <= distance_from_goal and non_of_enemies_on_line(p, enemie_goal_min, enemies):
                    kick(decisions, i, get_direction(p, enemie_goal_min), 60)
                elif dmax <= distance_from_goal and non_of_enemies_on_line(p, enemie_goal_max, enemies):
                    kick(decisions, i, get_direction(p, enemie_goal_max), 60)
                # non of them are good to go through so we will pass the ball or 
                else:
                    j = search_for_good_teammate(players, enemies, i, ball, not_lis=[0, 1, 2])
                    pj = players[j]
                    # the best guy to pass the ball is behind us... 
                    # we can do nothing except from...
                    # attack through inside the enemies goal like a bull(the cow)!
                    if pj['x'] < p['x']:
                        pos = go_poses[i]
                        l = [dmean, dmin, dmax]
                        index = min_index(l)+3
                        npos = go_poses[index]
                        if non_of_enemies_on_line(p, npos, enemies):
                           pos = npos
                        move(decisions, i, pos, 18)
                    else: # pass the ball
                        d = get_distance(p, pj)
                        kick(decisions, i, get_direction(p, pj), min(d, 60))
    for i in [3]: # just using a loop to seperate from other stuff
        p = players[i]
        if ball_color == red: # we have the ball
            poses = [enemie_goal_min, enemie_goal_max]
            pos = poses[random.randint(0, 1)]
            if ball_number != i or get_distance(p, pos) > distance_from_goal: # we can't kick the ball
                move(decisions, i, pos, 18)
            else: # we can kick the ball (to where?)
                kick(decisions, i, get_direction(p, pos), 60)
        else: # we don't have the ball
            move(decisions, i, ball, 18)
            grab(decisions, i)

    ######################################################################################
    return decisions
