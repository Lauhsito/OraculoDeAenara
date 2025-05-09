import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Cargar el archivo .env
load_dotenv("TokenDiscord.env")  # Asegurate de que el nombre coincida exactamente
TOKEN = os.getenv('DISCORD_TOKEN')

# Activar los intents necesarios
intents = discord.Intents.default()
intents.message_content = True

# Crear el bot con prefijo "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# Evento de conexión
@bot.event
async def on_ready():
    print(f"✅ El Oráculo está conectado como {bot.user}")

# Comando de prueba
@bot.command()
async def hola(ctx):
    await ctx.send(f"👁️ Hola, {ctx.author.name}... el Oráculo te observa.")

# Ejecutar el bot
bot.run(TOKEN)
