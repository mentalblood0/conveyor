from dataclasses import dataclass



@dataclass
class C:
	x: str = 'undefined'


c = C()
print(c.__dict__)