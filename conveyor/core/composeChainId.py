import base64

from . import uuid7



def composeChainId() -> str:
	n = uuid7()
	return base64.b64encode(n.to_bytes(((n.bit_length() + 7) // 8), byteorder='big'))