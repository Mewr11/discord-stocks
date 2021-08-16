import discord
from discord.ext import commands

import requests

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
KEY = os.getenv('POLYTON_KEY')

bot = commands.Bot(command_prefix='./')

@bot.command(name='echo', help='Repeats the argument back to you')
async def command_echo(ctx, arg):
    await ctx.send(arg)

@bot.command(name='view', help='<symbol> View the stock represented by <symbol>')
async def command_view(ctx, symbol):
    symbol = symbol.upper()
    resp = requests.get(f'https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?apiKey=1DEPJCKqNkQiOnChmhcRYe6M4GyoysgV')
    r = resp.json()['results'][0]
    message = f'Yesterday for {symbol}:\nOpen: ${r["o"]}\nClose: ${r["c"]}\nHigh: ${r["h"]}\nLow: ${r["l"]}'
    await ctx.send(message)

def main():
    bot.run(TOKEN)

if __name__ == '__main__':
    main()

