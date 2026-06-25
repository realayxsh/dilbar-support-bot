from __future__ import annotations
import discord
from typing import Optional


def embed_to_container(embed: discord.Embed) -> discord.ui.Container:
    container = discord.ui.Container()

    header_lines = []

    author_name = getattr(embed.author, 'name', None)
    if author_name:
        header_lines.append(f"**{author_name}**")

    title = embed.title
    url = embed.url
    if title:
        if url:
            header_lines.append(f"## [{title}]({url})")
        else:
            header_lines.append(f"## {title}")

    description = embed.description
    if description:
        header_lines.append(description)

    header_text = "\n".join(header_lines) if header_lines else None
    thumbnail_url = getattr(embed.thumbnail, 'url', None)
    if thumbnail_url and thumbnail_url.startswith(('http', 'attachment')):
        pass
    else:
        thumbnail_url = None

    if header_text:
        if thumbnail_url:
            container.add_item(
                discord.ui.Section(
                    discord.ui.TextDisplay(header_text),
                    accessory=discord.ui.Thumbnail(thumbnail_url),
                )
            )
        else:
            container.add_item(discord.ui.TextDisplay(header_text))

    for field in embed.fields:
        container.add_item(discord.ui.Separator())
        parts = []
        fname = getattr(field, 'name', None)
        fvalue = getattr(field, 'value', None)
        if fname and fname != '\u200b':
            parts.append(f"**{fname}**")
        if fvalue:
            parts.append(fvalue)
        if parts:
            container.add_item(discord.ui.TextDisplay("\n".join(parts)))

    image_url = getattr(embed.image, 'url', None)
    if image_url and image_url.startswith('http'):
        mg = discord.ui.MediaGallery()
        mg.add_item(media=image_url)
        container.add_item(mg)

    footer_text = getattr(embed.footer, 'text', None)
    if footer_text:
        container.add_item(discord.ui.Separator())
        container.add_item(discord.ui.TextDisplay(f"-# {footer_text}"))

    if not container.children:
        container.add_item(discord.ui.TextDisplay('\u200b'))

    return container


def _has_interactive_items(view) -> bool:
    """Return True if the view contains buttons, selects, or other interactive items."""
    if view is None:
        return False
    if isinstance(view, discord.ui.LayoutView):
        return False
    interactive = (discord.ui.Button, discord.ui.Select)
    for item in getattr(view, 'children', []):
        if isinstance(item, interactive):
            return True
    return False


def _convert_kwargs(kwargs: dict) -> dict:
    embed = kwargs.pop('embed', None)
    embeds = kwargs.pop('embeds', None)
    existing_view = kwargs.pop('view', None)

    if embed is not None or embeds:
        # If there's an interactive View (buttons/selects), keep the original
        # embed+view so the interactions remain functional.
        if _has_interactive_items(existing_view):
            if embed is not None:
                kwargs['embed'] = embed
            if embeds:
                kwargs['embeds'] = embeds
            kwargs['view'] = existing_view
            return kwargs

        if isinstance(existing_view, discord.ui.LayoutView):
            layout = existing_view
            if embed is not None:
                layout.add_item(embed_to_container(embed))
            elif embeds:
                for e in embeds:
                    layout.add_item(embed_to_container(e))
        else:
            layout = discord.ui.LayoutView()
            if embed is not None:
                layout.add_item(embed_to_container(embed))
            elif embeds:
                for e in embeds:
                    layout.add_item(embed_to_container(e))
        kwargs['view'] = layout
    elif existing_view is not None:
        kwargs['view'] = existing_view

    return kwargs


def build_layout(embed: Optional[discord.Embed] = None,
                 embeds: Optional[list] = None,
                 existing_view=None) -> discord.ui.LayoutView:
    return _convert_kwargs({
        'embed': embed,
        'embeds': embeds,
        'view': existing_view,
    }).get('view', discord.ui.LayoutView())


_patched = False


def patch_discord():
    """Monkey-patch discord send methods to auto-convert embeds to Component V2."""
    global _patched
    if _patched:
        return
    _patched = True

    # --- Messageable.send (covers channel.send, message.channel.send, etc.) ---
    _orig_messageable_send = discord.abc.Messageable.send

    async def _patched_messageable_send(self, content=None, **kwargs):
        if 'embed' in kwargs or 'embeds' in kwargs:
            kwargs = _convert_kwargs(kwargs)
        return await _orig_messageable_send(self, content, **kwargs)

    discord.abc.Messageable.send = _patched_messageable_send

    # --- InteractionResponse.send_message ---
    _orig_send_message = discord.InteractionResponse.send_message

    async def _patched_send_message(self, content=None, **kwargs):
        if 'embed' in kwargs or 'embeds' in kwargs:
            kwargs = _convert_kwargs(kwargs)
        return await _orig_send_message(self, content, **kwargs)

    discord.InteractionResponse.send_message = _patched_send_message

    # --- Webhook.send (interaction followups) ---
    _orig_webhook_send = discord.Webhook.send

    async def _patched_webhook_send(self, content=discord.utils.MISSING, **kwargs):
        if 'embed' in kwargs or 'embeds' in kwargs:
            kwargs = _convert_kwargs(kwargs)
        return await _orig_webhook_send(self, content, **kwargs)

    discord.Webhook.send = _patched_webhook_send

    # --- Message.edit ---
    _orig_message_edit = discord.Message.edit

    async def _patched_message_edit(self, **kwargs):
        if 'embed' in kwargs or 'embeds' in kwargs:
            kwargs = _convert_kwargs(kwargs)
        return await _orig_message_edit(self, **kwargs)

    discord.Message.edit = _patched_message_edit
