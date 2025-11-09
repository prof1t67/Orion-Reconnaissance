import discord
from discord.ext import commands
from discord import app_commands


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Prefix commands
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(
            f"Kicked {member.mention} for: {reason or 'No reason provided'}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(
            f"Banned {member.mention} for: {reason or 'No reason provided'}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"Unbanned {user.mention}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False)
        await member.add_roles(mute_role)
        await ctx.send(f"Muted {member.mention}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role:
            await member.remove_roles(mute_role)
            await ctx.send(f"Unmuted {member.mention}")
        else:
            await ctx.send("No 'Muted' role found.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def roleadd(self, ctx, member: discord.Member, role: discord.Role):
        await member.add_roles(role)
        await ctx.send(f"Added role {role.name} to {member.mention}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def rolerevoke(self, ctx, member: discord.Member,
                         role: discord.Role):
        await member.remove_roles(role)
        await ctx.send(f"Removed role {role.name} from {member.mention}")

    # Slash commands
    @app_commands.command(name="kick", description="Kick a member")
    async def kick_slash(self,
                         interaction: discord.Interaction,
                         member: discord.Member,
                         reason: str = "No reason provided"):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message(
                "You lack permission to kick members.", ephemeral=True)
            return
        await member.kick(reason=reason)
        await interaction.response.send_message(
            f"Kicked {member.mention} for: {reason}")

    @app_commands.command(name="ban", description="Ban a member")
    async def ban_slash(self,
                        interaction: discord.Interaction,
                        member: discord.Member,
                        reason: str = "No reason provided"):
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message(
                "You lack permission to ban members.", ephemeral=True)
            return
        await member.ban(reason=reason)
        await interaction.response.send_message(
            f"Banned {member.mention} for: {reason}")

    @app_commands.command(name="unban", description="Unban a user by ID")
    async def unban_slash(self, interaction: discord.Interaction,
                          user_id: str):
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message(
                "You lack permission to unban members.", ephemeral=True)
            return
        user = await self.bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"Unbanned {user.mention}")

    @app_commands.command(name="mute", description="Mute a member")
    async def mute_slash(self, interaction: discord.Interaction,
                         member: discord.Member):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "You lack permission to manage roles.", ephemeral=True)
            return
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await interaction.guild.create_role(name="Muted")
            for channel in interaction.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False)
        await member.add_roles(mute_role)
        await interaction.response.send_message(f"Muted {member.mention}")

    @app_commands.command(name="unmute", description="Unmute a member")
    async def unmute_slash(self, interaction: discord.Interaction,
                           member: discord.Member):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "You lack permission to manage roles.", ephemeral=True)
            return
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if mute_role:
            await member.remove_roles(mute_role)
            await interaction.response.send_message(f"Unmuted {member.mention}"
                                                    )
        else:
            await interaction.response.send_message("No 'Muted' role found.")

    @app_commands.command(name="roleadd", description="Add a role to a member")
    async def roleadd_slash(self, interaction: discord.Interaction,
                            member: discord.Member, role: discord.Role):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "You lack permission to manage roles.", ephemeral=True)
            return
        await member.add_roles(role)
        await interaction.response.send_message(
            f"Added role {role.name} to {member.mention}")

    @app_commands.command(name="rolerevoke",
                          description="Remove a role from a member")
    async def rolerevoke_slash(self, interaction: discord.Interaction,
                               member: discord.Member, role: discord.Role):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "You lack permission to manage roles.", ephemeral=True)
            return
        await member.remove_roles(role)
        await interaction.response.send_message(
            f"Removed role {role.name} from {member.mention}")

    async def cog_load(self):
        for guild in self.bot.guilds:
            try:
                self.bot.tree.add_command(self.kick_slash, guild=guild)
                self.bot.tree.add_command(self.ban_slash, guild=guild)
                self.bot.tree.add_command(self.unban_slash, guild=guild)
                self.bot.tree.add_command(self.mute_slash, guild=guild)
                self.bot.tree.add_command(self.unmute_slash, guild=guild)
                self.bot.tree.add_command(self.roleadd_slash, guild=guild)
                self.bot.tree.add_command(self.rolerevoke_slash, guild=guild)
            except Exception as e:
                print(f"Error loading moderation slash commands: {e}")
