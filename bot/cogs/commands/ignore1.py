import discord
from discord.ext import commands
import json

class devansh12(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Ignore commands"""  

    def help_custom(self):
		      emoji = '<:nsfw32:1103360693119496262>'
		      label = "Ignore"
		      description = ""
		      return emoji, label, description

    @commands.group()
    async def __Ignore__(self, ctx: commands.Context):
        """`ignore` , `ignore channel add` , `ignore channel remove`"""
       