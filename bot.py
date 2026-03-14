import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select, Modal, TextInput
import asyncio
import os

RODAPE_TEXTO = "Drakion Call Â© | Todos os Direitos Reservados."
RODAPE_ICONE = "https://cdn.discordapp.com/attachments/1482181421341872259/1482181591311581278/imagem.png"

ID_CARGO_PERMISSAO = 1481089914522173520
ID_CARGO_MEMBRO = 1481090300402204833
ID_CATEGORIA_CALL = 1482171487640223847

CARGOS_BYPASS_LIMITE = [
    1481089914522173520
]

CONFIG_CALL = {
    "titulo": "Painel de Calls",
    "descricao": (
        "Crie uma chamada para realizar eventos de Blox Fruits com outros membros.\n"
        "Você pode escolher entre PVP, Trial, Leviathan ou Vulcão.\n"
        "Caso queira jogar outro modo ou jogo, abra uma call de \"Jogando\".\n"
        "Se deseja conversar com outros membros, vÃ¡ para â ãƒ»criar-call.\n"
        "Evite abrir chamadas para conversar ou escutar mÃºsica. Utilize o canal adequado.\n"
        "Evite criar muitas chamadas sem necessidade, pois isso pode resultar em puniÃ§Ãµes.\n"
        "Caso haja algum erro ou dÃºvida, entre em contato com o suporte.\n"
        "Crie uma chamada geral ou de música com outros membros.\n"
        "Você pode escolher entre Criar chamada geral ou chamada de música.\n"
        "Caso precise de ajuda, entre em contato com o suporte."
    ),
    "cor": 0xFF0000, 
    "imagem": "https://cdn.discordapp.com/attachments/1310596794287128656/1322470018444689529/standard_1.gif"
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

class ParticipantCountSelect(discord.ui.Select):
    def __init__(self, event_name, bot_ref, category_id):
        self.event_name = event_name
        self.bot_ref = bot_ref
        self.category_id = category_id
        options = [discord.SelectOption(label=f"{i} Vagas", value=str(i)) for i in [1, 2, 3, 4, 5, 10, 15, 20]]
        options.append(discord.SelectOption(label="Sem Limite", value="0"))
        super().__init__(placeholder="Selecione a quantidade de vagas", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id in self.bot_ref.user_calls:
            return await interaction.response.send_message("âŒ VocÃª jÃ¡ possui uma call ativa!", ephemeral=True)
            
        await interaction.response.defer(ephemeral=True)
        limit = int(self.values[0])
        category = interaction.guild.get_channel(self.category_id)

        role_membro = interaction.guild.get_role(ID_CARGO_MEMBRO)
        
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(connect=True, speak=True),
            role_membro: discord.PermissionOverwrite(
                send_messages=True,
                read_message_history=True,
                attach_files=False, 
                speak=True,
                stream=True,
                connect=True
            )
        }

        for cargo_id in CARGOS_BYPASS_LIMITE:
            role_especial = interaction.guild.get_role(cargo_id)
            if role_especial:
                overwrites[role_especial] = discord.PermissionOverwrite(
                    connect=True, 
                    speak=True, 
                    view_channel=True
                )
        
        channel = await interaction.guild.create_voice_channel(
            name=get_channel_name(self.event_name),
            user_limit=limit,
            category=category,
            overwrites=overwrites
        )
        
        self.bot_ref.active_calls[channel.id] = interaction.user.id
        self.bot_ref.user_calls[interaction.user.id] = channel.id
        
        await interaction.followup.send(f"Sua call foi criada! Entre em 15 segundos antes que seja deletada {channel.mention}", ephemeral=True)
        
        await asyncio.sleep(15)
        if channel and len(channel.members) == 0:
            try:
                owner_id = self.bot_ref.active_calls.pop(channel.id, None)
                if owner_id:
                    self.bot_ref.user_calls.pop(owner_id, None)
                await channel.delete()
            except: pass

class EventCallView(discord.ui.View):
    def __init__(self, bot_ref):
        super().__init__(timeout=None)
        self.bot_ref = bot_ref

    @discord.ui.select(
        placeholder="Escolha uma Call...",
        custom_id="v_final_bf",
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
    async def callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        view = View().add_item(ParticipantCountSelect(select.values[0], self.bot_ref, ID_CATEGORIA_CALL))
        await interaction.response.send_message(f"Vagas para **{select.values[0]}**?", view=view, ephemeral=True)

class GeneralCallView(discord.ui.View):
    def __init__(self, bot_ref):
        super().__init__(timeout=None)
        self.bot_ref = bot_ref
        await interaction.response.defer(ephemeral=True)
        try:
            target_channel = self.bot_ref.get_channel(int(self.p_channel.value.strip()))
            cfg = CONFIG_CALL
            embed = discord.Embed(title=self.p_title.value, description=self.p_desc.value, color=cfg["cor"])
            if self.p_image.value: embed.set_image(url=self.p_image.value)
            embed.set_footer(text=RODAPE_TEXTO, icon_url=RODAPE_ICONE)
            view = EventCallView(self.bot_ref) if self.panel_type == "BF" else GeneralCallView(self.bot_ref)
            await target_channel.send(embed=embed, view=view)
            await interaction.followup.send(f"âœ… Enviado!", ephemeral=True)
        except Exception as e: await interaction.followup.send(f"âŒ Erro: {e}", ephemeral=True)

class SetupPanelView(discord.ui.View):
    def __init__(self, bot_ref):
        super().__init__(timeout=None)
        self.bot_ref = bot_ref
        
@discord.ui.button(label="Config Painel BF", style=discord.ButtonStyle.danger)
async def bf(self, interaction: discord.Interaction, button):
    await interaction.response.send_message("Painel BF configurado.", ephemeral=True)

@discord.ui.button(label="Config Painel Geral", style=discord.ButtonStyle.secondary)
async def geral(self, interaction: discord.Interaction, button):
    await interaction.response.send_message("Painel Geral configurado.", ephemeral=True)
    
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.active_calls = {} 
        self.user_calls = {}

    async def setup_hook(self):
        self.add_view(EventCallView(self))
        self.add_view(GeneralCallView(self))
        await self.tree.sync()
        print(f"âœ… Online!")

bot = MyBot()

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel and before.channel.id in bot.active_calls:
        if len(before.channel.members) == 0:
            await asyncio.sleep(5)
            if len(before.channel.members) == 0:
                try:
                    owner_id = bot.active_calls.pop(before.channel.id, None)
                    if owner_id: bot.user_calls.pop(owner_id, None)
                    await before.channel.delete()
                except: pass

@bot.tree.command(name="env_panel", description="Setup")
async def env_panel(interaction: discord.Interaction):
    cargo = interaction.guild.get_role(ID_CARGO_PERMISSAO)
    if cargo not in interaction.user.roles:
        return await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)

    await interaction.response.send_message("⚙️ Setup:", view=SetupPanelView(bot), ephemeral=True)

import os
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
