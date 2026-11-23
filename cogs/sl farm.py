# cogs / sl farm.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any
import re
import random
import asyncio
from more_itertools import constrained_batches
from selfcord import errors, Message, utils
from selfcord.ext import commands, tasks
from selfcord.abc import Messageable

if TYPE_CHECKING:
    from main import Bot

# +1 for '$'
def get_len(item: Sized) -> int:
    return len(item) + 1

class SlFarm(commands.Cog):
    def __init__(self, bot: Bot):
        self.get_wishlist = False
        self.bot = bot
        self.rolling: bool = False
        self.make_database: bool = False
        self.make_wishlist: bool = False
        self.char_count: int = 0
        self.char_name: str = ""
        self.chars: list[str] = []
        self.embed = None
        self.msg = None
        self.wishlist: list[str] = []
        self.char_list: list[str] = []
        self.wishlist_count: int = 0

    @commands.is_owner()
    @commands.command()
    async def start_sl(self, ctx: commands.Context[Bot]):
        async with ctx.bot.pool.acquire() as conn:
            cursor = await conn.execute("SELECT name FROM characters WHERE owner_id = ?", (self.bot.user.id))
            await conn.commit()
        self.chars = [row['name'] for row in await cursor.fetchall()]
        slash_roll_channel = self.bot.get_channel(self.bot.config['slash_roll_channel'])
        roll_type = self.bot.config['roll_type']
        # slash_roll = [command async for command in slash_roll_channel.slash_commands(query=roll_type)]  # type: ignore
        slash_roll = utils.get(
            await slash_roll_channel.application_commands(),
            name=roll_type,
            application_id=432610292342587392,
        )
        roll_cmd = self.bot.config['prefix'] + roll_type
        self.rolling = True
        await asyncio.sleep(random.uniform(1.6, 1.8))
        await ctx.send(roll_cmd)
        if not self.get_new_char_to_wish.is_running():
            self.get_new_char_to_wish.start()
        await self.waifu_roll(ctx.channel, roll_cmd, slash_roll)

    @commands.is_owner()
    @commands.command()
    async def stop_sl(self, ctx: commands.Context[Bot]):
        self.rolling = False
        if self.get_new_char_to_wish.is_running():
            self.get_new_char_to_wish.cancel()
        await ctx.send('stopped rolling')

    @commands.is_owner()
    @commands.command()
    async def cache_wl(self, ctx: commands.Context[Bot]):
        self.get_wishlist = True
        self.wishlist = []
        await ctx.send('$wlsv')

    @commands.is_owner()
    @commands.command()
    async def make_wl(self, ctx: commands.Context[Bot], flags: str, count: int):
        self.char_count = count
        self.char_list = []
        self.make_wishlist = True
        await ctx.send(f'${flags}y!-vs')

    @make_wl.error
    async def make_wl_handler(self, ctx: commands.Context[Bot], error: Any):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Syntax: **!make_wl <flags> <number of characters>**')

    @commands.is_owner()
    @commands.command()
    async def database(self, ctx: commands.Context[Bot], flags: str, count: int):
        self.char_count = count
        self.char_list = []
        async with self.bot.pool.acquire() as conn:
            await conn.execute("DELETE FROM characters WHERE owner_id = ?", (self.bot.user.id))
            await conn.commit()
        self.make_database = True
        await ctx.send(f'${flags}y!-vs')

    @database.error
    async def database_handler(self, ctx: commands.Context[Bot], error: Any):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Syntax: **!database <flags> <number of characters>**')

    @commands.Cog.listener('on_message')
    async def get_sl_chars(self, message: Message):
        if (
            message.channel.id not in [self.bot.config['channel_id'], self.bot.config['slash_roll_channel']]
            or not self.rolling
        ):
            return
        self.msg = message
        if message.embeds:
            self.embed = message.embeds[0]
            description = self.embed.description
            char_name = self.embed.author.name

            # if $wr command don't work add "or ':chaoskey:' in description and 'Your Soulmate in' not in description".
            if (
                description
                and any(x in description for x in self.bot.config['sl']['Soulmate_message'])
                and 'Your Soulmate in' not in description
            ):
                self.bot.logger.info(f'{char_name} SOULMATE!')
                async with self.bot.pool.acquire() as conn:
                    await conn.execute(
                        "DELETE FROM characters WHERE name = ? AND  owner_id = ?", (char_name, self.bot.user.id)
                    )
                    await conn.commit()
                    if char_name in self.chars:
                        self.chars.remove(char_name)
                    if char_name in self.wishlist:
                        self.wishlist.remove(char_name)
                    await self.bot.wr_channel.send(f'$wr {char_name}')

    @commands.Cog.listener('on_message')
    async def get_wishlist_chars(self, message: Message):
        if not self.get_wishlist or message.channel.id != self.bot.mudae_dm:
            return
        content = message.content.split('\n')
        self.wishlist.extend([i.strip() for i in content])
        self.wishlist_count =  int(count[1]) if (count := re.search(r'(\d+)/\d+', message.content.replace(",", ""))) else self.wishlist_count
        if len(self.wishlist) == self.wishlist_count + 2:
            self.get_wishlist = False
            del self.wishlist[0:2]
            msg = f'{self.wishlist_count} wishlist characters cached'
            self.bot.logger.info(msg)
            await self.bot.wish_channel.send(msg)
            self.wishlist_count = 0

    @commands.Cog.listener('on_message')
    async def get_make_wishlist_chars(self, message: Message):
        if not self.make_wishlist or message.channel.id != self.bot.mudae_dm:
            return
        content = message.content.split('\n')
        self.char_list.extend([i.strip() for i in content])
        if len(self.char_list) >= self.char_count + 2:
            self.make_wishlist = False
            del self.char_list[0:2]
            msg = f'{len(self.char_list[:self.char_count])} characters will be added to the wish list'
            self.bot.logger.info(msg)
            await self.bot.wish_channel.send(msg)
            for i in list(constrained_batches(self.char_list[: self.char_count], 1960, get_len=get_len)):
                await self.bot.wish_channel.send(f"$wish {'$'.join(i)}")
                time_to_sleep = random.uniform(3.2, 4.5)
                await asyncio.sleep(time_to_sleep)

    @commands.Cog.listener('on_message')
    async def ge_make_database_chars(self, message: Message):
        if not self.make_database or message.channel.id != self.bot.mudae_dm:
            return
        content = message.content.split('\n')
        self.char_list.extend([i.strip() for i in content])
        if len(self.char_list) >= self.char_count + 2:
            self.make_database = False
            del self.char_list[0:2]
            characters = [(character, self.bot.user.id) for character in self.char_list[: self.char_count]]
            async with self.bot.pool.acquire() as conn:
                await conn.executemany("INSERT INTO characters(name, owner_id) VALUES (?, ?)", characters)
                await conn.commit()
            msg = f'{len(self.char_list[:self.char_count])} characters added to the database'
            self.bot.logger.info(msg)
            await self.bot.wish_channel.send(msg)

    async def waifu_roll(
        self, channel: Messageable, roll_cmd: str, slash_roll: SlashCommand, is_slash_roll: bool = False
    ):
        rolls_left = -1

        while self.rolling:
            em = self.embed

            if em and em.footer and em.footer.text and "2 ROLLS" in em.footer.text:
                rolls_left = 2

            if rolls_left == 0 or any(x in self.msg.content for x in self.bot.config['sl']['no_rolls_left']):
                # Ran out of rolls
                await channel.send('$us 20')
                rolls_left = -1
                await asyncio.sleep(1)
            else:
                rolls_left -= 1
                if is_slash_roll:
                    try:
                        await slash_roll()
                        is_slash_roll = False
                    except errors.InvalidData:
                        pass
                else:
                    await channel.send(roll_cmd)
                    is_slash_roll = True
                time_to_sleep = random.uniform(1.6, 1.8)
                await asyncio.sleep(time_to_sleep)

    @tasks.loop(minutes=15)  # task runs every 15 minutes
    async def get_new_char_to_wish(self):
        if not self.rolling:
            return
        wish_channel = self.bot.get_channel(self.bot.config['wish_channel'])
        await wish_channel.send('$wl')

        def check(m: Message) -> bool:
            return bool(m.embeds) and self.bot.user.name in m.embeds[0].author.name and m.channel.id == wish_channel.id

        embed = (await self.bot.wait_for('message', check=check)).embeds[0].author.name.replace(",", "")
        num_of_char_to_wish = int(re.findall(r'\d+/(\d+)', embed)[0]) - (wished := int(re.findall(r'(\d+)/\d+', embed)[0]))
        if num_of_char_to_wish == 0 or wished >= 1000:
            return
    
        async with self.bot.pool.acquire() as conn:
            holder = ', '.join(['?' for _ in self.wishlist])
            cursor = await conn.execute(
                f"SELECT name FROM characters WHERE name NOT IN ({holder}) AND owner_id = ?",
                (*self.wishlist, self.bot.user.id),
            )
            await conn.commit()
        chars_to_wish = [row['name'] for row in await cursor.fetchmany(num_of_char_to_wish)]
        if chars_to_wish:
            for i in list(constrained_batches(chars_to_wish, 1960, get_len=get_len)):
                await wish_channel.send(f"$wish {'$'.join(i)}")
                time_to_sleep = random.uniform(2.2, 3.2)
                await asyncio.sleep(time_to_sleep)
            self.chars.extend(chars_to_wish)
            self.wishlist.extend(chars_to_wish)
        else:
            self.bot.logger.error('\033[1mError! run out of characters')
            await wish_channel.send('**Error!** run out of characters')
            self.get_new_char_to_wish.cancel()

    @get_new_char_to_wish.before_loop
    async def before_get_new_char_to_wish(self):
        await self.bot.wait_until_ready()  # wait until the bot logs in


async def setup(bot: Bot):
    await bot.add_cog(SlFarm(bot))
