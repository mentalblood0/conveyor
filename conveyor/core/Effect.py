import pydantic
from typing import Literal, Callable



def composeTry(f: Callable, handleError: Callable):

	def new_f(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except Exception as e:
			handleError(e)

	return new_f


@pydantic.validate_arguments
def composeSequence(functions: list[Callable]):

	def new_f(*args, **kwargs):

		for f in functions[:-1]:
			f(*args, **kwargs)

		return functions[-1](*args, **kwargs)

	return new_f


class Effect:

	@pydantic.validate_arguments
	def install(self, target: object, position: Literal['before', 'after']='before', handleError: Callable=lambda: None):

		for name in dir(self):
			if (
				not name.startswith('_')
				and name != 'install'
			):

				field = getattr(self, name)

				if callable(field):

					f = composeTry(field, handleError)

					if position == 'before':
						sequence = [f, getattr(target, name)]
					elif position == 'after':
						sequence = [getattr(target, name), f]

					object.__setattr__(target, name, composeSequence(sequence))
