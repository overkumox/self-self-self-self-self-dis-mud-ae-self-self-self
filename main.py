import logging

import aiofiles
import asqlite
import toml
from selfcord.ext import commands, tasks

from cogs import EXTENSIONS


config = toml.load('config.toml')
token = config['token']
wish_channel_id = config['wish_channel']
wr_channel_id = config['wr_channel']

# logging settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned, self_bot=True, chunk_guilds_at_startup=False)

        self.wr_channel = None
        self.owner_id = config['owner_id']
        self.config = config
        self.logger = logger
        self.wish_channel = None
        self.mudae_dm = None

    async def setup_hook(self):
        print(f"\033[31mLogged in as {bot.user}\033[39m")
        for extension in EXTENSIONS:
            await bot.load_extension(extension)
        print("Loaded cogs")
        self.get_wish_channel.start()
        self.pool = await asqlite.create_pool('database.db')
        async with self.pool.acquire() as conn, aiofiles.open('schema.sql') as fp:
            await conn.executescript(await fp.read())
            await conn.commit()

    @tasks.loop(count=1)
    async def get_wish_channel(self):
        self.wish_channel = self.get_channel(wish_channel_id)
        self.wr_channel = self.get_channel(wr_channel_id)
        self.mudae_dm = self.get_user(config['mudae_id']).dm_channel.id

    @get_wish_channel.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()


bot = Bot()
bot.run(token)
