import os
from dotenv import load_dotenv
import discord
from discord import Intents, Interaction
from discord.ext import commands
import asyncio
import pytubefix
import ffmpeg
    
# Discord bot initialization
# ---------------------------------------------------------------------------------
# Load variables from the .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_PREFIX = os.getenv("PREFIX")
FILE_PATH = os.getenv("FILE_PATH")
# Don't need this just yet but will make adding special intents later easier
intents = Intents.default()
intents.message_content = False
intents.members = False

# Extend discord bot class
class Bot(commands.Bot):
    """
    Custom bot for adding custom music discs to minecraft.
    """
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=DISCORD_PREFIX,
            intents=intents,
            case_insensitive=True,
            activity=discord.CustomActivity(name="Creating Custom Discs"),
            status=discord.Status.online
            )
        print(f"Created bot with prefix {DISCORD_PREFIX}.")

# Create discord bot
bot = Bot()

async def main():

    # Bot startup
    # ---------------------------------------------------------------------------------

    ytdl_format_options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
        }

    @bot.event
    async def on_ready():
        print(f'Logged into Discord as {bot.user}.')

    # Sync Commands
    # ---------------------------------------------------------------------------------

    @bot.command(name="localsync", description="Sync all commands in the current guild.")
    async def localsync(ctx: commands.Context):
        bot.tree.copy_global_to(guild=ctx.guild)
        await bot.tree.sync(guild=ctx.guild)
        await ctx.reply("Commands synced locally!")

    @bot.tree.command(name="upload", description="Upload audio from a Youtube video to the server.")
    async def upload(interaction: discord.Interaction, url: str, disc_name: str = None):
        await interaction.response.defer()
        print(f"Downloading audio from {url}")
        id = url.split("v=")[1]
        yt = pytubefix.YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        stream.download(output_path=FILE_PATH, filename=id)
        ffmpeg.input(f"{FILE_PATH}/{id}").output(f"{FILE_PATH}/{id}.mp3").run()
        os.remove(f"{FILE_PATH}/{id}")

        embed = discord.Embed(
            color=discord.Color.green()
        )
        embed.set_author(name="Successfully uploaded audio!")
        embed.add_field(name="Use this command to add the audio to the server:",
                value="```/audioplayer serverfile " + id + ".mp3```",
                inline=False)
        embed.add_field(name="And then while holding the disc:",
                value="```/audioplayer apply " + id + ".mp3" + (" " + '"' + disc_name + '"' if disc_name else "") + "```",
                inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)

    print("Starting Custom Music Discs...")
    async with bot:
        await bot.start(DISCORD_TOKEN)

asyncio.run(main())