from .. import Destroyer



@lambda c: c()
class DestroyerFactory:

	def __call__(self, input_status):
		return type(
			'_'.join(['Destoyer', input_status]),
			(Destroyer,),
			{'input_status': input_status}
		)



import sys
sys.modules[__name__] = DestroyerFactory