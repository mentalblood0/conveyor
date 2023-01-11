import typing
import pathlib
import pydantic
import dataclasses

from .Transforms import Transform



class Collision(Exception):
	pass


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Action:

	path: pathlib.Path
	prepare_now: bool = True

	def __post_init__(self):
		if self.prepare_now:
			self.prepare()

	@property
	def temp(self) -> pathlib.Path:
		raise NotImplementedError

	def prepare(self) -> None:
		raise NotImplementedError

	def commit(self) -> None:
		raise NotImplementedError

	def rollback(self) -> None:
		raise NotImplementedError


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Append(Action):

	data:  pydantic.StrictBytes

	equal_path: typing.Callable[[bytes], pathlib.Path]
	equal_data: Transform[bytes, bytes]

	handle_collisions: bool = True

	@property
	def temp(self) -> pathlib.Path:
		return self.path.with_suffix(self.path.suffix + '.new')

	@property
	def equal(self) -> typing.Self:
		data = self.equal_data(self.data)
		return dataclasses.replace(
			self,
			path = self.equal_path(data),
			data = data
		)

	def prepare(self) -> None:

		action: typing.Self = self

		while True:

			if action.path.exists():
				if action.data != action.path.read_bytes():
					action = action.equal
					continue
				else:
					break

			action.temp.parent.mkdir(parents=True, exist_ok=True)
			action.temp.write_bytes(self.data)

			break

	def commit(self) -> None:

		action: typing.Self = self

		while True:

			try:
				action.path.parent.mkdir(parents=True, exist_ok=True)
				try:
					action.temp.rename(action.path)
				except (FileExistsError, FileNotFoundError):
					if action.data != action.path.read_bytes():
						raise Collision(action.path.__str__())
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
			except:
				break
			p = p.parent


@pydantic.dataclasses.dataclass(frozen=True, kw_only=False)
class Delete(Action):

	@property
	def temp(self) -> pathlib.Path:
		return self.path.with_suffix('.del')

	def prepare(self) -> None:
		self.path.replace(self.temp)

	def commit(self) -> None:

		self.temp.unlink(missing_ok=True)

		p = self.temp.parent
		while True:
			try:
				p.rmdir()
			except:
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