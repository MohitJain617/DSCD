from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClientDetails(_message.Message):
    __slots__ = ["client_uuid"]
    CLIENT_UUID_FIELD_NUMBER: _ClassVar[int]
    client_uuid: str
    def __init__(self, client_uuid: _Optional[str] = ...) -> None: ...

class ServerDetails(_message.Message):
    __slots__ = ["addr", "name"]
    ADDR_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    addr: str
    name: str
    def __init__(self, name: _Optional[str] = ..., addr: _Optional[str] = ...) -> None: ...

class ServerList(_message.Message):
    __slots__ = ["server_list"]
    SERVER_LIST_FIELD_NUMBER: _ClassVar[int]
    server_list: _containers.RepeatedCompositeFieldContainer[ServerDetails]
    def __init__(self, server_list: _Optional[_Iterable[_Union[ServerDetails, _Mapping]]] = ...) -> None: ...

class StatusOfRegistry(_message.Message):
    __slots__ = ["connected"]
    CONNECTED_FIELD_NUMBER: _ClassVar[int]
    connected: bool
    def __init__(self, connected: bool = ...) -> None: ...
