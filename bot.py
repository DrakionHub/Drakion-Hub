import discord
from discord.ext import commands
from discord.ui import View, Select
import asyncio
import os

RODAPE_TEXTO = "Drakion Call © | Todos os Direitos Reservados."
RODAPE_ICONE = "https://cdn.discordapp.com/icons/1481089628374171651/de6d926a6fd65da6b783a0f96e929b49.png?size=2048"

ID_CARGO_PERMISSAO = 1481089914522173520
ID_CARGO_MEMBRO = 1482425956466429973
ID_CATEGORIA_CALL = 1482171487640223847

CARGOS_BYPASS_LIMITE = [
    1481089914522173520
]

CONFIG_CALL = {
    "titulo": "Painel de Calls",
    "descricao": (
        ":fire: ┃ Crie uma chamada para realizar eventos de Blox Fruits com outros membros.\n"
        ":mag_right: ┃ Escolha o tipo de call e depois selecione a quantidade de vagas.\n"
        ":apple: ┃ Crie uma chamada para realizar eventos de Blox Fruits com outros membros.\n"
        ":island: ┃ Você pode escolher entre PVP, Trial, Leviathan ou Vulcão.\n"
        ":video_game: ┃ Caso queira jogar outro modo ou jogo, abra uma call de \"Jogando\".\n"
        ":speech_balloon: ┃ Se deseja conversar com outros membros, abra uma call de \"criar-call\".\n"
        ":hammer_pick: ┃ Evite abrir chamadas para conversar ou escutar musica.\n"
        ":x: ┃ Evite criar muitas chamadas sem necessidade.\n"
        ":question: ┃ Caso haja algum erro ou dúvida, contate o suporte."
    ),
    "cor": 0xFF0000,
    "imagem": "https://cdn.discordapp.com/attachments/1482181421341872259/1482192202976202783/output.png"
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
        "Vulcão": "🌋》",
        "Eventos Marinhos": "🌊》",
        "Jogando": "🎮》",
        "Música": "🎶》",
        "Geral": "🔊》"
    }
    return f"{prefixes.get(name, '🔊》')}{name}"


class ParticipantCountSelect(Select):

    def __init__(self, event_name, bot):
        self.event_name = event_name
        self.bot = bot

        options = [
            discord.SelectOption(label="1 vaga", value="1"),
            discord.SelectOption(label="2 vagas", value="2"),
            discord.SelectOption(label="3 vagas", value="3"),
            discord.SelectOption(label="4 vagas", value="4"),
            discord.SelectOption(label="5 vagas", value="5"),
            discord.SelectOption(label="10 vagas", value="10"),
            discord.SelectOption(label="15 vagas", value="15"),
            discord.SelectOption(label="20 vagas", value="20"),
            discord.SelectOption(label="Sem limite", value="0")
        ]

        super().__init__(
            placeholder="Escolha o limite de vagas",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        if interaction.user.id in self.bot.user_calls:
            await interaction.response.send_message(
                "❌ Você já possui uma call ativa.",
                ephemeral=True
            )
            return

        limit = int(self.values[0])

        category = interaction.guild.get_channel(ID_CATEGORIA_CALL)
        role_membro = interaction.guild.get_role(ID_CARGO_MEMBRO)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(connect=True, speak=True),
            role_membro: discord.PermissionOverwrite(connect=True, speak=True)
        }

        for cargo_id in CARGOS_BYPASS_LIMITE:
            role = interaction.guild.get_role(cargo_id)
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
            f"✅ Call criada: {channel.mention}\nEntre em **15 segundos** ou ela será deletada.",
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
        placeholder="Escolha o tipo de call",
        custom_id="drakion_call_select",
        options=[
            discord.SelectOption(label="Geral", emoji="🔊", value="Geral"),
            discord.SelectOption(label="Música", emoji="🎶", value="Música"),
            discord.SelectOption(label="PVP", emoji="🥊", value="PVP"),
            discord.SelectOption(label="Trial", emoji="🌑", value="Trial"),
            discord.SelectOption(label="Leviathan", emoji="🐉", value="Leviathan"),
            discord.SelectOption(label="Vulcão", emoji="🌋", value="Vulcão"),
            discord.SelectOption(label="Eventos Marinhos", emoji="🌊", value="Eventos Marinhos"),
            discord.SelectOption(label="Jogando", emoji="🎮", value="Jogando")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):

        view = discord.ui.View()
        view.add_item(ParticipantCountSelect(select.values[0], self.bot))

        await interaction.response.send_message(
            f"Quantas vagas para **{select.values[0]}**?",
            view=view,
            ephemeral=True
        )


class MyBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

        self.active_calls = {}
        self.user_calls = {}

    async def setup_hook(self):

        self.add_view(EventCallView(self))
        await self.tree.sync()

        print("✅ Bot online")


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


@bot.tree.command(name="env_panel", description="Enviar painel de criação de calls")
async def env_panel(interaction: discord.Interaction):

    cargo = interaction.guild.get_role(ID_CARGO_PERMISSAO)

    if cargo not in interaction.user.roles:
        await interaction.response.send_message(
            "❌ Você não tem permissão.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=CONFIG_CALL["titulo"],
        description=CONFIG_CALL["descricao"],
        color=CONFIG_CALL["cor"]
    )

    embed.set_image(url=CONFIG_CALL["imagem"])
    embed.set_footer(text=RODAPE_TEXTO, icon_url=RODAPE_ICONE)

    await interaction.channel.send(
        embed=embed,
        view=EventCallView(bot)
    )

    await interaction.response.send_message(
        "✅ Painel enviado.",
        ephemeral=True
    )


TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
