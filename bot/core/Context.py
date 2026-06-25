from __future__ import annotations

from discord.ext import commands
import discord
import functools
from typing import Optional, Any
import asyncio
from utils.components import build_layout

__all__ = ("Context", )


class Context(commands.Context):
    """A custom implementation of commands.Context class."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return "<core.Context>"

    @property
    async def session(self):
        return self.bot.session

    @discord.utils.cached_property
    def replied_reference(self) -> Optional[discord.Message]:
        ref = self.message.reference
        if ref and isinstance(ref.resolved, discord.Message):
            return ref.resolved.to_reference()
        return None

    def with_type(func):

        @functools.wraps(func)
        async def wrapped(self, *args, **kwargs):
            context = args[0] if isinstance(args[0],
                                            commands.Context) else args[1]
            try:
                async with context.typing():
                    await func(*args, **kwargs)
            except discord.Forbidden:
                await func(*args, **kwargs)

        return wrapped

    async def show_help(self, command: str = None) -> Any:
        cmd = self.bot.get_command('help')
        command = command or self.command.qualified_name
        await self.invoke(cmd, command=command)

    @staticmethod
    def _convert_to_v2(kwargs: dict) -> dict:
        embed = kwargs.pop('embed', None)
        embeds = kwargs.pop('embeds', None)
        existing_view = kwargs.pop('view', None)

        if embed is not None or embeds:
            if isinstance(existing_view, discord.ui.LayoutView):
                layout = existing_view
                if embed is not None:
                    from utils.components import embed_to_container
                    layout.add_item(embed_to_container(embed))
                elif embeds:
                    from utils.components import embed_to_container
                    for e in embeds:
                        layout.add_item(embed_to_container(e))
            else:
                layout = build_layout(
                    embed=embed,
                    embeds=embeds,
                    existing_view=existing_view,
                )
            kwargs['view'] = layout
        elif existing_view is not None:
            kwargs['view'] = existing_view

        return kwargs

    async def send(self,
                   content: Optional[str] = None,
                   **kwargs) -> Optional[discord.Message]:
        if not (self.channel.permissions_for(self.me)).send_messages:
            try:
                await self.author.send(
                    "bot dont has perms to send msg in that channel")
            except discord.Forbidden:
                pass
            return
        kwargs = self._convert_to_v2(kwargs)
        return await super().send(content, **kwargs)

    async def reply(self,
                    content: Optional[str] = None,
                    **kwargs) -> Optional[discord.Message]:
        if not (self.channel.permissions_for(self.me)).send_messages:
            try:
                await self.author.send(
                    "bot dont has perms to send msg in that channel")
            except discord.Forbidden:
                pass
            return
        kwargs = self._convert_to_v2(kwargs)
        return await super().reply(content, **kwargs)

    async def release(self, delay: Optional[int] = None) -> None:
        delay = delay or 0
        await asyncio.sleep(delay)
