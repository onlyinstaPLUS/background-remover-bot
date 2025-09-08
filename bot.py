import logging
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)

# 🔑 Tokens
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")

# ✅ Required channel(s) (now supports 3 or more)
FORCE_JOIN_CHANNELS = ["@plusbotz","@EarnMoneyTips_Official","@Budget_Deals_Bazaar"]

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- Helper: Check if user is in required channels ---
async def is_user_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    for channel in FORCE_JOIN_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            logger.error(f"Channel check failed for {channel}: {e}")
            return False
    return True


# --- Force join message ---
async def send_force_join_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    # Dynamically create buttons for all channels
    for idx, channel in enumerate(FORCE_JOIN_CHANNELS, start=1):
        keyboard.append([InlineKeyboardButton(f"📢 Join Channel {idx}", url=f"https://t.me/{channel[1:]}")])

    # Add Try Again button
    keyboard.append([InlineKeyboardButton("🔄 Try Again", callback_data="try_again")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "⚠️ You must join our channel(s) before using this bot.\n\n"
        "✅ Join the channel(s) below and then click *Try Again*.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# --- Callback for "Try Again" ---
async def try_again_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Check membership again
    if await is_user_member(update, context):
        await query.edit_message_text("✅ You are now a member! Send your image again.")
    else:
        await query.edit_message_text("⚠️ You still need to join the channel(s). Please try again.")
        await send_force_join_message(update, context)


# --- Start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! Send me an image and I will remove its background.\n"
        "Use /help to learn more."
    )


# --- Help command ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Just send me any photo and I’ll remove its background using remove.bg API.\n\n"
        "⚠️ Note: You must join our channels to use this bot."
    )


# --- Handle image messages ---
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Process 1: Check membership
    if not await is_user_member(update, context):
        await send_force_join_message(update, context)
        return

    try:
        # Process 2: Continue if user is in channel
        processing_msg = await update.message.reply_text("⏳ Processing your image, please wait...")

        # Get the file
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_path = await file.download_to_drive("input.png")

        # Call remove.bg API
        with open(file_path, "rb") as image_file:
            response = requests.post(
                "https://api.remove.bg/v1.0/removebg",
                files={"image_file": image_file},
                data={"size": "auto"},
                headers={"X-Api-Key": REMOVE_BG_API_KEY},
            )

        if response.status_code == 200:
            output_file = "no_bg.png"
            with open(output_file, "wb") as out:
                out.write(response.content)

            await processing_msg.delete()
            await update.message.reply_photo(photo=open(output_file, "rb"))
        else:
            await processing_msg.edit_text(
                f"⚠️ Failed to remove background. Error: {response.text}"
            )

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again.")


# --- Main ---
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Callbacks
    application.add_handler(CallbackQueryHandler(try_again_callback, pattern="try_again"))

    # Images
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    application.run_polling()


if __name__ == "__main__":
    main()
