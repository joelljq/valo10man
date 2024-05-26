import json

import discord
import random

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# A list to keep track of users in the matchmaking pool
matchmaking_pool = []
ppoints = []
players = {}

maps = ['Pearl', 'Bind', 'Split', 'Ascent', 'Lotus', 'Icebox', 'Haven', 'Breeze']
startingside = ['Attacking', 'Defending']

# A dictionary to keep track of the points for each player
points = {}
oldpoints = {}
newpoints = {}


def update_points(winner, loser, rounds_difference):
    global points, mmr_gain_loss
    winner_id = str(winner)
    loser_id = str(loser)
    winner_rating = int(points[winner_id])
    loser_rating = int(points[loser_id])
    mmr_gain_loss = 8 + rounds_difference
    winner_new_rating = winner_rating + mmr_gain_loss
    loser_new_rating = loser_rating - mmr_gain_loss
    oldpoints[winner_id] = winner_rating
    newpoints[winner_id] = winner_new_rating
    oldpoints[loser_id] = loser_rating
    newpoints[loser_id] = loser_new_rating
    points[winner] = winner_new_rating
    points[loser] = loser_new_rating


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    global team1, team2, points, target_user, chosenmap
    if message.author == client.user:
        return
    if message.content.startswith('!join'):
        if str(message.author) not in points:
            points[str(message.author)] = 50
            save_points()
        if len(matchmaking_pool) < 10:
            if message.author in matchmaking_pool:
                await message.channel.send('You have already joined the matchmaking queue!')
            else:
                matchmaking_pool.append(message.author)
                await message.channel.send(f'{message.author.mention} has joined the matchmaking queue. '
                                           f'{len(matchmaking_pool)}/10 players in queue.')
        else:
            random.shuffle(matchmaking_pool)
            firsthalf = int(len(matchmaking_pool) / 2)
            secondhalf = int(len(matchmaking_pool))
            team1 = matchmaking_pool[:firsthalf]
            team2 = matchmaking_pool[firsthalf:secondhalf]
            for x in team1:
                if str(x) in points:
                    ppoints.append(points[str(x)])
            totalt1 = sum(ppoints)
            ppoints.clear()
            for x in team2:
                if str(x) in points:
                    ppoints.append(points[str(x)])
            totalt2 = sum(ppoints)
            ppoints.clear()
            while abs(totalt1 - totalt2) > 20:
                random.shuffle(matchmaking_pool)
                firsthalf = int(len(matchmaking_pool) / 2)
                secondhalf = int(len(matchmaking_pool))
                team1 = matchmaking_pool[:firsthalf]
                team2 = matchmaking_pool[firsthalf:secondhalf]
                for x in team1:
                    if str(x) in points:
                        ppoints.append(points[str(x)])
                totalt1 = sum(ppoints)
                ppoints.clear()
                for x in team2:
                    if str(x) in points:
                        ppoints.append(points[str(x)])
                totalt2 = sum(ppoints)
            chosenmap = random.choice(maps)
            random.shuffle(startingside)
            team1_str = [x.mention for x in team1]
            team2_str = [x.mention for x in team2]
            embed = discord.Embed(title="Match Details", color=0x00ff00)
            embed.add_field(name="Map", value=f"{chosenmap}", inline=False)
            embed.add_field(name="Team 1", value="\n".join(team1_str), inline=False)
            embed.add_field(name="Team 1 Total ELO: ", value=f"{totalt1}", inline=False)
            embed.add_field(name="Side", value=f"{startingside[0]}", inline=False)
            embed.add_field(name="Team 2", value="\n".join(team2_str), inline=False)
            embed.add_field(name="Team 2 Total ELO: ", value=f"{totalt2}", inline=False)
            embed.add_field(name="Side", value=f"{startingside[1]}", inline=False)
            await message.channel.send(embed=embed)
            matchmaking_pool.clear()

    if message.content.startswith('!leave'):
        if message.author in matchmaking_pool:
            matchmaking_pool.remove(message.author)
            await message.channel.send(f'{message.author.mention} has left the matchmaking queue. '
                                       f'{len(matchmaking_pool)}/10 players in queue.')
        else:
            await message.channel.send(f'{message.author.mention} you are not in the matchmaking queue.')

    if message.content.startswith('!start'):
        if len(matchmaking_pool) < 10:
            await message.channel.send(f'{message.author.mention} Not enough players in the matchmaking queue. '
                                       f'{len(matchmaking_pool)}/10 players in queue.')
        else:
            random.shuffle(matchmaking_pool)
            firsthalf = int(len(matchmaking_pool) / 2)
            secondhalf = int(len(matchmaking_pool))
            team1 = matchmaking_pool[:firsthalf]
            team2 = matchmaking_pool[firsthalf:secondhalf]
            chosenmap = random.choice(maps)
            random.shuffle(startingside)
            team1_str = [x.mention for x in team1]
            team2_str = [x.mention for x in team2]
            embed = discord.Embed(title="Match Details", color=0x00ff00)
            embed.add_field(name="Map", value=f"{chosenmap}", inline=False)
            embed.add_field(name="Team 1", value=", ".join(team1_str), inline=False)
            embed.add_field(name="Side", value=f"{startingside[0]}", inline=False)
            embed.add_field(name="Team 2", value=", ".join(team2_str), inline=False)
            embed.add_field(name="Side", value=f"{startingside[1]}", inline=False)
            await message.channel.send(embed=embed)
            matchmaking_pool.clear()

    if message.content.startswith('!forcestart'):
        if not message.author.guild_permissions.administrator:
            await message.channel.send("You don't have permission to use this command.")
            return
        random.shuffle(matchmaking_pool)
        firsthalf = int(len(matchmaking_pool) / 2)
        secondhalf = int(len(matchmaking_pool))
        team1 = matchmaking_pool[:firsthalf]
        team2 = matchmaking_pool[firsthalf:secondhalf]
        for x in team1:
            if str(x) in points:
                ppoints.append(points[str(x)])
        totalt1 = sum(ppoints)
        ppoints.clear()
        for x in team2:
            if str(x) in points:
                ppoints.append(points[str(x)])
        totalt2 = sum(ppoints)
        while abs(totalt1 - totalt2) > 20:
            random.shuffle(matchmaking_pool)
            firsthalf = int(len(matchmaking_pool) / 2)
            secondhalf = int(len(matchmaking_pool))
            team1 = matchmaking_pool[:firsthalf]
            team2 = matchmaking_pool[firsthalf:secondhalf]
            for x in team1:
                if str(x) in points:
                    ppoints.append(points[str(x)])
            totalt1 = sum(ppoints)
            ppoints.clear()
            for x in team2:
                if str(x) in points:
                    ppoints.append(points[str(x)])
            totalt2 = sum(ppoints)
        chosenmap = random.choice(maps)
        random.shuffle(startingside)
        team1_str = [x.mention for x in team1]
        team2_str = [x.mention for x in team2]
        embed = discord.Embed(title="Match Details", color=0x00ff00)
        embed.add_field(name="Map", value=f"{chosenmap}", inline=False)
        embed.add_field(name="Team 1", value="\n".join(team1_str), inline=False)
        embed.add_field(name="Team 1 Total ELO: ", value=f"{totalt1}", inline=False)
        embed.add_field(name="Side", value=f"{startingside[0]}", inline=False)
        embed.add_field(name="Team 2", value="\n".join(team2_str), inline=False)
        embed.add_field(name="Team 2 Total ELO: ", value=f"{totalt2}", inline=False)
        embed.add_field(name="Side", value=f"{startingside[1]}", inline=False)
        await message.channel.send(embed=embed)
        matchmaking_pool.clear()

    if message.content.startswith('!finish'):
        await message.channel.send('Enter the winning team (team1 or team2):')

        def check(m):
            return m.author == message.author and m.channel == message.channel

        winning_team_message = await client.wait_for('message', check=check)
        winning_team = winning_team_message.content.strip()
        if winning_team == 'team1' or winning_team == 'team2':
            await message.channel.send('Enter the points difference:')
            points_difference_message = await client.wait_for('message', check=check)
            points_difference = int(points_difference_message.content.strip())
            if winning_team == 'team1':
                for i in range(len(team1)):
                    update_points(team1[i], team2[i], points_difference)
                # for player in team2:
                #     for player2 in team1:
                #         update_points(player, player2, points_difference)
                embed = discord.Embed(title="Match Results", color=0x00ff00)
                embed.add_field(name="Winner", value="Team 1 Wins!", inline=False)
                embed.add_field(name="Map", value=f"{chosenmap}", inline=False)
                embed.add_field(name="Score", value=f"13 - {13 - points_difference}")
                resultsteam1 = ''
                for i in range(len(team1)):
                    resultsteam1 += f"{team1[i].mention}({oldpoints[str(team1[i])]}) --> {newpoints[str(team1[i])]}\n"
                embed.add_field(name="Team1", value=resultsteam1, inline=False)
                resultsteam2 = ''
                for i in range(len(team2)):
                    resultsteam2 += f"{team2[i].mention}({oldpoints[str(team2[i])]}) --> {newpoints[str(team2[i])]}\n"
                embed.add_field(name="Team2", value=resultsteam2, inline=False)
                await message.channel.send(embed=embed)
                save_points()
            elif winning_team == 'team2':
                for i in range(len(team2)):
                    update_points(team2[i], team1[i], points_difference)
                embed = discord.Embed(title="Match Results", color=0x00ff00)
                embed.add_field(name="Winner", value="Team 2 Wins!", inline=False)
                embed.add_field(name="Map", value=f"{chosenmap}", inline=False)
                embed.add_field(name="Score", value=f"13 - {13-points_difference}")
                resultsteam2 = ''
                for i in range(len(team2)):
                    resultsteam2 += f"{team2[i].mention}({oldpoints[str(team2[i])]}) --> {newpoints[str(team2[i])]}\n"
                embed.add_field(name="Team2", value=resultsteam2, inline=False)
                resultsteam1 = ''
                for i in range(len(team1)):
                    resultsteam1 += f"{team1[i].mention}({oldpoints[str(team1[i])]}) --> {newpoints[str(team1[i])]}\n"
                embed.add_field(name="Team1", value=resultsteam1, inline=False)
                await message.channel.send(embed=embed)
                save_points()


    if message.content.startswith('!leaderboard'):
        sorted_points = sorted(points.items(), key=lambda x: x[1], reverse=True)
        leaderboard_message = '\n'.join(
            [f'{i + 1}. {p[0]}: {p[1]}' for i, p in enumerate(sorted_points)])
        embed = discord.Embed(
            title="Leaderboard",
            description=f'```\n{leaderboard_message}\n```',
            color=discord.Color.blue()
        )
        await message.channel.send(embed=embed)

    if message.content.startswith('!mypoints'):
        if str(message.author) in points:
            userpoints = points[str(message.author)]
            await message.channel.send(f'You have {userpoints} Points')
        else:
            points[str(message.author)] = 50
            userpoints = points[str(message.author)]
            await message.channel.send(f'You have {userpoints} Points')

    if message.content.startswith('!help'):
        embed = discord.Embed(title="Help", description="List of commands", color=0xeee657)
        embed.add_field(name="!join", value="Join the queue")
        embed.add_field(name="!leave", value="Leave the queue")
        embed.add_field(name="!finish", value="Use to declare the winning team")
        embed.add_field(name="!leaderboard", value="Displays the leaderboard")
        embed.add_field(name="!mypoints", value="Shows your current points")
        embed.add_field(name="!help", value="Displays this help message")
        await message.channel.send(embed=embed)



def save_points():
    points_dict = {str(member): points[member] for member in points}
    with open(r"C:\Users\Admin\Documents\points.json", "w") as f:
        json.dump(points_dict, f)
    load_points()


def load_points():
    global points
    try:
        with open(r"C:\Users\Admin\Documents\points.json", "r") as f:
            points_dict = json.load(f)
            points = {key: value for key, value in points_dict.items()}
    except FileNotFoundError:
        points = {}


load_points()
client.run('DISCORD TOKEN')
