from __future__ import unicode_literals

import asyncio
import logging

import grpc

import remote_curse_pb2
import remote_curse_pb2_grpc
from os import mkdir
import yt_downloader

_cleanup_coroutines = []


class Hexman(remote_curse_pb2_grpc.HexManServicer):

    async def CurseMe(
            self, request: remote_curse_pb2.CurseRequest,
            context: grpc.aio.ServicerContext) -> remote_curse_pb2.CurseReply:
        try:
            mkdir("videos")
        except FileExistsError:
            pass
        results = yt_downloader.quick_search(request.keyword)
        for link in results:
            filename = results.get(link).get("title")
            yt_downloader.quick_load(link, filename) if results.get(
                link).get("views") < request.views else None
            yield remote_curse_pb2.CurseReply(filename=filename)


async def serve() -> None:
    server = grpc.aio.server()
    remote_curse_pb2_grpc.add_HexManServicer_to_server(Hexman(), server)
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()

    async def server_graceful_shutdown():
        logging.info("Starting graceful shutdown...")
        # Shuts down the server with 0 seconds of grace period. During the
        # grace period, the server won't accept new connections and allow
        # existing RPCs to continue within the grace period.
        await server.stop(5)

    _cleanup_coroutines.append(server_graceful_shutdown())
    await server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(serve())
    finally:
        loop.run_until_complete(*_cleanup_coroutines)
        loop.close()
