from pyrogram import Client, filters, types
import asyncio, os, time, requests, math
from moviepy.editor import VideoFileClip
from display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from PIL import Image
import json
from task_manager import read_tasks, write_task
from cookie import r_cookies, w_cookies, clear_cookies
# Function to process a task (this could be expanded to do anything)


API_ID = os.getenv('apiid')
API_HASH = os.getenv('apihash')
BOT_TOKEN = os.getenv('tk')
M_CHAT = int(os.getenv('mchat'))
AUTH_U = os.getenv('auth')

progress_s="free"

# Ensure all required environment variables are set
if not all([API_ID, API_HASH, BOT_TOKEN,M_CHAT]):
    raise ValueError("API_ID, API_HASH, M_CHAT and BOT_TOKEN environment variables must be set.")

# Initialize the Pyrogram client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


#nearest even
def mcp(num):
    return int((num + 1) // 2) * 10
    
# Function to upload a video from a URL to Telegram
async def upload_from_url(client: Client, chat_id:str, url: str):
    reply_msg = await app.send_message(chat_id=chat_id,text="Processing!....")
    try:
        if len(url) < 2:
            await reply_msg.edit_text("Please provide a URL!")
            return
        # Extract the URL from the command
        #url = message.text.split()[1]
        await reply_msg.edit_text("Starting download...")
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
                    if total_size > 0 and percent // 10 > tr_s:
                       tr_s = int(percent // 10)  # Store the latest 10% interval
                       progress_i = int(20 * downloaded_size / total_size)
                       progress = '[' + '✅️' * progress_i + '❌️' * (20 - progress_i) + ']'
                       await reply_msg.edit_text(f"Downloading: {progress} {percent:.2f}%")
                
        await reply_msg.edit_text("Download complete. Generating thumbnail...")
        thumb_path='thumb.jpg'
        with VideoFileClip(filename) as video:
              frame = video.get_frame(3.0)
              img = Image.fromarray(frame)
              img.save(thumb_path, "JPEG")
        await reply_msg.edit("Thumbnail generated. Uploading to Telegram...")
        start_time=time.time()
        s_v = await app.send_video(
               chat_id = chat_id,
               video = filename,
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
        fid=s_v.video.file_id
        try:
            await app.send_video(
            chat_id=M_CHAT,
            video=fid,
            caption=f"**Uploaded via RvXBot**"
            )
        except Exception as e:
            pass
        
        # Clean up the local files after uploading 
        os.remove(filename)
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)
        progress_s="free"
        await reply_msg.delete()

    except Exception as e:
        # Handle any errors and notify the user
        await reply_msg.edit_text(f"An error occurred: {str(e)}")
        
@app.on_message(filters.private & filters.regex(pattern=".*http.*"))
async def handle_message(client, message: types.Message):
    if str(message.chat.id) in AUTH_U:
        video_url = message.text  # Assuming the whole text is the video URL
        chat_id = message.chat.id
        await upload_from_url(client, chat_id=chat_id, url=video_url)
    else:
        await message.delete()

@app.on_message(filters.private & filters.command("setc"))
async def set_c(client,message:types.Message):
    try:
        st = message.text.split(" ")[0]
        if st == "" or not st:
            message.reply(f"Not Found cookies!...")
            return
        re = w_cookies(st);
        await message.reply(f"cookies settuped!\n{re}")
    except Exception as e:
        await message.reply(f"An Err {e}")

@app.on_message(filters.private & filters.command("rem_c"))
async def set_c(client,message:types.Message):
    try:
        st = message.text.split(" ")[0]
        if st == "" or not st:
            await message.reply(f"Not Found cookies!...")
            return
        re = clear_cookies(st);
        await message.reply(f"cookie cleared!\n{re}")
    except Exception as e:
        await message.reply(f"An Err {e}")

        

def process_task(task):
    chat_id = task["chat_id"]
    url = task["url"]
    # Example task processing: Send a request to the provided URL
    try:
        async def run_upload():
          async with app:
            await upload_from_url(app, chat_id=chat_id, url=video_url)

    # Run the async function in the event loop
        asyncio.run(run_upload())
    except requests.RequestException as e:
        print(f"Error processing task for chat_id {chat_id}: {e}")

# Automated function to listen for new tasks and process them
def listen_for_tasks():
    processed_task_ids = set()  # To track which tasks have already been processed
    while True:
        tasks = read_tasks()  # Get the current tasks
        for task in tasks:
            if task["chat_id"] not in processed_task_ids:
                print(f"Processing task for chat_id {task['chat_id']}...")
                process_task(task)
                processed_task_ids.add(task["chat_id"])  # Mark the task as processed
        # Sleep for a short interval (e.g., 5 seconds) before checking for new tasks again
        time.sleep(5)



# Main entry point to run both Flask app and Pyrogram client
    # Start Pyrogram client in a separate thread to allow Flask to run concurrentl
app.run()
listen_for_tasks()

    
    # Stop the Pyrogram client when the Flask app is stopped
    #app.stop()
