import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

# Cargar el archivo .env
load_dotenv("TokenDiscord.env")
TOKEN = os.getenv('DISCORD_TOKEN')

# Activar los intents necesarios
intents = discord.Intents.default()
intents.message_content = True

# Crear el bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ El Oráculo está conectado como {bot.user}")

async def setup():
    # Cargar los cogs
    for archivo in os.listdir('./cogs'):
        if archivo.endswith('.py'):
            await bot.load_extension(f'cogs.{archivo[:-3]}')
            print(f"🧩 Cargado: {archivo}")
    
    await bot.start(TOKEN)

# Ejecutar todo
asyncio.run(setup())
