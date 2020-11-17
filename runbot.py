import asyncio

import json
import time
import yaml
import discord
import discord.ext
import datetime as date
from discord.ext import commands
from datetime import datetime, timedelta

from discord.ext.commands import has_permissions, MissingPermissions

with open('config.yaml', 'r+') as config:
    parsedList = yaml.load(config, Loader=yaml.FullLoader)
    if parsedList['UseCustom'] != "None":
        defult = parsedList['DEFAULT']
        LogFormat = str(defult['LogFormat'])
        Log = str(defult['LOG'])
        Token = str(defult['Token'])
today = datetime.now()
client = discord.Client(command_prefix='$')
bot = commands.Bot(command_prefix="$", help_command=None)
with open('reports.json', 'r+') as f:
    f.close()


def infolog(ctx):
    with open('config.yaml', 'r+') as config:
        parsedList = yaml.load(config, Loader=yaml.FullLoader)
        if parsedList['UseCustom'] != "None":
            defult = parsedList['DEFAULT']
            LogFormat = str(defult['LogFormat'])
            Log = str(defult['LOG']).replace("[", "")
    Log = Log.replace("]", "")
    Log = Log.replace("{1}", str(ctx.message.author.name))
    Log = Log.replace("{2}", str(ctx.command.name))
    LogFormat = LogFormat.replace(r"['\\", "")
    LogFormat = LogFormat.replace(r"\\']", " ")
    Log = Log.replace("'", "")

    print(today.strftime(LogFormat) + "[INFO]: " + Log)


@bot.event
async def on_ready():
    with open('config.yaml', 'r+') as config:
        parsedList = yaml.load(config, Loader=yaml.FullLoader)
        if parsedList['UseCustom'] != "None":

            defult = parsedList['DEFAULT']
            LogFormat = str(defult['LogFormat'])
            Log = str(defult['LOG'])

        else:
            print(parsedList['CUSTOM'])
    Log = Log.replace("[", "")
    Log = Log.replace("]", "")
    Log = Log.replace("{1}", "SERVER")
    Log = Log.replace("{2}", f"ENABLE {bot.user}")
    Log = Log.replace(r"\ ", " ")
    LogFormat = LogFormat.replace(r"['\\", "")
    LogFormat = LogFormat.replace(r"\\']", " ")
    Log = Log.replace("'", "")
    print(today.strftime(LogFormat) + Log)


@bot.command()
async def ping(ctx):
    with open('config.yaml', 'r+') as config:
        parsedList = yaml.load(config, Loader=yaml.FullLoader)
        if parsedList['UseCustom'] != "None":
            defult = parsedList['DEFAULT']
            LogFormat = defult['LogFormat']
            Log = defult['LOG']
            AfkMessage = defult['AfkMessage']
            LOGIT = defult['LOGIT']
    config.close()
    embedd = discord.Embed(title="Pong!",
                           description=f"Client Online! "
                                       f"\nLogged on at: ***{today.strftime('[%d/%m/%Y][%H:%M:%S]')}***"
                                       f"\nUser is logged in on as: ***{bot.user}***"
                                       f"\nLatency: ***{round(bot.latency * 100)}*** ms\n"
                                       f"With the following configuration:\n"
                                       f"    Log Format: ***{LogFormat}***  \n"
                                       f"    Default Log: ***{Log}***\n"
                                       f"    Default Afk Message: ***{AfkMessage}***\n"
                                       f"    And it is ***{LOGIT}*** that the bot is logging commands today.",
                           color=discord.colour.Color.red())
    await ctx.send(embed=embedd)
    infolog(ctx)


@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, player: discord.Member, lengthsec, *reason):
    suffix = ""
    lengthsec = int(lengthsec)

    guild = ctx.guild
    for role in guild.roles:
        if role.name == "Muted":
            if role.name in player.roles:
                embed = discord.Embed(title="User Muted!",
                                      description=f"Failed to issue command! Player is already muted!",
                                      color=discord.colour.Color.red())
                await ctx.send(embed=embed)
                return
            await player.add_roles(role)
            embed = discord.Embed(title="User Muted!",
                                  description=f"{player.display_name} is muted by {ctx.message.author} for {reason}! "
                                              f"The mute lasts for {suffix} ",
                                  color=discord.colour.Color.green())
            await ctx.send(embed=embed)
            infolog(ctx)
            player.display_name = await asyncio.sleep(lengthsec)
            await player.remove_roles(role)
            return


@bot.command()
@has_permissions(kick_members=True)
async def kick(ctx, whom: discord.Member, *, reason):
    kickembed = discord.Embed(title="Kicked!",
                              description=f"You were kicked from {ctx.message.guild.name}"
                                          f" by {ctx.message.author.name} for {reason}!",
                              color=discord.colour.Color.red())
    await whom.send(embed=kickembed)
    await whom.kick()

    infolog(ctx)
    embed = discord.Embed(title="Player Kicked!",
                          description=f"User {whom} was kicked by {ctx.message.author.name} for {reason}",
                          color=discord.colour.Color.green())
    await ctx.send(embed=embed)


@bot.command()
@has_permissions(ban_members=True)
async def ban(ctx, whom: discord.Member, *, reason):
    banembed = discord.Embed(title="Banned!",
                             description=f"You were Banned from {ctx.message.guild.name} by {ctx.message.author.name} "
                                         f"for {reason}!",
                             color=discord.colour.Color.red())
    await whom.send(embed=banembed)
    await whom.ban()

    infolog(ctx)
    embed = discord.Embed(title="Player Banned!",
                          description=f"User {whom} was Banned by {ctx.message.author.name} for {reason}",
                          color=discord.colour.Color.green())
    await ctx.send(embed=embed)


@bot.command()
@has_permissions(ban_members=True)
async def unban(ctx, *, member):
    bannedPlayers = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')
    print(bannedPlayers)
    for member in bannedPlayers:
        user = member.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            embed = discord.Embed(title="Player Unbanned!",
                                  description=f"User {member_name + '#' + member_discriminator} was Unbanned by "
                                              f"{ctx.message.author.name}.",
                                  color=discord.colour.Color.green())
            await ctx.send(embed=embed)
            return
    infolog(ctx)


with open('reports.json', encoding='utf-8') as f:
    try:
        report = json.load(f)
    except ValueError:
        report = {'users': []}


@bot.command(pass_context=True)
@has_permissions(manage_roles=True, ban_members=True)
async def warn(ctx, user: discord.Member, *reason: str):
    if not reason:
        await ctx.send("Please provide a reason")
        return
    reason = ' '.join(reason)
    for current_user in report['users']:
        if current_user['name'] == user.name:
            current_user['reasons'].append(reason)
            break
    else:
        report['users'].append({
            'name': user.name,
            'reasons': [reason, ]
        })
    with open('reports.json', 'w+') as file:
        json.dump(report, file)
        infolog(ctx)

    for current_user in report['users']:
        if user.name == current_user['name']:
            if len(current_user['reasons']) == 5:
                player = user
                suffix = ""
                lengthsec = 600
                areason = f"User Reached 5 warnings, Muted for 10 minutes. with a final reason of {reason}"
                guild = ctx.guild
                for role in guild.roles:
                    if role.name == "Muted":
                        if role.name in player.roles:
                            embed = discord.Embed(title="User Muted!",
                                                  description=f"Failed to issue command! Player is already muted!",
                                                  color=discord.colour.Color.red())
                            await ctx.send(embed=embed)
                            return
                        await player.add_roles(role)
                        embed = discord.Embed(title="User Muted!",
                                              description=f"{player.display_name} is muted by {ctx.message.author} for {areason}! ",
                                              color=discord.colour.Color.green())
                        await ctx.send(embed=embed)
                        infolog(ctx)
                        player.display_name = await asyncio.sleep(lengthsec)
                        await player.remove_roles(role)
                        return
            else:
                embed = discord.Embed(tite="User Warned!",
                                      description=f"{user.display_name} warned was warned for {reason}!",
                                      color=discord.colour.Color.green())
                await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def warnings(ctx, user: discord.User):
    for current_user in report['users']:
        if user.name == current_user['name']:
            await ctx.send(
                f"{user.name} has been reported {len(current_user['reasons'])}"
                f" times : {', '.join(current_user['reasons'])}")

            break
    else:
        await ctx.send(f"{user.name} has never been reported")
        infolog(ctx)


@warn.error
async def kick_error(error, ctx):
    if isinstance(error, MissingPermissions):
        text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
        await ctx.send(ctx.message.channel, text)


start_time = time.time()
import sys

sys.setrecursionlimit((10 * 10) * 10)


@bot.command(pass_context=True, aliases=['uptime', 'updog'])
async def botuptime(ctx):
    current_time = time.time()
    difference = int(round(current_time - start_time))
    text = str(date.timedelta(seconds=difference))
    embed = discord.Embed(title="Updog!", description=f"The bot has been up for {text}",
                          colour=discord.colour.Color.green())
    try:
        await ctx.send(embed=embed)
    except discord.HTTPException:
        await ctx.send("Current uptime: " + text)


@bot.command()
@has_permissions(manage_messages=True)
async def clear(ctx, limit: int = None):
    passed = 0
    failed = 0
    async for msg in ctx.message.channel.history(limit=limit):
        try:
            await msg.delete()
            passed += 1
        except:
            failed += 1
    infolog(ctx)
    print(f"[Complete] Removed {passed} messages with {failed} fails")
    embed = discord.Embed(title="Cleared!", description=f"Removed {passed} messages, with {failed} deletes!",
                          color=discord.colour.Color.green())
    await ctx.send(embed=embed)


@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await discord.VoiceChannel.connect(channel)
    infolog(ctx)
    embed = discord.Embed(title='Joining!', description=f"Joining {channel}!", color=discord.colour.Color.green())
    await ctx.send(embed=embed)


@bot.command()
async def leave(ctx):
    server = ctx.message.guild.voice_client
    await server.disconnect()
    infolog(ctx)
    await ctx.send("Goodbye cruel world!")


@bot.command(aliases=['help','helpme'])
async def commands(ctx):
    embed = discord.Embed(title="Help Incoming!!!", color=discord.colour.Color.green())
    embed.add_field(name="$ping",value="Displays the ping, and the configuration of the bot.",inline=True)
    embed.add_field(name="$uptime",value="Displays the uptime of the bot.",inline=True)
    embed.add_field(name="$join",value="Makes to the bot join the voice channel",inline=True)
    embed.add_field(name="$leave",value="Makes to the bot leave the voice channel",inline=True)
    embed.add_field(name="$mute",value="Mutes a member.\nUsage = $mute {player} {length} {reason}",inline=True)
    embed.add_field(name="$kick",value="Kicks a player from the server. {REQUIRES KICK_PLAYERS}\nUsage = $kick {"
                                       "player} {length} {reason}",inline=True)
    embed.add_field(name="$ban",value="Bans a player from the server. {REQUIRES BAN_PLAYERS}\nUsage = $ban {player} {"
                                      "reason}",inline=True)
    embed.add_field(name="$unban",value="Unbans a banned player. {REQUIRES BAN_PLAYERS}\nUsage =$unban {player}",inline=True)
    embed.add_field(name="$warn",value="Warns a player. {REQUIRES MANAGE_ROLES & BAN_PLAYERS}\nUsage =$warn {player} "
                                       "{reason}",inline=True)
    embed.add_field(name="$warnings",value="Displays the warnings of a member.\nUsage = $warnings {player}",inline=True)
    await ctx.send(embed=embed)
bot.run(token)
