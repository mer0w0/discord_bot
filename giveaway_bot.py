import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import re
import os
from dotenv import load_dotenv  # ← 追加

load_dotenv()  # .envファイルを読み込む
TOKEN = os.getenv("DISCORD_TOKEN")  # 環境変数からトークンを取得

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def parse_time(time_str: str) -> int:
    """
    例:
    "3d" -> 259200
    "5h30m" -> 19800
    "1d12h15m" -> 133500
    """
    pattern = r"(\d+)([dhm])"
    matches = re.findall(pattern, time_str)
    if not matches:
        return None

    total_seconds = 0
    for value, unit in matches:
        value = int(value)
        if unit == "d":
            total_seconds += value * 86400
        elif unit == "h":
            total_seconds += value * 3600
        elif unit == "m":
            total_seconds += value * 60
    return total_seconds

@bot.event
async def on_ready():
    await bot.tree.sync()  # スラッシュコマンドをDiscordに同期
    print(f"ログインしました: {bot.user}")

@bot.tree.command(name="giveaway", description="指定時間後に抽選を行います！")
async def giveaway(interaction: discord.Interaction, duration: str, prize: str = "秘密の賞品 🎁"):
    seconds = parse_time(duration)
    if not seconds:
        await interaction.response.send_message("時間指定が正しくないよ！ (例: 3d, 5h30m, 2d4h20m)", ephemeral=True)
        return

    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=f"賞品: **{prize}**\n\n参加するには 🎉 を押してね！\n"
                    f"抽選は {duration} 後に行われます！",
        color=discord.Color.blurple()
    )
    msg = await interaction.channel.send(embed=embed)
    await msg.add_reaction("🎉")

    await interaction.response.send_message("Giveawayを開始しました！ 🎉", ephemeral=True)

    await asyncio.sleep(seconds)

    msg = await interaction.channel.fetch_message(msg.id)
    users = await msg.reactions[0].users().flatten()
    users.remove(bot.user)

    if len(users) == 0:
        await interaction.channel.send("参加者がいませんでした…😢")
        return

    winner = random.choice(users)
    await interaction.channel.send(f"🎉 おめでとう！ {winner.mention} さんが **{prize}** を獲得しました！ 🎉")

bot.run(TOKEN)
