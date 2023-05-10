import rss_parser


class RssFeed:
	''' Helper-class for arr
	'''

	def __init__(self, file):
		self._sourcefile = file
		self._sources = self._load(self._sourcefile)
		self._source = list(self._sources.keys())[1]
		self._titles = None
		self._title_of_feed = None
		self._links = None
		self._parser = rss_parser.Parser()


	def _save(self, file, data):
		with open(file, 'w') as f:
			tmp = ''
			
			for key in data:
				pattern = key +','+ data[key] +';'
				tmp += pattern
			
			tmp = tmp[:-1]
			f.write(tmp)

			
	def _load(self, file):
		with open(file, 'r') as f:
			tmp = f.read().strip().split(';')
			d = dict()
			
			for item in tmp:
				key, val = item.split(',')
				d[key] = val
			
			return d


	def add_source(self, key, addr):
		'''	Add new feed to sources: key is name for dropdown-menu and
			addr is its URL-address.
		'''
		self._sources[key] = addr
		
		
	def del_source(self, key=None):
		'''	Key can be the name of the feed or index-number of the feed.
			Remove one feed from sources.
		'''
		if isinstance(key, int): key = sorted(self._sources.keys())[key]
		self._sources.pop(key)
		

	def show_sources(self):
		''' Print all names and URLs of sources.
		'''
		for i,key in enumerate(sorted(self._sources.keys())):
			print('{}: {}\t{}'.format(i, key, self._sources[key]))
			

	def current_source(self):
		''' Print the name and URL of current feed.
		'''
		print(self._source, self._sources[self._source])
		

	def select_source(self, key):
		''' Key can be the name of the feed or index-number of the feed.
		'''
		if isinstance(key, str):
			self._source = key
		else:
			self._source = sorted(self._sources.keys())[key]
		
		try: self._title_of_feed, self._titles, self._links = self._parser.parse(self._sources[self._source])
		except (OSError, ValueError): raise

