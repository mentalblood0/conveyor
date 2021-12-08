from conveyor import Mover



class PersonalizationRequestToCreatedMover(Mover):

	input_status = 'PersonalizationRequest'
	moved_status = 'end'

	output_status = 'created'

	def transform(self, data):
		return [data, data]



import sys
sys.modules[__name__] = PersonalizationRequestToCreatedMover