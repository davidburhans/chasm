import pytest

from chasm.server import get_host_class

def test_get_host_class():
	class First:
		class Nested:
			def foo(self, x):
				return x*2
	result, fn = get_host_class('First.Nested.foo', scope=locals())
	assert result == First.Nested
	assert fn == 'foo'
	inst = result()
	assert getattr(inst, fn)(2) == 2*2
