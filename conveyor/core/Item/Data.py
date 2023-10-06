import typing
import hashlib
import dataclasses

from .Digest import Digest



def default_algorithm(input_: bytes) -> bytes:
	return hashlib.sha3_512(input_).digest()

@dataclasses.dataclass(frozen = True, kw_only = True)
class Data:

	Digest = Digest

	value     : bytes
	test      : Digest | None                   = dataclasses.field(default=None, compare=False)
	algorithm : typing.Callable[[bytes], bytes] = default_algorithm

	def __post_init__(self):
		if self.test is not None:
			if (correct := Data(value = self.value).digest) != self.test:
				raise ValueError(f'Provided digest "{self.test}" is not correct (correct is "{correct}")')

	@property
	def digest(self) -> Digest:
		return Digest(self.algorithm(self.value))

	@property
	def string(self) -> str:
		return self.value.decode()