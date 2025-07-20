import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "REPLACE_WITH_YOUR_TELEGRAM_BOT_TOKEN"
TMDB_API_KEY = "REPLACE_WITH_YOUR_TMDB_API_KEY"
# --- END CONFIGURATION ---

TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_movie_poster(movie_name: str) -> str | None:
    search_url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": movie_name}
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
    await update.message.reply_text(
        "Hello! 👋 Send me the name of any movie, and I will find its poster for you."
    )


async def send_poster(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    if "REPLACE_WITH_YOUR_TELEGRAM_BOT_TOKEN" in TELEGRAM_BOT_TOKEN or "REPLACE_WITH_YOUR_TMDB_API_KEY" in TMDB_API_KEY:
        logger.error("FATAL: Please replace TELEGRAM_BOT_TOKEN and TMDB_API_KEY with real values.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_poster))

    logger.info("Bot is starting up...")
    application.run_polling()


if __name__ == "__main__":
    main()