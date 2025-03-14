import discord
from discord import app_commands
from discord.ext import commands
import logging
from datetime import datetime
from utils.database import db
from models import Guild, GuildSettings
from utils.embeds import create_embed, create_error_embed
from utils.permissions import has_bot_manager_role

logger = logging.getLogger(__name__)

class ApplicationModal(discord.ui.Modal, title='Server Application'):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.TextInput(
            label='Name',
            placeholder='Your name',
            custom_id='name',
            style=discord.TextStyle.short,
            required=True,
            max_length=50
        ))
        self.add_item(discord.ui.TextInput(
            label='Age',
            placeholder='Your age',
            custom_id='age',
            style=discord.TextStyle.short,
            required=True,
            max_length=3
        ))
        self.add_item(discord.ui.TextInput(
            label='Why do you want to join?',
            placeholder='Tell us why you want to join our server...',
            custom_id='reason',
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        ))
        self.add_item(discord.ui.TextInput(
            label='What can you contribute?',
            placeholder='What skills or contributions can you bring to our community?',
            custom_id='contribution',
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        ))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Get the application channel from database
            session = db.get_session()
            guild = session.query(Guild).filter_by(guild_id=str(interaction.guild_id)).first()
            if not guild or not guild.settings or not guild.settings.application_channel_id:
                await interaction.response.send_message(
                    embed=create_error_embed(
                        "Error",
                        "Application channel not set. Please ask an admin to set it up."
                    ),
                    ephemeral=True
                )
                return

            # Get the channel
            channel = interaction.guild.get_channel(int(guild.settings.application_channel_id))
            if not channel:
                await interaction.response.send_message(
                    embed=create_error_embed(
                        "Error",
                        "Application channel not found. Please contact an admin."
                    ),
                    ephemeral=True
                )
                return

            # Create and send application embed
            embed = discord.Embed(
                title="New Application",
                description=f"Application from {interaction.user.mention}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Name", value=self.children[0].value, inline=True)
            embed.add_field(name="Age", value=self.children[1].value, inline=True)
            embed.add_field(name="Why they want to join", value=self.children[2].value, inline=False)
            embed.add_field(name="Potential contributions", value=self.children[3].value, inline=False)
            embed.set_footer(text=f"User ID: {interaction.user.id}")

            await channel.send(embed=embed)
            await interaction.response.send_message(
                embed=create_embed(
                    "Application Submitted",
                    "Your application has been submitted successfully! The staff team will review it soon.",
                    discord.Color.green()
                ),
                ephemeral=True
            )
            logger.info(f'Application submitted by {interaction.user} in {interaction.guild.name}')
        except Exception as e:
            logger.error(f'Error processing application: {str(e)}')
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Error",
                    "An error occurred while submitting your application. Please try again later."
                ),
                ephemeral=True
            )
        finally:
            session.close()

class Applications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="apply", description="Submit a server application")
    async def apply(self, interaction: discord.Interaction):
        """Open the application form"""
        try:
            modal = ApplicationModal()
            await interaction.response.send_modal(modal)
            logger.info(f'{interaction.user} opened application form')
        except Exception as e:
            logger.error(f'Error opening application form: {str(e)}')
            await interaction.response.send_message(
                embed=create_error_embed(
                    "Error",
                    "An error occurred while opening the application form."
                ),
                ephemeral=True
            )

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @has_bot_manager_role(require_full_perms=True)
    async def set_application_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel where applications will be sent"""
        try:
            session = db.get_session()
            guild = session.query(Guild).filter_by(guild_id=str(ctx.guild.id)).first()
            
            if not guild:
                guild = Guild(guild_id=str(ctx.guild.id))
                session.add(guild)
                session.commit()
                
            if not guild.settings:
                guild.settings = GuildSettings()
                
            guild.settings.application_channel_id = str(channel.id)
            session.commit()
            
            await ctx.send(
                embed=create_embed(
                    "Application Channel Set",
                    f"Applications will now be sent to {channel.mention}",
                    discord.Color.green()
                )
            )
            logger.info(f'{ctx.author} set application channel to {channel.name}')
        except Exception as e:
            logger.error(f'Error setting application channel: {str(e)}')
            await ctx.send(
                embed=create_error_embed(
                    "Error",
                    "An error occurred while setting the application channel."
                )
            )
        finally:
            session.close()

async def setup(bot):
    await bot.add_cog(Applications(bot))
