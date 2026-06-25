import discord
from discord.ext import commands


class devansh7(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Vanityroles commands"""
  
    def help_custom(self):
		      emoji = '<:icons_premiumchannel:1103358451490496644>'
		      label = "Vanityroles"
		      description = ""
		      return emoji, label, description

    @commands.group()
    async def __Vanityroles__(self, ctx: commands.Context):
        """`vanityroles` , `vanityroles show` , `vanityroles config` , `vanityroles reset` , `vanityroles setup`"""