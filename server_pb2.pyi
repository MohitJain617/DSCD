from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Article(_message.Message):
    __slots__ = ["FASHION", "POLITICS", "SPORTS", "author", "client", "content", "day", "month", "year"]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    CLIENT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    DAY_FIELD_NUMBER: _ClassVar[int]
    FASHION: bool
    FASHION_FIELD_NUMBER: _ClassVar[int]
    MONTH_FIELD_NUMBER: _ClassVar[int]
    POLITICS: bool
    POLITICS_FIELD_NUMBER: _ClassVar[int]
    SPORTS: bool
    SPORTS_FIELD_NUMBER: _ClassVar[int]
    YEAR_FIELD_NUMBER: _ClassVar[int]
    author: str
    client: ClientDetails
    content: str
    day: int
    month: int
    year: int
    def __init__(self, SPORTS: bool = ..., FASHION: bool = ..., POLITICS: bool = ..., author: _Optional[str] = ..., day: _Optional[int] = ..., month: _Optional[int] = ..., year: _Optional[int] = ..., content: _Optional[str] = ..., client: _Optional[_Union[ClientDetails, _Mapping]] = ...) -> None: ...

class ArticleList(_message.Message):
    __slots__ = ["articles"]
    ARTICLES_FIELD_NUMBER: _ClassVar[int]
    articles: _containers.RepeatedCompositeFieldContainer[Article]
    def __init__(self, articles: _Optional[_Iterable[_Union[Article, _Mapping]]] = ...) -> None: ...

class ClientDetails(_message.Message):
    __slots__ = ["client_uuid"]
    CLIENT_UUID_FIELD_NUMBER: _ClassVar[int]
    client_uuid: str
    def __init__(self, client_uuid: _Optional[str] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class RequestMessage(_message.Message):
    __slots__ = ["FASHION", "POLITICS", "SPORTS", "allTags", "author", "client", "day", "month", "year"]
    ALLTAGS_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    CLIENT_FIELD_NUMBER: _ClassVar[int]
    DAY_FIELD_NUMBER: _ClassVar[int]
    FASHION: bool
    FASHION_FIELD_NUMBER: _ClassVar[int]
    MONTH_FIELD_NUMBER: _ClassVar[int]
    POLITICS: bool
    POLITICS_FIELD_NUMBER: _ClassVar[int]
    SPORTS: bool
    SPORTS_FIELD_NUMBER: _ClassVar[int]
    YEAR_FIELD_NUMBER: _ClassVar[int]
    allTags: bool
    author: str
    client: ClientDetails
    day: int
    month: int
    year: int
    def __init__(self, allTags: bool = ..., SPORTS: bool = ..., FASHION: bool = ..., POLITICS: bool = ..., author: _Optional[str] = ..., day: _Optional[int] = ..., month: _Optional[int] = ..., year: _Optional[int] = ..., client: _Optional[_Union[ClientDetails, _Mapping]] = ...) -> None: ...

class ServerDetails(_message.Message):
    __slots__ = ["addr", "name"]
    ADDR_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    addr: str
    name: str
    def __init__(self, name: _Optional[str] = ..., addr: _Optional[str] = ...) -> None: ...

class ServerList(_message.Message):
    __slots__ = ["serverlist"]
    SERVERLIST_FIELD_NUMBER: _ClassVar[int]
    serverlist: _containers.RepeatedCompositeFieldContainer[ServerDetails]
    def __init__(self, serverlist: _Optional[_Iterable[_Union[ServerDetails, _Mapping]]] = ...) -> None: ...

class StatusOfClientRequest(_message.Message):
    __slots__ = ["request_status"]
    REQUEST_STATUS_FIELD_NUMBER: _ClassVar[int]
    request_status: bool
    def __init__(self, request_status: bool = ...) -> None: ...
