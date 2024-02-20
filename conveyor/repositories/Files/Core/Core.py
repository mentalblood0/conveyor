import typing
import shutil
import pathlib
import contextlib
import dataclasses

from conveyor.core.Item import Digest, Data

from ....core import Transforms
from .Pathify import Pathify
from .Transaction import Transaction


@dataclasses.dataclass(frozen=True, kw_only=True)
class Core:
    Transforms = Transforms
    Pathify = Pathify

    root: pathlib.Path
    suffix: str

    prepare: Transforms.Transform[bytes, bytes]
    sidestep: Transforms.Transform[bytes, bytes]
    pathify: Transforms.Transform[Digest, pathlib.Path]

    transaction_: Transaction | None = None

    empty: Digest = Data(value=b"").digest

    def path(self, digest: Digest) -> pathlib.Path:
        return pathlib.Path(self.root, self.pathify(digest)).with_suffix(self.suffix)

    def append(self, data: Data) -> None:
        if not data.value:
            return

        with self.transaction() as t:
            if t.transaction_ is None:
                raise ValueError
            t.transaction_.append(
                Transaction.Append(
                    path=self.path(data.digest),
                    data=data.value,
                    transforms=self.prepare,
                    equal_path=lambda b: self.path(Data(value=b).digest),
                    equal_data=self.sidestep,
                )
            )

    def __getitem__(self, digest: Digest) -> Data:
        if digest == self.empty:
            return Data(value=b"")

        try:
            return Data(
                value=(~self.prepare)(self.path(digest).read_bytes()), test=digest
            )
        except FileNotFoundError as e:
            raise KeyError(f"{self.root} {digest.string}") from e

    def __delitem__(self, digest: Digest) -> None:
        with self.transaction() as t:
            if t.transaction_ is None:
                raise ValueError
            t.transaction_.append(Transaction.Delete(self.path(digest)))

    @property
    def _transaction(self):
        if self.transaction_ is None:
            return Transaction()
        return self.transaction_

    @contextlib.contextmanager
    def transaction(self) -> typing.Iterator[typing.Self]:
        t = self._transaction
        try:
            try:
                yield dataclasses.replace(self, transaction_=t)
                if self.transaction_ is None:
                    t.commit()
            except Exception:
                t.rollback()
                raise
        except FileNotFoundError as e:
            raise KeyError from e

    def __len__(self) -> int:
        return sum(1 for _ in self.root.rglob(f"*{self.suffix}"))

    def clear(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)
