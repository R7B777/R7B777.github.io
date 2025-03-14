import discord
from discord.ext import commands
import logging
from utils.permissions import has_bot_manager_role

logger = logging.getLogger(__name__)

class Channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def setup_bot_role(self, ctx, role_number: int = 1):
        """Create the BotManager role if it doesn't exist"""
        try:
            # Validate role number
            if role_number not in [1, 2]:
                await ctx.send("❌ Role number must be either 1 or 2!")
                logger.warning(f"{ctx.author} attempted to create invalid BotManager role number: {role_number}")
                return

            role_name = f"BotManager {role_number}" if role_number > 1 else "BotManager"
            logger.info(f"Attempting to create {role_name} role in guild {ctx.guild.name}...")

            # Check if role already exists
            existing_role = discord.utils.get(ctx.guild.roles, name=role_name)
            if existing_role:
                await ctx.send(f"⚠️ {role_name} role already exists!")
                logger.info(f"{role_name} role already exists in guild {ctx.guild.name}")
                return

            # Verify bot's role hierarchy
            if not ctx.guild.me.guild_permissions.manage_roles:
                await ctx.send("❌ I don't have permission to manage roles!")
                logger.error(f"Bot lacks manage_roles permission in guild {ctx.guild.name}")
                return

            if ctx.guild.me.top_role.position <= 1:
                await ctx.send("❌ Please move my role higher in the hierarchy to manage roles!")
                logger.error(f"Bot's role position too low in guild {ctx.guild.name}")
                return

            # Create new role
            role = await ctx.guild.create_role(
                name=role_name,
                color=discord.Color.blue(),
                reason=f"Role {role_number} for managing bot commands",
                permissions=discord.Permissions(
                    manage_messages=True,
                    manage_channels=True,
                    manage_roles=True,
                    kick_members=True if role_number == 1 else False,
                    ban_members=True if role_number == 1 else False
                )
            )

            # Confirmation message
            await ctx.send(
                f"✅ Created {role.mention} role successfully!\n"
                f"This role has the following permissions:\n"
                f"• {'Full moderation access' if role_number == 1 else 'Basic moderation access'}\n"
                f"• Manage messages and channels\n"
                f"• Manage roles below its position\n\n"
                f"Assign this role to users who should manage bot features."
            )
            logger.info(f'{ctx.author} created {role_name} role successfully in guild {ctx.guild.name}')

        except discord.Forbidden:
            error_msg = f"Missing permissions to create {role_name} role"
            logger.error(f"{error_msg} in guild {ctx.guild.name}")
            await ctx.send(f"❌ {error_msg}!")
        except Exception as e:
            error_msg = f'Error creating {role_name} role: {str(e)}'
            logger.error(f"{error_msg} in guild {ctx.guild.name}")
            await ctx.send(f"❌ An error occurred while creating the role: {str(e)}")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @has_bot_manager_role(require_full_perms=True)  # Only BotManager 1 can use this
    async def set_permissions(self, ctx, channel: discord.TextChannel, role: discord.Role, *permissions):
        """Set channel permissions for a role
        Usage: !set_permissions #channel @role permission1=true permission2=false
        Available permissions: view, send, read_history, manage, attach_files"""
        try:
            # Create permission overwrite object
            overwrite = {}
            valid_permissions = {
                'view': 'view_channel',
                'send': 'send_messages',
                'read_history': 'read_message_history',
                'manage': 'manage_messages',
                'attach_files': 'attach_files'
            }

            for perm in permissions:
                try:
                    name, value = perm.split('=')
                    if name not in valid_permissions:
                        continue
                    overwrite[valid_permissions[name]] = value.lower() == 'true'
                except ValueError:
                    continue

            await channel.set_permissions(role, **overwrite)

            # Create permission summary
            perm_list = [f"{k}: {v}" for k, v in overwrite.items()]
            summary = "\n".join(perm_list)

            await ctx.send(f"✅ Updated permissions for {role.mention} in {channel.mention}:\n```\n{summary}\n```")
            logger.info(f'{ctx.author} updated permissions for {role.name} in channel {channel.name}')
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to modify channel permissions!")
        except Exception as e:
            logger.error(f'Error setting channel permissions: {str(e)}')
            await ctx.send("❌ An error occurred while setting permissions.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @has_bot_manager_role(require_full_perms=True)  # Only BotManager 1 can use this
    async def view_permissions(self, ctx, channel: discord.TextChannel, role: discord.Role):
        """View current channel permissions for a role"""
        try:
            perms = channel.permissions_for(role)

            # Create a formatted list of permissions
            permission_list = [
                f"View Channel: {perms.view_channel}",
                f"Send Messages: {perms.send_messages}",
                f"Read History: {perms.read_message_history}",
                f"Manage Messages: {perms.manage_messages}",
                f"Attach Files: {perms.attach_files}"
            ]

            formatted_perms = "\n".join(permission_list)
            await ctx.send(f"📋 Permissions for {role.mention} in {channel.mention}:\n```\n{formatted_perms}\n```")
            logger.info(f'{ctx.author} viewed permissions for {role.name} in channel {channel.name}')
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to view channel permissions!")
        except Exception as e:
            logger.error(f'Error viewing channel permissions: {str(e)}')
            await ctx.send("❌ An error occurred while viewing permissions.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @has_bot_manager_role()
    async def lock(self, ctx, channel: discord.TextChannel = None):
        """Lock a text channel"""
        channel = channel or ctx.channel
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            await ctx.send(f'🔒 Channel {channel.mention} has been locked.')
            logger.info(f'{ctx.author} locked channel {channel.name}')
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to lock this channel!")
        except Exception as e:
            logger.error(f'Error locking channel: {str(e)}')
            await ctx.send("❌ An error occurred while locking the channel.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @has_bot_manager_role()
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        """Unlock a text channel"""
        channel = channel or ctx.channel
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
            await ctx.send(f'🔓 Channel {channel.mention} has been unlocked.')
            logger.info(f'{ctx.author} unlocked channel {channel.name}')
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unlock this channel!")
        except Exception as e:
            logger.error(f'Error unlocking channel: {str(e)}')
            await ctx.send("❌ An error occurred while unlocking the channel.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def create_channel(self, ctx, channel_name: str, channel_type: str = "text"):
        """Create a new channel"""
        try:
            if channel_type.lower() == "text":
                channel = await ctx.guild.create_text_channel(channel_name)
            elif channel_type.lower() == "voice":
                channel = await ctx.guild.create_voice_channel(channel_name)
            else:
                await ctx.send("Invalid channel type. Use 'text' or 'voice'.")
                return

            await ctx.send(f'Channel {channel.mention} has been created!')
            logger.info(f'{ctx.author} created channel {channel_name} of type {channel_type}')
        except discord.Forbidden:
            await ctx.send("I don't have permission to create channels!")
        except Exception as e:
            logger.error(f'Error creating channel: {e}')
            await ctx.send("An error occurred while creating the channel.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def delete_channel(self, ctx, channel: discord.TextChannel):
        """Delete a channel"""
        try:
            await channel.delete()
            await ctx.send(f'Channel {channel.name} has been deleted!')
            logger.info(f'{ctx.author} deleted channel {channel.name}')
        except discord.Forbidden:
            await ctx.send("I don't have permission to delete this channel!")
        except Exception as e:
            logger.error(f'Error deleting channel: {e}')
            await ctx.send("An error occurred while deleting the channel.")


async def setup(bot):
    await bot.add_cog(Channels(bot))
