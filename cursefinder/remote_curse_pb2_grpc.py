# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import remote_curse_pb2 as remote__curse__pb2


class HexManStub(object):
    """The greeting service definition.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CurseMe = channel.unary_stream(
                '/remotecurse.HexMan/CurseMe',
                request_serializer=remote__curse__pb2.CurseRequest.SerializeToString,
                response_deserializer=remote__curse__pb2.CurseReply.FromString,
                )


class HexManServicer(object):
    """The greeting service definition.
    """

    def CurseMe(self, request, context):
        """Sends a greeting
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_HexManServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CurseMe': grpc.unary_stream_rpc_method_handler(
                    servicer.CurseMe,
                    request_deserializer=remote__curse__pb2.CurseRequest.FromString,
                    response_serializer=remote__curse__pb2.CurseReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'remotecurse.HexMan', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class HexMan(object):
    """The greeting service definition.
    """

    @staticmethod
    def CurseMe(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/remotecurse.HexMan/CurseMe',
            remote__curse__pb2.CurseRequest.SerializeToString,
            remote__curse__pb2.CurseReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)