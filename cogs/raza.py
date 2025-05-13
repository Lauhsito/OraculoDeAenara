import discord
from discord.ext import commands
import random
import json
import os

# ID del creador/admin
CREADOR_ID = 621412276452327440

# Lista de razas (nombre, emoji)
RAZAS = [
    ("Humano", "🧙‍♂️"),
    ("Elfo", "🧝‍♂️"),
    ("Orco", "👹"),
    ("Draconiano", "🐉"),
    ("Hada", "🧚‍♀️"),
    ("Centauro", "🐎"),
    ("Goblin", "🟢"),
    ("Mecánico", "🤖"),
    ("🎲 Aleatoria", "🎲")
]

# --- Subclase del SELECT ---
class RazaSelect(discord.ui.Select):
    def __init__(self, user_id, personajes, guardar_func):
        self.user_id = user_id
        self.personajes = personajes
        self.guardar_func = guardar_func

        opciones = [
            discord.SelectOption(label=nombre, value=nombre, emoji=emoji)
            for nombre, emoji in RAZAS
        ]

        super().__init__(placeholder="Selecciona tu raza...", options=opciones)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ No puedes elegir por otro usuario.", ephemeral=True)
            return

        eleccion = self.values[0]
        if eleccion == "🎲 Aleatoria":
            eleccion = random.choice([n for n, _ in RAZAS if n != "🎲 Aleatoria"])

        self.personajes[str(self.user_id)] = eleccion
        self.guardar_func()
        await interaction.response.edit_message(
            content=f"✅ Has creado tu personaje como **{eleccion}**.", view=None
        )

# --- Subclase del VIEW ---
class RazaView(discord.ui.View):
    def __init__(self, user_id, personajes, guardar_func):
        super().__init__(timeout=60)
        self.add_item(RazaSelect(user_id, personajes, guardar_func))

# --- COG principal ---
class CrearPersonaje(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.archivo = "personajes.json"
        self.personajes = self.cargar_personajes()

    def cargar_personajes(self):
        if os.path.exists(self.archivo):
            with open(self.archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def guardar_personajes(self):
        with open(self.archivo, "w", encoding="utf-8") as f:
            json.dump(self.personajes, f, indent=4)

    @commands.command(name="crearpj")
    async def crear_personaje(self, ctx):
        user_id = ctx.author.id

        if str(user_id) in self.personajes and user_id != CREADOR_ID:
            await ctx.send("⚠️ Ya has creado tu personaje.")
            return

        view = RazaView(user_id, self.personajes, self.guardar_personajes)
        await ctx.send("🌌 Elige tu raza para comenzar tu viaje en Aenara:", view=view)

    @commands.command(name="verpj")
    async def ver_personaje(self, ctx):
        raza = self.personajes.get(str(ctx.author.id))
        if not raza:
            await ctx.send("❌ Aún no has creado tu personaje.")
        else:
            await ctx.send(f"📜 Tu personaje es un **{raza}**.")

    @commands.command(name="eliminarpj")
    async def eliminar_personaje(self, ctx):
        if ctx.author.id != CREADOR_ID:
            await ctx.send("❌ Solo el creador puede usar este comando.")
            return

        if str(ctx.author.id) in self.personajes:
            self.personajes.pop(str(ctx.author.id))
            self.guardar_personajes()
            await ctx.send("🗑️ Tu personaje fue eliminado.")
        else:
            await ctx.send("ℹ️ No habías creado un personaje.")

    @commands.command(name="modificarpj")
    async def modificar_personaje(self, ctx, *, nueva_raza: str):
        if ctx.author.id != CREADOR_ID:
            await ctx.send("❌ Solo el creador puede modificar razas manualmente.")
            return

        nombres_validos = [n for n, _ in RAZAS if n != "🎲 Aleatoria"]

        if nueva_raza not in nombres_validos:
            await ctx.send(f"❌ Raza inválida. Opciones válidas: {', '.join(nombres_validos)}")
            return

        self.personajes[str(ctx.author.id)] = nueva_raza
        self.guardar_personajes()
        await ctx.send(f"♻️ Raza modificada manualmente a **{nueva_raza}**.")

# --- Registro del COG ---
async def setup(bot):
    await bot.add_cog(CrearPersonaje(bot))
