from __future__ import annotations
from core import Ventura



#____________ Commands ___________

#####################3
from .commands.help import Help
from .commands.general import General
from .commands.moderation import Moderation
from .commands.anti import Security
from .commands.raidmode import Automod
from .commands.welcome import Welcomer
from .commands.Afk import afk
from .commands.extra import Utility
from .commands.owner import Owner
from .commands.vcroles import Voice
from .commands.role import Server
from .commands.ignore import Ignore
from .commands.vanityroles import Vanityroles
from .commands.ticket import Ticket
from .commands.jsk import Jsk
from .commands.giveaway import Giveaway



#____________ Events _____________
from .events.antiban import antiban
from .events.antichannel import antichannel
from .events.antiguild import antiguild
from .events.antirole import antirole
from .events.antibot import antibot
from .events.antikick import antikick
from .events.antiprune import antiprune
from .events.antiwebhook import antiwebhook
from .events.antiping import antipinginv
from .events.antiemostick import antiemostick
from .events.antintegration import antintegration
from .events.antispam import AntiSpam
from .events.autoblacklist import AutoBlacklist
from .events.antiemojid import antiemojid
from .events.antiemojiu import antiemojiu
from .events.Errors import Errors
from .events.on_guild import Guild
from .events.autorole import Autorole2
from .events.greet2 import greet
from .events.voiceupdate import Vcroles2


##############33cogs#############
from .commands.anti1 import devansh1
from .commands.general1 import devansh102
from .commands.raidmode1 import shree1227
from .commands.welcome1 import devanshshree3110
from .commands.vanityroles1 import devansh7
from .commands.ticket1 import devansh16
from .commands.server import devansh1227
from .commands.mod2 import devansh3110
from .commands.extra1 import devansh2
from .commands.voice import shree00
from .commands.vcrole1 import devansh00
from .commands.ignore1 import devansh12


async def setup(bot: Ventura):
  await bot.add_cog(Help(bot))
  await bot.add_cog(General(bot))
  await bot.add_cog(Moderation(bot))
  await bot.add_cog(Security(bot))
  await bot.add_cog(Automod(bot))
  await bot.add_cog(Welcomer(bot))
  await bot.add_cog(afk(bot))
  await bot.add_cog(Utility(bot))
  await bot.add_cog(Voice(bot))
  await bot.add_cog(Owner(bot))
  await bot.add_cog(Server(bot))
  await bot.add_cog(Vanityroles(bot))
  await bot.add_cog(Ticket(bot))
  await bot.add_cog(Ignore(bot))
  await bot.add_cog(Jsk(bot))
  await bot.add_cog(Giveaway(bot))


####################



  await bot.add_cog(devansh1(bot))
  await bot.add_cog(devansh102(bot))
  await bot.add_cog(shree1227(bot))
  await bot.add_cog(devanshshree3110(bot))
  await bot.add_cog(devansh7(bot))
  await bot.add_cog(devansh16(bot))
  await bot.add_cog(devansh1227(bot))
  await bot.add_cog(devansh3110(bot))
  await bot.add_cog(devansh2(bot))
  await bot.add_cog(shree00(bot))
  await bot.add_cog(devansh00(bot))
  await bot.add_cog(devansh12(bot))



###########################events################3

  await bot.add_cog(antiban(bot))
  await bot.add_cog(antichannel(bot))
  await bot.add_cog(antiguild(bot))
  await bot.add_cog(antirole(bot))
  await bot.add_cog(antibot(bot))
  await bot.add_cog(antikick(bot))
  await bot.add_cog(antiprune(bot))
  await bot.add_cog(antiwebhook(bot))
  await bot.add_cog(antipinginv(bot))
  await bot.add_cog(antiemostick(bot))
  await bot.add_cog(antintegration(bot))
  await bot.add_cog(AntiSpam(bot))
  await bot.add_cog(AutoBlacklist(bot))
  await bot.add_cog(antiemojid(bot))
  await bot.add_cog(antiemojiu(bot))
  await bot.add_cog(Guild(bot))
  await bot.add_cog(Errors(bot))
  await bot.add_cog(Autorole2(bot))
  await bot.add_cog(greet(bot))
  await bot.add_cog(Vcroles2(bot))
