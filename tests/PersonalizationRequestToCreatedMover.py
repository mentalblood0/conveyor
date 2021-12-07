from conveyor import Mover



class PersonalizationRequestToCreatedMover(Mover):

	input_status = 'PersonalizationRequest'
	output_status = 'created'



import sys
sys.modules[__name__] = PersonalizationRequestToCreatedMover