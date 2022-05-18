from . import uuid7



def composeChainId() -> str:
	return hex(uuid7())