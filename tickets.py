import discord
from discord import app_commands
from discord.ext import commands
import logging
from datetime import datetime
from utils.permissions import has_bot_manager_role
from utils.embeds import create_embed, create_error_embed

logger = logging.getLogger(__name__)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            channel = interaction.channel
            if not channel.name.startswith('ticket-'):
                await interaction.response.send_message("This is not a ticket channel!", ephemeral=True)
                return

            await interaction.response.send_message("🔒 Closing ticket in 5 seconds...")
            await channel.send("Ticket closed by " + interaction.user.mention)
            await channel.edit(archived=True)
            logger.info(f'Ticket {channel.name} closed by {interaction.user}')
        except Exception as e:
            logger.error(f'Error closing ticket: {str(e)}')
            await interaction.response.send_message("❌ An error occurred while closing the ticket.", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_view = TicketView()
        bot.add_view(self.ticket_view)

    @app_commands.command(name="ticket", description="Create a support ticket")
    async def create_ticket(self, interaction: discord.Interaction, reason: str):
        """Create a support ticket"""
        try:
            # Get or create ticket category
            category = discord.utils.get(interaction.guild.categories, name="Tickets")
            if not category:
                await interaction.response.send_message(
                    "❌ Tickets category not found. Ask an admin to set it up using !setup_tickets",
                    ephemeral=True
                )
                return

            # Create ticket channel
            channel_name = f"ticket-{interaction.user.name.lower()}"
            existing_ticket = discord.utils.get(category.channels, name=channel_name)
            
            if existing_ticket:
                await interaction.response.send_message(
                    f"❌ You already have an open ticket: {existing_ticket.mention}",
                    ephemeral=True
                )
                return

            # Set up channel permissions
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }

            # Add permissions for BotManager roles
            for role in interaction.guild.roles:
                if role.name in ["BotManager", "BotManager 2"]:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            channel = await category.create_text_channel(
                name=channel_name,
                overwrites=overwrites
            )

            # Create ticket embed
            embed = discord.Embed(
                title="Support Ticket",
                description=f"Ticket created by {interaction.user.mention}\nReason: {reason}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f"User ID: {interaction.user.id}")

            await channel.send(embed=embed, view=self.ticket_view)
            await interaction.response.send_message(
                f"✅ Ticket created! Check {channel.mention}",
                ephemeral=True
            )
            logger.info(f'Ticket created by {interaction.user} for reason: {reason}')
        except Exception as e:
            logger.error(f'Error creating ticket: {str(e)}')
            await interaction.response.send_message(
                "❌ An error occurred while creating the ticket.",
                ephemeral=True
            )

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @has_bot_manager_role(require_full_perms=True)
    async def setup_tickets(self, ctx):
        """Set up the tickets category and permissions"""
        try:
            # Check if category exists
            category = discord.utils.get(ctx.guild.categories, name="Tickets")
            if category:
                await ctx.send("❌ Tickets category already exists!")
                return

            # Create category with proper permissions
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }

            # Add permissions for BotManager roles
            for role in ctx.guild.roles:
                if role.name in ["BotManager", "BotManager 2"]:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            category = await ctx.guild.create_category("Tickets", overwrites=overwrites)
            await ctx.send("✅ Tickets category created successfully!")
            logger.info(f'Tickets category created by {ctx.author}')
        except Exception as e:
            logger.error(f'Error setting up tickets: {str(e)}')
            await ctx.send("❌ An error occurred while setting up the ticket system.")

async def setup(bot):
    await bot.add_cog(Tickets(bot))
