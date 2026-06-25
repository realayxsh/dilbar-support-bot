from __future__ import annotations
from discord.ext import commands
from utils.Tools import *
from discord import *
from utils.config import OWNER_IDS, No_Prefix
import json, discord
import typing
import aiohttp
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator

from typing import Optional


class Owner(commands.Cog):

    def __init__(self, client):
        self.client = client
      
    @commands.command(name="slist")
    @commands.is_owner()
    async def slist(self, ctx):
        devansh37 = ([devansh for devansh in self.client.guilds])
        devansh37 = sorted(devansh37,
                         key=lambda devansh: devansh.member_count,
                         reverse=True)
        entries = [
            f"`[{i}]` | [{g.name}](https://discord.com/channels/{g.id}) - {g.member_count}"
            for i, g in enumerate(devansh37, start=1)
        ]
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            description="",
            title=f"Server List of Ventura - {len(self.client.guilds)}",
            color=discord.Color.default(),
            per_page=10),
                              ctx=ctx)
        await paginator.paginate()

    @commands.command(name="restart", help="Restarts the client.")
    @commands.is_owner()
    async def _restart(self, ctx: Context):
        await ctx.reply("Restarting!")
        restart_program()
      
    @commands.command(name="sync", help="Syncs all database.")
    @commands.is_owner()
    async def _sync(self, ctx):
        await ctx.reply("Syncing...", mention_author=False)
        with open('anti.json', 'r') as f:
            data = json.load(f)
        for guild in self.client.guilds:
            if str(guild.id) not in data['guild']:
                data['guilds'][str(guild.id)] = 'on'
                with open('anti.json', 'w') as f:
                    json.dump(data, f, indent=4)
            else:
                pass
        with open('config.json', 'r') as f:
            data = json.load(f)
        for op in data["guilds"]:
            g = self.client.get_guild(int(op))
            if not g:
                data["guilds"].pop(str(op))
                with open('config.json', 'w') as f:
                    json.dump(data, f, indent=4)

    @commands.group(name="blacklist",
                    help="let's you add someone in blacklist",
                    aliases=["bl"])
    @commands.is_owner()
    async def blacklist(self, ctx):
        if ctx.invoked_subcommand is None:
            with open("blacklist.json") as file:
                blacklist = json.load(file)
                entries = [
                    f"`[{no}]` | <@!{mem}> (ID: {mem})"
                    for no, mem in enumerate(blacklist['ids'], start=1)
                ]
                paginator = Paginator(source=DescriptionEmbedPaginator(
                    entries=entries,
                    title=
                    f"List of Blacklisted users of Ventura - {len(blacklist['ids'])}",
                    description="",
                    per_page=10,
                    color=discord.Color.default()),
                                      ctx=ctx)
                await paginator.paginate()

    @blacklist.command(name="add")
    @commands.is_owner()
    async def blacklist_add(self, ctx: Context, member: discord.Member):
        try:
            with open('blacklist.json', 'r') as bl:
                blacklist = json.load(bl)
                if str(member.id) in blacklist["ids"]:
                    embed = discord.Embed(
                        title="Error!",
                        description=f"{member.name} is already blacklisted",
                        color=discord.Color.default())
                    await ctx.reply(embed=embed, mention_author=False)
                else:
                    add_user_to_blacklist(member.id)
                    embed = discord.Embed(
                        title="Blacklisted",
                        description=f"Successfully Blacklisted {member.name}",
                        color=discord.Color.default())
                    with open("blacklist.json") as file:
                        blacklist = json.load(file)
                        embed.set_footer(
                            text=
                            f"There are now {len(blacklist['ids'])} users in the blacklist"
                        )
                        await ctx.reply(embed=embed, mention_author=False)
        except:
            embed = discord.Embed(title="Error!",
                                  description=f"An Error Occurred",
                                  color=discord.Color.default())
            await ctx.reply(embed=embed, mention_author=False)

    @blacklist.command(name="remove")
    @commands.is_owner()
    async def blacklist_remove(self, ctx, member: discord.Member = None):
        try:
            remove_user_from_blacklist(member.id)
            embed = discord.Embed(
                title="User removed from blacklist",
                description=
                f"<a:green_tick:1103363669263405157> | **{member.name}** has been successfully removed from the blacklist",
                color=discord.Color.default())
            with open("blacklist.json") as file:
                blacklist = json.load(file)
                embed.set_footer(
                    text=
                    f"There are now {len(blacklist['ids'])} users in the blacklist"
                )
                await ctx.reply(embed=embed, mention_author=False)
        except:
            embed = discord.Embed(
                title="Error!",
                description=f"**{member.name}** is not in the blacklist.",
                color=discord.Color.default())
            await ctx.reply(embed=embed, mention_author=False)

    @commands.group(
        name="np",
        help="Manage the no-prefix list (owner only)"
    )
    @commands.is_owner()
    async def _np(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @_np.command(name="list")
    @commands.is_owner()
    async def np_list(self, ctx):
        with open("info.json") as f:
            np = json.load(f)
            nplist = np["np"]
            npl = ([await self.client.fetch_user(nplu) for nplu in nplist])
            npl = sorted(npl, key=lambda nop: nop.created_at)
            entries = [
                f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) (ID: {mem.id})"
                for no, mem in enumerate(npl, start=1)
            ]
            paginator = Paginator(source=DescriptionEmbedPaginator(
                entries=entries,
                title=f"No Prefix — Dilbar Support ({len(nplist)})",
                description="",
                per_page=10,
                color=discord.Color.default()),
                                  ctx=ctx)
            await paginator.paginate()

    @_np.command(name="add", help="Add user to no prefix")
    @commands.is_owner()
    async def np_add(self, ctx, user: discord.User):
        with open('info.json', 'r') as idk:
            data = json.load(idk)
        np = data["np"]
        if user.id in np:
            embed = discord.Embed(
                description=
                f"**The User You Provided Already In My No Prefix**",
                color=discord.Color.default())
            await ctx.reply(embed=embed)
            return
        else:
            data["np"].append(user.id)
        with open('info.json', 'w') as idk:
            json.dump(data, idk, indent=4)
            embed1 = discord.Embed(
                description=
                f"<a:green_tick:1103363669263405157> | Added no prefix to {user} for all",
                color=discord.Color.default())
          
            await ctx.reply(embed=embed1)

    @_np.command(name="remove", help="Remove user from no prefix")
    @commands.is_owner()
    async def np_remove(self, ctx, user: discord.User):
        with open('info.json', 'r') as idk:
            data = json.load(idk)
        np = data["np"]
        if user.id not in np:
            embed = discord.Embed(
                description="**{} is not in no prefix!**".format(user),
                color=discord.Color.default())
            await ctx.reply(embed=embed)
            return
        else:
            data["np"].remove(user.id)
        with open('info.json', 'w') as idk:
            json.dump(data, idk, indent=4)
            embed2 = discord.Embed(
                description=
                f"<a:green_tick:1103363669263405157> | Removed no prefix from {user} for all",
                color=discord.Color.default())

            await ctx.reply(embed=embed2)



    @commands.command()
    @commands.is_owner()
    async def dm(self, ctx, user: discord.User, *, message: str):
        """ DM the user of your choice """
        try:
            await user.send(message)
            await ctx.send(f"<a:green_tick:1103363669263405157> | Successfully Sent a DM to **{user}**")
        except discord.Forbidden:
            await ctx.send("This user might be having DMs blocked or it's a bot account...")           


    @commands.group()
    @commands.is_owner()
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))
            
            
    @change.command(name="nickname")
    @commands.is_owner()
    async def change_nickname(self, ctx, *, name: str = None):
        """ Change nickname. """
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"<a:green_tick:1103363669263405157> | Successfully changed nickname to **{name}**")
            else:
                await ctx.send("<a:green_tick:1103363669263405157> | Successfully removed nickname")
        except Exception as err:
            await ctx.send(err)


    @commands.command()
    @commands.is_owner()
    async def globalban(self, ctx, *, user: discord.User = None):
        if user is None:
            return await ctx.send(
                "You need to define the user"
            )
        for guild in self.client.guilds:
            for member in guild.members:
                if member == user:
                    await user.ban(reason="lund le lo")


    # ── Bot customization ──────────────────────────────────────────────────────

    @commands.hybrid_command(name="seticon",
                             help="Change the bot's avatar. Attach an image or provide a URL.",
                             usage="seticon [url] (or attach image)")
    @commands.is_owner()
    async def seticon(self, ctx, url: str = None):
        """Change the bot's profile picture via the Discord API."""
        # Resolve image bytes: attachment first, then URL argument
        image_url = url
        if ctx.message.attachments:
            image_url = ctx.message.attachments[0].url

        if not image_url:
            embed = discord.Embed(
                description="<:dot_white:1103476115709890682> Please attach an image or provide a URL.\n"
                            "**Usage:** `-seticon <url>` or attach an image to the command.",
                color=discord.Color.default())
            return await ctx.reply(embed=embed, mention_author=False)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status != 200:
                        embed = discord.Embed(
                            description="<:dot_white:1103476115709890682> Could not download the image. Make sure the URL is valid.",
                            color=discord.Color.default())
                        return await ctx.reply(embed=embed, mention_author=False)
                    data = await resp.read()

            await self.client.user.edit(avatar=data)
            embed = discord.Embed(
                description="<a:green_tick:1103363669263405157> | **Bot avatar updated successfully!**",
                color=discord.Color.default())
            embed.set_thumbnail(url=self.client.user.display_avatar.url)
            await ctx.reply(embed=embed, mention_author=False)

        except discord.HTTPException as e:
            embed = discord.Embed(
                description=f"<:dot_white:1103476115709890682> Failed to update avatar: `{e}`",
                color=discord.Color.default())
            await ctx.reply(embed=embed, mention_author=False)


    @commands.hybrid_command(name="setbanner",
                             help="Change the bot's banner. Attach an image or provide a URL.",
                             usage="setbanner [url] (or attach image)")
    @commands.is_owner()
    async def setbanner(self, ctx, url: str = None):
        """Change the bot's profile banner via the Discord API."""
        image_url = url
        if ctx.message.attachments:
            image_url = ctx.message.attachments[0].url

        if not image_url:
            embed = discord.Embed(
                description="<:dot_white:1103476115709890682> Please attach an image or provide a URL.\n"
                            "**Usage:** `-setbanner <url>` or attach an image to the command.",
                color=discord.Color.default())
            return await ctx.reply(embed=embed, mention_author=False)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status != 200:
                        embed = discord.Embed(
                            description="<:dot_white:1103476115709890682> Could not download the image. Make sure the URL is valid.",
                            color=discord.Color.default())
                        return await ctx.reply(embed=embed, mention_author=False)
                    data = await resp.read()

            await self.client.user.edit(banner=data)
            embed = discord.Embed(
                description="<a:green_tick:1103363669263405157> | **Bot banner updated successfully!**",
                color=discord.Color.default())
            await ctx.reply(embed=embed, mention_author=False)

        except discord.HTTPException as e:
            embed = discord.Embed(
                description=f"<:dot_white:1103476115709890682> Failed to update banner: `{e}`\n"
                            f"*(Note: Bot banner requires the bot to be verified / in 100+ servers)*",
                color=discord.Color.default())
            await ctx.reply(embed=embed, mention_author=False)


    # ── Send Embed (v2 Modal) ──────────────────────────────────────────────────

    @commands.hybrid_command(name="sendembed",
                             help="Send a custom embed to any channel using a modal form.",
                             usage="sendembed <#channel>",
                             with_app_command=True)
    @commands.is_owner()
    async def sendembed(self, ctx, channel: discord.TextChannel = None):
        """Open a Discord v2 modal form to compose and send an embed to any channel."""
        if channel is None:
            embed = discord.Embed(
                description="<:dot_white:1103476115709890682> Please specify a channel.\n"
                            "**Usage:** `-sendembed #channel`",
                color=discord.Color.default())
            return await ctx.reply(embed=embed, mention_author=False)

        # Store channel ref so the modal can access it
        target_channel = channel

        class EmbedModal(discord.ui.Modal, title="Send Embed — Dilbar Support"):
            embed_title = discord.ui.TextInput(
                label="Title",
                placeholder="Embed title (optional)",
                required=False,
                max_length=256,
            )
            description = discord.ui.TextInput(
                label="Description",
                style=discord.TextStyle.long,
                placeholder="Embed description (supports markdown)",
                required=True,
                max_length=4000,
            )
            thumbnail_url = discord.ui.TextInput(
                label="Thumbnail URL",
                placeholder="https://... (optional)",
                required=False,
                max_length=500,
            )
            image_url = discord.ui.TextInput(
                label="Image URL",
                placeholder="https://... (optional)",
                required=False,
                max_length=500,
            )
            footer_text = discord.ui.TextInput(
                label="Footer Text",
                placeholder="Footer (optional)",
                required=False,
                max_length=2048,
            )

            async def on_submit(self, interaction: discord.Interaction):
                embed = discord.Embed(color=discord.Color.default())
                if self.embed_title.value:
                    embed.title = self.embed_title.value
                if self.description.value:
                    embed.description = self.description.value
                if self.thumbnail_url.value:
                    embed.set_thumbnail(url=self.thumbnail_url.value)
                if self.image_url.value:
                    embed.set_image(url=self.image_url.value)
                if self.footer_text.value:
                    embed.set_footer(text=self.footer_text.value)

                try:
                    await target_channel.send(embed=embed)
                    confirm = discord.Embed(
                        description=f"<a:green_tick:1103363669263405157> | Embed sent to {target_channel.mention}",
                        color=discord.Color.default())
                    await interaction.response.send_message(embed=confirm, ephemeral=True)
                except discord.Forbidden:
                    err = discord.Embed(
                        description=f"<:dot_white:1103476115709890682> I don't have permission to send in {target_channel.mention}.",
                        color=discord.Color.default())
                    await interaction.response.send_message(embed=err, ephemeral=True)
                except discord.HTTPException as e:
                    await interaction.response.send_message(
                        f"Failed to send embed: `{e}`", ephemeral=True)

            async def on_error(self, interaction: discord.Interaction, error: Exception):
                await interaction.response.send_message(
                    f"Something went wrong: `{error}`", ephemeral=True)

        # Modals require an interaction — works via slash command or hybrid
        if ctx.interaction:
            await ctx.interaction.response.send_modal(EmbedModal())
        else:
            # Prefix fallback: send a trigger button so the user gets an interaction
            class ModalTrigger(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=60)

                @discord.ui.button(label="Open Embed Builder", style=discord.ButtonStyle.primary,
                                   emoji="<:dot_white:1103476115709890682>")
                async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user != ctx.author:
                        return await interaction.response.send_message("Not for you.", ephemeral=True)
                    await interaction.response.send_modal(EmbedModal())
                    self.stop()

            prompt = discord.Embed(
                description=f"Click below to open the embed builder for {target_channel.mention}",
                color=discord.Color.default())
            await ctx.reply(embed=prompt, view=ModalTrigger(), mention_author=False)
