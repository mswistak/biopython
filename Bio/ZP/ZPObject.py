import tarfile, os
import cPickle as pickle

from Region import Region



class ZPObject(object):
	"""
	Object which stores collections of long sequences grouped in Regions.
	Each Region consists of Segments of a given length.
	"""

	def __init__(self, archivePath, regionDict=None, maxSegmentSize=1000):
		"""Create ZPObject"""

		self._archivePath = str(archivePath)
		self._regionDict = regionDict
		self._maxSegmentSize = int(maxSegmentSize)
		self._saved = False

		if regionDict is None or type(regionDict) != dict:
			self._regionDict = {}


	def _setPath(self, archivePath):
		"""Change archivePath for ZPObject, all Regions and all Segments
		consisting it. Private method used only after loading a ZPObject
		to ensure that sequences will be extracted from the appropriate
		archive even if it has been renamed or moved in the filesystem."""

		self._archivePath = archivePath
		for reg in self._regionDict.itervalues():
			reg._setPath(archivePath)


	def setPath(self, archivePath):
		"""Change archivePath. Results in removal of files containing
		the sequence from old archive and from the filesystem. Sequence
		will be stored as attributes in the Segment objects until save
		command is invoked."""

		#change archivePath for each Region
		for reg in self._regionDict.itervalues():
			reg.setPath(archivePath)

		#if ZPObject has been saved
		if self._saved:
			#extract file containing ZPObject instance from archive
			with tarfile.open(self._archivePath, "r") as tar:
				tar.extract("head")

			#remove file with object and archive from filesystem
			os.remove("head")
			os.remove(self._archivePath)

		#set new archivePath and change flag (ZPObject is not saved)
		self._archivePath = archivePath
		self._saved = False


	def getPath(self):
		"""Get current path to archive."""

		return self._archivePath


	def getRegionSizes(self):
		"""Get dictionary of sizes of Regions."""

		rSize = {}
		for reg in self._regionDict.iterkeys():
			rSize[reg] = self._regionDict[reg].getSize()

		return rSize


	def getRegionNames(self):
		"""Get list of Regions' names."""

		return self._regionDict.keys()
			

	def getMaxSegmentSize(self):
		"""Get maximal Segment size."""

		return self._maxSegmentSize


	def setMaxSegmentSize(self, size):
		"""Change maximal allowed Segment size. Setting new size will
		trigger deleting all Segments and creating new with different
		size."""

		try:
			#ensure that size is a number
			size = int(size)
		except ValueError:
			raise ValueError("Given size is not a number: %s" % size)

		#change size for ZPObject and all Regions
		self._maxSegmentSize = size
		for reg in self._regionDict.itervalues():
			reg.setMaxSegmentSize(size)


	def getRegion(self, regionName):
		"""Get Region by its name."""

		try:
			return self._regionDict[regionName]
		except KeyError:
			raise KeyError("Region %s does not exist." % regionName)


	def getRegionsDict(self):
		"""Get dictionary of Regions."""

		return self._regionDict


	def getRegionsList(self):
		"""Get list of Region objects."""

		return self._regionDict.values()


	def getRegionsIterator(self):
		"""Get iterator over Region objects."""

		return self._regionDict.itervalues()


	def createRegion(self, regionName, sequence=None):
		"""Create new Region with specified name and sequence if there
		is no Region with a given name."""

		if regionName not in self._regionDict.keys():
			self._regionDict[regionName] = \
				Region(self._archivePath, \
					regionName, \
					self._maxSegmentSize, \
					sequence)
		else:
			raise ValueError("Region %s already exists." % regionName)


	def addRegion(self, region):
		"""Add copy of a given Region obbject if there is no Region with
		the same name."""

		self.createRegion(region.getName(), region.getSequence())


	def delRegion(self, regionName):
		"""Delete Region with specified name."""

		try:
			self._regionDict[regionName].delAllSegments()
			del self._regionDict[regionName]
		except KeyError:
			raise KeyError("Region %s does not exist." % regionName)


	def updateRegion(self, region):
		"""Add copy of a given Region no matter if Region with the same
		name exists or not. If such Region exists it will be overridden."""

		self._regionDict[region.getName()] = \
				Region(self._archivePath, \
					region.getName(), \
					self._maxSegmentSize, \
					region.getSequence())


	def getSequence(self, regionName, start=0, end=None):
		"""Access sequence (or subsequence) of a given Region."""

		try:
			return self._regionDict[regionName].getSequence(start, end)
		except KeyError:
			raise KeyError("Region %s does not exist." % regionName)


	def setSequence(self, sequence, regionName, start=0, end=None):
		"""Change sequence (or subsequence) of a given Region."""

		try:
			self._regionDict[regionName].setSequence(sequence, start, end)
		except KeyError:
			self.createRegion(regionName, sequence)


	def appendSequence(self, sequence, regionName):
		"""Append sequence to a Region."""

		try:
			self._regionDict[regionName].appendSequence(sequence)
		except KeyError:
			self.createRegion(regionName, sequence)
		

	def prependSequence(self, sequence, regionName):
		"""Prepend sequence to a Region."""

		try:
			self._regionDict[regionName].prependSequence(sequence)
		except KeyError:
			self.createRegion(regionName, sequence)
		

	def delSequence(self, regionName, start=0, end=None):
		"""Delete sequence from a Region."""

		try:
			self._regionDict[regionName].delSequence(start, end)
		except KeyError:
			raise KeyError("Region %s does not exist." % regionName)
		

	def save(self):
		"""Save ZPObject along with all sequences."""

		#save all regions
		for reg in self._regionDict.itervalues():
			reg.save()

		#if ZPObject has been saved
		if self._saved:
			#extract file containing ZPObject instance
			with tarfile.open(self._archivePath, "r") as tar:
				tar.extract("head")

		#save instance to file
		pickle.dump(self, open("head", "wb"))

		#add saved instance to archive
		with tarfile.open(self._archivePath, "a") as tar:
			tar.add("head")

		#clean-up
		os.remove("head")

		#update flag; ZPObject has been saved
		self._saved = True
