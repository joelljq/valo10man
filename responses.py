import random

def randomize_players(players):
    players = list(players.items())
    random.shuffle(players)
    firsthalf = int(len(players)/2)
    print(firsthalf)
    secondhalf = len(players)
    print(secondhalf)
    team1 = players[:firsthalf]
    team2 = players[firsthalf:]
    return (team1, team2)

def calculate_elo_points(team):
    return sum(elo for name, elo in team)

def divide_players_into_teams(players):
    teams = randomize_players(players)
    team1, team2 = teams
    while abs(calculate_elo_points(team1) - calculate_elo_points(team2)) > 10:
        teams = randomize_players(players)
        team1, team2 = teams
    return teams

players = {"Verros#9372": 50, "Shawty#2831": 60, "OneClickGamer#8558": 70, "jRon.#4112": 80, "2rei#9996": 90}

teams = divide_players_into_teams(players)

team1, team2 = teams

print("Team 1:", team1)
print("Team 2:", team2)
print("Team 1 ELO points:", calculate_elo_points(team1))
print("Team 2 ELO points:", calculate_elo_points(team2))