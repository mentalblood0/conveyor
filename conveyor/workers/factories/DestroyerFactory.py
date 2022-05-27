import pydantic
from ..Destroyer import Destroyer



@lambda c: c()
class DestroyerFactory:

	@pydantic.validate_arguments
	def __call__(self, input_type: str, input_status: str):
		return type(
			'__'.join([
				'Destoyer',
				input_type,
				input_status
			]),
			(Destroyer,),
			{
				'input_type': input_type,
				'input_status': input_status
			}
		)