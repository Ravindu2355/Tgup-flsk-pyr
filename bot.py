from pyrogram import Client, filters, types
from flask import Flask, request, jsonify
import asyncio

# Initialize the Pyrogram client
app = Client("my_bot", api_id="YOUR_API_ID", api_hash="YOUR_API_HASH", bot_token="YOUR_BOT_TOKEN")

# Initialize the Flask app
flask_app = Flask(__name__)

# Function to upload a video from a URL to Telegram
async def upload_from_url(client: Client, chat_id:str, url: str,message):
    try:
        # Check if the command contains a URL argument
        if len(message.text.split()) < 2:
            await message.reply("Please provide a URL!")
            return

        # Extract the URL from the command
        url = message.text.split()[1]
        reply_msg = await message.reply("Starting download...")
        progress_s="Download starting...."
        # Start downloading the file
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))  # Get the total file size
        filename = url.split("/")[-1]  # Extract the filename from the URL
        if '?' in filename:
            filename = filename.split("?")[0]
        downloaded_size = 0
        tr_s = 0
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    percent = (downloaded_size / total_size) * 100
                    # Update progress approximately every 2%
                    #if total_size > 0 and downloaded_size % (total_size // 50) == 0:
                    if total_size > 0 and percent >= tr_s:
                        tr_s = tr_s + 2
                        progress_i = int(20 * downloaded_size / total_size)
                        progress='[' + '✅️' * progress_i + '❌️' * (20 - progress_i) + ']'
                        await reply_msg.edit_text(f"Downloading: {progress} {percent:.2f}%")
                        #progress_s=f"downloading...\n{progress}\n{percent:.2f}%"
                        print(percent)
        await reply_msg.edit_text("Download complete. Generating thumbnail...")
        thumb_path='thumb.jpg'
        with VideoFileClip(filename) as video:
              frame = video.get_frame(3.0)
              img = Image.fromarray(frame)
              img.save(thumb_path, "JPEG")
        await reply_msg.edit("Thumbnail generated. Uploading to Telegram...")
        start_time=time.time()
        await client.send_video(
            chat_id=message.chat.id,
            video=filename,
            caption=f'Uploaded: {filename}',
            thumb=thumb_path,
            supports_streaming=True,  # Ensure the video is streamable
            progress=progress_for_pyrogram,
            progress_args=(
                "uploading!",
                 reply_msg,
                 start_time
           )
        )
        
        # Clean up the local files after uploading
        os.remove(filename)
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)
        progress_s="free"
        await reply_msg.edit_text("Upload complete!")

    except Exception as e:
        # Handle any errors and notify the user
        await message.reply(f"An error occurred: {str(e)}")
        

# Telegram bot handler for messages with URLs
@app.on_message(filters.private & ~filters.via_bot & filters.regex(pattern=".*http.*"))
async def handle_message(client, message: types.Message):
    video_url = message.text  # Assuming the whole text is the video URL
    chat_id = message.chat.id
    await upload_from_url(client, chat_id=chat_id, url=video_url,message)
    
# Flask route to handle upload requests
@flask_app.route('/upload', methods=['GET'])
def upload_video():
    chat_id = request.args.get('chat_id')
    video_url = request.args.get('video_url')

    if not chat_id or not video_url:
        return jsonify({"error": "Both 'chat_id' and 'video_url' parameters are required"}), 400

    async def run_upload():
        async with app:
            await upload_from_url(app, chat_id=chat_id, video_url=video_url)

    # Run the async function in the event loop
    asyncio.run(run_upload())

    return jsonify({"message": "Video upload started!"})

# Main entry point to run both Flask app and Pyrogram client
if __name__ == '__main__':
    # Start Pyrogram client in a separate thread to allow Flask to run concurrently
    app.start()

    # Run Flask app (use a different port if needed)
    flask_app.run(port=8000)

    # Stop the Pyrogram client when the Flask app is stopped
    app.stop()
