from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Timestamp(_message.Message):
    __slots__ = ("seconds", "nanos")
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    NANOS_FIELD_NUMBER: _ClassVar[int]
    seconds: int
    nanos: int
    def __init__(self, seconds: _Optional[int] = ..., nanos: _Optional[int] = ...) -> None: ...

class Member(_message.Message):
    __slots__ = ("id", "first_name", "last_name", "full_name", "email", "phone", "address", "membership_number", "membership_status", "join_date", "created_at", "updated_at", "active_borrowings_count", "overdue_borrowings_count")
    ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    MEMBERSHIP_NUMBER_FIELD_NUMBER: _ClassVar[int]
    MEMBERSHIP_STATUS_FIELD_NUMBER: _ClassVar[int]
    JOIN_DATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_BORROWINGS_COUNT_FIELD_NUMBER: _ClassVar[int]
    OVERDUE_BORROWINGS_COUNT_FIELD_NUMBER: _ClassVar[int]
    id: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone: str
    address: str
    membership_number: str
    membership_status: str
    join_date: str
    created_at: str
    updated_at: str
    active_borrowings_count: int
    overdue_borrowings_count: int
    def __init__(self, id: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., full_name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., address: _Optional[str] = ..., membership_number: _Optional[str] = ..., membership_status: _Optional[str] = ..., join_date: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ..., active_borrowings_count: _Optional[int] = ..., overdue_borrowings_count: _Optional[int] = ...) -> None: ...

class MemberList(_message.Message):
    __slots__ = ("results", "count", "next", "previous")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    NEXT_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[Member]
    count: int
    next: str
    previous: str
    def __init__(self, results: _Optional[_Iterable[_Union[Member, _Mapping]]] = ..., count: _Optional[int] = ..., next: _Optional[str] = ..., previous: _Optional[str] = ...) -> None: ...

class Book(_message.Message):
    __slots__ = ("id", "isbn", "title", "author", "publisher", "publication_year", "description", "total_copies", "available_copies", "condition", "language", "is_available", "borrowing_count", "active_borrowings_count", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ISBN_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    PUBLISHER_FIELD_NUMBER: _ClassVar[int]
    PUBLICATION_YEAR_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COPIES_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_COPIES_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    BORROWING_COUNT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_BORROWINGS_COUNT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    isbn: str
    title: str
    author: str
    publisher: str
    publication_year: int
    description: str
    total_copies: int
    available_copies: int
    condition: str
    language: str
    is_available: bool
    borrowing_count: int
    active_borrowings_count: int
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[str] = ..., isbn: _Optional[str] = ..., title: _Optional[str] = ..., author: _Optional[str] = ..., publisher: _Optional[str] = ..., publication_year: _Optional[int] = ..., description: _Optional[str] = ..., total_copies: _Optional[int] = ..., available_copies: _Optional[int] = ..., condition: _Optional[str] = ..., language: _Optional[str] = ..., is_available: bool = ..., borrowing_count: _Optional[int] = ..., active_borrowings_count: _Optional[int] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class BookList(_message.Message):
    __slots__ = ("results", "count", "next", "previous")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    NEXT_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[Book]
    count: int
    next: str
    previous: str
    def __init__(self, results: _Optional[_Iterable[_Union[Book, _Mapping]]] = ..., count: _Optional[int] = ..., next: _Optional[str] = ..., previous: _Optional[str] = ...) -> None: ...

class Borrowing(_message.Message):
    __slots__ = ("id", "member", "member_id", "member_name", "book", "book_id", "book_title", "borrowed_at", "due_date", "returned_at", "status", "days_until_due", "days_overdue", "is_overdue", "notes", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_NAME_FIELD_NUMBER: _ClassVar[int]
    BOOK_FIELD_NUMBER: _ClassVar[int]
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    BOOK_TITLE_FIELD_NUMBER: _ClassVar[int]
    BORROWED_AT_FIELD_NUMBER: _ClassVar[int]
    DUE_DATE_FIELD_NUMBER: _ClassVar[int]
    RETURNED_AT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DAYS_UNTIL_DUE_FIELD_NUMBER: _ClassVar[int]
    DAYS_OVERDUE_FIELD_NUMBER: _ClassVar[int]
    IS_OVERDUE_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    member: str
    member_id: str
    member_name: str
    book: str
    book_id: str
    book_title: str
    borrowed_at: str
    due_date: str
    returned_at: str
    status: str
    days_until_due: int
    days_overdue: int
    is_overdue: bool
    notes: str
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[str] = ..., member: _Optional[str] = ..., member_id: _Optional[str] = ..., member_name: _Optional[str] = ..., book: _Optional[str] = ..., book_id: _Optional[str] = ..., book_title: _Optional[str] = ..., borrowed_at: _Optional[str] = ..., due_date: _Optional[str] = ..., returned_at: _Optional[str] = ..., status: _Optional[str] = ..., days_until_due: _Optional[int] = ..., days_overdue: _Optional[int] = ..., is_overdue: bool = ..., notes: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class BorrowingList(_message.Message):
    __slots__ = ("results", "count", "next", "previous")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    NEXT_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[Borrowing]
    count: int
    next: str
    previous: str
    def __init__(self, results: _Optional[_Iterable[_Union[Borrowing, _Mapping]]] = ..., count: _Optional[int] = ..., next: _Optional[str] = ..., previous: _Optional[str] = ...) -> None: ...

class Fine(_message.Message):
    __slots__ = ("id", "borrowing_id", "member_id", "member_name", "book_id", "book_title", "amount", "reason", "is_paid", "paid_at", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    BORROWING_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_NAME_FIELD_NUMBER: _ClassVar[int]
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    BOOK_TITLE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    IS_PAID_FIELD_NUMBER: _ClassVar[int]
    PAID_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    borrowing_id: str
    member_id: str
    member_name: str
    book_id: str
    book_title: str
    amount: str
    reason: str
    is_paid: bool
    paid_at: str
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[str] = ..., borrowing_id: _Optional[str] = ..., member_id: _Optional[str] = ..., member_name: _Optional[str] = ..., book_id: _Optional[str] = ..., book_title: _Optional[str] = ..., amount: _Optional[str] = ..., reason: _Optional[str] = ..., is_paid: bool = ..., paid_at: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class FineList(_message.Message):
    __slots__ = ("results", "count", "next", "previous")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    NEXT_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[Fine]
    count: int
    next: str
    previous: str
    def __init__(self, results: _Optional[_Iterable[_Union[Fine, _Mapping]]] = ..., count: _Optional[int] = ..., next: _Optional[str] = ..., previous: _Optional[str] = ...) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ("email", "password")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    email: str
    password: str
    def __init__(self, email: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class LoginResponse(_message.Message):
    __slots__ = ("token", "member", "message")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    token: str
    member: Member
    message: str
    def __init__(self, token: _Optional[str] = ..., member: _Optional[_Union[Member, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class SignupRequest(_message.Message):
    __slots__ = ("first_name", "last_name", "email", "password", "phone", "address")
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    first_name: str
    last_name: str
    email: str
    password: str
    phone: str
    address: str
    def __init__(self, first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., email: _Optional[str] = ..., password: _Optional[str] = ..., phone: _Optional[str] = ..., address: _Optional[str] = ...) -> None: ...

class SignupResponse(_message.Message):
    __slots__ = ("token", "member", "message")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    token: str
    member: Member
    message: str
    def __init__(self, token: _Optional[str] = ..., member: _Optional[_Union[Member, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class ErrorResponse(_message.Message):
    __slots__ = ("error", "detail", "field_errors")
    class FieldErrorsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    FIELD_ERRORS_FIELD_NUMBER: _ClassVar[int]
    error: str
    detail: str
    field_errors: _containers.ScalarMap[str, str]
    def __init__(self, error: _Optional[str] = ..., detail: _Optional[str] = ..., field_errors: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ActionResponse(_message.Message):
    __slots__ = ("message", "success")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    message: str
    success: bool
    def __init__(self, message: _Optional[str] = ..., success: bool = ...) -> None: ...

class MemberStats(_message.Message):
    __slots__ = ("total_borrowings", "active_borrowings", "overdue_borrowings", "total_fines", "total_fine_amount")
    TOTAL_BORROWINGS_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_BORROWINGS_FIELD_NUMBER: _ClassVar[int]
    OVERDUE_BORROWINGS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FINES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FINE_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    total_borrowings: int
    active_borrowings: int
    overdue_borrowings: int
    total_fines: int
    total_fine_amount: str
    def __init__(self, total_borrowings: _Optional[int] = ..., active_borrowings: _Optional[int] = ..., overdue_borrowings: _Optional[int] = ..., total_fines: _Optional[int] = ..., total_fine_amount: _Optional[str] = ...) -> None: ...

class BookStats(_message.Message):
    __slots__ = ("total_borrowings", "active_borrowings", "average_borrowing_duration")
    TOTAL_BORROWINGS_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_BORROWINGS_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_BORROWING_DURATION_FIELD_NUMBER: _ClassVar[int]
    total_borrowings: int
    active_borrowings: int
    average_borrowing_duration: float
    def __init__(self, total_borrowings: _Optional[int] = ..., active_borrowings: _Optional[int] = ..., average_borrowing_duration: _Optional[float] = ...) -> None: ...
