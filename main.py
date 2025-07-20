import os
import logging
import requests
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
# ----------------------

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_movie_poster(movie_name: str) -> str | None:
    """Searches for a movie on TMDB and returns the URL of its poster."""
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": movie_name}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return f"{TMDB_IMAGE_BASE_URL}{poster_path}"
    except requests.exceptions.RequestException as e:
        logger.error(f"TMDB API Error: {e}")
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! 👋 Send me any movie name and I’ll fetch its poster for you."
    )


async def send_poster(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    movie_name = update.message.text
    logger.info(f"User asked for: {movie_name}")

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)

    poster_url = get_movie_poster(movie_name)

    if poster_url:
        await update.message.reply_photo(
            photo=poster_url,
            caption=f"Here's the poster for '{movie_name}'."
        )
    else:
        await update.message.reply_text(
            f"Sorry, I couldn't find a poster for '{movie_name}'. Please check the name and try again."
        )


def main() -> None:
    if not TELEGRAM_BOT_TOKEN or not TMDB_API_KEY:
        logger.error("Environment variables TELEGRAM_BOT_TOKEN or TMDB_API_KEY not set.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_poster))

    logger.info("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
