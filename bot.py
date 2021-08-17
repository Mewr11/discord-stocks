import discord
from discord.ext import commands

import yfinance as yf

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='./')

@bot.command(name='echo', help='Repeats the argument back to you')
async def command_echo(ctx, arg):
    await ctx.send(arg)

@bot.command(name='view', help='<symbol> View the stock represented by <symbol>')
async def command_view(ctx, symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d")
    c, o, h, l = hist['Close'][0], hist['Open'][0], hist['High'][0], hist['Low'][0]
    d = hist.index[0].date().strftime('%d %b %Y')
    await ctx.send(f'{d} for {symbol.upper()}:\nCurrent - ${c:.2f}\nOpen - ${o:.2f}\nHigh - ${h:.2f}\nLow - ${l:.2f}')

def main():
    bot.run(TOKEN)

if __name__ == '__main__':
    main()

