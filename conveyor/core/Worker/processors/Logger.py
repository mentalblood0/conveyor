import typing
import datetime
import traceback
import dataclasses

from ... import Item, Repository

from .. import Action
from ..Processor import Processor



@dataclasses.dataclass(frozen = True, kw_only = True)
class Error(Action.Action):

	old       : Item
	exception : Exception

	type      : Item.Type

	@property
	def item(self) -> Item:
		return Item(
			type     = self.type,
			status   = Item.Status('created'),
			data     = Item.Data(value = '\n'.join(traceback.format_exception(self.exception)).encode()),
			metadata = Item.Metadata({
				Item.Metadata.Key('error_type')  : Item.Metadata.Enumerable(self.exception.__class__.__name__),
				Item.Metadata.Key('error_text')  : str(self.exception),
				Item.Metadata.Key('item_type')   : self.old.type,
				Item.Metadata.Key('item_status') : self.old.status.value
			}),
			chain    = Item.Chain(ref = Item.Data(value = b'')),
			reserver = Item.Reserver(exists = False),
			created  = Item.Created(datetime.datetime.now())
		)

	def __call__(self, repository: Repository) -> None:
		Action.Append(self.item)(repository)

	@property
	def info(self) -> typing.Iterable[tuple[str, typing.Any]]:
		yield ('old', self.old)

@dataclasses.dataclass(frozen = True, kw_only = True)
class Solution(Action.Action):

	ref  : Item | Action.Success

	type : Item.Type

	@property
	def old(self) -> Item:
		match self.ref:
			case Item():
				return self.ref
			case Action.Success():
				return self.ref.item

	def __call__(self, repository: Repository) -> None:
		Action.Delete(
			Error(
				old       = self.old,
				exception = Exception(),
				type      = self.type
			).item
		)(repository)

	@property
	def info(self) -> typing.Iterable[tuple[str, typing.Any]]:
		yield ('old', self.old)

@dataclasses.dataclass(frozen = True, kw_only = True)
class Logger(Processor[Action.Action, Action.Action]):

	Error    = Error
	Solution = Solution

	normal : Item.Type
	errors : Item.Type

	def __call__(self, input: typing.Callable[[], typing.Iterable[Action.Action]], config: typing.Any) -> typing.Iterable[Action.Action]:

		try:

			for a in input():

				match a:

					case Action.Success():
						yield Solution(
							ref  = a,
							type = self.errors
						)

					case _:

						info = Item.Metadata({})
						for k, v in a.info:
							match v:
								case Item.Metadata.Value:
									info = info | {Item.Metadata.Key(f'action_{k}'): v}
								case Item():
									info = info | {Item.Metadata.Key(f'action_{k}_type'):   v.type.value}
									info = info | {Item.Metadata.Key(f'action_{k}_status'): v.status.value}
								case _ :
									pass

						entry = Item(
							type     = self.normal,
							status   = Item.Status('preaction'),
							data     = Item.Data(value = b''),
							metadata = info | {
								Item.Metadata.Key('action') : Item.Metadata.Enumerable(a.__class__.__name__),
							},
							chain    = Item.Chain(ref = Item.Data(value = str(a).encode())),
							reserver = Item.Reserver(exists = False),
							created  = Item.Created(datetime.datetime.now())
						)

						yield Action.Append(entry)
						yield a
						yield Action.Update(
							old = entry,
							new = dataclasses.replace(entry, status = Item.Status('postaction'))
						)

		except Processor.Error[Item] as e:

			yield Error(
				old       = e.input,
				exception = e.exception,
				type      = self.errors
			)