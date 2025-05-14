import discord
from discord.ext import commands
import random
import json
import os

CREADOR_ID = 621412276452327440

RAZAS = [
    ("Humano", "🧙‍♂️"),
    ("Elfo", "🧝‍♂️"),
    ("Orco", "👹"),
    ("Draconiano", "🐉"),
    ("Hada", "🧚‍♀️"),
    ("Centauro", "🐎"),
    ("Goblin", "🟢"),
    ("Máquina", "🤖"),
    ("🎲 Aleatoria", "🎲")
]

GENEROS = ["Masculino", "Femenino"]

ELEMENTOS = [
    ("Agua", "💧"),
    ("Planta", "🌿"),
    ("Hielo", "❄️"),
    ("Fuego", "🔥"),
    ("Viento", "🍃"),
    ("Piedra", "🪨"),
    ("Eléctrico", "⚡")
]

# --- SELECT DE RAZA ---
class RazaSelect(discord.ui.Select):
    def __init__(self, user_id, personajes, guardar_func, bot):
        self.user_id = user_id
        self.personajes = personajes
        self.guardar_func = guardar_func
        self.bot = bot

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

        self.personajes[str(self.user_id)] = {"raza": eleccion}
        self.guardar_func()

        await interaction.response.edit_message(content=f"✅ Has elegido ser un **{eleccion}**.", view=None)

        view = GeneroView(self.user_id, self.personajes, self.guardar_func, self.bot)
        await interaction.followup.send("⚧️ Ahora elige el **género** de tu personaje:", view=view)

# --- VIEW DE RAZA ---
class RazaView(discord.ui.View):
    def __init__(self, user_id, personajes, guardar_func, bot):
        super().__init__(timeout=60)
        self.add_item(RazaSelect(user_id, personajes, guardar_func, bot))

# --- SELECT DE GÉNERO ---
class GeneroSelect(discord.ui.Select):
    def __init__(self, user_id, personajes, guardar_func, bot):
        self.user_id = user_id
        self.personajes = personajes
        self.guardar_func = guardar_func
        self.bot = bot

        opciones = [discord.SelectOption(label=g, value=g) for g in GENEROS]

        super().__init__(placeholder="Selecciona el género...", options=opciones)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ No puedes elegir por otro usuario.", ephemeral=True)
            return

        genero = self.values[0]
        self.personajes[str(self.user_id)]["genero"] = genero
        self.guardar_func()

        await interaction.response.edit_message(content=f"✅ Género seleccionado: **{genero}**.", view=None)

        canal = interaction.channel
        usuario = interaction.user

        await canal.send("📝 ¿Cuál es el **nombre** de tu personaje?")

        def check(m):
            return m.author.id == usuario.id and m.channel.id == canal.id

        try:
            respuesta = await self.bot.wait_for("message", timeout=60, check=check)
            self.personajes[str(self.user_id)]["nombre"] = respuesta.content
            self.guardar_func()
        except Exception:
            await canal.send("⏰ Tiempo agotado. Podés completar tu ficha más tarde.")
            return

        # Selección de elemento
        view = ElementoView(self.user_id, self.personajes, self.guardar_func)
        await canal.send("🔮 Finalmente, elige tu **elemento**:", view=view)

# --- VIEW DE GÉNERO ---
class GeneroView(discord.ui.View):
    def __init__(self, user_id, personajes, guardar_func, bot):
        super().__init__(timeout=60)
        self.add_item(GeneroSelect(user_id, personajes, guardar_func, bot))

# --- SELECT DE ELEMENTO ---
class ElementoSelect(discord.ui.Select):
    def __init__(self, user_id, personajes, guardar_func):
        self.user_id = user_id
        self.personajes = personajes
        self.guardar_func = guardar_func

        opciones = [
            discord.SelectOption(label=nombre, value=nombre, emoji=emoji)
            for nombre, emoji in ELEMENTOS
        ]

        super().__init__(placeholder="Selecciona tu elemento...", options=opciones)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ No puedes elegir por otro usuario.", ephemeral=True)
            return

        elemento = self.values[0]
        self.personajes[str(self.user_id)]["elemento"] = elemento
        self.guardar_func()

        await interaction.response.edit_message(content=f"🔗 Elemento seleccionado: **{elemento}**. ¡Tu ficha ha sido completada!", view=None)

# --- VIEW DE ELEMENTO ---
class ElementoView(discord.ui.View):
    def __init__(self, user_id, personajes, guardar_func):
        super().__init__(timeout=60)
        self.add_item(ElementoSelect(user_id, personajes, guardar_func))

# --- COG ---
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

        view = RazaView(user_id, self.personajes, self.guardar_personajes, self.bot)
        await ctx.send("🌌 Elige tu raza para comenzar tu viaje en Aenara:", view=view)

    @commands.command(name="verpj")
    async def ver_personaje(self, ctx):
        pj = self.personajes.get(str(ctx.author.id))
        if not pj:
            await ctx.send("❌ Aún no has creado tu personaje.")
        else:
            ficha = f"📜 **Tu personaje:**\n"
            for clave, valor in pj.items():
                ficha += f"• **{clave.capitalize()}**: {valor}\n"
            await ctx.send(ficha)

# --- Registro del COG ---
async def setup(bot):
    await bot.add_cog(CrearPersonaje(bot))
