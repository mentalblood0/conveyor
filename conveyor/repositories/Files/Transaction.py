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
	equal_data: Transform[bytes]

	handle_collisions: bool = True

	@property
	def temp(self) -> pathlib.Path:
		return self.path.with_suffix(self.path.suffix + '.new')

	def prepare(self) -> None:
		self.temp.parent.mkdir(parents=True, exist_ok=True)
		self.temp.write_bytes(self.data)

	@pydantic.validate_arguments
	def commit(self) -> None:

		action: typing.Self = self

		while True:

			try:
				self.path.parent.mkdir(parents=True, exist_ok=True)
				try:
					self.temp.rename(self.path)
				except FileExistsError:
					if self.data != self.path.read_bytes():
						raise Collision(self.path.__str__())
				break

			except Collision:
				if not self.handle_collisions:
					raise

			data = self.equal_data(action.data)
			action = dataclasses.replace(
				self,
				path = self.equal_path(data),
				data = data
			)

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


@pydantic.dataclasses.dataclass(frozen=False, kw_only=False)
class Transaction:

	Action = Action

	Append = Append
	Delete = Delete

	actions: typing.Sequence[Action] = dataclasses.field(default_factory=list)

	@pydantic.validate_arguments
	def add(self, new_actions: typing.Sequence[Action]):
		self.actions = (*self.actions, *new_actions)
		for a in new_actions:
			a.prepare()

	def commit(self) -> None:
		for a in self.actions:
			a.commit()

	def rollback(self) -> None:
		for a in self.actions:
			a.rollback()