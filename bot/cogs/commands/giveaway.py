import discord
from discord.ext import commands, tasks
import json, random, time, os
from core.Cog import Cog
from core.Ventura import Ventura
from utils.Tools import blacklist_check, ignore_check

GIVEAWAYS_FILE = "giveaways.json"


def _load() -> dict:
    if not os.path.exists(GIVEAWAYS_FILE):
        return {}
    with open(GIVEAWAYS_FILE, "r") as f:
        return json.load(f)


def _save(data: dict):
    with open(GIVEAWAYS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def _parse_duration(s: str) -> int:
    """Convert duration string (10s, 5m, 2h, 1d) to seconds."""
    s = s.strip().lower()
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if s and s[-1] in units:
        return int(s[:-1]) * units[s[-1]]
    return int(s)


class Giveaway(Cog, name="Giveaway"):
    """Run and manage giveaways with custom emoji reactions."""

    def __init__(self, client: Ventura):
        self.bot = client
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        data = _load()
        now = int(time.time())
        changed = False
        for key, gw in list(data.items()):
            if gw.get("ended"):
                continue
            if now >= gw["ends_at"]:
                await self._end_giveaway(key, gw, data)
                changed = True
        if changed:
            _save(data)

    @check_giveaways.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    async def _end_giveaway(self, key: str, gw: dict, data: dict):
        try:
            channel = self.bot.get_channel(gw["channel_id"])
            if channel is None:
                return
            message = await channel.fetch_message(gw["message_id"])
            emoji = gw.get("emoji", "🎉")

            reaction = None
            for r in message.reactions:
                if str(r.emoji) == emoji:
                    reaction = r
                    break

            users = []
            if reaction:
                users = [u async for u in reaction.users() if not u.bot]
            winners = random.sample(users, min(gw["winners"], len(users))) if users else []

            embed = discord.Embed(color=discord.Color.default())
            embed.title = "🎉 Giveaway Ended"
            if winners:
                embed.description = (
                    f"**Prize:** {gw['prize']}\n"
                    f"**Winner(s):** {', '.join(w.mention for w in winners)}\n"
                    f"**Hosted by:** <@{gw['host_id']}>"
                )
                await channel.send(
                    f"🎉 Congratulations {' '.join(w.mention for w in winners)}! "
                    f"You won **{gw['prize']}**!"
                )
            else:
                embed.description = (
                    f"**Prize:** {gw['prize']}\n"
                    "No valid entries — no winner selected.\n"
                    f"**Hosted by:** <@{gw['host_id']}>"
                )
            embed.set_footer(text="Dilbar Support Giveaways")

            await message.edit(embed=embed)
            data[key]["ended"] = True
            data[key]["winner_ids"] = [w.id for w in winners]
        except Exception as e:
            print(f"[Giveaway] Error ending {key}: {e}")

    @commands.hybrid_command(
        name="gcreate",
        aliases=["gstart"],
        help=(
            "Start a giveaway.\n"
            "Duration: 10s, 5m, 2h, 1d\n"
            "Winners: number of winners to pick\n"
            "Emoji: custom reaction emoji (default 🎉) — owner can set any emoji\n"
            "Prize: what you are giving away\n\n"
            "Example: `-gcreate #events 1h 2 🎊 Discord Nitro`"
        ),
        usage="gcreate <#channel> <duration> <winners> [emoji] <prize>",
    )
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def gcreate(
        self,
        ctx,
        channel: discord.TextChannel,
        duration: str,
        winners: int,
        emoji: str = "🎉",
        *,
        prize: str,
    ):
        try:
            seconds = _parse_duration(duration)
        except (ValueError, IndexError):
            return await ctx.reply(
                embed=discord.Embed(
                    description="<:dot_white:1103476115709890682> Invalid duration. Use `10s`, `5m`, `2h`, or `1d`.",
                    color=discord.Color.default(),
                ),
                mention_author=False,
            )

        if winners < 1:
            return await ctx.reply(
                embed=discord.Embed(
                    description="<:dot_white:1103476115709890682> Winners must be at least 1.",
                    color=discord.Color.default(),
                ),
                mention_author=False,
            )

        ends_at = int(time.time()) + seconds
        embed = discord.Embed(
            title=f"🎉 Giveaway — {prize}",
            description=(
                f"React with {emoji} to enter!\n\n"
                f"**Winners:** {winners}\n"
                f"**Ends:** <t:{ends_at}:R> (<t:{ends_at}:f>)\n"
                f"**Hosted by:** {ctx.author.mention}"
            ),
            color=discord.Color.default(),
        )
        embed.set_footer(text="Dilbar Support Giveaways")

        msg = await channel.send(embed=embed)
        try:
            await msg.add_reaction(emoji)
        except discord.HTTPException:
            await msg.add_reaction("🎉")
            emoji = "🎉"

        data = _load()
        key = f"{channel.id}-{msg.id}"
        data[key] = {
            "channel_id": channel.id,
            "message_id": msg.id,
            "guild_id": ctx.guild.id,
            "host_id": ctx.author.id,
            "prize": prize,
            "winners": winners,
            "emoji": emoji,
            "ends_at": ends_at,
            "ended": False,
            "winner_ids": [],
        }
        _save(data)

        await ctx.reply(
            embed=discord.Embed(
                description=f"<a:green_tick:1103363669263405157> | Giveaway started in {channel.mention}!",
                color=discord.Color.default(),
            ),
            mention_author=False,
        )

    @commands.hybrid_command(
        name="gend",
        help="End a giveaway early and pick a winner immediately.",
        usage="gend <#channel> <message_id>",
    )
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def gend(self, ctx, channel: discord.TextChannel, message_id: str):
        data = _load()
        key = f"{channel.id}-{message_id}"
        if key not in data:
            return await ctx.reply(
                embed=discord.Embed(
                    description="<:dot_white:1103476115709890682> Giveaway not found. Check the channel and message ID.",
                    color=discord.Color.default(),
                ),
                mention_author=False,
            )
        if data[key].get("ended"):
            return await ctx.reply(
                embed=discord.Embed(
                    description="<:dot_white:1103476115709890682> That giveaway has already ended.",
                    color=discord.Color.default(),
                ),
                mention_author=False,
            )
        data[key]["ends_at"] = int(time.time()) - 1
        await self._end_giveaway(key, data[key], data)
        _save(data)
        await ctx.reply(
            embed=discord.Embed(
                description="<a:green_tick:1103363669263405157> | Giveaway ended early.",
                color=discord.Color.default(),
            ),
            mention_author=False,
        )

    @commands.hybrid_command(
        name="greroll",
        help="Reroll a giveaway to pick a new random winner.",
        usage="greroll <#channel> <message_id>",
    )
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def greroll(self, ctx, channel: discord.TextChannel, message_id: str):
        data = _load()
        key = f"{channel.id}-{message_id}"
        if key not in data:
            return await ctx.reply(
                embed=discord.Embed(
                    description="<:dot_white:1103476115709890682> Giveaway not found.",
                    color=discord.Color.default(),
                ),
                mention_author=False,
            )
        gw = data[key]
        try:
            msg = await channel.fetch_message(int(message_id))
        except discord.NotFound:
            return await ctx.reply(
                embed=discord.Embed(
                    description="<:dot_white:1103476115709890682> Could not find that message.",
                    color=discord.Color.default(),
                ),
                mention_author=False,
            )

        emoji = gw.get("emoji", "🎉")
        reaction = None
        for r in msg.reactions:
            if str(r.emoji) == emoji:
                reaction = r
                break

        users = []
        if reaction:
            users = [u async for u in reaction.users() if not u.bot]
        winners = random.sample(users, min(gw["winners"], len(users))) if users else []

        if winners:
            await ctx.reply(
                embed=discord.Embed(
                    description=f"🎉 New winner(s): {', '.join(w.mention for w in winners)}! Congratulations!",
                    color=discord.Color.default(),
                ),
                mention_author=False,
            )
        else:
            await ctx.reply(
                embed=discord.Embed(
                    description="<:dot_white:1103476115709890682> No valid entries to reroll.",
                    color=discord.Color.default(),
                ),
                mention_author=False,
            )

    @commands.hybrid_command(
        name="glist",
        help="List all active giveaways in this server.",
        usage="glist",
    )
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def glist(self, ctx):
        data = _load()
        active = [
            gw for gw in data.values()
            if gw.get("guild_id") == ctx.guild.id and not gw.get("ended")
        ]
        if not active:
            return await ctx.reply(
                embed=discord.Embed(
                    description="<:dot_white:1103476115709890682> No active giveaways in this server.",
                    color=discord.Color.default(),
                ),
                mention_author=False,
            )
        lines = []
        for gw in active:
            ch = f"<#{gw['channel_id']}>"
            lines.append(
                f"• **{gw['prize']}** — {ch} — {gw['winners']} winner(s) — ends <t:{gw['ends_at']}:R>"
            )
        embed = discord.Embed(
            title=f"Active Giveaways ({len(active)})",
            description="\n".join(lines),
            color=discord.Color.default(),
        )
        embed.set_footer(text="Dilbar Support Giveaways")
        await ctx.reply(embed=embed, mention_author=False)


async def setup(client: Ventura):
    await client.add_cog(Giveaway(client))
