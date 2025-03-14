rom discord.ext import commands
import discord

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = CustomHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Bot Commands", color=discord.Color.blue())
        
        for cog, commands in mapping.items():
            if cog and commands:
                command_list = [f"`{c.name}`" for c in commands if not c.hidden]
                if command_list:
                    cog_name = cog.qualified_name
                    embed.add_field(name=cog_name, value=", ".join(command_list), inline=False)

        embed.set_footer(text="Use !help <command> for more details about a command")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=f"Command: {command.name}", color=discord.Color.blue())
        embed.add_field(name="Description", value=command.help or "No description available")
        embed.add_field(name="Usage", value=f"`!{command.name} {command.signature}`")
        await self.get_destination().send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
