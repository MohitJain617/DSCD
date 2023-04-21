from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ProcessFilesRequest(_message.Message):
    __slots__ = ["filenames", "num_reducers", "task"]
    FILENAMES_FIELD_NUMBER: _ClassVar[int]
    NUM_REDUCERS_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    filenames: _containers.RepeatedScalarFieldContainer[str]
    num_reducers: int
    task: str
    def __init__(self, filenames: _Optional[_Iterable[str]] = ..., task: _Optional[str] = ..., num_reducers: _Optional[int] = ...) -> None: ...

class ProcessFilesResponse(_message.Message):
    __slots__ = ["response"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: bool
    def __init__(self, response: bool = ...) -> None: ...
