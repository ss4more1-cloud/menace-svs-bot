import os
import asyncio
from datetime import datetime, timedelta, timezone

import discord

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

# أوقات بداية SvS بتوقيت UTC
# مثال: 18:00,22:00
SVS_TIMES = [
    x.strip() for x in os.getenv("SVS_TIMES", "18:00").split(",")
    if x.strip()
]

intents = discord.Intents.none()
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
                            f"🕐 Start time: <t:{timestamp}:F>\n"
                            f"⏳ <t:{timestamp}:R>\n\n"
                            "☠️ **MENACE — ENTER THE THREAT.**"
                        )

                        await channel.send(message)
                        sent_reminders.add(key)

        await asyncio.sleep(20)


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
