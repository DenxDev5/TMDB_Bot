import logging
import requests
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction

# --- CONFIGURATION (from environment variables) ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
# ---------------------------------------------------

TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_movie_poster(movie_name: str) -> str | None:
    """Searches for a movie on TMDB and returns the URL of its poster."""
    search_url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": movie_name
    }
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return f"{TMDB_IMAGE_BASE_URL}{poster_path}"
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
    except (KeyError, IndexError):
        logger.warning(f"No valid results found for movie: {movie_name}")

    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "Hello! 👋 Send me the name of any movie, and I will find its poster for you."
    )


async def send_poster(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles user messages, finds the poster, and sends it."""
    movie_name = update.message.text
    logger.info(f"User '{update.effective_user.name}' requested poster for: {movie_name}")
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)

    poster_url = get_movie_poster(movie_name)

    if poster_url:
        await update.message.reply_photo(
            photo=poster_url,
            caption=f"Here's the poster for '{movie_name}'."
        )
    else:
        await update.message.reply_text(
            f"Sorry, I couldn't find a poster for '{movie_name}'. Please check the spelling and try again."
        )


def main() -> None:
    """Starts the Telegram bot and waits for messages."""
    if not TELEGRAM_BOT_TOKEN or not TMDB_API_KEY:
        logger.error("FATAL: TELEGRAM_BOT_TOKEN or TMDB_API_KEY not set in environment variables.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_poster))

    logger.info("Bot is starting up...")
    application.run_polling()


if __name__ == "__main__":
    main()
