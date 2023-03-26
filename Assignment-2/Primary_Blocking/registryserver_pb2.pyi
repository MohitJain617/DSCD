from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ReplicaDetails(_message.Message):
    __slots__ = ["addr", "name"]
    ADDR_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    addr: str
    name: str
    def __init__(self, name: _Optional[str] = ..., addr: _Optional[str] = ...) -> None: ...

class ReplicaList(_message.Message):
    __slots__ = ["replica_list"]
    REPLICA_LIST_FIELD_NUMBER: _ClassVar[int]
    replica_list: _containers.RepeatedCompositeFieldContainer[ReplicaDetails]
    def __init__(self, replica_list: _Optional[_Iterable[_Union[ReplicaDetails, _Mapping]]] = ...) -> None: ...
