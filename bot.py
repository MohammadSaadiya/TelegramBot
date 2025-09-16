import os
import random
from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, Defaults
from telegram.ext import MessageHandler, filters

#  Config 
TZ = ZoneInfo("Asia/Jerusalem")
MATCH_DAY = 0 
MATCH_TIMES = [
    time(13, 0, tzinfo=TZ),
    time(14, 0, tzinfo=TZ),
    time(15, 0, tzinfo=TZ),
    time(16, 0, tzinfo=TZ),
    time(17, 0, tzinfo=TZ),
]


GROUP_CHAT_ID = -4822583297

RESET_DAY = 0  # Sunday
RESET_TIME = time(0, 26, tzinfo=TZ)  

# State
participants = []       # list of user IDs (as strings)
names = {}              # userID -> full name
Is_approvesd = []  
BringBall = []      
is_open = False         # True means list is open
last_chat_id = None     # last chat that spoke to the bot (not required for reset)

#  Helpers 
def get_players_list() -> str:
    if not is_open:
        return "🛛 The list is currently closed."
    if not participants:
        return "👥 No players yet."
    lines = []
    for i, uid in enumerate(participants, start=1):
        name = names.get(uid, "Unknown")
        if uid in Is_approvesd:
            if uid in BringBall:
                lines.append(f"{i}. {name} ✅ ball emoji")
            else:
                lines.append(f"{i}. {name} ✅")
        else:
            lines.append(f"{i}. {name}")
    return "👥 Players:\n" + "\n".join(lines)

async def reject_if_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """If the command is sent in the known group chat, nudge user to DM and return True (reject)."""
    if update.effective_chat and update.effective_chat.id == GROUP_CHAT_ID:
        mention = update.effective_user.mention_html()
        bot_username = context.bot.username
        await update.message.reply_html(
            f"{mention} please message me in a private chat 👇 "
            f"<a href='https://t.me/{bot_username}'>click here</a>",
            disable_web_page_preview=True,
        )
        return True
    return False

#  Commands 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id
    last_chat_id = update.effective_chat.id
    # Show chat id (as you had)
    await update.message.reply_text(last_chat_id)
    await update.message.reply_text("Hey! I’m your bot and I’m alive 🤖")

async def print_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id
    last_chat_id = update.effective_chat.id
    if await reject_if_group(update, context): 
        return
    await update.message.reply_text(get_players_list())

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_open, last_chat_id
    last_chat_id = update.effective_chat.id
    if await reject_if_group(update, context): 
        return
    if is_open:
        await update.message.reply_text("ℹ️ The list is already open.")
        return
    is_open = True
    participants.clear()
    names.clear()
    await update.message.reply_text("✅ The list is OPEN! Use /add to join.")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id
    last_chat_id = update.effective_chat.id
    if await reject_if_group(update, context): 
        return
    if not is_open:
        await update.message.reply_text("🛛 The list is currently closed.")
        return
    user = update.effective_user
    uid = str(user.id)
    if uid not in participants:
        participants.append(uid)
        names[uid] = user.full_name
        await update.message.reply_text("You have been added to the list!")
    else:
        await update.message.reply_text("You are already in the list!")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id
    last_chat_id = update.effective_chat.id
    if await reject_if_group(update, context): 
        return
    if not is_open:
        await update.message.reply_text("🛛 The list is currently closed.")
        return
    uid = str(update.effective_user.id)
    if uid in participants:
        participants.remove(uid)
        names.pop(uid, None)
        if uid in Is_approvesd : 
            Is_approvesd.remove(uid)
        if uid in BringBall :
            BringBall.remove(uid)
        await update.message.reply_text("You have been removed from the list!")
    else:
        await update.message.reply_text("You are not in the list!")

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id
    last_chat_id = update.effective_chat.id
    if await reject_if_group(update, context): 
        return
    if not is_open:
        await update.message.reply_text("🛛 The list is currently closed.")
        return
    uid = str(update.effective_user.id)
    if uid in participants:
        if uid in Is_approvesd:
            await update.message.reply_text("You have already approved.")
            return
        else:
            Is_approvesd.append(uid)
        await update.message.reply_text("You have approved to go to the game!")
    else:
        await update.message.reply_text("You are not in the list!")

async def Ball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id
    last_chat_id = update.effective_chat.id
    if await reject_if_group(update, context): 
        return
    if not is_open:
        await update.message.reply_text("🛛 The list is currently closed.")
        return
    uid = str(update.effective_user.id)
    if uid in participants:
        if uid in BringBall:
            await update.message.reply_text("Youve already brought the ball")
            return
        else:
            BringBall.append(uid)
        await update.message.reply_text("You have approved to bring the ball to the game!")
    else:
        await update.message.reply_text("You are not in the list!")

async def shuffle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_chat_id
    last_chat_id = update.effective_chat.id
    if await reject_if_group(update, context): 
        return
    if not is_open:
        await update.message.reply_text("🛛 The list is currently closed.")
        return
    if len(participants) < 3:
        await update.message.reply_text("Not enough participants to shuffle into 3 teams.")
        return
    random.shuffle(participants)
    teams = [[], [], []]
    for idx, uid in enumerate(participants):
        teams[idx % 3].append(names.get(uid, "Unknown"))
    msg = "Teams:\n"
    for i, team in enumerate(teams, start=1):
        msg += f"\nTeam {i}:\n" + "\n".join(f"- {name}" for name in team)
    await update.message.reply_text(msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 *Available Commands:*\n\n"
        "/start - Show bot is alive & display your chat ID\n"
        "/create - Open a new player list (clears old one)\n"
        "/add - Join the current list\n"
        "/remove - Leave the list\n"
        "/print - Show the current list of players\n"
        "/approve - Mark yourself as attending the game\n"
        "/Ball - Volunteer to bring the ball\n"
        "/shuffle - Randomly split players into 3 teams\n"
        "/help - Show this help message\n"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Unknown command. Use /help to see the available commands."
    )
# ===== Job Callback =====
async def reset_week(context: ContextTypes.DEFAULT_TYPE):
    global is_open
    participants.clear()
    names.clear()
    is_open = False
    Is_approvesd.clear()
    BringBall.clear()
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text="🧹 Weekly reset done! List cleared and CLOSED."
    )
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text="🔔 Attention: The weekly reset has occurred. Please use /create to open a new list!"
    )

async def post_match_list(context: ContextTypes.DEFAULT_TYPE):
    # Optional: a header to make it obvious in the group
    header = "📣 Match-day check-in — current list:\n"
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=header + get_players_list()
    )
# ===== Main =====
def main():
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN missing. Put it in .env like BOT_TOKEN=123:ABC...")

    app = (
        Application.builder()
        .token(token)
        .defaults(Defaults(parse_mode=ParseMode.HTML))
        .build()
    )

    # --- Schedule the weekly reset at startup (so it runs even if nobody sends /start) ---
    app.job_queue.run_daily(
        reset_week,
        time=RESET_TIME,
        days=(RESET_DAY,),
        name="weekly_reset",
        chat_id=GROUP_CHAT_ID
    )
    print(f"[Scheduler] weekly_reset set for day={RESET_DAY} at {RESET_TIME} ({TZ}) to chat {GROUP_CHAT_ID}")
    for t in MATCH_TIMES:
        job_name = f"match_list_{t.hour:02d}00"
        app.job_queue.run_daily(
            post_match_list,
            time=t,
            days=(MATCH_DAY,),
            name=job_name,
            chat_id=GROUP_CHAT_ID
        )
    

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("print", print_list))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("shuffle", shuffle))
    app.add_handler(CommandHandler("Ball", Ball))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.run_polling()

if __name__ == "__main__":
    main()
