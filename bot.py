import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import asyncio
import os

TOKEN = os.getenv("TOKEN")

FOOTER_TEXT = "Drakion Call © | All Rights Reserved."
FOOTER_ICON = "https://cdn.discordapp.com/icons/1481089628374171651/de6d926a6fd65da6b783a0f96e929b49.png?size=2048"

ID_PERMISSION_ROLE = 1482423776158154953
ID_MEMBER_ROLE = 1482425956466429973
ID_CALL_CATEGORY = 1482171487640223847
GUILD_ID = 1481089628374171651

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.guilds = True
intents.message_content = True


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
    return f"{prefixes.get(name,'🔊》')}{name}"


class ParticipantSelect(Select):

    def __init__(self, event_name, bot):
        self.event_name = event_name
        self.bot = bot

        options = [
            discord.SelectOption(label="1", value="1"),
            discord.SelectOption(label="2", value="2"),
            discord.SelectOption(label="3", value="3"),
            discord.SelectOption(label="4", value="4"),
            discord.SelectOption(label="5", value="5"),
            discord.SelectOption(label="10", value="10"),
            discord.SelectOption(label="15", value="15"),
            discord.SelectOption(label="20", value="20"),
            discord.SelectOption(label="Unlimited", value="0")
        ]

        super().__init__(
            placeholder="Select slot amount",
            options=options,
            custom_id="slot_select"
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

        channel = await interaction.guild.create_voice_channel(
            name=get_channel_name(self.event_name),
            category=category,
            user_limit=limit
        )

        self.bot.user_calls[interaction.user.id] = channel.id

        await interaction.response.send_message(
            f"✅ Call created: {channel.mention}",
            ephemeral=True
        )


class CallView(View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.select(
        placeholder="Select call type",
        custom_id="call_type_select",
        options=[
            discord.SelectOption(label="General", emoji="🔊"),
            discord.SelectOption(label="Music", emoji="🎶"),
            discord.SelectOption(label="PVP", emoji="🥊"),
            discord.SelectOption(label="Trial", emoji="🌑"),
            discord.SelectOption(label="Leviathan", emoji="🐉"),
            discord.SelectOption(label="Volcano", emoji="🌋"),
            discord.SelectOption(label="Sea Events", emoji="🌊"),
            discord.SelectOption(label="Gaming", emoji="🎮")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):

        view = View()
        view.add_item(ParticipantSelect(select.values[0], self.bot))

        await interaction.response.send_message(
            "Select slot amount:",
            view=view,
            ephemeral=True
        )


class EmbedModal(Modal, title="Create Embed"):

    message = TextInput(
        label="Embed text",
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction):

        embed = discord.Embed(
            description=self.message.value,
            color=0xff0000
        )

        embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)

        await interaction.channel.send(embed=embed)

        await interaction.response.send_message(
            "✅ Embed sent.",
            ephemeral=True
        )


class MyBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents
        )

        self.user_calls = {}

    async def setup_hook(self):

        self.add_view(CallView(self))

        guild = discord.Object(id=GUILD_ID)

        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

        print("✅ Commands synced")


bot = MyBot()


@bot.tree.command(
    name="send_panel",
    description="Send call panel",
    guild=discord.Object(id=GUILD_ID)
)
async def send_panel(interaction: discord.Interaction):

    if not any(role.id == ID_PERMISSION_ROLE for role in interaction.user.roles):
        await interaction.response.send_message(
            "❌ No permission",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="Call Panel",
        description= "🔥 ┃ Create a call to organize *Blox Fruits* events with other members."
"🔎 ┃ Choose the type of call and then select the number of slots."
"🍎 ┃ Use calls to coordinate raids, bosses and activities."
"🏝 ┃ You can choose between *PVP, Trial, Leviathan or Volcano*."
"🎮 ┃ If you want to play another mode or game, open a *Gaming* call."
"💬 ┃ If you just want to chat with other members, open a *General* call."
"🛠 ┃ Avoid opening calls only to listen to music."
"❌ ┃ Avoid creating unnecessary calls."
"❓ ┃ If you encounter any issues, contact the support team.",
        color=0xff0000
    )

    embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)

    await interaction.channel.send(
        embed=embed,
        view=CallView(bot)
    )

    await interaction.response.send_message(
        "✅ Panel sent",
        ephemeral=True
    )


@bot.tree.command(
    name="embed",
    description="Create embed",
    guild=discord.Object(id=GUILD_ID)
)
async def embed(interaction: discord.Interaction):

    if not any(role.id == ID_PERMISSION_ROLE for role in interaction.user.roles):
        await interaction.response.send_message(
            "❌ No permission",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(EmbedModal())


bot.run(TOKEN)
