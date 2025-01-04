from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
from app import keep_alive
import os
from dotenv import load_dotenv

load_dotenv()

# Replace with your bot's API key and channel ID
API_KEY = os.getenv('API_KEY')
CHANNEL_ID = os.getenv('CHANNEL_ID')  # Replace with your channel's ID
BOT_CREATOR_ID = os.getenv('BOT_CREATOR_ID')  # Replace with your Telegram ID


# Function to check if the sender is the bot creator
def is_creator(update: Update) -> bool:
    return update.effective_user.id == BOT_CREATOR_ID

def get_gas_to_usdt(value=1):
    if value == 0:
        return 0.0  # Return 0 directly for input value 0
    
    # API Request
    try:
        url = "https://min-api.cryptocompare.com/data/price?fsym=NEO&tsyms=USDT"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues
        data = response.json()
        usdt_val = data.get('USDT')  # Safely get 'USDT' value
        if usdt_val is None:
            return "Error: 'USDT' key not found in API response."
        # Calculate equivalent USDT balance
        usdt_balance = float(value) * usdt_val
        # Format the output for readability
        return round(usdt_balance, 6)  # Rounded to 6 decimal places
    except requests.exceptions.RequestException as e:
        return f"API Request Error: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

# Function to send periodic updates to the channel
async def send_update(context: ContextTypes.DEFAULT_TYPE) -> None:
    # Example message, replace with real data or dynamic content
    gas_value = 1  # Replace with the actual value you want to convert
    usdt_balance = round(get_gas_to_usdt(gas_value), 2)
    message = f"$ {usdt_balance}"
    await context.bot.send_message(chat_id=CHANNEL_ID, text=message)

# Command to start sending updates
async def start_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_creator(update):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    await update.message.reply_text("Starting periodic updates to the channel.")
    await send_update(context)
    context.job_queue.run_repeating(send_update, interval=60, first=0)

# Command to stop sending updates
async def stop_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_creator(update):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    await update.message.reply_text("Stopping periodic updates to the channel.")
    context.job_queue.stop()

# Command to get your Telegram ID
async def get_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Your Telegram ID is: {update.effective_user.id}")

# Main function to set up the bot
def main():
    # Create the application
    application = Application.builder().token(API_KEY).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_updates))
    application.add_handler(CommandHandler("stop", stop_updates))
    # application.add_handler(CommandHandler("get_my_id", get_my_id))

    # Run the bot
    print("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    keep_alive()
    main()
