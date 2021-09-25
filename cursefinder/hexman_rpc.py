from __future__ import unicode_literals

import asyncio
import logging

import grpc

import remote_curse_pb2
import remote_curse_pb2_grpc

import youtube_dl
from os import getcwd, path, mkdir
from youtubesearchpython import CustomSearch, VideoSortOrder


def quick_load(link: str, filename: str):
    ydl_opts = {'ffmpeg_location': "./ffmpeg-4.4-full_build/bin",
                'outtmpl': path.join(path.join(getcwd(), "videos"), f'{filename}.mp4')}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.extract_info(
                link, force_generic_extractor=ydl.params.get('force_generic_extractor', False))
            ydl.download([link])
            filename = f'{filename}.mp4'
        except youtube_dl.utils.DownloadError:
            return
    return filename


def quick_search(query):
    results = {}
    customSearch = CustomSearch(query, VideoSortOrder.uploadDate, limit=10)
    for value in customSearch.result().get("result"):
        views = value.get("viewCount")
        try:
            parsed_views = int(views.get("text").split(" ")[0].replace(
                ",", "")) if views.get("text") != "No views" else -1
            results[value.get("link")] = {"id": value.get(
                "id"), "title": value.get("title"), "views": parsed_views}
        except AttributeError:
            pass  # trips on streams
    return results


class Hexman(remote_curse_pb2_grpc.HexManServicer):

    async def CurseMe(
            self, request: remote_curse_pb2.CurseRequest,
            context: grpc.aio.ServicerContext) -> remote_curse_pb2.CurseReply:
        try:
            mkdir("videos")
        except FileExistsError:
            pass
        results = quick_search(request.keyword)
        for link in results:
            filename = results.get(link).get("title")
            quick_load(link, filename) if results.get(
                link).get("views") < request.views else None
            yield remote_curse_pb2.CurseReply(filename=filename)


async def serve() -> None:
    server = grpc.aio.server()
    remote_curse_pb2_grpc.add_HexManServicer_to_server(Hexman(), server)
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        # Shuts down the server with 0 seconds of grace period. During the
        # grace period, the server won't accept new connections and allow
        # existing RPCs to continue within the grace period.
        await server.stop(0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
