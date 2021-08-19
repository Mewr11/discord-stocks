import discord
from discord.ext import commands, tasks

import yfinance as yf
import pandas as pd

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

pd.options.plotting.backend = 'plotly'

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

@bot.command(name='graph', help='<symbol> View a 1-month graph of a stock')
async def command_graph(ctx, symbol):
    guild_id = ctx.guild.id

    ticker = yf.Ticker(symbol)
    hist = ticker.history('1mo')['Close']
    hist = hist.rename(symbol.upper())

    fig = hist.plot(template='simple_white',
                    labels=dict(value='Stock Price', variable='Stock'))
    fig.update_yaxes(tickprefix='$')

    fig.to_image('png')
    if not os.path.exists('images'):
        os.mkdir('images')
    fig.write_image(f'images/{guild_id}.png')

    await ctx.send(file=discord.File(f'images/{guild_id}.png'))

@tasks.loop(seconds=60)
async def task_test():
    for guild in bot.guilds:
        if guild.id in guild_report:
            for channel in guild.channels:
                if channel.name == 'stock-reports':
                    msg = 'Stocks in report:'
                    for symbol in guild_report[guild.id]:
                        msg += ' - ' + symbol + '\n'
                    await channel.send(msg)

@bot.event
async def on_ready():
    task_test.start()

def main():
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
