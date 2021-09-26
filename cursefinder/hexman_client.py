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
        self._curse_started = threading.Event()
        self._curse_finished = threading.Event()

        self._consumer_future = None

    def _response_watcher(
            self,
            response_iterator: Iterator[remote_curse_pb2.CurseReply]) -> None:
        try:
            for response in response_iterator:
                # NOTE: All fields in Proto3 are optional. This is the recommended way
                # to check if a field is present or not, or to exam which one-of field is
                # fulfilled by this message.
                if response.HasField("call_info"):
                    self._on_call_info(response.call_info)
                elif response.HasField("call_state"):
                    self._on_call_state(response.call_state.state)
                else:
                    raise RuntimeError(
                        "Received curse without call_info and call_state"
                    )
        except Exception as e:
            self._curse_started.set()
            raise

    def curse(self) -> None:
        request = remote_curse_pb2.CurseRequest()
        request.keyword = self._keyword
        request.views = self._views
        response_iterator = self._stub.CurseMe(iter((request,)))
        # Instead of consuming the response on current thread, spawn a consumption thread.
        self._consumer_future = self._executor.submit(response_iterator)
        print(f"submitted {self._keyword} request limited {self._views}")

    def wait_peer(self) -> None:
        logging.info("Waiting for peer to connect [%s]...", self._phone_number)
        self._peer_responded.wait(timeout=None)
        if self._consumer_future.done():
            # If the future raises, forwards the exception here
            self._consumer_future.result()
        return self._call_state is phone_pb2.CallState.State.ACTIVE

    def curse_session(self) -> None:
        logging.info("Consuming audio resource [%s]", self._audio_session_link)
        self._call_finished.wait(timeout=None)


def process_call(executor: ThreadPoolExecutor, channel: grpc.Channel,
                 keyword: str, views: int) -> None:
    call_maker = CurseClient(executor, channel, keyword, views)
    call_maker.curse()
    # if call_maker.wait_peer():
    #     call_maker.audio_session()
    #     logging.info("Call finished!")
    # else:
    #     logging.info("Call failed: peer didn't answer")


def run():
    executor = ThreadPoolExecutor()
    with grpc.insecure_channel("localhost:50051") as channel:
        future = executor.submit(process_call, executor, channel,
                                 "alien", 5000)
        future.result()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()
