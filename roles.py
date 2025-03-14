import discord
from discord.ext import commands
import logging
from utils.permissions import has_bot_manager_role

logger = logging.getLogger(__name__)

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def create_role(self, ctx, *, role_name: str):
        """Create a new role"""
        try:
            role = await ctx.guild.create_role(name=role_name)
            await ctx.send(f'Role {role.name} has been created!')
            logger.info(f'{ctx.author} created role {role_name}')
        except discord.Forbidden:
            await ctx.send("I don't have permission to create roles!")
        except Exception as e:
            logger.error(f'Error creating role: {e}')
            await ctx.send("An error occurred while creating the role.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @has_bot_manager_role()  # Allows both BotManager roles, but checks hierarchy for BotManager 2
    async def assign_role(self, ctx, member: discord.Member, role: discord.Role):
        """Assign a role to a member"""
        try:
            # Additional hierarchy check for the bot
            if role >= ctx.guild.me.top_role:
                await ctx.send("I cannot assign roles higher than or equal to my highest role!")
                return

            await member.add_roles(role)
            await ctx.send(f'Role {role.name} has been assigned to {member.name}!')
            logger.info(f'{ctx.author} assigned role {role.name} to {member.name}')
        except discord.Forbidden:
            await ctx.send("I don't have permission to assign roles!")
        except Exception as e:
            logger.error(f'Error assigning role: {e}')
            await ctx.send("An error occurred while assigning the role.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @has_bot_manager_role()  # Allows both BotManager roles, but checks hierarchy for BotManager 2
    async def remove_role(self, ctx, member: discord.Member, role: discord.Role):
        """Remove a role from a member"""
        try:
            # Additional hierarchy check for the bot
            if role >= ctx.guild.me.top_role:
                await ctx.send("I cannot remove roles higher than or equal to my highest role!")
                return

            await member.remove_roles(role)
            await ctx.send(f'Role {role.name} has been removed from {member.name}!')
            logger.info(f'{ctx.author} removed role {role.name} from {member.name}')
        except discord.Forbidden:
            await ctx.send("I don't have permission to remove roles!")
        except Exception as e:
            logger.error(f'Error removing role: {e}')
            await ctx.send("An error occurred while removing the role.")

async def setup(bot):
    await bot.add_cog(Roles(bot))
