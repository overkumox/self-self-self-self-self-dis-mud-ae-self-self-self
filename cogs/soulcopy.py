# cogs / sl copy.py
from __future__ import annotations

import logging
import asyncio
from typing import TYPE_CHECKING, Sized

from more_itertools import constrained_batches
from selfcord.ext import commands

if TYPE_CHECKING:
    from selfcord import Message

    from main import Bot


# +1 for '$'
def get_len(item: Sized) -> int:
    return len(item) + 1


class SlCopy(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.get_sl_list = False
        self.char_count = 0
        self.sl_list: list[str] = []
        self.chars: list[str] = []
        self.soulcopy_channel = None

    @commands.is_owner()
    @commands.command()
    async def get_sl(self, ctx: commands.Context[Bot], flags: str, count: int) -> None:
        self.char_count = count
        self.soulcopy_channel = ctx.channel
        self.sl_list = []
        self.get_sl_list = True
        await asyncio.sleep(2)
        await ctx.send(f"$sl{flags}ud-s")

    @commands.is_owner()
    @commands.command()
    async def resume_soulcopy(self, ctx: commands.Context[Bot]) -> None:
        if self.chars:
            await asyncio.sleep(2)
            characters = self.chars.pop(0)
            await ctx.send(f"$soulcopy {'$'.join(characters)}")

    @commands.Cog.listener("on_message")
    async def get_sl_chars(self, message: Message) -> None:
        if not self.chars or not self.soulcopy_channel or message.channel != self.soulcopy_channel or message.content not in ["Transferência bem sucedida!", "¡Transferencia exitosa!", "Successful copy!"]:
            return
        await asyncio.sleep(2)
        characters = self.chars.pop(0)
        await self.soulcopy_channel.send(f"$soulcopy {'$'.join(characters)}")

    @commands.Cog.listener("on_message")
    async def get_chars(self, message: Message) -> None:
        if message.channel.id != self.bot.mudae_dm:
            return

        if self.get_sl_list:
            content = message.content.replace("\\", "").split("\n")
            self.sl_list.extend([i.strip() for i in content])
            print(len(self.sl_list))
            if len(self.sl_list) >= self.char_count + 5:
                self.get_sl_list = False
                del self.sl_list[0:5]
                msg = f"{len(self.sl_list[:self.char_count])} characters added to sl list"
                logging.info(msg)
                await self.soulcopy_channel.send(msg)
                self.chars: list[tuple[str]] = list(
                    constrained_batches(self.sl_list[: self.char_count], 1988, get_len=get_len)
                )
                if self.chars:
                    characters = self.chars.pop(0)
                    await self.soulcopy_channel.send(f"$soulcopy {'$'.join(characters)}")


async def setup(bot: Bot) -> None:
    await bot.add_cog(SlCopy(bot))
