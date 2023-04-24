from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ProcessFilesRequest(_message.Message):
    __slots__ = ["ports", "task"]
    PORTS_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    ports: _containers.RepeatedScalarFieldContainer[str]
    task: str
    def __init__(self, task: _Optional[str] = ..., ports: _Optional[_Iterable[str]] = ...) -> None: ...

class ProcessFilesResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: bool
    def __init__(self, response: bool = ...) -> None: ...
