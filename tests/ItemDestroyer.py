from conveyor.workers import Destroyer



class ItemDestroyer(Destroyer):

	input_status = 'end'



import sys
sys.modules[__name__] = ItemDestroyer