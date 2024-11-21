from pyrogram import Client, filters, types
import asyncio, os, time, requests, math, psutil
from moviepy.editor import VideoFileClip
from display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from PIL import Image
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from task_manager import read_tasks, write_task
from cookie import r_cookies, w_cookies, clear_cookies
from threading import Thread
#from dl_m3u8 import download_m3u8_segments
# Function to process a task (this could be expanded to do anything)

flask_app = Flask(__name__)
CORS(flask_app)

@flask_app.route('/')
def site1_home():
    return "Welcome to Site 1 this can help for uper"

sizelimit=2147483648

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

def get_file_name_from_response(response):
    # Check if Content-Disposition header is present
    content_disposition = response.headers.get('Content-Disposition')
    if content_disposition:
        # Extract the filename from the Content-Disposition header
        filename_part = content_disposition.split('filename=')[-1]
        filename = filename_part.strip(' "')
        return filename
    
    # Fallback to extracting the file name from the URL
    return f"video_{str(time.time())}.mp4"

# Function to upload a video from a URL to Telegram
async def upload_from_url(client: Client, chat_id:str, url: str, n_caption=None):
    global progress_s
    reply_msg = await app.send_message(chat_id=chat_id,text="Processing!....")
    progress_s="Processing...!"
    try:
        if len(url) < 2:
            await reply_msg.edit_text("Please provide a URL!")
            progress_s="free"
            return
        await reply_msg.edit_text("Starting download...")
        progress_s="Download starting...."
        cookies = r_cookies()
        if not cookies:
            response = requests.get(url, cookies=cookies, stream=True)
        else:
            response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))  # Get the total file size
        if total_size >= sizelimit:
            await reply_msg.edit_text("That file was bigger than telegram size limitations for me🥲")
            return
        filename = url.split("/")[-1]  # Extract the filename from the URL
        if '?' in filename:
            filename = filename.split("?")[0]
        if "." not in filename:
            filename = get_file_name_from_response(response)
        m_caption = f'Uploaded: {filename}'
        if n_caption is not None:
            m_caption = n_caption
        downloaded_size = 0
        tr_s = ''
        start_t=time.time()
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    percent = (downloaded_size / total_size) * 100
                    now_t=time.time()
                    diffr=now_t-start_t
                    progress_s=f"Downloading... {percent}% of {humanbytes(total_size)}"
                    #if total_size > 0 and percent // 10 > tr_s:
                    if round(diffr % 10.00) == 0 or downloaded_size == total_size:
                       speed = downloaded_size / diffr
                       elapsed_time = round(diffr) * 1000
                       time_to_completion = round((total_size - downloaded_size) / speed) * 1000
                       estimated_total_time = elapsed_time + time_to_completion
                       elapsed_time = TimeFormatter(milliseconds=elapsed_time)
                       estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
                       progress_i = int(20 * downloaded_size / total_size)
                       progress = '[' + '✅️' * math.floor(progress_i) + '❌️' * math.floor((20 - progress_i)) + ']'
                       tmp = "{0} of {1}\nSpeed: {2}/s\nETA: {3}\n".format(
                          humanbytes(downloaded_size),
                          humanbytes(total_size),
                          humanbytes(speed),
                          # elapsed_time if elapsed_time != '' else "0 s",
                          estimated_total_time if estimated_total_time != '' else "0 s"
                       )
                       nn_s = f"Downloading: {progress}\n\nP:{percent:.2f}%\n{tmp}"
                       if nn_s != tr_s:  #avoiding same message sending err......
                           tr_s = nn_s
                           await reply_msg.edit_text(nn_s)
        await reply_msg.edit_text("Download complete. Generating thumbnail...")
        progress_s="Download complete. Generating thumbnail..."
        thumb_path='thumb.jpg'
        duration = 0
        with VideoFileClip(filename) as video:
              duration = int(video.duration)
              frame = video.get_frame(3.0)
              img = Image.fromarray(frame)
              img.save(thumb_path, "JPEG")
        await reply_msg.edit(f"Thumbnail generated.\nduration detected as {duration} Uploading to Telegram...")
        progress_s=f"Thumbnail generated.\nduration detected as {duration} Uploading to Telegram..."
        start_time=time.time()
        s_v = await app.send_video(
               chat_id = int(chat_id),
               video = filename,
               duration=duration,
               caption=m_caption,
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
            chat_id=int(M_CHAT),
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
        progress_s=f"An error occurred: {str(e)}"
        print(e)
        
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

@app.on_message(filters.private & filters.command("ping"))
async def c_pin(client,message:types.Message):
    start_time = time.time()  # Record start time
    reply_msg = await message.reply("🔰Ping checking...🔰")
    end_time = time.time()  # Record end time after sending
    latency = (end_time - start_time) * 1000  # Convert to milliseconds
    await reply_msg.edit_text(f"Ping: {latency:.2f} ms")

@app.on_message(filters.private & filters.command("disc"))
async def c_disc(client,message:types.Message):
    disk_usage = psutil.disk_usage('/')
    total_space = disk_usage.total / (1024 ** 3)  # Convert to GB
    used_space = disk_usage.used / (1024 ** 3)    # Convert to GB
    free_space = disk_usage.free / (1024 ** 3)    # Convert to GB
    await message.reply(
        f"Disk Space:\n"
        f"Total: {total_space:.2f} GB\n"
        f"Used: {used_space:.2f} GB\n"
        f"Free: {free_space:.2f} GB"
    )
        
@flask_app.route('/makefree')
async def pr_free():
    global progress_s
    if progress_s != "free" and "error" in progress_s:
        progress_s = "free"
        return jsonify({"s":1,"message":"success!"})
    else:
        return jsonify({"s":0,"message": "Not Errored!"})
        

@flask_app.route('/progress')
def s_pro():
    return jsonify({"s":1,"progress": progress_s,"message":"success!"})

def run_upload_t(chat_id, video_url,n_caption):
    asyncio.run(upload_from_url(app, chat_id=chat_id, url=video_url, n_caption=n_caption))

@flask_app.route('/upload', methods=['GET'])
def upload_video():
    chat_id = int(request.args.get('chatid'))
    video_url = request.args.get('url')
    n_caption = request.args.get('cap')
    if not chat_id or not video_url:
        return jsonify({"s":0,"message": "No parameter found!"})
    if not n_caption:
        n_caption = None
    if progress_s != "free":
        return jsonify({"s":0,"message": "Sorry bot is busy right now try again later!"})
    try:
        upload_thread = Thread(target=run_upload_t, args=(chat_id, video_url, n_caption))
        upload_thread.start()
        return jsonify({"s":1,"message": "Video add to Uploading!","resd":f"chat_id: {chat_id} & url: {video_url}"})
    except Exception as e:
        return jsonify({"s":0,"message": f"Err on run: {e}","resd":f"chat_id: {chat_id} & url: {video_url}"})
# Main entry point to run both Flask app and Pyrogram client
    # Start Pyrogram client in a separate thread to allow Flask to run concurrentl
#if __name__ == "__main__":
def run_flask():
    flask_app.run(host='0.0.0.0', port=5000)

flask_thread = Thread(target=run_flask)
flask_thread.start()

app.run()
    # Stop the Pyrogram client when the Flask app is stopped
    #app.stop()
