# Chasm

Use Chasm to open a rift betwen the interface of an object and the execution of instance methods. 

Sample:
``
class DataAdapter:
	def new_data(self, new):
		'write data to database'
		# write data
		#no need to return

	def do_heavy_lifting(self, *input_data):
		'Do a lot of data-heavy queries'
		# do stuff
		# do more stuff
		# do even more stuff
		# ...
		# do the most stuff
		return result

# Example Usage
da = DataAdapter()
da.new_data('test data')
da.do_heavy_lifting(1,4,6,2,4,3,1)
```
With the above code, it probably doesn't matter how often `DataAdapter.new_data` is called. However, given the amount of data that needs to be sent "over-the-wire" for `DataAdapter.do_heavy_lifting` can cause serious bottlenecks if called too often. This is where `ChasmMixin` comes in.

ChasmMixin Sample:
```
from chasm import ChasmMixin
from chasm.aop import remote

class DataAdapter(ChasmMixin):
	def new_data(self, new):
		'write data to database'
		# write data
		#no need to return

	# tell chasm to execute this code on a remote server
	# a ChasmServer running on the SQL machine with help
	# throughput a considerable amount
	#
	# query=True tells the client to expect a response
	# by default query=True, this allows for non-blocking
	# distribution of work
	@remote(query=True)
	def do_heavy_lifting(self, *input_data):
		'Do a lot of data-heavy queries'
		# do stuff
		# do more stuff
		# do even more stuff
		# ...
		# do the most stuff
		return result

# Example Usage
# NOTE: ChasmServer must be hosting `DataAdapter`
# at `host_addr` and `host_port` prior to running
da = DataAdapter.Client(addr=host_addr, port=host_port)
da.new_data('test data')
da.do_heavy_lifting(1,4,6,2,4,3,1)

# Example ChasmServer host
from chasm.server import ChasmServer
daServer = ChasmServer(DataAdapter)
daServer.listen(port=listen_port, block=True)
```
