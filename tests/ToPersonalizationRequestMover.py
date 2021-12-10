from conveyor import Item
from conveyor.workers import Mover



class PersonalizationRequestToCreatedMover(Mover):

	input_type = 'undefined'
	input_status = 'PersonalizationRequest'
	moved_status = 'end'

	output_type = 'PersonalizationRequest'
	output_status = 'created'

	def transform(self, item):
		return [item, item]



import sys
sys.modules[__name__] = PersonalizationRequestToCreatedMover