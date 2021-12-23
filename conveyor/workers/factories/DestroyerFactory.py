from ..Destroyer import Destroyer



@lambda c: c()
class DestroyerFactory:

	def __call__(self, input_type, input_status):
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