import discord
from discord.ext import commands, tasks

import yfinance as yf
import pandas as pd

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

pd.options.plotting.backend = 'plotly'

bot = commands.Bot(command_prefix='$')
guild_report = {}


@bot.command(name='echo', help='Repeats the argument back to you')
async def command_echo(ctx, arg):
    await ctx.send(arg)


@bot.command(name='view', help='<symbol> View the current, open, and daily high and low of a stock')
async def command_view(ctx, symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period='1d')
    if len(hist) == 0:
        await ctx.send(f'{symbol.upper()} not found.')
        return
    c, o, h, l = hist['Close'][0], hist['Open'][0], hist['High'][0], hist['Low'][0]
    d = hist.index[0].date().strftime('%d %b %Y')
    await ctx.send(f'{d} for {symbol.upper()}:\nCurrent - ${c:.2f}\nOpen - ${o:.2f}\nHigh - ${h:.2f}\nLow - ${l:.2f}')

@bot.command(name='add', help='<symbol> Add a stock to the daily report')
async def command_add(ctx, symbol):
    symbol = symbol.upper()
    if len(yf.Ticker(symbol).history(period='1d')) == 0:
        await ctx.send(f'{symbol} not found.')
        return
    guild = ctx.guild
    if guild.id in guild_report:
        if symbol not in guild_report[guild.id]:
            guild_report[guild.id].append(symbol)
        else:
            await ctx.send(f'{symbol} is already in the daily report.')
    else:
        guild_report[guild.id] = [symbol]
    await ctx.send('Current Report:\n' + ' - '.join(guild_report[guild.id]))

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
    
    if len(hist) == 0:
        await ctx.send(f'{symbol.upper()} not found.')
        return

    hist = hist.rename(symbol.upper())

    fig = hist.plot(template='simple_white',
                    labels=dict(value='Stock Price', variable='Stock'))
    fig.update_yaxes(tickprefix='$')

    fig.to_image('png')
    if not os.path.exists('images'):
        os.mkdir('images')
    fig.write_image(f'images/{guild_id}.png')

    await ctx.send(file=discord.File(f'images/{guild_id}.png'))

@tasks.loop(seconds=86400)
async def task_test():
    for guild in bot.guilds:
        if guild.id in guild_report:
            for channel in guild.channels:
                if channel.name == 'stock-reports':
                    r = {}
                    for symbol in guild_report[guild.id]:
                        t = yf.Ticker(symbol)
                        hist = t.history(period='1mo', interval='1d')['Close']
                        hist = hist.rename(symbol.upper())

                        r[symbol.upper()] = hist
                    df = pd.DataFrame(r)

                    fig = df.plot(template='simple_white',
                                  labels=dict(value='Stock Price', variable='Stock'))
                    fig.update_yaxes(tickprefix='$')

                    fig.to_image('png')
                    if not os.path.exists('images'):
                        os.mkdir('images')
                    fig.write_image(f'images/dr{guild.id}.png')

                    await channel.send(file=discord.File(f'images/dr{guild.id}.png'))

@bot.event
async def on_ready():
    for guild in bot.guilds:
        guild_report[guild.id] = ['AMC', 'GME']
    task_test.start()

def main():
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
