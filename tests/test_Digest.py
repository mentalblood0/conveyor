from conveyor.core.Item import Digest



def test_value():
	v = b' ' * 32
	assert Digest(v).value == v


def test_string():
	l = 32
	s = Digest(b' ' * 32).string
	assert len(s) > l


def test_path():

	p = Digest(b' ' * 32).path

	p.parent.mkdir(parents=True, exist_ok=True)
	p.touch(exist_ok=True)

	p.unlink()
	while len(p.parts) > 1:
		p = p.parent
		p.rmdir()


def test_equal():
	v = b' ' * 32
	assert Digest(v) == Digest(v)
	assert Digest(v) != Digest(b'x' * 32)
	assert Digest(v) != Digest(b' ' * 33)