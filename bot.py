import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import asyncio
import os

FOOTER_TEXT = "Drakion Call © | All Rights Reserved."
FOOTER_ICON = "https://cdn.discordapp.com/icons/1481089628374171651/de6d926a6fd65da6b783a0f96e929b49.png?size=2048"

ID_PERMISSION_ROLE = 1482423776158154953
ID_MEMBER_ROLE = 1482425956466429973
ID_CALL_CATEGORY = 1482171487640223847

# COLOQUE O ID DO SEU SERVIDOR AQUI
GUILD_ID = 1481089628374171651

BYPASS_LIMIT_ROLES = [
    1481089914522173520,
    1482423776158154953,
    1482425821460304144
]

CALL_CONFIG = {
    "title": "Call Panel",
    "description": (
        "🔥 ┃ Create a call to organize **Blox Fruits** events with other members.\n"
        "🔎 ┃ Choose the type of call and then select the number of slots.\n"
        "🍎 ┃ Use calls to coordinate raids, bosses and activities.\n"
        "🏝 ┃ You can choose between **PVP, Trial, Leviathan or Volcano**.\n"
        "🎮 ┃ If you want to play another mode or game, open a **Gaming** call.\n"
        "💬 ┃ If you just want to chat with other members, open a **General** call.\n"
        "🛠 ┃ Avoid opening calls only to listen to music.\n"
        "❌ ┃ Avoid creating unnecessary calls.\n"
        "❓ ┃ If you encounter any issues, contact the support team."
    ),
    "color": 0xFF0000,
    "image": "https://cdn.discordapp.com/attachments/1482181421341872259/1482192202976202783/output.png"
}

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True
intents.guilds = True


def get_channel_name(name):
    prefixes = {
        "PVP": "🥊》",
        "Trial": "🌑》",
        "Leviathan": "🐉》",
        "Volcano": "🌋》",
        "Sea Events": "🌊》",
        "Gaming": "🎮》",
        "Music": "🎶》",
        "General": "🔊》"
    }
    return f"{prefixes.get(name, '🔊》')}{name}"


class ParticipantCountSelect(Select):

    def __init__(self, event_name, bot):
        self.event_name = event_name
        self.bot = bot

        options = [
            discord.SelectOption(label="1 slot", value="1"),
            discord.SelectOption(label="2 slots", value="2"),
            discord.SelectOption(label="3 slots", value="3"),
            discord.SelectOption(label="4 slots", value="4"),
            discord.SelectOption(label="5 slots", value="5"),
            discord.SelectOption(label="10 slots", value="10"),
            discord.SelectOption(label="15 slots", value="15"),
            discord.SelectOption(label="20 slots", value="20"),
            discord.SelectOption(label="Unlimited", value="0")
        ]

        super().__init__(
            placeholder="Choose the participant limit",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        if interaction.user.id in self.bot.user_calls:
            await interaction.response.send_message(
                "❌ You already have an active call.",
                ephemeral=True
            )
            return

        limit = int(self.values[0])

        category = interaction.guild.get_channel(ID_CALL_CATEGORY)
        role_member = interaction.guild.get_role(ID_MEMBER_ROLE)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(connect=True, speak=True),
            role_member: discord.PermissionOverwrite(connect=True, speak=True)
        }

        for role_id in BYPASS_LIMIT_ROLES:
            role = interaction.guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(connect=True, speak=True)

        channel = await interaction.guild.create_voice_channel(
            name=get_channel_name(self.event_name),
            category=category,
            user_limit=limit,
            overwrites=overwrites
        )

        self.bot.active_calls[channel.id] = interaction.user.id
        self.bot.user_calls[interaction.user.id] = channel.id

        await interaction.response.send_message(
            f"✅ Call created: {channel.mention}\nJoin within **15 seconds** or it will be deleted.",
            ephemeral=True
        )

        await asyncio.sleep(15)

        if len(channel.members) == 0:
            try:
                owner = self.bot.active_calls.pop(channel.id)
                self.bot.user_calls.pop(owner)
                await channel.delete()
            except:
                pass


class EventCallView(View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.select(
        placeholder="Choose the type of call",
        custom_id="drakion_call_select",
        options=[
            discord.SelectOption(label="General", emoji="🔊", value="General"),
            discord.SelectOption(label="Music", emoji="🎶", value="Music"),
            discord.SelectOption(label="PVP", emoji="🥊", value="PVP"),
            discord.SelectOption(label="Trial", emoji="🌑", value="Trial"),
            discord.SelectOption(label="Leviathan", emoji="🐉", value="Leviathan"),
            discord.SelectOption(label="Volcano", emoji="🌋", value="Volcano"),
            discord.SelectOption(label="Sea Events", emoji="🌊", value="Sea Events"),
            discord.SelectOption(label="Gaming", emoji="🎮", value="Gaming")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):

        view = discord.ui.View()
        view.add_item(ParticipantCountSelect(select.values[0], self.bot))

        await interaction.response.send_message(
            f"How many slots for **{select.values[0]}**?",
            view=view,
            ephemeral=True
        )


class EmbedModal(Modal, title="Create Embed"):

    embed_text = TextInput(
        label="Embed Text",
        style=discord.TextStyle.paragraph,
        placeholder="Write the embed message here...",
        required=True,
        max_length=2000
    )

    async def on_submit(self, interaction: discord.Interaction):

        embed = discord.Embed(
            description=self.embed_text.value,
            color=0xFF0000
        )

        embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)

        await interaction.channel.send(embed=embed)

        await interaction.response.send_message(
            "✅ Embed sent successfully.",
            ephemeral=True
        )


class MyBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

        self.active_calls = {}
        self.user_calls = {}

    async def setup_hook(self):

        self.add_view(EventCallView(self))

        guild = discord.Object(id=GUILD_ID)

        await self.tree.sync(guild=guild)

        print("✅ Bot is online")


bot = MyBot()


@bot.event
async def on_voice_state_update(member, before, after):

    if before.channel and before.channel.id in bot.active_calls:

        if len(before.channel.members) == 0:

            await asyncio.sleep(5)

            if len(before.channel.members) == 0:

                try:
                    owner = bot.active_calls.pop(before.channel.id)
                    bot.user_calls.pop(owner)
                    await before.channel.delete()
                except:
                    pass


@bot.tree.command(name="send_panel", description="Send the call creation panel")
async def send_panel(interaction: discord.Interaction):

    if not any(role.id == ID_PERMISSION_ROLE for role in interaction.user.roles):
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=CALL_CONFIG["title"],
        description=CALL_CONFIG["description"],
        color=CALL_CONFIG["color"]
    )

    embed.set_image(url=CALL_CONFIG["image"])
    embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)

    await interaction.channel.send(
        embed=embed,
        view=EventCallView(bot)
    )

    await interaction.response.send_message(
        "✅ Panel sent successfully.",
        ephemeral=True
    )


@bot.tree.command(name="embed", description="Create an embed message")
async def embed(interaction: discord.Interaction):

    if not any(role.id == ID_PERMISSION_ROLE for role in interaction.user.roles):
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(EmbedModal())


TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
