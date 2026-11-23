# cogs / commands.py
from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING, Any

import toml
import tomli_w
from selfcord import Message
from selfcord.ext import commands

if TYPE_CHECKING:
    from main import Bot
wishlist = []


class Commands(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.is_upgrade = False
        self.upgrade_channel = None
        self.msg: Message

    def update_config(self):
        with open('config.toml', 'wb') as f:
            tomli_w.dump(self.bot.config, f)

        self.bot.config = toml.load('config.toml')

    @commands.Cog.listener('on_message')
    async def get_upgrade_warn(self, message: Message):
        if message.channel != self.upgrade_channel or not self.is_upgrade:
            return
        self.msg = message

    @commands.is_owner()
    @commands.command(aliases=['max_kl'])
    async def max_qq(self, ctx: commands.Context[Bot]):
        self.upgrade_channel = ctx.channel
        self.is_upgrade = True
        await ctx.send('$Quantity 100')
        time_to_sleep = random.uniform(1.5, 2.2)
        await asyncio.sleep(time_to_sleep)
        i = 0
        while i < 1:
            if 'Reach the level **100**' in self.msg.content:
                await ctx.send('y')
                await asyncio.sleep(time_to_sleep)
            elif 'You need' in self.msg.content or 'Prerequisites' in self.msg.content:
                break
            else:
                await ctx.send('$Quality 100')
                await asyncio.sleep(time_to_sleep)
                i += 1
        await asyncio.sleep(time_to_sleep)
        await ctx.send('y')
        self.is_upgrade = False

    @commands.is_owner()
    @commands.command()
    async def max_k(self, ctx: commands.Context[Bot]):
        self.upgrade_channel = ctx.channel
        self.is_upgrade = True
        max_k = self.bot.config['max_k']
        await ctx.send(max_k[0])
        max_k.pop(0)
        time_to_sleep = random.uniform(1.5, 2.2)
        await asyncio.sleep(time_to_sleep)
        i = 0
        while i < len(self.bot.config['max_k']):
            if 'Do you really want to melt those kakera' in self.msg.content:
                await ctx.send('y')
                await asyncio.sleep(time_to_sleep)
            elif 'A kakera command is being processed' in self.msg.content:
                await ctx.send(max_k[i])
                await asyncio.sleep(time_to_sleep)

            elif any(
                x in self.msg.content
                for x in ["You don't have any kakera!", 'Tier locked!', 'A command is already awaiting an answer!']
            ):
                break
            else:
                await ctx.send(max_k[i])
                await asyncio.sleep(time_to_sleep)
                i += 1
        await asyncio.sleep(time_to_sleep)
        await ctx.send('y')
        self.is_upgrade = False

    @commands.is_owner()
    @commands.command()
    async def say(self, ctx: commands.Context[Bot], *, arg: str):
        await asyncio.sleep(0.5)
        await ctx.send(arg)

    @commands.is_owner()
    @commands.command()
    async def dl(self, ctx: commands.Context[Bot], dl_type: str):
        await ctx.send(' '.join([f'${i}' for i in self.bot.config['dl'][dl_type]]))

    @dl.error
    async def dl_handler(self, ctx: commands.Context[Bot], error: Any):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(', '.join([i for i in self.bot.config['dl']]))

    @commands.is_owner()
    @commands.command()
    async def kt(self, ctx: commands.Context[Bot], number_of_towers: int):
        await ctx.send(f'$buildall {number_of_towers}')
        await asyncio.sleep(random.uniform(0.5, 0.8))
        await ctx.send('y')

    @kt.error
    async def kt_handler(self, ctx: commands.Context[Bot], error: Any):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Syntax: **kt <number of towers**')

    @commands.is_owner()
    @commands.command()
    async def roll_type(self, ctx: commands.Context[Bot], roll_type: str):
        self.bot.config['roll_type'] = roll_type
        self.update_config()
        await ctx.send(f'new roll type: **{self.bot.config["roll_type"]}**')

    @roll_type.error
    async def roll_type_handler(self, ctx: commands.Context[Bot], error: Any):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(self.bot.config["roll_type"])

    @commands.is_owner()
    @commands.command()
    async def roll_channel(self, ctx: commands.Context[Bot], channel_id: int):
        self.bot.config['channel_id'] = channel_id
        self.update_config()
        await ctx.send(f'new rolling channel: **{self.bot.config["channel_id"]}**')

    @roll_channel.error
    async def roll_channel_handler(self, ctx: commands.Context[Bot], error: Any):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(self.bot.config["channel_id"])

    @commands.is_owner()
    @commands.command()
    async def wish_channel(self, ctx: commands.Context[Bot], wish_channel_id: int):
        self.bot.config['wish_channel'] = wish_channel_id
        self.update_config()
        self.bot.wish_channel = self.bot.get_channel(wish_channel_id)
        await ctx.send(f'new wish channel: **{self.bot.wish_channel.id}**')

    @wish_channel.error
    async def wish_channel_handler(self, ctx: commands.Context[Bot], error: Any):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(self.bot.wish_channel.id)

    @commands.is_owner()
    @commands.command()
    async def wr_channel(self, ctx: commands.Context[Bot], wr_channel_id: int):
        self.bot.config['wr_channel'] = wr_channel_id
        self.update_config()
        self.bot.wish_channel = self.bot.get_channel(wr_channel_id)
        await ctx.send(f'new wish channel: **{self.bot.wr_channel.id}**')

    @wr_channel.error
    async def wr_channel_handler(self, ctx: commands.Context[Bot], error: Any):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(self.bot.wr_channel.id)

    @commands.is_owner()
    @commands.command()
    async def slash_roll_channel(self, ctx: commands.Context[Bot], slash_roll_channel: int):
        self.bot.config['slash_roll_channel'] = slash_roll_channel
        self.update_config()
        await ctx.send(f'new slash roll channel: **{self.bot.config["slash_roll_channel"]}**')

    @slash_roll_channel.error
    async def slash_roll_channel_handler(self, ctx: commands.Context[Bot], error: Any):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(self.bot.config['slash_roll_channel'])

async def setup(bot: Bot):
    await bot.add_cog(Commands(bot))
