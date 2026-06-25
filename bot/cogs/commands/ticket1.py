import discord
from discord.ext import commands
import json

class devansh16(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Ticket commands"""  

    def help_custom(self):
		      emoji = '<:Icon_Ticket:1103358644747251742>'
		      label = "Ticket"
		      description = ""
		      return emoji, label, description

    @commands.group()
    async def __Tickets__(self, ctx: commands.Context):
        """`sendpanel`"""
       
    

    
   

