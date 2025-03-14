import discord
from discord.ext import commands
import random
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player != interaction.user:
            await interaction.response.send_message('It is not your turn!', ephemeral=True)
            return

        if interaction.user not in (view.player1, view.player2):
            await interaction.response.send_message('You are not part of this game!', ephemeral=True)
            return

        # Place the mark
        if view.current_player == view.player1:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            view.board[self.y][self.x] = view.X
            view.current_player = view.player2
        else:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            view.board[self.y][self.x] = view.O
            view.current_player = view.player1

        self.disabled = True
        
        # Check for winner
        winner = view.check_winner()
        if winner is not None:
            if winner == view.X:
                content = f'Game Over! {view.player1.mention} won!'
            elif winner == view.O:
                content = f'Game Over! {view.player2.mention} won!'
            else:
                content = "Game Over! It's a tie!"

            for child in view.children:
                child.disabled = True
            view.stop()
        else:
            content = f"It's {view.current_player.mention}'s turn!"

        await interaction.response.edit_message(content=content, view=view)

class TicTacToe(discord.ui.View):
    X = -1
    O = 1
    Tie = 2

    def __init__(self, player1: discord.Member, player2: discord.Member):
        super().__init__()
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.board = [[0, 0, 0] for _ in range(3)]
        
        # Add the buttons to the view
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_winner(self) -> int:
        # Check rows
        for row in self.board:
            value = sum(row)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check columns
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # Check if board is full
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games: Dict[int, TicTacToe] = {}

    @commands.command(name='flip', aliases=['coin'])
    async def flip_coin(self, ctx):
        """Flip a coin - returns heads or tails"""
        result = random.choice(['Heads 🪙', 'Tails 🪙'])
        await ctx.send(f'The coin shows: **{result}**')
        logger.info(f'{ctx.author} flipped a coin, got {result}')

    @commands.command(name='tictactoe', aliases=['ttt'])
    async def tic_tac_toe(self, ctx, opponent: discord.Member):
        """Start a game of Tic Tac Toe with another player"""
        if opponent.bot:
            await ctx.send("You can't play against bots!")
            return
        if opponent == ctx.author:
            await ctx.send("You can't play against yourself!")
            return

        # Check if either player is in an active game
        if ctx.channel.id in self.active_games:
            await ctx.send("There's already a game in progress in this channel!")
            return

        view = TicTacToe(ctx.author, opponent)
        self.active_games[ctx.channel.id] = view
        
        await ctx.send(
            f'Tic Tac Toe: {ctx.author.mention} vs {opponent.mention}\n'
            f"It's {ctx.author.mention}'s turn!",
            view=view
        )
        logger.info(f'{ctx.author} started a tic-tac-toe game with {opponent}')

        # Wait for the game to finish and clean up
        await view.wait()
        if ctx.channel.id in self.active_games:
            del self.active_games[ctx.channel.id]

async def setup(bot):
    await bot.add_cog(Games(bot))
