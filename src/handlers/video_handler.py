from pyrogram import Client
from pyrogram.types import Message
from pyrogram.filters import video, private, user
from call_throttle import throttle

import os, shutil
import asyncio
from contextlib import suppress
from typing import List
import logging

from src.loader import bot
from src.config import Config


s = asyncio.Semaphore(1)
logger = logging.getLogger(__name__)


@throttle(calls=1, period=3)
async def progress_upload(current: float, total: float, m: Message, id):
    p = f"{current * 100 / total:.1f}%"
    print(p)
    with suppress(Exception):
        t = f"<b>↙️ Loading... ({p})</b>"
        try:
            await m.edit_text(t)
        except:
            ...


@throttle(calls=1, period=3)
async def progress_download(current: float, total: float, m: Message, id):
    p = f"{current * 100 / total:.1f}%"
    print(p)
    with suppress(Exception):
        t = f"<b>↗️ Sending... ({p})</b>"
        try:
            await m.edit_text(t)
        except:
            ...


def get_input_name(id) -> str:
    return os.path.join(Config.DIR_MEDIA, f"input_{id}.mp4")

def get_output_name(id) -> str:
    return os.path.join(Config.DIR_MEDIA, f"output_{id}.mp4")


async def reset_bitrate_video(
    file_size: int,
    bit_rate_v: int, bit_rate_a: int,
    id,
    fps: int = 30
) -> int:
    """Starts the ffmpeg process which converts the video
    
    :param int file_size:
    Byte count.
    
    :param int bit_rate_v:
    Final video-bitrate.
    
    :param int bit_rate_a:
    Final audio-bitrate.
    
    :param Any id:
    Unique part in file name.
    
    :param int fps:
    Final fps in video.
    
    :return: Process exit code.
    :rtype: int
    """
    file_size = int(file_size)
    bit_rate_v = int(bit_rate_v)
    bit_rate_a = int(bit_rate_a)
    fps = int(fps)
    
    FFMPEG_BIN = Config.FFMPEG_BIN or "C:\\ffmpeg-6.0-full_build-shared\\bin\\ffmpeg.exe"
    
    process = await asyncio.create_subprocess_exec(
        FFMPEG_BIN,
        *[
            "-y", 
            "-f", "mp4",
            "-i", get_input_name(id),
            
            "-r", f"{fps}",
            "-c:v", "libx264", "-b:v", f"{bit_rate_v}k",  # video
            "-c:a", "aac", "-b:a", f"{bit_rate_a}k",      # audio
            
            "-preset", "fast", "-f", "mp4",
            get_output_name(id)
        ],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    await process.wait()
    
    stdout, stderr = await process.communicate()
    out = stdout or stderr
    logger.info(out.decode())
    
    return process.returncode


def rm_all(folder: str, safe_files: List[str], filename_is_exist: str) -> bool:
    """Remove all files in directory
    
    :param str folder:
    Target folder.
    
    :param List[str] safe_files:
    List of files that will not be deleted.
    
    :param str filename_is_exist:
    Check if this file exists.
    
    :return: Does the transferred file exist?
    :rtype: bool
    """
    flag = False
    
    os.makedirs(Config.DIR_MEDIA, exist_ok=True)
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        
        if filename_is_exist == file_path:
            flag = True
            
        if file_path in safe_files:
            continue
        
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error('Failed to delete %s. Reason: %s' % (file_path, e))
    
    return flag


async def process_video(message: Message, m: Message):
    """ Video processing.\n
    File cleaning, uploading, processing and sending.
    
    :param Message message:
    Query context.
    
    :param Message m:
    Info context.
    
    :raises RPCError: In case of a Telegram RPC error.
    """
    with suppress(Exception):
        t = "<b>↙️ Loading...</b>"
        try:
            await m.edit_text(t)
        except:
            m = await message.reply(t, quote=True)
    
    id = message.video.file_unique_id
    
    exists = rm_all(
        Config.DIR_MEDIA,
        [get_input_name(id)],
        get_input_name(id)
    )

    if not exists:
        await message.download(
            file_name=get_input_name(id),
            progress=progress_download,
            progress_args=(m, id)
        )
    
    with suppress(Exception):
        t = "<b>🔄 Processing...</b>"
        try:
            await m.edit_text(t)
        except:
            m = await message.reply(t, quote=True)
    
    status_code = await reset_bitrate_video(
        file_size=message.video.file_size,
        bit_rate_v=Config.DEFAULT_BIT_RATE_V,
        bit_rate_a=Config.DEFAULT_BIT_RATE_A,
        fps=Config.DEFAULT_FPS,
        id=id
    )
    
    if status_code:
        await message.reply("<b>An error occurred (ffmpeg)</b>")
    
    with suppress(Exception):
        t = "<b>↗️ Sending...</b>"
        try:
            await m.edit_text(t)
        except:
            m = await message.reply(t, quote=True)
        
    await message.reply_video(
        video=get_output_name(id),
        caption=message.caption,
        progress=progress_upload,
        progress_args=(m, id)
    )
    
    with suppress(Exception):
        t = "<b>ℹ️ Success</b>"
        try:
            await m.edit_text(t)
        except:
            m = await message.reply(t, quote=True)
    

async def pre_process_video(message: Message):
    """ Wrapper over handler, for timeout and errors.
    
    :param Message message:
    Query context.
    """
    
    m = await message.reply("<b>⏺ In queue...</b>", quote=True)
    
    # Perhaps it's worth rewriting through the queue
    async with s:
        try:
            task = process_video(message, m)
            await asyncio.wait_for(task, timeout=Config.TIMEOUT)
        
        except asyncio.TimeoutError:
            await message.reply(f"<b>Your video processing timed out ({Config.TIMEOUT})</b>")
            
        except Exception as e:
            await message.reply(f"<b>An error occurred ({e})</b>")
            logger.error(f"pre_process_video: {e}")


@bot.on_message(private & video & user(list(Config.ADMIN_IDS)))
async def video_handler(client: Client, message: Message):
    await pre_process_video(message)
