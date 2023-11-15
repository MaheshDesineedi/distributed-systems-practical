from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class BankRequest(_message.Message):
    __slots__ = ["id", "interface", "money", "customer_request_id", "logical_clock"]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERFACE_FIELD_NUMBER: _ClassVar[int]
    MONEY_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    LOGICAL_CLOCK_FIELD_NUMBER: _ClassVar[int]
    id: int
    interface: str
    money: int
    customer_request_id: int
    logical_clock: int
    def __init__(self, id: _Optional[int] = ..., interface: _Optional[str] = ..., money: _Optional[int] = ..., customer_request_id: _Optional[int] = ..., logical_clock: _Optional[int] = ...) -> None: ...

class BankResponse(_message.Message):
    __slots__ = ["result", "balance"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    result: str
    balance: int
    def __init__(self, result: _Optional[str] = ..., balance: _Optional[int] = ...) -> None: ...
