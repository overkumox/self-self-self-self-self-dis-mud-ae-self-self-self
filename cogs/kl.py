# cogs / kl.py
from __future__ import annotations

import asyncio
import itertools
import random
from typing import TYPE_CHECKING

from selfcord import errors
from selfcord.ext import commands

if TYPE_CHECKING:
    from selfcord import Message

    from main import Bot


class Kl(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.is_kl = False
        self.msg = None
        self.kl_channel_id: None

    @commands.is_owner()
    @commands.command()
    async def kl(self, ctx: commands.Context[Bot], is_kl: bool) -> None:
        self.is_kl = is_kl
        if is_kl:
            self.kl_channel_id = ctx.channel.id
            await ctx.send("start kl")
            await self.auto_kl()
        else:
            await ctx.send("pause kl")

    @commands.Cog.listener("on_message")
    async def get_kl_warning(self, message: Message) -> None:
        if self.is_kl and message.channel.id == self.kl_channel_id:
            self.msg = message

    async def auto_kl(self) -> None:
        is_alrp = True
        while self.is_kl:
            if any(x in self.msg.content for x in self.bot.config["kl"]["kl_confirmation"]):
                try:
                    await self.msg.channel.send("y")
                except (errors.InvalidData, errors.NotFound, errors.DiscordServerError):
                    pass
                await asyncio.sleep(random.uniform(14.2, 14.4))

            elif any(x in self.msg.content for x in self.bot.config["kl"]["too_many_pins"]):
                for _ in itertools.repeat(None, 2):
                    try:
                        await self.msg.channel.send("$arlp")
                    except (errors.InvalidData, errors.NotFound, errors.DiscordServerError):
                        pass
                    await asyncio.sleep(random.uniform(2.2, 3.2))
                    if any(x in self.msg.content for x in self.bot.config["kl"]["no_pins"]):
                        break

            elif any(x in self.msg.content for x in self.bot.config["kl"]["no_kakera"]):
                try:
                    await self.msg.channel.send(f"$givescrap {self.bot.user.mention} 1000000000")
                except (errors.InvalidData, errors.NotFound, errors.DiscordServerError):
                    pass
                await asyncio.sleep(random.uniform(0.5, 0.7))

            elif all(x in self.msg.content for x in [self.bot.config["kl"]["givescrap_confirmation"], self.bot.user.name]):
                try:
                    await self.msg.channel.send("y")
                except (errors.InvalidData, errors.NotFound, errors.DiscordServerError):
                    pass
                await asyncio.sleep(random.uniform(0.5, 0.8))

            elif any(x in self.msg.content for x in self.bot.config["kl"]["givescrap_error"]):
                self.is_kl = False

            else:
                await asyncio.sleep(random.uniform(15.8, 15.9))
                try:
                    await self.msg.channel.send("$kl 12000")
                except (errors.InvalidData, errors.NotFound, errors.DiscordServerError):
                    pass
                await asyncio.sleep(random.uniform(14.2, 14.4))
                if (is_alrp:= not is_alrp):
                    try:
                        await self.msg.channel.send("$arlp")
                    except (errors.InvalidData, errors.NotFound, errors.DiscordServerError):
                        pass
                    await asyncio.sleep(random.uniform(0.5, 0.8))
                


async def setup(bot: Bot) -> None:
    await bot.add_cog(Kl(bot))
