from __future__ import unicode_literals
import youtube_dl
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from os import remove


def quick_load(link: str):
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        res = ydl.extract_info(
                    link, force_generic_extractor=ydl.params.get('force_generic_extractor', False))
        ydl.download([link])
        print(res.keys())
        filename = f'{res.get("title")}.mp4'
    return filename


def quick_clip(link: str, start: int, end: int):
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        res = ydl.extract_info(
                    link, force_generic_extractor=ydl.params.get('force_generic_extractor', False))
        ydl.download([link])
        print(res.keys())
        filename = f'{res.get("title")}'
    ffmpeg_extract_subclip(f'{filename+link.replace("https://www.youtube.com/watch?v=", "-")}.mp4', start, end, targetname=f'{filename}_clip.mp4')
    remove(f'{filename+link.replace("https://www.youtube.com/watch?v=", "-")}.mp4')


quick_load("https://www.youtube.com/watch?v=SSuvPuQM7qc")
# quick_clip("https://www.youtube.com/watch?v=VFe_7Ra3sJ8", 22, 25)
