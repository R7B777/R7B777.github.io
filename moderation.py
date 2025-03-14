import discord
from discord.ext import commands
import logging
from datetime import timedelta
from utils.permissions import has_bot_manager_role

logger = logging.getLogger(__name__)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @has_bot_manager_role(require_full_perms=True)  # Only BotManager 1 can use this
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick a member from the server"""
        try:
            await member.kick(reason=reason)
            await ctx.send(f'{member.name} has been kicked. Reason: {reason or "No reason provided"}')
            logger.info(f'{ctx.author} kicked {member} for reason: {reason}')
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick this member!")
        except Exception as e:
            logger.error(f'Error kicking member: {e}')
            await ctx.send("An error occurred while trying to kick the member.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @has_bot_manager_role(require_full_perms=True)  # Only BotManager 1 can use this
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban a member from the server"""
        try:
            await member.ban(reason=reason)
            await ctx.send(f'{member.name} has been banned. Reason: {reason or "No reason provided"}')
            logger.info(f'{ctx.author} banned {member} for reason: {reason}')
        except discord.Forbidden:
            await ctx.send("I don't have permission to ban this member!")
        except Exception as e:
            logger.error(f'Error banning member: {e}')
            await ctx.send("An error occurred while trying to ban the member.")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    @has_bot_manager_role()  # Both BotManager roles can use this
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason=None):
        """Timeout a member for specified minutes"""
        try:
            duration = timedelta(minutes=minutes)
            await member.timeout(duration, reason=reason)
            await ctx.send(f'{member.name} has been timed out for {minutes} minutes. Reason: {reason or "No reason provided"}')
            logger.info(f'{ctx.author} timed out {member} for {minutes} minutes. Reason: {reason}')
        except discord.Forbidden:
            await ctx.send("I don't have permission to timeout this member!")
        except Exception as e:
            logger.error(f'Error timing out member: {e}')
            await ctx.send("An error occurred while trying to timeout the member.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
