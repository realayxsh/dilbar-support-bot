from __future__ import annotations
import discord
from discord.ext import commands, tasks
from core import *
from utils.Tools import *


class Jsk(commands.Cog):

    def __init__(self, bot):
        self.bot = bot