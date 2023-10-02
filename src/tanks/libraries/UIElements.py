import discord

import src.tanks.libraries.jsonManager as jsonManager
import src.tanks.libraries.commands as commands


class PlayerCardRotatorButtons(discord.ui.View):
    def __init__(self, client, *, timeout=180):
        super().__init__(timeout=timeout)
        self.client = client

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.red, emoji="⬅️")
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = jsonManager.read_games_json()
        message = interaction.response._parent.message
        client = self.client
        new_embed = None
        if message.channel.type == discord.ChannelType.private:
            is_in_games = jsonManager.is_player_in_game(message, interaction.response._parent.user.id)
            is_in_multiple_games = jsonManager.is_player_in_multiple_games(message,
                                                                           interaction.response._parent.user.id)
            if is_in_games and not is_in_multiple_games:
                guild_id, channel_id = jsonManager.get_player_server_channel_single(
                    message, interaction.response._parent.user.id)
                new_embed = await commands.flip_through_player_stats_card(message, data, -1, client, guild_id,
                                                                          channel_id)
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
            is_in_games = jsonManager.is_player_in_game(message, interaction.response._parent.user.id)
            is_in_multiple_games = jsonManager.is_player_in_multiple_games(
                message, interaction.response._parent.user.id)
            if is_in_games and not is_in_multiple_games:
                guild_id, channel_id = jsonManager.get_player_server_channel_single(
                    message, interaction.response._parent.user.id)
                new_embed = await commands.flip_through_player_stats_card(message, data, 1, client, guild_id,
                                                                          channel_id)
        else:
            new_embed = await commands.flip_through_player_stats_card(message, data, 1, client)
        if new_embed is not None:
            await interaction.response.edit_message(view=self, embed=new_embed)
        else:
            await interaction.response.edit_message(view=self)
