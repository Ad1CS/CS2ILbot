import discord
from discord.ext import commands
from discord.ui import Button, View, Select
import os

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ALLOWED_USER_IDS = [
    1446497991572717679, 1446498166525661244, 1456602743870590996,
    1446494647018061844, 1446498334951870586
]

def is_allowed_user():
    """Check if the user is in the allowed list."""
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.id in ALLOWED_USER_IDS:
            return True
        await interaction.response.send_message(
            "❌ You are not authorized to use this command.", ephemeral=True
        )
        return False
    return commands.check(predicate)


# Rules - exact text from server
RULES = [
    "חל איסור חמור לקלל",
    "אין לשלוח תמונות חושפניות",
    "אין לעשות ספאם / וויס צ'אנג' / איירפ",
    "אין להטריד גולש אחר בשרת – דבר זה יוביל אתכם לבאן",
    "אין להתחצף בצ'אט פרטי באופן שיפגע באנשים אחרים",
    "אין לשלוח אימוג'ים, גיפים או תמונות לא צנועות / חינמיות",
    "אין לפרסם קישורים – דבר זה יוביל אתכם לאזהרה ובמקרים חמורים לבאן",
    "אין לבחור מוניטין, אם תבחרו תקבלו כפל 2 מהזמן",
    "אין להטריל צוות סתם",
    "אין לפרסם קישורים אלה במקומות המיועדים",
    "אין לפרסם פרטים אישיים של גולש אחר",
    "יש לכבד כל גולש בשרת, לא משנה אם הוא מקלל אתכם – פנו לצוות",
    "אין לעשות טרולים בשרת – דבר זה יוביל לבאן זמני",
    "אין לעשות סקאם"
]

RULES_TITLE = "ברוכים הבאים לשרת סיאס הגדול בישראל"



class RoleSelectionView(View):
    def __init__(self):
        super().__init__(timeout=None)

        # Add role selection dropdown
        self.add_item(RoleSelect())


class RoleSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="עדכוני שרת",
                description="קבל עדכונים על השרתים",
                emoji="🖥️",
                value="1456714494414819472"
            ),
            discord.SelectOption(
                label="עדכוני סיאס",
                description="CS2 קבל התראות על עדכונים של ",
                emoji="🎮",
                value="1446503623021559909"
            )
        ]

        super().__init__(
            placeholder="בחר רולים שאתה רוצה לקבל...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="role_select"
        )

    async def callback(self, interaction: discord.Interaction):
        selected_role_id = int(self.values[0])
        role = interaction.guild.get_role(selected_role_id)

        if not role:
            await interaction.response.send_message(
                "❌ שגיאה: לא נמצא הרול. נא ליצור קשר עם המנהלים.",
                ephemeral=True
            )
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                f"✅ הרול **{role.name}** הוסר בהצלחה!",
                ephemeral=True
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"✅ קיבלת את הרול **{role.name}**!",
                ephemeral=True
            )


@bot.event
async def on_ready():
    print(f'{bot.user} מחובר ופועל!')
    print(f'Bot ID: {bot.user.id}')

    # Sync commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")


@bot.tree.command(name="rules", description="הצג את חוקי השרת")
@is_allowed_user()
async def rules(interaction: discord.Interaction):
    """Display server rules in a beautiful embed"""

    embed = discord.Embed(
        title="📜 חוקי שרת CS2IL",
        description=f"**{RULES_TITLE}**\n\n*אי ידיעת החוקים לא משחררת מאחריות*",
        color=discord.Color.from_rgb(255, 102, 0)  # CS2 Orange
    )

    # Add rules in chunks to avoid exceeding field value limit
    rules_chunks = []
    current_chunk = ""
    for i, rule in enumerate(RULES, 1):
        rule_line = f"**{i}.** {rule}\n\n"
        if len(current_chunk) + len(rule_line) > 1024:
            rules_chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += rule_line

    if current_chunk:
        rules_chunks.append(current_chunk)

    for i, chunk in enumerate(rules_chunks):
        embed.add_field(
            name=f"⚠️ חוקי השרת (חלק {i + 1})" if len(rules_chunks) > 1 else "⚠️ חוקי השרת",
            value=chunk,
            inline=False
        )


    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="roles", description="בחר רולים לעדכונים")
@is_allowed_user()
async def roles(interaction: discord.Interaction):
    """Display role selection menu"""

    embed = discord.Embed(
        title="🎭 בחירת רולים",
        description=(
            "**בחר את הרולים שאתה רוצה לקבל:**\n\n"
            "🖥️ **עדכוני שרת** - עדכונים על השרתים שלנו\n"
            "🎮 **עדכוני סיאס** - עדכונים על Counter-Strike 2\n\n"
            "*השתמש בתפריט למטה כדי לבחור*\n"
            "*לחץ שוב על רול כדי להסיר אותו*"
        ),
        color=discord.Color.blue()
    )

    embed.set_footer(text="ניתן לשנות את הרולים בכל עת")

    view = RoleSelectionView()
    await interaction.response.send_message(embed=embed, view=view)


@bot.tree.command(name="setup_rules", description="[ADMIN] הגדר הודעת חוקים קבועה בערוץ")
@is_allowed_user()
async def setup_rules(interaction: discord.Interaction, channel: discord.TextChannel = None):
    """Setup permanent rules message in a channel"""

    if channel is None:
        channel = interaction.channel

    embed = discord.Embed(
        title="📜 חוקי שרת CS2IL",
        description=(
            f"**{RULES_TITLE}**\n\n"
            "נא לקרוא בעיון את כל החוקים. אי ידיעת החוקים לא משחררת מאחריות.\n"
            "הפרת חוקים תוביל לאזהרות, השתקות או באן מהשרת.\n"
        ),
        color=discord.Color.from_rgb(255, 102, 0)
    )

    rules_chunks = []
    current_chunk = ""
    for i, rule in enumerate(RULES, 1):
        rule_line = f"**{i}.** {rule}\n\n"
        if len(current_chunk) + len(rule_line) > 1024:
            rules_chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += rule_line

    if current_chunk:
        rules_chunks.append(current_chunk)

    for i, chunk in enumerate(rules_chunks):
        embed.add_field(
            name=f"⚠️ חוקי השרת (חלק {i + 1})" if len(rules_chunks) > 1 else "⚠️ חוקי השרת",
            value=chunk,
            inline=False
        )

    embed.add_field(
        name="📌 חשוב לזכור",
        value=(
            "• כבד את כל חברי הקהילה\n"
            "• אל תשתף מידע אישי של אחרים\n"
            "• השתמש בערוצים המתאימים\n"
            "• צוות המנהלים כאן כדי לעזור 🛡️"
        ),
        inline=False
    )

    embed.set_footer(
        text="CS2IL Community • נוצר ב-2025",
        icon_url=interaction.guild.icon.url if interaction.guild.icon else None
    )

    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)

    await channel.send(embed=embed)
    await interaction.response.send_message(
        f"✅ הודעת החוקים נשלחה ל-{channel.mention}",
        ephemeral=True
    )


@bot.tree.command(name="setup_roles", description="[ADMIN] הגדר הודעת בחירת רולים קבועה")
@is_allowed_user()
async def setup_roles_permanent(interaction: discord.Interaction, channel: discord.TextChannel = None):
    """Setup permanent role selection message"""

    if channel is None:
        channel = interaction.channel

    embed = discord.Embed(
        title="🎭 בחירת רולים - CS2IL",
        description=(
            "**קבל עדכונים על מה שמעניין אותך!**\n\n"
            "השתמש בתפריט למטה כדי לבחור את הרולים שאתה רוצה:\n\n"
            "🖥️ **עדכוני שרת** - עדכונים על השרתים שלנו\n"
            "🎮 **עדכוני סיאס** - עדכונים על Counter-Strike 2\n\n"
            "*ניתן לשנות את הבחירה שלך בכל עת!*\n"
            "*לחץ שוב על רול כדי להסיר אותו*"
        ),
        color=discord.Color.blue()
    )

    embed.set_footer(text="לחץ על התפריט למטה כדי לבחור")

    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)

    view = RoleSelectionView()
    await channel.send(embed=embed, view=view)
    await interaction.response.send_message(
        f"✅ הודעת בחירת הרולים נשלחה ל-{channel.mention}",
        ephemeral=True
    )


@bot.event
async def on_member_join(member):
    """Welcome new members"""
    # Try to find welcome channel
    welcome_channel = discord.utils.get(member.guild.channels, name="welcome")
    if not welcome_channel:
        welcome_channel = discord.utils.get(member.guild.channels, name="general")

    if welcome_channel:
        embed = discord.Embed(
            title=f"ברוך הבא ל-CS2IL! 🎮",
            description=(
                f"היי {member.mention}!\n\n"
                f"ברוך הבא לקהילת CS2 הישראלית!\n"
                f"נא לקרוא את החוקים ולבחור רולים.\n\n"
                f"השתמש ב-`/rules` לצפייה בחוקים\n"
                f"השתמש ב-`/roles` לבחירת רולים\n\n"
                f"**תהנה ויאללה לשחק! 🔥**"
            ),
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await welcome_channel.send(embed=embed)



# Run the bot
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        print("⚠️ נא להגדיר את DISCORD_BOT_TOKEN במשתני הסביבה")
        print("להוצאת טוקן:")
        print("1. לך ל-https://discord.com/developers/applications")
        print("2. צור אפליקציה חדשה או בחר קיימת")
        print("3. לך ל-Bot בתפריט הצד")
        print("4. לחץ על 'Reset Token' והעתק את הטוקן")
    else:
        bot.run(TOKEN)