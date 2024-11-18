from pyrogram import Client, filters, types
from flask import Flask, request, jsonify
import asyncio

# Initialize the Pyrogram client
app = Client("my_bot", api_id="YOUR_API_ID", api_hash="YOUR_API_HASH", bot_token="YOUR_BOT_TOKEN")

# Initialize the Flask app
flask_app = Flask(__name__)

# Function to upload a video from a URL to Telegram
async def upload_from_url(client: Client, chat_id: int, video_url: str, caption="Uploaded video"):
    try:
        await client.send_video(chat_id=chat_id, video=video_url, caption=caption)
        print("Video uploaded successfully!")
    except Exception as e:
        print(f"Failed to upload video: {e}")

# Telegram bot handler for messages with URLs
@app.on_message(filters.private & ~filters.via_bot & filters.regex(pattern=".*http.*"))
async def handle_message(client, message: types.Message):
    video_url = message.text  # Assuming the whole text is the video URL
    chat_id = message.chat.id
    await upload_from_url(client, chat_id=chat_id, video_url=video_url)
    await message.reply("Your video upload has been initiated!")

# Flask route to handle upload requests
@flask_app.route('/upload', methods=['GET'])
def upload_video():
    chat_id = request.args.get('chat_id')
    video_url = request.args.get('video_url')

    if not chat_id or not video_url:
        return jsonify({"error": "Both 'chat_id' and 'video_url' parameters are required"}), 400

    async def run_upload():
        async with app:
            await upload_from_url(app, chat_id=int(chat_id), video_url=video_url)

    # Run the async function in the event loop
    asyncio.run(run_upload())

    return jsonify({"message": "Video upload started!"})

# Main entry point to run both Flask app and Pyrogram client
if __name__ == '__main__':
    # Start Pyrogram client in a separate thread to allow Flask to run concurrently
    app.start()

    # Run Flask app (use a different port if needed)
    flask_app.run(port=5000, debug=True)

    # Stop the Pyrogram client when the Flask app is stopped
    app.stop()
