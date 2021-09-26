from concurrent.futures import ThreadPoolExecutor
import logging
import threading
from typing import Iterator

import grpc
import grpc
import remote_curse_pb2
import remote_curse_pb2_grpc


class CurseClient:
    def __init__(self, executor: ThreadPoolExecutor, channel: grpc.Channel,
                 keyword: str, views: int) -> None:
        self._executor = executor
        self._channel = channel
        self._stub = remote_curse_pb2_grpc.HexManStub(channel)
        self._keyword = keyword
        self._views = views

        self._consumer_future = None

    def call(self) -> None:
        request = remote_curse_pb2.CurseRequest()
        request.keyword = self._keyword
        request.views = self._views
        response_iterator = self._stub.CurseMe(iter((request,)))
        # Instead of consuming the response on current thread, spawn a consumption thread.
        self._consumer_future = self._executor.submit(response_iterator)


def process_call(executor: ThreadPoolExecutor, channel: grpc.Channel,
                 keyword: str, views: int) -> None:
    call_maker = CurseClient(executor, channel, keyword, views)
    call_maker.call()


def run():
    executor = ThreadPoolExecutor()
    with grpc.insecure_channel("localhost:50051") as channel:
        future = executor.submit(process_call, executor, channel,
                                 "alien", 100)
        future.result()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()
