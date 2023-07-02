# discord.gg/psxslot
# discord.gg/psxslot

#packski on discord made this

import discord
from discord.ext import commands
import asyncio
import aiosqlite
import random
from enum import Enum
import time
import os, threading, requests, json, multiprocessing

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

Username = "packownsyouniggaaaaaaa" # Username of roblox account
workspacefolder = "C:/Users/packisdaddy/AppData/Local/Packages/ROBLOXCORPORATION.ROBLOX_55nm5eh3cm0pr/AC/workspace" # The Workspace Folder Of Your Executor
withwebhook = "webhook here"
depowebhook = "webhook here"

codes = []

workspacefolder += "/gamble" # Ignore
os.makedirs(workspacefolder, exist_ok=True)
temp = open(f"{workspacefolder}/withdraws.txt", "w")
temp.close()
temp = open(f"{workspacefolder}/deposits.txt", "w")
temp.close()


@bot.event
async def on_ready():
    print("Online")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)
    bot.db = await aiosqlite.connect("bank.db")
    async with bot.db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS wallet (balance INTEGER, user INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS deposited_amounts (user_id INTEGER, amount INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS withdraw_amounts (user_id INTEGER, amount INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS wagered (user_id INTEGER, amount INTEGER)")
        await cursor.execute("CREATE TABLE IF NOT EXISTS affiliates (affiliate INTEGER, user_id INTEGER)")
    await bot.db.commit()
    print("db ready")


async def get_affiliate(user_id):
    async with bot.db.cursor() as cursor:
        await cursor.execute('SELECT affiliate FROM affiliates WHERE user_id = ?', (user_id,))
        data = await cursor.fetchone()
        

        if data:
            user = data[0]
            user_2 = bot.get_user(user)
            user = f"{user_2.mention}"
        else:
            user = "Nobody"

        await bot.db.commit()
        return user

async def update_wagered_amount(user_id, amount):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT amount FROM wagered WHERE user_id = ?", (user_id,))
        data = await cursor.fetchone()
        if data:
            current_amount = data[0]
            new_amount = current_amount + amount
            await cursor.execute('UPDATE wagered SET amount = ? WHERE user_id = ?', (new_amount, user_id,))
        else:
            await cursor.execute("INSERT INTO wagered(user_id, amount) VALUES(?, ?)", (user_id, amount,))
        await bot.db.commit()

async def get_wagered_amount(user_id):
    async with bot.db.cursor() as cursor:
        await cursor.execute('SELECT amount FROM wagered WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        if row:
            return row[0]
        return 0
    
async def update_withdrawed_amount(user_id, amount):
    async with bot.db.cursor() as cursor:
        await cursor.execute('SELECT amount FROM withdraw_amounts WHERE user_id = ?', (user_id,))
        data = await cursor.fetchone()
        if data:
            await cursor.execute('UPDATE withdraw_amounts SET amount = ? WHERE user_id = ?', (amount, user_id))
        else:
            await cursor.execute('INSERT INTO withdraw_amounts(user_id, amount) VALUES (?, ?)', (user_id, amount,))
        await bot.db.commit()

async def get_withdrawed_amount(user_id):
    async with bot.db.cursor() as cursor:
        await cursor.execute('SELECT amount FROM withdraw_amounts WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        if row:
            return row[0]
        return 0
    
async def update_deposited_amount(user_id, amount):
    async with bot.db.cursor() as cursor:
        await cursor.execute('SELECT amount FROM deposited_amounts WHERE user_id = ?', (user_id,))
        data = await cursor.fetchone()
        if data:
            await cursor.execute('UPDATE deposited_amounts SET amount = ? WHERE user_id = ?', (amount, user_id))
        else:
            await cursor.execute('INSERT INTO deposited_amounts(user_id, amount) VALUES (?, ?)', (user_id, amount,))
        await bot.db.commit()



async def get_deposited_amount(user_id):
    async with bot.db.cursor() as cursor:
        await cursor.execute('SELECT amount FROM deposited_amounts WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        if row:
            return row[0]
        return 0

async def test_code(code, gems):
    count = 0
    for item in codes:
        if item[1] == code:
            user_id = item[0]
            await update_wallet(user_id, gems)
            await update_deposited_amount(user_id, gems)
            deposited_amount = await get_deposited_amount(user_id)
            balance = await get_balance(user_id)
            message = {
                "content": f"<@{user_id}> Deposited {shorten_number(gems)}",
                "embeds": [
                    {
                        "title": "✅ Deposit completed",
                        "description": f"💎 **Amount:** {shorten_number(gems)}\n💎 **New Balance:** {shorten_number(balance)}",
                        "author": {
                            "icon_url": "https://api.creavite.co/out/DDTkNGXNaFZ3rw6qir_static.png",
                            "name": "JiggysBet"
                        },
                        "color": 9498256
                    }
                ]
            }
            requests.post(url=depowebhook, json=message)
            codes.remove(item)
        count += 1



def send_message(message):
    f = open(f"{workspacefolder}/withdraws.txt", "a")
    f.write(f"{message}\n")
    f.close()

async def background_function():
    while 1:
        await asyncio.sleep(1)
        f = open(f"{workspacefolder}/deposits.txt", "r")
        lines = f.readlines()
        f.close()
        for message2 in lines:
            message = message2.replace("\n", "")
            msg = message.split(",")
            code = msg[0]
            gems = int(msg[1])
            await test_code(code=code, gems=gems)
        f = open(f"{workspacefolder}/deposits.txt", "w")
        f.writelines("")

def between_callback():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(background_function())
    loop.close()

_thread = threading.Thread(target=between_callback)
_thread.start()

async def create_balance(user):
    async with bot.db.cursor() as cursor:
        await cursor.execute("INSERT INTO wallet(balance, user) VALUES(?, ?)", (0, user.id))
    await bot.db.commit()
    return

async def get_balance(user):
    if user is None:
        return

    user_id = user.id if hasattr(user, 'id') else user

    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT balance FROM wallet WHERE user = ?", (user_id,))
        data = await cursor.fetchone()
        if data is None:
            await create_balance(user)
            return 0
        balance = data[0]
        return balance


async def update_wallet(user, amount: int):
    if user is None:
        return

    user_id = user.id if hasattr(user, 'id') else user

    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT balance FROM wallet WHERE user = ?", (user_id,))
        data = await cursor.fetchone()
        if data is None:
            await create_balance(user)
            return 0
        balance = data[0]

        balance += amount
        if balance < 0:
            balance = 0

        await cursor.execute("UPDATE wallet SET balance = ? WHERE user = ?", (balance, user_id))
    await bot.db.commit()


def shorten_number(number):
    if number == 0:
        return '0'

    suffixes = ['', 'k', 'M', 'B', 'T', 'Q']
    suffix_index = 0
    while number >= 1000 and suffix_index < len(suffixes) - 1:
        number /= 1000
        suffix_index += 1

    if number >= 100:
        return f"{int(number)}{suffixes[suffix_index]}"
    elif number >= 10:
        return f"{number:.1f}{suffixes[suffix_index]}"
    else:
        return f"{number:.2f}{suffixes[suffix_index]}"

def parse_amount(amount: str) -> int:
    suffixes = {
        "m": 1_000_000,
        "b": 1_000_000_000,
        "t": 1_000_000_000_000,
        "q": 1_000_000_000_000_000
    }

    suffix = amount[-1]
    if suffix.lower() in suffixes:
        try:
            value = float(amount[:-1])
            return int(value * suffixes[suffix.lower()])
        except ValueError:
            raise ValueError("Invalid amount format.")
    
    try:
        return int(amount)
    except ValueError:
        raise ValueError("Invalid amount format.")
    
#balance
@bot.tree.command(name="balance", description="Check your balance")
@discord.app_commands.checks.cooldown(1, 2)
@commands.guild_only()
async def balance(interaction: discord.Interaction, member: discord.Member = None):
    if not member:
        member = interaction.user
        user_id = interaction.user.id
    else:
        user_id = member.id

    # Get the current balance and deposited amount
    balance = await get_balance(member)

    formatted_balance = shorten_number(balance)

    deposited = await get_deposited_amount(user_id)
    withdrawed = await get_withdrawed_amount(user_id)
    wagered = await get_wagered_amount(user_id)
    affiliate = await get_affiliate(user_id)
    embed = discord.Embed(title=f"{member.name}#{member.discriminator}'s Info", color=0x47a8e8)
    embed.description = f"**💎 Balance:** {formatted_balance}\n💎 **Deposited:** {shorten_number(deposited)}\n💎 **Withdrawn:** {shorten_number(withdrawed)}\n\n🍀 **Total Wagered:** {shorten_number(wagered)}\n🍀 **Affiliated To:** {affiliate}\n"

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="dice", description="Roll a dice for gems.")
@discord.app_commands.checks.cooldown(1, 3)
@commands.guild_only()
async def dice(interaction: discord.Interaction, gems: str):
    try:
        gems = parse_amount(gems)
    except ValueError:
        embed = discord.Embed(title="❌ Dice Creation Failed", color=0x47a8e8)
        embed.description = "Enter a valid amount of gems to continue with this transaction."
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if gems < 100_000_000:
        embed = discord.Embed(title="❌ Dice Creation Failed", color=0x47a8e8)
        embed.description = "Amount must be greater than **100M gems.**"
        return await interaction.response.send_message(embed=embed)

    balance = await get_balance(interaction.user)
    if balance < gems:
        embed = discord.Embed(title="❌ Dice Creation Failed", color=0x47a8e8)
        embed.description = "You don't have enough gems to complete this transaction."
        return await interaction.response.send_message(embed=embed)


    current_timestamp = int(time.time())
    five_seconds_later = current_timestamp + 5


    await update_wallet(interaction.user, -gems)
    await update_wagered_amount(interaction.user.id, gems)

    winnings = gems * 2
    embed = discord.Embed(title="🎲 Dice Roll", color=0x47a8e8)
    embed.description = f"⏰ **Status:** Rolling in <t:{five_seconds_later}:R>\n\n💎 **Amount:** {shorten_number(gems)}\n💎 **Potential Winnings:** {shorten_number(winnings)}"
    await interaction.response.send_message(embed=embed,)

    await asyncio.sleep(5)


    if gems > 30_000_000_000:
        bot_rolled = random.randint(3,6)
        user_rolled = random.randint(1,5)
    else:
        bot_rolled = random.randint(3,6)
        user_rolled = random.randint(1,6)


    winnings = gems * 2
    emoji = "<:rolling_dice:1117533054152482896>"
    if bot_rolled > user_rolled:
        winner = "<@1112439312852717709>"
        embed = discord.Embed(title="❌ Dice Roll Lost", color=0x47a8e8)
        embed.description = f"⏰ **Status:** Rolled the dice\n\n{emoji} **You rolled:** {user_rolled}\n{emoji} **Bot rolled:** {bot_rolled}\n\n💎 **Amount:** {shorten_number(gems)}\n💎 **Winnings:** {shorten_number(winnings)}\n\n🎖️ **Winner**: {winner}"
    elif bot_rolled == user_rolled:
        await update_wallet(interaction.user, gems)
        embed = discord.Embed(title="🎲 Dice Roll Tied", color=0x47a8e8)
        embed.description = f"⏰ **Status:** Rolled the dice\n\n{emoji} **You rolled:** {user_rolled}\n{emoji} **Bot rolled:** {bot_rolled}\n\n💎 **Amount:** {shorten_number(gems)}\n💎 **Winnings:** {shorten_number(winnings)}\n\n🎖️ **Winner**: None"
    else:
        await update_wallet(interaction.user, winnings)
        winner = interaction.user.mention
        embed = discord.Embed(title="✅ Dice Roll Won", color=0x47a8e8)
        embed.description = f"⏰ **Status:** Rolled the dice\n\n{emoji} **You rolled:** {user_rolled}\n{emoji} **Bot rolled:** {bot_rolled}\n\n💎 **Amount:** {shorten_number(gems)}\n💎 **Winnings:** {shorten_number(winnings)}\n\n🎖️ **Winner**: {winner}"


    message = await interaction.original_response()
    await message.edit(embed=embed)


# upgrader win chance
def get_win_chance(multiplier):
    win_chance = 50 * (1.5 / multiplier) * 1.1   # Actual win chance reduced by 5%
    return win_chance

#upgrader
@bot.tree.command(name="upgrader", description="Bet gems on a multiplier")
@commands.guild_only()
@discord.app_commands.checks.cooldown(1, 5)
async def upgrader(interaction: discord.Interaction, gems: str, multiplier: float):
    balance = await get_balance(interaction.user)
    gems = parse_amount(gems)
    if gems < 100_000_000:
        embed = discord.Embed(title="❌ Upgrader Creation Failed", color=0x47a8e8)
        embed.description = "Amount must be greater than **100M gems.**"
        return await interaction.response.send_message(embed=embed)

    if not (1.5 <= multiplier <= 5):
        embed = discord.Embed(title="❌ Upgrader Creation Failed", color=0x47a8e8)
        embed.description = "Minimum multiplier is 1.5 and max is 5.0."
        return await interaction.response.send_message(embed=embed)

    if balance < gems:
        embed = discord.Embed(title="❌ Upgrader Creation Failed", color=0x47a8e8)
        embed.description = "You don't have enough gems to complete this transaction."
        return await interaction.response.send_message(embed=embed)

    win_chance = get_win_chance(multiplier)

    await update_wallet(interaction.user, -gems)
    await update_wagered_amount(interaction.user.id, gems)

    current_timestamp = int(time.time())
    five_seconds_later = current_timestamp + 5
    embed = discord.Embed(title="✅ Upgrade Created", color=0x47a8e8)
    embed.description = f"💎 **Bet:** {shorten_number(gems)}\n🍀 **Win Chance:** {win_chance:.1f}%\n🌟 **Multiplier:** {multiplier}\n\n⏰ **Rolling in** <t:{five_seconds_later}:R>"
    message = await interaction.response.send_message(embed=embed)

    await asyncio.sleep(5)  # Wait for 5 seconds

    if random.random() <= win_chance / 100:
        # The user has won based on the win chance
        winnings = round(gems * multiplier)
        await update_wallet(interaction.user, winnings)
        color = 0x90EE90
        embed = discord.Embed(title="✅ Upgrade Won", color=color)
        embed.description = f"💎 **Bet:** {shorten_number(gems)}\n💎 **Winnings:** {shorten_number(winnings)}\n🍀 **Win Chance:** {win_chance:.1f}%\n🌟 **Multiplier:** x{multiplier}"
    else:
        # The user has lost
        winnings = round(gems * multiplier)
        color = 0xe8503f
        embed = discord.Embed(title="❌ Upgrade Lost", color=color)
        embed.description = f"💎 **Bet:** {shorten_number(gems)}\n💎 **Lost Winnings:** {shorten_number(winnings)}\n🍀 **Win Chance:** {win_chance:.1f}%\n🌟 **Multiplier:** x{multiplier}" 

    message = await interaction.original_response()
    await message.edit(embed=embed)

#coinflip cmd
class CoinFlip(discord.ui.View):
    def __init__(self, author_id, bet_amount):
        super().__init__()
        self.author_id = author_id
        self.value = None
        self.bot_called = False
        self.other_user = None
        self.other_user_id = None
        self.cancelled = False
        self.bet_amount = bet_amount
        self.joining_user = None 

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green, custom_id="join_button")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.author_id:
            embed = discord.Embed(title="❌ Coinflip Error", color=0x47a8e8)
            embed.description = "You can't join your own coinflip game."
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            balance = await get_balance(interaction.user)
            if balance < self.bet_amount:
                embed = discord.Embed(title="❌ Coinflip Join Failed", color=0x47a8e8)
                embed.description = "You don't have enough gems to join this game."
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                self.joining_user = interaction.user
                embed = discord.Embed(title="✅ Coinflip Joined", color=0x47a8e8)
                embed.description = "You successfully joined the coinflip game! "
                await interaction.response.send_message(embed=embed, ephemeral=True)
                self.value = False
                self.stop()

    @discord.ui.button(label="Call A Bot", style=discord.ButtonStyle.blurple, custom_id="callbot_button")
    async def callbot(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            embed = discord.Embed(title="❌ Coinflip Error", color=0x47a8e8)
            embed.description = "You aren't the author of this game."
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        self.bot_called = True
        embed = discord.Embed(title="✅ Bot Called", color=0x47a8e8)
        embed.description = "Successfully called a bot!"
        await interaction.response.send_message(embed=embed, ephemeral=True)        
        self.value = False
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel_button")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            embed = discord.Embed(title="❌ Coinflip Error", color=0x47a8e8)
            embed.description = "You aren't the author of this game."
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(title="✅ Cancelled", color=0x47a8e8)
        embed.description = "Your flip was cancelled, your gems have been refunded."
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.cancelled = True  # Set the cancelled attribute to True
        self.value = False
        self.stop()



choice1 = Enum(value='Coinflip', names=['Heads', 'Tails'], module=__name__)


@bot.tree.command(name="flip", description="Start a coinflip game")
async def flip(interaction: discord.Interaction, choice: choice1, gems: str):
    channel_id = 1118117882728022056
    balance = await get_balance(interaction.user)
    try:
        gems = parse_amount(gems)
    except ValueError:
        embed = discord.Embed(title="❌ Coinflip Creation Failed", color=0x47a8e8)
        embed.description = "Enter a valid amount of gems to continue with this transaction."
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if gems < 100_000_00:
        embed = discord.Embed(title="❌ Coinflip Creation Failed", color=0x47a8e8)
        embed.description = "Bet amount must be at least **100M gems**."
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if balance < gems:
        embed = discord.Embed(title="❌ Coinflip Creation Failed", color=0x47a8e8)
        embed.description = "You dont have enough gems to create this game."
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    author_id = interaction.user.id
    view = CoinFlip(author_id, gems)

    user_pick = choice.name.capitalize()
    other_pick = "Tails" if choice.name == "Heads" else "Heads"

    winnings = gems * 2

    await update_wallet(interaction.user, -gems)
    await update_wagered_amount(interaction.user.id, gems)

    embed = discord.Embed(title="✅ Coinflip Created", color=0x47a8e8)
    embed.description = f"💬 **Channel:** <#{channel_id}>\n💎 **Amount:** {shorten_number(gems)}"
    message = await interaction.response.send_message(embed=embed)

    channel = interaction.guild.get_channel(channel_id)
    embed = discord.Embed(title=f"{interaction.user}'s Coinflip", color=0x47a8e8)
    embed.description = f"⏰ **Status:** Waiting for players..\n\n{user_pick}: {interaction.user.mention}\n{other_pick}: Undecided\n\n💎 **Amount:** {shorten_number(gems)}\n💎**Potential Winnings:** {shorten_number(winnings)}\n\n🎖️ **Winner:** Undecided"
    waiting_message = await channel.send(embed=embed, view=view)

    await view.wait()

    if view.cancelled:
        await update_wallet(interaction.user, gems)
        await waiting_message.delete()
        return

    if view.bot_called:

        user_pick = choice.name.capitalize()
        bot_pick = "Tails" if user_pick == "Heads" else "Heads"

        if user_pick == "Heads":
            result = random.choices(["Heads", "Tails"], [1, 4])[0]  # Adjust weights here
        else:
            result = random.choices(["Heads", "Tails"], [4, 1])[0]  # Adjust weights here


        other_user = "<@1112439312852717709>"

        if result == user_pick:
            winner = interaction.user.mention # Game creator wins
            await update_wallet(interaction.user, winnings)
        elif result == bot_pick:
            winner = other_user # Other user wins
        else:
            winner = "Undecided"

    else:
        user_pick = choice.name.capitalize()
        other_pick = "Tails" if user_pick == "Heads" else "Heads"

        other_user_id = None
        other_user = None

        joining_user = None

        while joining_user is None:
            await asyncio.sleep(1)
            joining_user = view.joining_user

        other_user_id = joining_user.id
        other_user = joining_user.mention
        result = random.choice(["Heads", "Tails"])  # Randomly select the result

        await update_wallet(other_user_id, -gems)

        if result == user_pick:
            winner = interaction.user.mention  # Game creator wins
            await update_wallet(interaction.user, winnings)
        elif result == other_pick:
            winner = other_user  # Other user wins
            await update_wallet(other_user_id, winnings)
        else:
            winner = "Undecided"


    embed = discord.Embed(title=f"{interaction.user}'s Coinflip", color=0x47a8e8)
    current_timestamp = int(time.time())
    five_seconds_later = current_timestamp + 5
    embed.description = f"⏰ **Status:** Flipping<t:{five_seconds_later}:R>\n\n{user_pick}: {interaction.user.mention}\n{other_pick}: {other_user}\n\n💎 **Amount:** {shorten_number(gems)}\n💎**Potential Winnings:** {shorten_number(winnings)}\n\n🎖️ **Winner:** Undecided"
    await waiting_message.edit(embed=embed)

    await asyncio.sleep(5)

    await waiting_message.edit(view=None)

    embed = discord.Embed(title=f"{interaction.user}'s Coinflip", color=0x47a8e8)
    embed.description = f"⏰ **Status:** Flipped **{result}**\n\n{user_pick}: {interaction.user.mention}\n{other_pick}: {other_user}\n\n💎 **Amount:** {shorten_number(gems)}\n💎**Winnings:** {shorten_number(winnings)}\n\n🎖️ **Winner:** {winner}"
    await waiting_message.edit(embed=embed)

    await asyncio.sleep(30)
    await waiting_message.delete()

#Tip command
@bot.tree.command(name="tip", description="Tip a user any amount of gems.")
@discord.app_commands.checks.cooldown(1, 3)
async def tip(interaction: discord.Interaction, user: discord.Member, gems: str):
    balance = await get_balance(interaction.user)
    user_balance = await get_balance(user)
    channel_id = 1118117880102391958
    try:
        gems = parse_amount(gems)
    except ValueError:
        embed = discord.Embed(title="❌ Tip Error", color=0x47a8e8)
        embed.description = "Enter a valid number."
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if gems > balance:
        embed = discord.Embed(title="❌ Tip Error", color=0x47a8e8)
        embed.description = "You dont have enough balance to complete this transaction."
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if gems < 10_000_000:
        embed = discord.Embed(title="❌ Tip Error", color=0x47a8e8)
        embed.description = "The minimum tip amount is **10M gems**"
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    await update_wallet(interaction.user, -gems)
    await update_wallet(user.id, gems)

    embed = discord.Embed(title="✅ Tip Completed", color=0x47a8e8)
    embed.description = f"💎 **Gems:** {shorten_number(gems)}\n📤 **Sender:** {interaction.user.mention}\n📥 **Receiver:** {user.mention}"
    await interaction.response.send_message(embed=embed)

    channel = interaction.guild.get_channel(channel_id)
    embed = discord.Embed(title="✅ Tip Completed", color=0x47a8e8)
    embed.description = f"💎 **Gems:** {shorten_number(gems)}\n📤 **Sender:** {interaction.user.mention}\n📥 **Receiver:** {user.mention}"
    return await channel.send(f"{interaction.user.mention} Has tipped {shorten_number(gems)} gems to {user.mention}!",embed=embed)


@bot.tree.command(name="deposit", description="Deposit gems to gamble.")
@discord.app_commands.checks.cooldown(1, 3)
async def deposit(interaction: discord.Interaction):
    words = ['apple', 'banana', 'fruit', 'car', 'base', 'good', 'life', 'up', 'time', 'left', 'down', 'code']

    random_words = random.sample(words, 3)

    code = " ".join(random_words)

    codes.append([str(interaction.user.id), code])
    embed = discord.Embed(title="✅ Deposit Created", color=0x47a8e8)
    embed.description = f"⚠️ **WARNING** ⚠️ Your code might be tagged, send it in chat before sending!\n\n 👱 **Username:** `{Username}`\n📫 **Message:** `{code}`\n💎 **Gems:** Any amount of gems"
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="withdraw", description="Withdraw Gems")
async def withdraw(interaction: discord.Interaction, amount: str, username: str):
        amount = parse_amount(amount)
        balance = await get_balance(interaction.user)
        if balance >= amount:
            await update_wallet(interaction.user, amount)
            gems = amount
            if gems >= 1000000000000 :  # if gems are greater than or equal to 1 trillion
                gems_formatted = f"{gems / 1000000000000:.1f}t"  # display gems in trillions with one decimal point
            elif gems >= 1000000000 :  # if gems are greater than or equal to 1 billion
                gems_formatted = f"{gems / 1000000000:.1f}b"  # display gems in billions with one decimal point
            elif gems >= 1000000 :  # if gems are greater than or equal to 1 million
                gems_formatted = f"{gems / 1000000:.1f}m"  # display gems in millions with one decimal point
            elif gems >= 1000 :  # if gems are greater than or equal to 1 thousand
                gems_formatted = f"{gems / 1000:.1f}k"  # display gems in thousands with one decimal point
            else :  # if gems are less than 1 thousand
                gems_formatted = str(gems)  # display gems as is
            message = {
                "content" : f"<@{interaction.user.id}> Withdrew {gems_formatted}!"
            }
            requests.post(
                url=withwebhook,
                json=message)
            send_message(f"{username},{amount}")
            new_balance = balance - amount
            embed = discord.Embed(title="✅ Withdraw Created", color=0x47a8e8)
            embed.description = f"**Username:** `{username}`\n📫 **Gems:** `{shorten_number(gems)}`\n💎 **New Balance:** {shorten_number(new_balance)} "

            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="❌ Withdraw Creation Failed", color=0x47a8e8)
            embed.description = "You dont have enough gems to complete this **transaction****"
            return await interaction.response.send_message(embed=embed)

#add balance (ADMIN)
@bot.tree.command(name="addbal", description="Add balance to another user")
@discord.app_commands.checks.cooldown(1, 3)
@commands.guild_only()
async def add_balance(interaction: discord.Interaction, amount: str, member: discord.Member):
    allowed_user_ids = {"1073119307334156328", "1073119307334156328"}
    if str(interaction.user.id) not in allowed_user_ids:
        embed = discord.Embed(title="❌ Error", color=0x47a8e8)
        embed.description = f"You are not allowed to use this command!"
        return await interaction.response.send_message(embed=embed, ephemeral=True)    
    
    amount = amount.lower().strip()
    try:
        amount = parse_amount(amount)
    except ValueError:
        return await interaction.response.send_message("Invalid amount. Please enter a valid number or a number followed by 'k', 'm', 'b', 't', 'q', or 'qi' to indicate thousands, millions, billions, trillions, quadrillions, or trillinos.")

    if amount <= 0:
        return await interaction.response.send_message("Invalid amount. Please enter a positive number.")

    await update_wallet(member, amount)
    embed = discord.Embed(title="✅ Added Balance", color=0x47a8e8)
    embed.description = f"**Added {shorten_number(amount)} gems to {member.mention}**"
    return await interaction.response.send_message(embed=embed)

#reset balance (ADMIN)
@bot.tree.command(name="reset", description="Reset a user's gems and net profit")
@commands.guild_only()
async def reset(interaction: discord.Interaction, member: discord.Member):
    allowed_user_ids = {"1073119307334156328", "1073119307334156328", "1073119307334156328"}
    if str(interaction.user.id) not in allowed_user_ids:
        return await interaction.response.send_message("You are not one of the listed owners that can access this command")
    
    balance = await get_balance(member)    
    await update_wallet(member, -balance)
    await bot.db.commit()

    return await interaction.response.send_message(f"{member.mention}'s balance has been reset.")

bot.run("token here")
