
import discord
import json
from discord.ext import commands
import datetime


class Vanityroles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.group(aliases=['vr'])
    @commands.has_permissions(administrator=True)
    async def vanityroles(self, ctx):
     if ctx.subcommand_passed is None:
        await ctx.send_help(ctx.command)
        ctx.command.reset_cooldown(ctx)
      
    @vanityroles.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx, vanity,
                     channel: discord.TextChannel,role: discord.Role):
        with open("vanityroles.json", "r") as f:
            idk = json.load(f)
            if ctx.author == ctx.guild.owner or ctx.guild.me.top_role <= ctx.author.top_role:
                if role.permissions.administrator or role.permissions.ban_members or role.permissions.kick_members:
                    embed1 = discord.Embed(
                        description=
                        "Vanity roles won't be setup while role have administrator",
                        color=discord.Color.default())
                    await ctx.send(embed=embed1)
                else:
                    pop = {
                        "vanity": vanity,
                        "role": role.id,
                        "channel": channel.id
                    }
                    idk[str(ctx.guild.id)] = pop
                    embed = discord.Embed(color=discord.Color.default())
                    embed.set_author(name=f"Vanity Roles Config For {ctx.guild}", icon_url=ctx.author.display_avatar.url, url="https://discord.gg/W9GQPFCKqq")
                    embed.add_field(name="<:dot_white:1103476115709890682> **__Vanity__**", value='Not Set' if vanity is None else vanity, inline=False)
                    embed.add_field(name="<:dot_white:1103476115709890682> **__Role__**", value='Not Set' if role is None else role.mention, inline=False)
                    embed.add_field(name="<:dot_white:1103476115709890682> **__Channel__**", value='Not Set' if channel is None else channel.mention, inline=False)

                    await ctx.send(embed=embed, mention_author=False)
                    with open("vanityroles.json", "w") as f:
                        json.dump(idk, f, indent=4)
            else:
                embed5 = discord.Embed(
                    description=
                    """You have to be top of my role""",
                    color=discord.Color.default())
                await ctx.reply(embed=embed5, mention_author=False)

  
    @vanityroles.command(aliases=[('delete','remove')])
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx):
        with open("vanityroles.json", "r") as f:
            xd = json.load(f)
            if ctx.author == ctx.guild.owner or ctx.guild.me.top_role <= ctx.author.top_role:
                if str(ctx.guild.id) not in xd:
                    embed1 = discord.Embed(
                        description=
                        "Please add vanity roles first",
                        color=discord.Color.default())
                    await ctx.reply(embed=embed1, mention_auto=False)
                else:
                    xd.pop(str(ctx.guild.id))
                    await ctx.reply(embed=discord.Embed(color=discord.Color.default(), description="Successfully Removed Vanity-Roles Setup"),
                        mention_author=False)
                    with open('vanityroles.json', 'w') as f:
                        json.dump(xd, f, indent=4)
            else:
                embed5 = discord.Embed(
                    description=
                    """You have to be top of my role""",
                    color=discord.Color.default())
                await ctx.reply(embed=embed5, mention_author=False)

    @vanityroles.command(aliases=[("show")])
    
    
    
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        with open("vanityroles.json", "r") as f:
            xd = json.load(f)
        if str(ctx.guild.id) not in xd:
            embed1 = discord.Embed(
                        description=
                        "Please add vanity roles first",
                        color=discord.Color.default())
            await ctx.reply(embed=embed1, mention_author=False)
        elif str(ctx.guild.id) in xd:
            vanity = xd[str(ctx.guild.id)]["vanity"]
            role = xd[str(ctx.guild.id)]["role"]
            channel = xd[str(ctx.guild.id)]["channel"]
            channel = self.bot.get_channel(channel)
            role = ctx.guild.get_role(role)
            embed = discord.Embed(color=discord.Color.default())
            embed.set_author(name=f"Vanity Roles Config For {ctx.guild}", icon_url=ctx.author.display_avatar.url, url="https://discord.gg/W9GQPFCKqq")
            embed.add_field(name="<:dot_white:1103476115709890682> **__Vanity__**", value='Not Set' if vanity is None else vanity, inline=False)
            embed.add_field(name="<:dot_white:1103476115709890682> **__Role__**", value='Not Set' if role is None else role.mention, inline=False)
            embed.add_field(name="<:dot_white:1103476115709890682> **__Channel__**", value='Not Set' if channel is None else channel.mention, inline=False)

            await ctx.send(embed=embed, mention_author=False)


    
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        with open("vanityroles.json", "r") as f:
            jnl = json.load(f)
        if str(before.guild.id) not in jnl:
            return

        vanity = jnl[str(before.guild.id)]["vanity"]
        role = jnl[str(before.guild.id)]["role"]
        channel = jnl[str(before.guild.id)]["channel"]

        if str(before.status) == "offline":
            return

        gchannel = self.bot.get_channel(channel)
        grole = after.guild.get_role(role)

        if before.bot or before.guild.id != after.guild.id or before.activity == after.activity:
            return

        if vanity in str(after.activity).lower() and grole not in after.roles:
            await after.add_roles(grole, reason=f"Added {vanity} In Status")
            embed = discord.Embed(color=discord.Color.default(), title="New Vanity Status!",
                                  description=f"{after.mention}, Thank you for showing support for `{vanity}` in your status!\n Your support means a lot to us and helps us grow. We truly appreciate it and hope that you continue to enjoy our community. Thank you again!")
            await gchannel.send(embed=embed)

        elif vanity not in str(after.activity).lower() and grole in after.roles:
            await after.remove_roles(grole, reason=f"Removed {vanity} From Status")
            embed = discord.Embed(color=discord.Color.default(),
                                  title="New Vanity Status Remove!",
                                  description=f"{after.mention}, Thank you for showing support for `{vanity}` in your status!\n Your support means a lot to us and helps us grow. We truly appreciate it and hope that you continue to enjoy our community. Thank you again!")
            await gchannel.send(embed=embed)