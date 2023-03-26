from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ReplicaDetails(_message.Message):
    __slots__ = ["addr", "name"]
    ADDR_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    addr: str
    name: str
    def __init__(self, name: _Optional[str] = ..., addr: _Optional[str] = ...) -> None: ...

class RequestStatus(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: bool = ...) -> None: ...
