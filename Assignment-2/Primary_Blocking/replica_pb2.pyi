from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DeleteDetails(_message.Message):
    __slots__ = ["primary_hop", "uuid", "version"]
    PRIMARY_HOP_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    primary_hop: bool
    uuid: str
    version: str
    def __init__(self, uuid: _Optional[str] = ..., version: _Optional[str] = ..., primary_hop: bool = ...) -> None: ...

class DeleteResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class ReadDetails(_message.Message):
    __slots__ = ["uuid"]
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class ReadResponse(_message.Message):
    __slots__ = ["content", "name", "status", "version"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    content: str
    name: str
    status: str
    version: str
    def __init__(self, status: _Optional[str] = ..., name: _Optional[str] = ..., content: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

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

class WriteDetails(_message.Message):
    __slots__ = ["content", "name", "primary_hop", "uuid", "version"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_HOP_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    content: str
    name: str
    primary_hop: bool
    uuid: str
    version: str
    def __init__(self, name: _Optional[str] = ..., content: _Optional[str] = ..., uuid: _Optional[str] = ..., version: _Optional[str] = ..., primary_hop: bool = ...) -> None: ...

class WriteResponse(_message.Message):
    __slots__ = ["content", "name", "status", "version"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    content: str
    name: str
    status: str
    version: str
    def __init__(self, status: _Optional[str] = ..., name: _Optional[str] = ..., content: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...
