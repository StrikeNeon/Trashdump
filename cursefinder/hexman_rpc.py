from __future__ import unicode_literals

import asyncio
import logging

import grpc

import remote_curse_pb2
import remote_curse_pb2_grpc
from os import mkdir
import yt_downloader


from concurrent.futures import ThreadPoolExecutor
import logging
import threading
import time
from typing import Iterable

from google.protobuf.json_format import MessageToJson
import grpc

import remote_curse_pb2
import remote_curse_pb2_grpc


class HexMan(remote_curse_pb2_grpc.HexManServicer):

    def __init__(self):
        self._id_counter = 0
        self._lock = threading.RLock()

    def CurseMe(
            self, request_iterator: [remote_curse_pb2.CurseRequest],
            context: grpc.ServicerContext) -> Iterable[remote_curse_pb2.CurseReply]:
        print(request_iterator)
        try:
            mkdir("videos")
        except FileExistsError:
            pass
        results = yt_downloader.quick_search(request_iterator.keyword)
        print(len(results))
        for link in results:
            result = results.get(link)
            print(link, result)
            filename = yt_downloader.quick_load(link, result.get("title")) if results.get(
                link).get("views") < request_iterator.views else None
            print(filename)
            yield remote_curse_pb2.CurseReply(filename=filename)


def serve(address: str) -> None:
    server = grpc.server(ThreadPoolExecutor())
    remote_curse_pb2_grpc.add_HexManServicer_to_server(HexMan(), server)
    server.add_insecure_port(address)
    server.start()
    logging.info("Server serving at %s", address)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve("[::]:50051")
