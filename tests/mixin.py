import pytest

from chasm import ChasmMixin

# Usage
class UserServer():
  users = dict()
  def add_user(self, id, name):
    self.users[id] = name

  def get_user(self, id):
    return self.users.get(id, None)

def test_userserver():
	client = UserServer()
	client.add_user(1, 'dave')
	client.add_user(2, 'test')

	assert client.get_user(2) == 'test'