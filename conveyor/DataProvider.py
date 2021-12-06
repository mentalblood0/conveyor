from abc import ABCMeta

from . import InputProvider, OutputProvider



class DataProvider(InputProvider, OutputProvider, metaclass=ABCMeta):
	pass



import sys
sys.modules[__name__] = DataProvider