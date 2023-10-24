import discord

import src.tanks.libraries.jsonManager as jsonManager
import src.tanks.libraries.commands as commands


class PlayerCardRotatorButtons(discord.ui.View):
    def __init__(self, client, guild_id, channel_id, *, timeout=180):
        super().__init__(timeout=timeout)
        self.client = client
        self.guild_id = guild_id
        self.channel_id = channel_id

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.red, emoji="⬅️")
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = jsonManager.read_games_json()
        message = interaction.response._parent.message
        client = self.client
        new_embed = None
        if message.channel.type == discord.ChannelType.private:
            new_embed = await commands.flip_through_player_stats_card(message, data, -1, client, self.guild_id,
                                                                      self.channel_id)
        else:
            new_embed = await commands.flip_through_player_stats_card(message, data, -1, client)
        if new_embed is not None:
            await interaction.response.edit_message(view=self, embed=new_embed)
        else:
            await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green, emoji="➡️")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = jsonManager.read_games_json()
        message = interaction.response._parent.message
        client = self.client
        new_embed = None
        if message.channel.type == discord.ChannelType.private:
            new_embed = await commands.flip_through_player_stats_card(message, data, 1, client, self.guild_id,
                                                                      self.channel_id)
        else:
            new_embed = await commands.flip_through_player_stats_card(message, data, 1, client)
        if new_embed is not None:
            await interaction.response.edit_message(view=self, embed=new_embed)
        else:
            await interaction.response.edit_message(view=self)


class SelectDMGame(discord.ui.Select):
    def __init__(self, message, client):
        servers = jsonManager.get_player_server_channels(message)
        options = []
        for idx, server in enumerate(servers):
            guild = client.get_guild(int(server[0]))
            channel = discord.utils.get(client.get_all_channels(), id=int(server[1]))
            options.append(discord.SelectOption(label=f'{(int(idx)+1)}. {str(guild)}', description=f'#{str(channel)}'))
        self.has_clicked = False
        self.message = message
        self.client = client
        super().__init__(placeholder="Select a current game", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if not self.has_clicked:
            await interaction.response.edit_message(delete_after=0)
            server_id = (int(self.values[0].split()[0][:-1])-1)
            server = jsonManager.get_player_server_channels(self.message)[server_id]
            await commands.dm_multiple_commands(self.client, self.message, server[0], server[1])
            if self.values[0] == "Option 3":
                pass
            self.has_clicked = True
        else:
            await interaction.response.defer(thinking=False)


class SelectDMGameView(discord.ui.View):
    def __init__(self, message, client, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(SelectDMGame(message, client))
