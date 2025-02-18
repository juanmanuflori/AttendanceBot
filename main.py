import discord
import os
import random
import csv
from discord.ext import commands
from datetime import datetime


print("🚀 Starting bot...")  # This will appear in logs immediately

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is online: {bot.user}")


# Enable necessary intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store attendance
attendance_log = {}
attendance_active = False  # Flag to track if attendance is open
current_code = None  # Store the current generated code
attendance_event_name = "Attendance Event"  # Default name


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


# Step 1: Create a modal (pop-up form) for users to enter the code
class AttendanceModal(discord.ui.Modal, title="Enter Attendance Code"):
    code = discord.ui.TextInput(label="Enter your code",
                                style=discord.TextStyle.short,
                                required=True)

    async def on_submit(self, interaction: discord.Interaction):
        global attendance_active, current_code
        if not attendance_active:
            await interaction.response.send_message(
                "❌ Attendance has been closed!", ephemeral=True)
            return

        user_display_name = interaction.user.display_name  # Get the display name

        if self.code.value == current_code:
            attendance_log[user_display_name] = "✅ Present"
            await interaction.response.send_message(
                f"✅ {interaction.user.mention}, you have checked in successfully!",
                ephemeral=True)
        else:
            await interaction.response.send_message(
                "❌ Invalid code. Please try again.", ephemeral=True)


# Step 2: Start Attendance (Generate Random Code with Event Name)
@bot.command()
@commands.has_permissions(administrator=True)
async def StartAttendance(ctx, *, event_name: str = "Attendance Event"):
    """Starts attendance, names the event, and asks users to enter the code privately."""
    global attendance_active, current_code, attendance_log, attendance_event_name

    if attendance_active:
        await ctx.send(
            f"⚠️ **An attendance session is already running for `{attendance_event_name}`!**"
        )
        return

    attendance_active = True  # Enable attendance
    attendance_log.clear()  # Reset attendance log for each session
    attendance_event_name = event_name  # Set the event name
    current_code = str(random.randint(1000,
                                      9999))  # Generate a random 4-digit code

    # Try sending the code via DM
    try:
        await ctx.author.send(
            f"📢 **New Attendance Code for {attendance_event_name}:** `{current_code}` (Do not share this publicly!)"
        )
        await ctx.send(
            f"📢 **{attendance_event_name}** attendance has started! Click the button below to check in.",
            view=CheckInView())
        return  # Exit function if DM was successful
    except discord.Forbidden:
        await ctx.send(
            f"⚠️ {ctx.author.mention}, I couldn't DM you the code. Creating a private thread instead."
        )

    # If DM fails, create a private thread
    try:
        thread = await ctx.channel.create_thread(
            name=f"{attendance_event_name} Code",
            type=discord.ChannelType.private_thread)
        await thread.send(
            f"📢 **New Attendance Code for {attendance_event_name}:** `{current_code}` (Do not share this publicly!)"
        )
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to create private threads.")

    # Announce the start of attendance
    await ctx.send(
        f"📢 **{attendance_event_name}** attendance has started! Click the button below to check in.",
        view=CheckInView())


# Step 3: Stop Attendance (Auto Shows Attendance List)
@bot.command()
@commands.has_permissions(administrator=True)
async def StopAttendance(ctx):
    """Stops attendance, preventing further check-ins and showing the list."""
    global attendance_active

    if not attendance_active:
        await ctx.send("⚠️ **There is no active attendance session to stop.**")
        return

    attendance_active = False  # Disable attendance

    if not attendance_log:
        await ctx.send(
            f"📋 **{attendance_event_name} Attendance List:**\nNo one has checked in yet."
        )
    else:
        report = "\n".join(
            [f"👤 {user}: {status}" for user, status in attendance_log.items()])
        await ctx.send(
            f"📋 **{attendance_event_name} Attendance List:**\n{report}")

    await ctx.send("⛔ Attendance has been stopped. No more check-ins allowed.")


# Step 4: Create a Button for Users to Click
class CheckInView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Check-In", style=discord.ButtonStyle.primary)
    async def checkin_button(self, interaction: discord.Interaction,
                             button: discord.ui.Button):
        """Opens the private check-in modal when clicked."""
        if not attendance_active:
            await interaction.response.send_message(
                "❌ Attendance has been closed!", ephemeral=True)
            return
        await interaction.response.send_modal(AttendanceModal())


# Step 5: View Attendance List (Generates CSV)
@bot.command()
@commands.has_permissions(administrator=True)
async def ViewAttendance(ctx):
    """Allows an admin to download the attendance list as a CSV file."""
    if not attendance_active and not attendance_log:
        await ctx.send(
            "⚠️ **There is no active or recorded attendance session.**")
        return

    # Create CSV file
    filename = f"attendance_{attendance_event_name.replace(' ', '_')}.csv"
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["User", "Status", "Timestamp"])

        for user, status in attendance_log.items():
            writer.writerow(
                [user, status,
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

    # Send the CSV file to Discord
    await ctx.send(f"📋 **{attendance_event_name} Attendance List:**",
                   file=discord.File(filename))
import os
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 8080))  # Use Railway's default port
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run).start()

# Run bot
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)
