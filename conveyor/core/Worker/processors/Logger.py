import typing
import pydantic
import datetime
import dataclasses

from ... import Item

from .. import Action
from ..Processor import Processor



@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
class Logger(Processor[Action.Action, Action.Action]):

	@pydantic.validate_arguments
	def __call__(self, input: typing.Iterable[Action.Action], config: dict[str, typing.Any]) -> typing.Iterable[Action.Action]:
		for a in input:
			entry = Item(
				type     = Item.Type('log'),
				status   = Item.Status('preaction'),
				data     = Item.Data(value = b''),
				metadata = Item.Metadata({
					Item.Metadata.Key('action') : a.__class__.__name__.lower()
				}),
				chain    = Item.Chain(ref = Item.Data(value = str(a).encode())),
				reserver = Item.Reserver(exists = False, value = None),
				created  = Item.Created(datetime.datetime.now())
			)
			yield Action.Append(entry)
			yield a
			yield Action.Update(
				old = entry,
				new = dataclasses.replace(entry, status = Item.Status('postaction'))
			)