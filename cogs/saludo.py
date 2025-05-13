from discord.ext import commands

class Saludo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hola(self, ctx):
        await ctx.send(f"👁️ Hola, {ctx.author.name}... el Oráculo te observa.")

# Esto es lo que hay que corregir:
async def setup(bot):
    await bot.add_cog(Saludo(bot))
