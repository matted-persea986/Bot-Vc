import os
import discord
from discord.ext import commands

# الأفضل تحط التوكن في Secrets / Environment Variables
TOKEN = os.getenv("MTQ4MTg4OTQ3OTAwNTMwNjkzMQ.GbEPRk.EATaww7FkubkEjMfQ6M4pjmUxuaEg5Cy1CT0Uk")

if not TOKEN:
    raise RuntimeError("ما لقيت TOKEN. أضفه في Replit Secrets باسم TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# نخزن آخر روم صوتي لكل سيرفر
last_voice_channels = {}


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.command()
async def join(ctx):
    """يدخل نفس الروم الصوتي اللي فيه صاحب الأمر"""
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ ادخل روم صوتي أولاً.")
        return

    channel = ctx.author.voice.channel
    last_voice_channels[ctx.guild.id] = channel.id

    voice_client = ctx.guild.voice_client

    try:
        if voice_client and voice_client.is_connected():
            if voice_client.channel.id != channel.id:
                await voice_client.move_to(channel)
                await ctx.send(f"✅ انتقلت إلى: **{channel.name}**")
            else:
                await ctx.send(f"✅ أنا بالفعل داخل: **{channel.name}**")
        else:
            await channel.connect(self_deaf=True)
            await ctx.send(f"✅ دخلت إلى: **{channel.name}**")
    except Exception as e:
        await ctx.send(f"❌ صار خطأ: `{e}`")


@bot.command()
async def stay(ctx):
    """يحفظ الروم الحالي كغرفة ثابتة للبوت"""
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ ادخل روم صوتي أولاً.")
        return

    channel = ctx.author.voice.channel
    last_voice_channels[ctx.guild.id] = channel.id

    voice_client = ctx.guild.voice_client
    try:
        if voice_client and voice_client.is_connected():
            await voice_client.move_to(channel)
        else:
            await channel.connect(self_deaf=True)

        await ctx.send(f"✅ تم تثبيت البوت في **{channel.name}**")
    except Exception as e:
        await ctx.send(f"❌ صار خطأ: `{e}`")


@bot.command()
async def leave(ctx):
    """يخرج البوت من الروم الصوتي"""
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect(force=True)
        await ctx.send("👋 خرجت من الروم الصوتي.")
    else:
        await ctx.send("❌ أنا لست داخل أي روم صوتي.")


@bot.event
async def on_voice_state_update(member, before, after):
    # نهتم فقط بحالة البوت نفسه
    if not bot.user or member.id != bot.user.id:
        return

    guild = member.guild
    saved_channel_id = last_voice_channels.get(guild.id)

    # إذا البوت انقطع من الروم بالكامل
    disconnected = before.channel is not None and after.channel is None
    if disconnected and saved_channel_id:
        channel = guild.get_channel(saved_channel_id)
        if channel is None:
            return

        try:
            # إذا كان ما فيه اتصال حالي، يرجع يدخل
            if guild.voice_client is None or not guild.voice_client.is_connected():
                await channel.connect(self_deaf=True)
                print(f"↩️ رجعت إلى {channel.name} في {guild.name}")
        except Exception as e:
            print(f"فشل إعادة الاتصال: {e}")


bot.run(TOKEN)