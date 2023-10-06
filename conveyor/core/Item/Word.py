import re
import dataclasses

from .Enumerable import Enumerable



@dataclasses.dataclass(frozen = True, kw_only = False)
class Word(Enumerable):

	value: str

	def __post_init__(self):
		if re.match(r'\w+', self.value) is None:
			raise ValueError('`Word` value must be word')