# cogs / sl farm.py
from __future__ import annotations

import asyncio
import random
import re
import traceback
from datetime import datetime, timedelta, UTC
from typing import TYPE_CHECKING

from selfcord import ButtonStyle, Message, SlashCommand, errors, utils
from selfcord.ext import commands

if TYPE_CHECKING:
    from selfcord.abc import Messageable

    from main import Bot


class AutoRoll(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.msg: Message = None
        self.embed = None
        self.rolling = False
        self.roll_channel = None
        self.cannot_react_until = datetime.now(UTC)

    @commands.is_owner()
    @commands.command()
    async def start_rolling(self, ctx: commands.Context[Bot]):
        await ctx.send("started rolling")
        slash_roll_channel = self.bot.get_channel(self.bot.config["slash_roll_channel"])
        roll_type = self.bot.config["roll_type"]
        slash_roll = utils.get(
            await slash_roll_channel.application_commands(),
            name=roll_type,
            application_id=432610292342587392,
        )
        roll_cmd = self.bot.config["prefix"] + roll_type
        self.rolling = True
        await ctx.send(roll_cmd)
        await asyncio.sleep(2.6)
        await self.waifu_roll(ctx.channel, roll_cmd, slash_roll)

    @commands.is_owner()
    @commands.command()
    async def stop_rolling(self, ctx: commands.Context[Bot]):
        self.rolling = False
        await ctx.send("stopped rolling")

    @commands.Cog.listener("on_message")
    async def dk(self, message: Message):
        if message.author == self.bot.user and message.content == "$dk":
            self.cannot_react_until = datetime.now(UTC)

    @commands.Cog.listener("on_message")
    async def kakera_react_warning(self, message: Message):
        if (
            not self.rolling
            or message.channel.id not in (self.bot.config["channel_id"], self.bot.config["slash_roll_channel"])
            or message.embeds
            or not message.content.startswith(f"**{self.bot.user}**, You can't react")
        ):
            return
        hours, minutes = re.search(r"\*\*(?:(?P<hours>\d)h )?(?P<minutes>\d{1,2})\*\*", message.content).groups()
        self.cannot_react_until = datetime.now(UTC) + timedelta(minutes=int(minutes), hours=int(hours or 0))

    @commands.Cog.listener("on_message")
    async def kakera_react(self, message: Message):
        if (
            not self.rolling
            or message.channel.id not in (self.bot.config["channel_id"], self.bot.config["slash_roll_channel"])
            or not message.embeds
            or not message.components
        ):
            return

        KAKERA = ["kakeraW", "kakeraC2"] # "kakeraR", "kakeraL", "kakeraD2"
        for button in (button for row in message.components for button in row.children):
            if (
                (emoji := button.emoji.name) == "kakeraP"  
                or ((embed := message.embeds[0]) and embed.footer and f"{self.bot.user}" in embed.footer.text)
                and (
                    emoji.startswith("sp") 
                    or button.style == ButtonStyle.success
                    or (
                        datetime.now(UTC) > self.cannot_react_until 
                        and "<:sp:1437140700604137554>" in (description := embed.description) 
                        and (emoji in KAKERA or "💎/2" in description)
                        )
                    )
                ):
                await asyncio.sleep(random.uniform(1.5, 1.8))
                try:
                    await button.click()
                except (errors.InvalidData, errors.NotFound, errors.DiscordServerError):
                    traceback.print_exc()

    @commands.Cog.listener("on_message")
    async def get_roll_warn(self, message: Message):
        if (
            message.channel.id not in [self.bot.config["channel_id"], self.bot.config["slash_roll_channel"]]
            or not self.rolling
        ):
            return
        if message.embeds:
            self.embed = message.embeds[0]
        else:
            self.msg = message

    async def waifu_roll(self, channel: Messageable, roll_cmd: str, slash_roll: SlashCommand, is_slash_roll: bool = False):
        rolls_left = -1

        while self.rolling:
            em = self.embed

            if em and em.footer and em.footer.text and "2 ROLLS" in em.footer.text:
                rolls_left = 2

            if rolls_left == 0 or any(x in self.msg.content for x in self.bot.config["sl"]["no_rolls_left"] if self.msg):
                # Ran out of rolls
                
                try:
                    await channel.send("$us 20")
                except (errors.InvalidData, errors.NotFound, errors.DiscordServerError):
                    traceback.print_exc()
                rolls_left = -1
                await asyncio.sleep(1)
            else:
                rolls_left -= 1
                if is_slash_roll:
                    try:
                        await slash_roll()
                    except (errors.InvalidData, errors.NotFound, errors.DiscordServerError):
                        traceback.print_exc()
                    is_slash_roll = False
                    # print(f"slash: {datetime.now(UTC)}")
                    await asyncio.sleep(0.9)
                else:
                    try:
                        await channel.send(roll_cmd)
                    except (errors.InvalidData, errors.NotFound, errors.DiscordServerError):
                        traceback.print_exc()
                    is_slash_roll = True
                    # print(f"prefix: {datetime.now(UTC)}")
                    # time_to_sleep = random.uniform(1.25, 1.3)
                    # time_to_sleep = random.uniform(2.6, 3.5)
                    # await asyncio.sleep(1.25)
                    await asyncio.sleep(0.9)


async def setup(bot: Bot):
    await bot.add_cog(AutoRoll(bot))
