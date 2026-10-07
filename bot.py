import os
import asyncio
from datetime import datetime, timedelta, timezone

import discord

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", "0"))

# أوقات بداية SvS بتوقيت UTC
# مثال: 18:00,22:00
SVS_TIMES = [
    x.strip() for x in os.getenv("SVS_TIMES", "18:00").split(",")
    if x.strip()
]

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

sent_reminders = set()


def get_next_svs():
    now = datetime.now(timezone.utc)
    candidates = []

    for time_str in SVS_TIMES:
        try:
            hour, minute = map(int, time_str.split(":"))
            start = now.replace(
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0
            )

            if start <= now:
                start += timedelta(days=1)

            candidates.append(start)

        except ValueError:
            continue

    return min(candidates) if candidates else None


async def svs_scheduler():
    await client.wait_until_ready()

    while not client.is_closed():
        now = datetime.now(timezone.utc)
        svs_start = get_next_svs()

        if svs_start:
            reminder_time = svs_start - timedelta(minutes=5)

            # انتظر حتى موعد التنبيه
            seconds = (reminder_time - now).total_seconds()

            if 0 < seconds <= 3600:
                await asyncio.sleep(seconds)

                key = svs_start.isoformat()

                if key not in sent_reminders:
                    channel = client.get_channel(CHANNEL_ID)

                    if channel:
                        timestamp = int(svs_start.timestamp())

                        message = (
    "🔔 **MENACE | SvS ALERT**\n\n"
    "⚔️ **SvS starts in 5 minutes!**\n\n"
    f"Start time: <t:{timestamp}:d>\n"
    f"⏳ at <t:{timestamp}:t>\n\n"
    "☠️ **MENACE - SvS time.**"
)

                        await channel.send(message)
                        sent_reminders.add(key)

        await asyncio.sleep(20)

@client.event
async def on_member_join(member):
    channel = client.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        message = (
            "☠️ **WELCOME TO MENACE**\n\n"
            f"👋 Welcome, {member.mention}!\n\n"
            "⚔️ Respect your teammates.\n"
            "🤝 Work together.\n"
            "🎯 Follow the battle plan.\n"
            "🔥 Stay active.\n"
            "🏆 Fight for victory.\n\n"
            "📜 Please read the rules before joining the action.\n\n"
            "WE ARE MENACE. ☠️"
        )
        await channel.send(message)
@client.event
async def on_ready():
    print(f"MENACE SVS connected as {client.user}")

    if not hasattr(client, "scheduler_started"):
        client.scheduler_started = True
        asyncio.create_task(svs_scheduler())


if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing")

if CHANNEL_ID == 0:
    raise RuntimeError("CHANNEL_ID is missing")

client.run(TOKEN)
