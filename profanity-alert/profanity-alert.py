import discord
from discord.ext import commands
import re


class ProfanityAlert(commands.Cog):
    """
    Plugin to detect profanity in messages and send alerts to designated channels.
    - Staff profanity -> Alert to a specific channel
    - Customer profanity -> Ping role with blacklist permissions
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.api.get_plugin_partition(self)
        
        # Basic profanity list - you can expand this
        self.bad_words = [
            'fuck', 'shit', 'damn', 'ass', 'bitch', 'bastard',
            'crap', 'hell', 'piss', 'dick', 'cock', 'pussy',
            'whore', 'slut', 'fag', 'retard', 'nigger', 'cunt'
        ]
        
        # Compile regex pattern for better performance
        pattern = r'\b(' + '|'.join(map(re.escape, self.bad_words)) + r')\b'
        self.profanity_pattern = re.compile(pattern, re.IGNORECASE)

    async def get_config(self):
        """Fetch plugin config from database"""
        config = await self.db.find_one({'_id': 'config'})
        if config is None:
            # Default config
            config = {
                '_id': 'config',
                'staff_alert_channel': None,
                'customer_alert_channel': None,
                'blacklist_role': None,
                'staff_roles': []
            }
            await self.db.insert_one(config)
        return config

    def check_profanity(self, text):
        """Check if text contains profanity"""
        if not text:
            return None
        matches = self.profanity_pattern.findall(text)
        return matches if matches else None

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages and check for profanity"""
        if message.author.bot:
            return

        # Skip if not in a modmail thread
        if not hasattr(message.channel, 'recipient'):
            return

        config = await self.get_config()
        
        # Check for profanity in message
        bad_words_found = self.check_profanity(message.content)
        if not bad_words_found:
            return

        thread = message.channel
        is_staff = any(role.id in config['staff_roles'] for role in message.author.roles) if hasattr(message.author, 'roles') else False

        # Handle staff profanity
        if is_staff and config['staff_alert_channel']:
            alert_channel = self.bot.get_channel(int(config['staff_alert_channel']))
            if alert_channel:
                embed = discord.Embed(
                    title="⚠️ Staff Profanity Detected",
                    description=f"**Staff Member:** {message.author.mention} ({message.author.id})\n"
                                f"**Thread:** {thread.mention}\n"
                                f"**Words Detected:** {', '.join(set(bad_words_found))}\n"
                                f"**Message:** {message.content[:1000]}",
                    color=discord.Color.orange(),
                    timestamp=message.created_at
                )
                embed.set_footer(text=f"Staff ID: {message.author.id}")
                await alert_channel.send(embed=embed)

        # Handle customer profanity
        elif not is_staff and config['customer_alert_channel'] and config['blacklist_role']:
            alert_channel = self.bot.get_channel(int(config['customer_alert_channel']))
            blacklist_role = message.guild.get_role(int(config['blacklist_role']))
            
            if alert_channel and blacklist_role:
                embed = discord.Embed(
                    title="⚠️ Customer Profanity Detected",
                    description=f"**User:** {message.author.mention} ({message.author.id})\n"
                                f"**Thread:** {thread.mention}\n"
                                f"**Words Detected:** {', '.join(set(bad_words_found))}\n"
                                f"**Message:** {message.content[:1000]}",
                    color=discord.Color.red(),
                    timestamp=message.created_at
                )
                embed.set_footer(text=f"User ID: {message.author.id}")
                await alert_channel.send(
                    content=blacklist_role.mention,
                    embed=embed,
                    allowed_mentions=discord.AllowedMentions(roles=True)
                )

    @commands.group(name='profanityalert', aliases=['pa'], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def profanity_alert(self, ctx):
        """Manage profanity alert settings"""
        await ctx.send_help(ctx.command)

    @profanity_alert.command(name='staffchannel')
    @commands.has_permissions(administrator=True)
    async def set_staff_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the channel for staff profanity alerts"""
        config = await self.get_config()
        
        if channel is None:
            config['staff_alert_channel'] = None
            await self.db.update_one(
                {'_id': 'config'},
                {'$set': {'staff_alert_channel': None}}
            )
            await ctx.send("✅ Staff alert channel has been cleared.")
        else:
            config['staff_alert_channel'] = str(channel.id)
            await self.db.update_one(
                {'_id': 'config'},
                {'$set': {'staff_alert_channel': str(channel.id)}}
            )
            await ctx.send(f"✅ Staff profanity alerts will be sent to {channel.mention}")

    @profanity_alert.command(name='customerchannel')
    @commands.has_permissions(administrator=True)
    async def set_customer_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the channel for customer profanity alerts"""
        config = await self.get_config()
        
        if channel is None:
            config['customer_alert_channel'] = None
            await self.db.update_one(
                {'_id': 'config'},
                {'$set': {'customer_alert_channel': None}}
            )
            await ctx.send("✅ Customer alert channel has been cleared.")
        else:
            config['customer_alert_channel'] = str(channel.id)
            await self.db.update_one(
                {'_id': 'config'},
                {'$set': {'customer_alert_channel': str(channel.id)}}
            )
            await ctx.send(f"✅ Customer profanity alerts will be sent to {channel.mention}")

    @profanity_alert.command(name='blacklistrole')
    @commands.has_permissions(administrator=True)
    async def set_blacklist_role(self, ctx, role: discord.Role = None):
        """Set the role to ping when customers use profanity"""
        config = await self.get_config()
        
        if role is None:
            config['blacklist_role'] = None
            await self.db.update_one(
                {'_id': 'config'},
                {'$set': {'blacklist_role': None}}
            )
            await ctx.send("✅ Blacklist role has been cleared.")
        else:
            config['blacklist_role'] = str(role.id)
            await self.db.update_one(
                {'_id': 'config'},
                {'$set': {'blacklist_role': str(role.id)}}
            )
            await ctx.send(f"✅ {role.mention} will be pinged for customer profanity.")

    @profanity_alert.command(name='staffroles')
    @commands.has_permissions(administrator=True)
    async def set_staff_roles(self, ctx, *roles: discord.Role):
        """Set which roles are considered staff (separate multiple with spaces)"""
        config = await self.get_config()
        
        if not roles:
            config['staff_roles'] = []
            await self.db.update_one(
                {'_id': 'config'},
                {'$set': {'staff_roles': []}}
            )
            await ctx.send("✅ Staff roles list has been cleared.")
        else:
            role_ids = [str(role.id) for role in roles]
            config['staff_roles'] = role_ids
            await self.db.update_one(
                {'_id': 'config'},
                {'$set': {'staff_roles': role_ids}}
            )
            role_mentions = ', '.join(role.mention for role in roles)
            await ctx.send(f"✅ Staff roles set to: {role_mentions}")

    @profanity_alert.command(name='addword')
    @commands.has_permissions(administrator=True)
    async def add_word(self, ctx, word: str):
        """Add a word to the profanity filter"""
        word = word.lower().strip()
        if word not in self.bad_words:
            self.bad_words.append(word)
            # Recompile pattern
            pattern = r'\b(' + '|'.join(map(re.escape, self.bad_words)) + r')\b'
            self.profanity_pattern = re.compile(pattern, re.IGNORECASE)
            await ctx.send(f"✅ Added `{word}` to the profanity filter.")
        else:
            await ctx.send(f"⚠️ `{word}` is already in the filter.")

    @profanity_alert.command(name='removeword')
    @commands.has_permissions(administrator=True)
    async def remove_word(self, ctx, word: str):
        """Remove a word from the profanity filter"""
        word = word.lower().strip()
        if word in self.bad_words:
            self.bad_words.remove(word)
            # Recompile pattern
            pattern = r'\b(' + '|'.join(map(re.escape, self.bad_words)) + r')\b'
            self.profanity_pattern = re.compile(pattern, re.IGNORECASE)
            await ctx.send(f"✅ Removed `{word}` from the profanity filter.")
        else:
            await ctx.send(f"⚠️ `{word}` is not in the filter.")

    @profanity_alert.command(name='config', aliases=['settings'])
    @commands.has_permissions(administrator=True)
    async def show_config(self, ctx):
        """Show current profanity alert configuration"""
        config = await self.get_config()
        
        staff_channel = f"<#{config['staff_alert_channel']}>" if config['staff_alert_channel'] else "Not set"
        customer_channel = f"<#{config['customer_alert_channel']}>" if config['customer_alert_channel'] else "Not set"
        blacklist_role = f"<@&{config['blacklist_role']}>" if config['blacklist_role'] else "Not set"
        
        staff_roles = "Not set"
        if config['staff_roles']:
            staff_roles = ', '.join(f"<@&{role_id}>" for role_id in config['staff_roles'])
        
        embed = discord.Embed(
            title="Profanity Alert Configuration",
            color=discord.Color.blue()
        )
        embed.add_field(name="Staff Alert Channel", value=staff_channel, inline=False)
        embed.add_field(name="Customer Alert Channel", value=customer_channel, inline=False)
        embed.add_field(name="Blacklist Role", value=blacklist_role, inline=False)
        embed.add_field(name="Staff Roles", value=staff_roles, inline=False)
        embed.add_field(name="Words Tracked", value=f"{len(self.bad_words)} words", inline=False)
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ProfanityAlert(bot))
