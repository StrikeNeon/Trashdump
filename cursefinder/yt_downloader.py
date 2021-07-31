from __future__ import unicode_literals
import youtube_dl
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from os import remove
from youtubesearchpython import CustomSearch, VideoSortOrder
from pprint import PrettyPrinter

printer = PrettyPrinter(indent=1)


def quick_load(link: str):
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        res = ydl.extract_info(
                    link, force_generic_extractor=ydl.params.get('force_generic_extractor', False))
        ydl.download([link])
        # print(res.keys())
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


def quick_search(query):
    results = {}
    customSearch = CustomSearch(query, VideoSortOrder.uploadDate, limit=10)
    for value in customSearch.result().get("result"):
        # printer.pprint(value)
        views = value.get("viewCount")
        parsed_views = int(views.get("text").split(" ")[0].replace(",", "")) if views.get("text") != "No views" else -1
        results[value.get("link")] = {"id": value.get("id"), "title": value.get("title"), "views": parsed_views}
    return results


results = quick_search("conspiracy")
for link in results:
    quick_load(link) if results.get(link).get("views") < 1000 else None
# # quick_clip("https://www.youtube.com/watch?v=VFe_7Ra3sJ8", 22, 25)
