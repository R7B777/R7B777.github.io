import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.database import db
from utils.embeds import create_warning_embed, create_error_embed, create_success_embed
from models import Warning, Guild
from datetime import datetime

logger = logging.getLogger(__name__)

class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """Warn a member using slash command"""
        try:
            # Get or create guild in database
            session = db.get_session()
            guild = session.query(Guild).filter_by(guild_id=str(interaction.guild_id)).first()
            if not guild:
                guild = Guild(guild_id=str(interaction.guild_id))
                session.add(guild)
                session.commit()

            # Create warning
            warning = Warning(
                guild_id=guild.id,
                user_id=str(member.id),
                moderator_id=str(interaction.user.id),
                reason=reason
            )
            session.add(warning)
            session.commit()

            # Get warning count
            warning_count = session.query(Warning).filter_by(
                guild_id=guild.id,
                user_id=str(member.id)
            ).count()

            # Create and send embed
            embed = create_warning_embed(member, reason, interaction.user, warning_count)
            await interaction.response.send_message(embed=embed)
            
            # DM the warned user
            try:
                dm_embed = create_error_embed(
                    "You have been warned",
                    f"You received a warning in {interaction.guild.name}\nReason: {reason or 'No reason provided'}"
                )
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                logger.warning(f"Could not send DM to {member}")

            logger.info(f'{interaction.user} warned {member} for reason: {reason}')
        except Exception as e:
            logger.error(f'Error warning member: {str(e)}')
            await interaction.response.send_message(
