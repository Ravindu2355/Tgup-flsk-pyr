import os, time
import requests
from urllib.parse import urljoin
from display_progress import humanbytes, TimeFormatter


async def download_m3u8_segments(msg, m3u8_url, output_path="output.mp4"):
  # Step 1: Download and parse the .m3u8 file
    await msg.edit_text("m3u8 parser running...")
    try:
        response = requests.get(m3u8_url)
        response.raise_for_status()
        m3u8_content = response.text
    except requests.RequestException as e:
        print(f"Error downloading .m3u8 file: {e}")
        await msg.edit_text(f"Err on dl: {e}")
        return None

    # Step 2: Extract the segment URLs from the .m3u8 file
    segment_urls = []
    lines = m3u8_content.splitlines()
    for line in lines:
        if line.endswith(".ts"):  # Typical segment file extension
            segment_url = urljoin(m3u8_url, line)
            segment_urls.append(segment_url)

    # Step 3: Get the total size of all segments (for progress tracking)
    total_size = 0
    for segment_url in segment_urls:
        segment_response = requests.head(segment_url)  # GET header info to check size
        if segment_response.status_code == 200:
            total_size += int(segment_response.headers.get('Content-Length', 0))
    await msg.edit_text("m3u8 dl setuped...\nstaring download...")
    # Step 4: Download all video segments and save to a temporary file
    temp_filename = "temp_video.ts"
    downloaded_size = 0  # Track the downloaded size
    start_time=time.time()
    with open(temp_filename, "wb") as temp_file:
        for i, segment_url in enumerate(segment_urls, 1):
            try:
                segment_response = requests.get(segment_url, stream=True)
                segment_response.raise_for_status()

                # Write the segment to the temporary file and update progress
                segment_size = int(segment_response.headers.get('Content-Length', 0))
                for chunk in segment_response.iter_content(chunk_size=1024):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded_size += len(chunk)
              now=time.time()
              diffr=now-start_time
              progress_percentage = (downloaded_size / total_size) * 100
              prog=f"Downloading segment {i}/{len(segment_urls)} - {progress_percentage:.2f}% complete"
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
                       nn_s = f"Downloading: {progress_percentage}\n\nP:{percent:.2f}%\n{tmp}"
                       if nn_s != tr_s:  #avoiding same message sending err......
                           tr_s = nn_s
                           await msg.edit_text(nn_s)
            except requests.RequestException as e:
                print(f"Error downloading segment {segment_url}: {e}")
                await msg.edit_text(f"Err on dl segments: {e}")
                return None

    # Step 5: Rename the temporary file to the desired output name
    os.rename(temp_filename, output_path)
    print(f"\nDownload complete: {output_path}")
    return output_path


# Example usage
#download_m3u8_segments(m3u8_url, save_path)
