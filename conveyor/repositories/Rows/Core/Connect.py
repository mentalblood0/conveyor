import typing
import sqlalchemy



Connect = typing.Callable[[], typing.ContextManager[sqlalchemy.Connection]]