import discord
from discord.ext import commands
import json

class devansh15(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Encryption commands"""  

    def help_custom(self):
		      emoji = '<:encryption:1103360958748954654>'
		      label = "Encryption"
		      description = ""
		      return emoji, label, description

    @commands.group()
    async def __Encryption__(self, ctx: commands.Context):
        """`h encode` , `encode base85` , `encode ascii85` ,`encode base64` , `encode rot13` , `encode base32` , `encode hex` , `h decode` , `decode base85` , `decode base64` , `decode hex` , `decode ascii85` , `decode base32` , `decode rot13`"""