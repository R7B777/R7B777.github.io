import discord
from discord.ext import commands
from utils.checks import has_admin_permissions
import logging

logger = logging.getLogger(__name__)

class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @has_admin_permissions()
    async def create_channel(self, ctx, channel_name: str, channel_type: str = "text"):
        """Creates a new channel"""
        try:
            if channel_type.lower() == "text":
                channel = await ctx.guild.create_text_channel(channel_name)
            elif channel_type.lower() == "voice":
                channel = await ctx.guild.create_voice_channel(channel_name)
            else:
                await ctx.send("Invalid channel type. Use 'text' or 'voice'.")
                return
            
            await ctx.send(f"Channel {channel.name} created successfully!")
            logger.info(f"Channel {channel.name} created by {ctx.author.name}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to create channels!")

    @commands.command()
    @has_admin_permissions()
    async def create_role(self, ctx, role_name: str, color: discord.Color = discord.Color.default()):
        """Creates a new role"""
        try:
            role = await ctx.guild.create_role(name=role_name, color=color)
            await ctx.send(f"Role {role.name} created successfully!")
            logger.info(f"Role {role.name} created by {ctx.author.name}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to create roles!")

    @commands.command()
    @has_admin_permissions()
    async def assign_role(self, ctx, member: discord.Member, role: discord.Role):
        """Assigns a role to a member"""
        try:
            await member.add_roles(role)
            await ctx.send(f"Role {role.name} assigned to {member.name}")
            logger.info(f"Role {role.name} assigned to {member.name} by {ctx.author.name}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to assign roles!")

async def setup(bot):
    await bot.add_cog(Management(bot))
