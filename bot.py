import discord
from discord.ext import commands

import yfinance as yf

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='./')
guild_report = {}


@bot.command(name='echo', help='Repeats the argument back to you')
async def command_echo(ctx, arg):
    await ctx.send(arg)


@bot.command(name='view', help='<symbol> View the current, open, and daily high and low of a stock')
async def command_view(ctx, symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d")
    c, o, h, l = hist['Close'][0], hist['Open'][0], hist['High'][0], hist['Low'][0]
    d = hist.index[0].date().strftime('%d %b %Y')
    await ctx.send(f'{d} for {symbol.upper()}:\nCurrent - ${c:.2f}\nOpen - ${o:.2f}\nHigh - ${h:.2f}\nLow - ${l:.2f}')

@bot.command(name='add', help='<symbol> Add a stock to the daily report')
async def command_add(ctx, symbol):
    guild_id = ctx.guild.id
    if guild_id in guild_report:
        guild_report[guild_id].append(symbol.upper())
    else:
        guild_report[guild_id] = [symbol.upper()]
    await ctx.send('Current Report:\n' + ' - '.join(guild_report[guild_id]))

@bot.command(name='remove', help='<symbol> Remove a stock from the daily report')
async def command_remove(ctx, symbol):
    guild_id = ctx.guild.id
    symbol = symbol.upper()
    if guild_id in guild_report:
        if symbol in guild_report[guild_id]:
            guild_report[guild_id].remove(symbol)
            await ctx.send(f'Removed {symbol}. Current Report:\n' + ' - '.join(guild_report[guild_id]))
        else:
            await ctx.send(f'{symbol} is not in the current report.')
    else:
        await ctx.send(f'{symbol} is not in the current report.')

@bot.command(name='clear', help='Remove all stocks from the daily report')
async def command_clear(ctx):
    guild_id = ctx.guild.id
    guild_report[guild_id] = []
    await ctx.send('Daily report cleared.')

def main():
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
