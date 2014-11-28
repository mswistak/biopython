import tarfile, os
import cPickle as pickle

from Region import Region



class ZPObject(object):

	def __init__(self, archivePath, regionDict=None, maxSegmentSize=1000):
		self._archivePath = archivePath
		self._regionDict = regionDict
		self._maxSegmentSize = maxSegmentSize
		self._saved = False

		if regionDict == None or type(regionDict) != dict:
			regionDict = {}


	def _setPath(self, archivePath):
		self._archivePath = archivePath
		for reg in self._regionDict.itervalues():
			reg._setPath(archivePath)


	def setPath(self, archivePath):
		for reg in self._regionDict.itervalues():
			reg.setPath(archivePath)

		if self._saved:
			with tarfile.open(self._archivePath, "r") as tar:
				tar.extract("head")
			os.remove("head")
			os.remove(self._archivePath)

		self._archivePath = archivePath
		self._saved = False


	def getPath(self):
		return self._archivePath


	def getRegionSizes(self):
		rSize = {}
		for reg in self._regionDict.iterkeys():
			rSize[reg] = self._regionDict[reg].getSize()

		return rSize


	def getRegionNames(self):
		return self._regionDict.keys()
			

	def getMaxSegmentSize(self):
		return self._maxSegmentSize


	def setMaxSegmentSize(self, size):
		size = int(size)
		self._maxSegmentSize = size
		for reg in self._regionDict.itervalues():
			reg.setMaxSegmentSize(size)


	def getRegion(self, regionName):
		try:
			return self._regionDict[regionName]
		except KeyError:
			raise KeyError("Region %s does not exist." % regionName)


	def getRegionsDict(self):
		return self._regionDict


	def getRegionsList(self):
		return self._regionDict.values()


	def getRegionsIterator(self):
		return self._regionDict.itervalues()


	def createRegion(self, regionName, sequence=None):
		if regionName not in self._regionDict.keys():
			self._regionDict[regionName] = Region(self._archivePath, regionName, self._maxSegmentSize, sequence)
		else:
			raise ValueError("Region %s already exists." % region.getName())


	def addRegion(self, region):
		if region.getName() not in self._regionDict.keys():
			self._regionDict[region.getName()] = Region(self._archivePath, region.getName(), self._maxSegmentSize, region.getSequence())
		else:
			raise ValueError("Region %s already exists." % region.getName())


	def delRegion(self, regionName):
		try:
			self._regionDict[regionName].delAllSegments()
			del self._regionDict[regionName]
		except KeyError:
			raise KeyError("Region %s does not exist." % regionName)


	def updateRegion(self, region):
		self._regionDict[region.getName()] = Region(self._archivePath, region.getName(), self._maxSegmentSize, region.getSequence())


	def getSequence(self, regionName, start=0, end=None):
		try:
			return self._regionDict[regionName].getSequence(start, end)
		except KeyError:
			raise KeyError("Region %s does not exist." % regionName)


	def setSequence(self, sequence, regionName, start=0, end=None):
		try:
			self._regionDict[regionName].setSequence(sequence, start, end)
		except KeyError:
			self.createRegion(regionName, sequence)


	def appendSequence(self, sequence, regionName):
		try:
			self._regionDict[regionName].appendSequence(sequence)
		except KeyError:
			self.createRegion(regionName, sequence)
		

	def prependSequence(self, sequence, regionName):
		try:
			self._regionDict[regionName].prependSequence(sequence)
		except KeyError:
			self.createRegion(regionName, sequence)
		

	def save(self):
		for reg in self._regionDict.itervalues():
			reg.save()

		if self._saved:
			with tarfile.open(self._archivePath, "r") as tar:
				tar.extract("head")

		pickle.dump(self, open("head", "wb"))
		with tarfile.open(self._archivePath, "a") as tar:
			tar.add("head")

		os.remove("head")
		self._saved = True
