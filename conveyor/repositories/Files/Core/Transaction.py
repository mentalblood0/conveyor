import abc
import typing
import pathlib
import dataclasses

from ....core.Transforms import Transform


class Collision(Exception):
    pass


@dataclasses.dataclass(frozen=True, kw_only=False)
class Action(metaclass=abc.ABCMeta):
    path: pathlib.Path
    prepare_now: bool = True

    @typing.final
    def __post_init__(self):
        if self.prepare_now:
            self.prepare()

    @property
    @abc.abstractmethod
    def temp(self) -> pathlib.Path:
        pass

    @abc.abstractmethod
    def prepare(self) -> None:
        pass

    @abc.abstractmethod
    def commit(self) -> None:
        pass

    @abc.abstractmethod
    def rollback(self) -> None:
        pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Append(Action):
    data: bytes
    transforms: Transform[bytes, bytes]

    equal_path: typing.Callable[[bytes], pathlib.Path]
    equal_data: Transform[bytes, bytes]

    handle_collisions: bool = True

    @property
    def temp(self) -> pathlib.Path:
        return self.path.with_suffix(self.path.suffix + ".new")

    @property
    def equal(self) -> typing.Self:
        data = self.equal_data(self.data)
        return dataclasses.replace(self, path=self.equal_path(data), data=data)

    def prepare(self) -> None:
        action: typing.Self = self
        transformed = self.transforms(self.data)

        while True:
            if action.path.exists():
                if transformed != action.path.read_bytes():
                    action = action.equal
                    continue
                else:
                    break

            action.temp.parent.mkdir(parents=True, exist_ok=True)
            action.temp.write_bytes(transformed)

            break

    def _commit(self, action: typing.Self):
        action.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            action.temp.rename(action.path)
        except (FileExistsError, FileNotFoundError):
            if action.data != action.path.read_bytes():
                raise Collision(str(action.path))

    def commit(self) -> None:
        action: typing.Self = self

        while True:
            try:
                self._commit(action)
                break
            except Collision:
                if not self.handle_collisions:
                    raise

            action = action.equal

    def rollback(self) -> None:
        self.temp.unlink(missing_ok=True)

        p = self.temp.parent
        while True:
            try:
                p.rmdir()
            except Exception:
                break
            p = p.parent


@dataclasses.dataclass(frozen=True, kw_only=False)
class Delete(Action):
    @property
    def temp(self) -> pathlib.Path:
        return self.path.with_suffix(".del")

    def prepare(self) -> None:
        self.path.replace(self.temp)

    def commit(self) -> None:
        self.temp.unlink(missing_ok=True)

        p = self.temp.parent
        while True:
            try:
                p.rmdir()
            except Exception:
                break
            p = p.parent

    def rollback(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.temp.replace(self.path)


class Transaction(list[Action]):
    Action = Action

    Append = Append
    Delete = Delete

    def commit(self) -> None:
        for a in self:
            a.commit()

    def rollback(self) -> None:
        for a in self:
            a.rollback()
