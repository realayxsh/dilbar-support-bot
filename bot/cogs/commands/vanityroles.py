
import discord
import json
import os
import asyncio
import aiohttp
from discord.ext import commands, tasks

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VANITY_FILE = os.path.join(BASE_DIR, "vanityroles.json")


def _load():
    with open(VANITY_FILE, "r") as f:
        return json.load(f)


def _save(data):
    with open(VANITY_FILE, "w") as f:
        json.dump(data, f, indent=4)


class Vanityroles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._bio_scan.start()

    def cog_unload(self):
        self._bio_scan.cancel()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _has_vanity_in_status(self, member: discord.Member, vanity: str) -> bool:
        """Return True if vanity string appears in any of the member's activities."""
        for activity in member.activities:
            if isinstance(activity, discord.CustomActivity):
                text = (activity.name or "") + " " + (activity.state or "")
            else:
                text = str(activity.name or "")
            if vanity.lower() in text.lower():
                return True
        return False

    async def _get_bio(self, user_id: int, guild_id: int) -> str:
        """Fetch the user's About Me bio via the Discord HTTP API."""
        token = os.environ.get("TOKEN", "")
        url = (
            f"https://discord.com/api/v10/users/{user_id}/profile"
            f"?guild_id={guild_id}&with_mutual_guilds=false"
        )
        headers = {"Authorization": f"Bot {token}"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return (data.get("user") or {}).get("bio") or ""
        except Exception:
            pass
        return ""

    async def _check_member(
        self,
        member: discord.Member,
        vanity: str,
        role: discord.Role,
        channel: discord.TextChannel | None,
    ):
        """Add or remove the vanity role based on status + bio."""
        if member.bot:
            return

        in_status = self._has_vanity_in_status(member, vanity)
        bio = await self._get_bio(member.id, member.guild.id)
        in_bio = vanity.lower() in bio.lower() if bio else False
        has_vanity = in_status or in_bio
        where = "status" if in_status else "bio"

        if has_vanity and role not in member.roles:
            await member.add_roles(role, reason=f"Has {vanity} in {where}")
            if channel:
                embed = discord.Embed(
                    color=discord.Color.default(),
                    title="Vanity Role Awarded!",
                    description=(
                        f"{member.mention}, thank you for repping `{vanity}` in your "
                        f"**{where}**! You've been given {role.mention}. 🎉"
                    ),
                )
                await channel.send(embed=embed)

        elif not has_vanity and role in member.roles:
            await member.remove_roles(role, reason=f"No longer has {vanity} in status/bio")
            if channel:
                embed = discord.Embed(
                    color=discord.Color.default(),
                    title="Vanity Role Removed",
                    description=(
                        f"{member.mention}, `{vanity}` is no longer in your status or bio — "
                        f"{role.mention} has been removed."
                    ),
                )
                await channel.send(embed=embed)

    # ── background bio scan ──────────────────────────────────────────────────

    @tasks.loop(minutes=5)
    async def _bio_scan(self):
        """Scan all members' bios every 5 min (no Discord event fires on bio change)."""
        data = _load()
        for guild_id, cfg in data.items():
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                continue
            vanity = cfg["vanity"]
            role = guild.get_role(cfg["role"])
            channel = self.bot.get_channel(cfg["channel"])
            if not role:
                continue
            for member in guild.members:
                if member.bot:
                    continue
                try:
                    await self._check_member(member, vanity, role, channel)
                    await asyncio.sleep(0.5)   # gentle rate-limit
                except Exception:
                    pass

    @_bio_scan.before_loop
    async def _before_bio_scan(self):
        await self.bot.wait_until_ready()

    # ── presence event ───────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        data = _load()
        guild_id = str(after.guild.id)
        if guild_id not in data:
            return

        cfg = data[guild_id]
        vanity = cfg["vanity"]
        role = after.guild.get_role(cfg["role"])
        channel = self.bot.get_channel(cfg["channel"])

        if after.bot:
            return

        await self._check_member(after, vanity, role, channel)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Also fires on role/nick changes — re-check bio whenever a member is updated."""
        data = _load()
        guild_id = str(after.guild.id)
        if guild_id not in data:
            return

        cfg = data[guild_id]
        vanity = cfg["vanity"]
        role = after.guild.get_role(cfg["role"])
        channel = self.bot.get_channel(cfg["channel"])

        if after.bot:
            return

        await self._check_member(after, vanity, role, channel)

    # ── commands ─────────────────────────────────────────────────────────────

    @commands.group(aliases=["vr"])
    @commands.has_permissions(administrator=True)
    async def vanityroles(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)

    @vanityroles.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def vr_setup(self, ctx, vanity: str, channel: discord.TextChannel, role: discord.Role):
        """Set up vanity roles: vanityroles setup <vanity> <#channel> <@role>"""
        if role.permissions.administrator or role.permissions.ban_members or role.permissions.kick_members:
            return await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.default(),
                    description="⚠️ Cannot use a role with Administrator / Ban / Kick permissions.",
                )
            )

        data = _load()
        data[str(ctx.guild.id)] = {
            "vanity": vanity,
            "role": role.id,
            "channel": channel.id,
        }
        _save(data)

        embed = discord.Embed(color=discord.Color.default())
        embed.set_author(name=f"Vanity Roles — {ctx.guild}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.add_field(name="Vanity", value=f"`{vanity}`", inline=False)
        embed.add_field(name="Role", value=role.mention, inline=False)
        embed.add_field(name="Log Channel", value=channel.mention, inline=False)
        embed.set_footer(text="Members with the vanity in their status or bio will auto-receive the role.")
        await ctx.send(embed=embed)

    @vanityroles.command(name="reset", aliases=["delete", "remove"])
    @commands.has_permissions(administrator=True)
    async def vr_reset(self, ctx):
        """Remove vanity roles setup for this server."""
        data = _load()
        if str(ctx.guild.id) not in data:
            return await ctx.send(
                embed=discord.Embed(color=discord.Color.default(), description="No vanity roles setup found for this server.")
            )
        data.pop(str(ctx.guild.id))
        _save(data)
        await ctx.send(
            embed=discord.Embed(color=discord.Color.default(), description="✅ Vanity roles setup removed.")
        )

    @vanityroles.command(name="config", aliases=["show"])
    @commands.has_permissions(administrator=True)
    async def vr_config(self, ctx):
        """Show current vanity roles config."""
        data = _load()
        if str(ctx.guild.id) not in data:
            return await ctx.send(
                embed=discord.Embed(color=discord.Color.default(), description="No vanity roles setup found for this server.")
            )
        cfg = data[str(ctx.guild.id)]
        role = ctx.guild.get_role(cfg["role"])
        channel = self.bot.get_channel(cfg["channel"])

        embed = discord.Embed(color=discord.Color.default())
        embed.set_author(name=f"Vanity Roles — {ctx.guild}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.add_field(name="Vanity", value=f"`{cfg['vanity']}`", inline=False)
        embed.add_field(name="Role", value=role.mention if role else "Deleted role", inline=False)
        embed.add_field(name="Log Channel", value=channel.mention if channel else "Deleted channel", inline=False)
        await ctx.send(embed=embed)

    @vanityroles.command(name="check")
    @commands.has_permissions(administrator=True)
    async def vr_check(self, ctx, member: discord.Member = None):
        """Manually check a member (or yourself) for the vanity string."""
        member = member or ctx.author
        data = _load()
        if str(ctx.guild.id) not in data:
            return await ctx.send(
                embed=discord.Embed(color=discord.Color.default(), description="No vanity roles setup found for this server.")
            )
        cfg = data[str(ctx.guild.id)]
        vanity = cfg["vanity"]
        role = ctx.guild.get_role(cfg["role"])
        channel = self.bot.get_channel(cfg["channel"])

        msg = await ctx.send(embed=discord.Embed(color=discord.Color.default(), description=f"⏳ Checking {member.mention}…"))
        await self._check_member(member, vanity, role, channel)
        bio = await self._get_bio(member.id, ctx.guild.id)
        in_status = self._has_vanity_in_status(member, vanity)
        in_bio = vanity.lower() in bio.lower() if bio else False

        embed = discord.Embed(color=discord.Color.default(), title=f"Vanity check — {member}")
        embed.add_field(name="Vanity", value=f"`{vanity}`", inline=False)
        embed.add_field(name="In status", value="✅" if in_status else "❌", inline=True)
        embed.add_field(name="In bio", value="✅" if in_bio else "❌", inline=True)
        embed.add_field(name="Has role", value="✅" if role in member.roles else "❌", inline=True)
        await msg.edit(embed=embed)
