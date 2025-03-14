import discord
from discord.ext import commands
import logging
from utils.permissions import has_bot_manager_role
from utils.embeds import create_embed, create_error_embed

logger = logging.getLogger(__name__)

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @has_bot_manager_role()  # Both BotManager roles can use this
    async def say(self, ctx, channel: discord.TextChannel, *, message: str):
        """Make the bot say something in a specified channel"""
        try:
            await channel.send(message)
            await ctx.message.add_reaction('✅')
            logger.info(f'{ctx.author} used say command in {channel.name}')
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to send messages in that channel!")
        except Exception as e:
            logger.error(f'Error in say command: {str(e)}')
            await ctx.send("❌ An error occurred while sending the message.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @has_bot_manager_role(require_full_perms=True)  # Only BotManager 1 can use this
    async def embed(self, ctx, channel: discord.TextChannel, title: str, *, description: str):
        """Create and send an embed message
        Usage: !embed #channel "Title" Description text here"""
        try:
            # Create and send the embed
            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color.blue(),
            )
            embed.set_footer(text=f"Created by {ctx.author}")
            
            await channel.send(embed=embed)
            await ctx.message.add_reaction('✅')
            logger.info(f'{ctx.author} created an embed in {channel.name}')
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to send messages in that channel!")
        except Exception as e:
            logger.error(f'Error creating embed: {str(e)}')
            await ctx.send("❌ An error occurred while creating the embed.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @has_bot_manager_role(require_full_perms=True)  # Only BotManager 1 can use this
    async def embedcolor(self, ctx, channel: discord.TextChannel, color: str, title: str, *, description: str):
        """Create and send a colored embed message
        Usage: !embedcolor #channel blue "Title" Description text here
        Available colors: blue, red, green, gold, purple"""
        try:
            # Convert color string to discord.Color
            colors = {
                'blue': discord.Color.blue(),
                'red': discord.Color.red(),
                'green': discord.Color.green(),
                'gold': discord.Color.gold(),
                'purple': discord.Color.purple()
            }
            
            embed_color = colors.get(color.lower(), discord.Color.blue())
            
            # Create and send the embed
            embed = discord.Embed(
                title=title,
                description=description,
                color=embed_color,
            )
            embed.set_footer(text=f"Created by {ctx.author}")
            
            await channel.send(embed=embed)
            await ctx.message.add_reaction('✅')
            logger.info(f'{ctx.author} created a {color} embed in {channel.name}')
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to send messages in that channel!")
        except Exception as e:
            logger.error(f'Error creating colored embed: {str(e)}')
            await ctx.send("❌ An error occurred while creating the embed.")

async def setup(bot):
    await bot.add_cog(Utility(bot))
