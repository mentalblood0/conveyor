import pathlib
import pydantic
import dataclasses



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

	data: pydantic.StrictBytes

	@property
	def temp(self) -> pathlib.Path:
		return self.path.with_suffix(self.path.suffix + '.new')

	def prepare(self) -> None:
		self.temp.parent.mkdir(parents=True, exist_ok=True)
		self.temp.write_bytes(self.data)

	def commit(self) -> None:
		self.path.parent.mkdir(parents=True, exist_ok=True)
		self.temp.replace(self.path)

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

	Append = Append
	Delete = Delete

	actions: list[Action] = dataclasses.field(default_factory=list)

	@pydantic.validate_arguments
	def add(self, new_actions: list[Action]):
		self.actions.extend(new_actions)
		for a in new_actions:
			a.prepare()

	def commit(self) -> None:
		for a in self.actions:
			a.commit()

	def rollback(self) -> None:
		for a in self.actions:
			a.rollback()