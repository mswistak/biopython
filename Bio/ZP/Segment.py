import tarfile, zlib, os
import cPickle as pickle


class Segment(object):

	def __init__(self, archivePath, segmentName, maxSegmentSize, sequence):
		self._archivePath = archivePath
		self._segmentName = segmentName
		self._maxSegmentSize = maxSegmentSize
		self._sequence = sequence
		self._segmentSize = len(sequence)


	def _setPath(self, archivePath):
		self._archivePath = archivePath


	def setPath(self, archivePath):
		if self._sequence == None:
			self._sequence = self.getSequence()

			with tarfile.open(self._archivePath, "r") as tar:
				tar.extract(self._segmentName)
			os.remove(self._segmentName)

		self._archivePath = archivePath


	def getSize(self):
		return self._segmentSize


	def getMaxSize(self):
		return self._maxSegmentSize


	def getSequence(self, start=0, end=None):
		if end == None:
			end = self._segmentSize

		if self._sequence != None:
			return self._sequence[start:end]
		else:
			with tarfile.open(self._archivePath, "r") as tar:
				sequence = zlib.decompress( pickle.load( tar.extractfile(self._segmentName) ) )

			return sequence[start:end]


	def setSequence(self, newSeq, start=0, end=None):
		if end == None:
			end = self._segmentSize
		seq = self.getSequence()
		
		if self._sequence == None:
			with tarfile.open(self._archivePath, "r") as tar:
				tar.extract(self._segmentName)
			os.remove(self._segmentName)

		seq = seq[:start] + newSeq + seq[end:]

		if len(seq) > self._maxSegmentSize:
			self._sequence = seq[:self._maxSegmentSize]
		else:
			self._sequence = seq
		self._segmentSize = len(self._sequence)

		return seq[self._segmentSize:]


	def appendSequence(self, sequence):
		return self.setSequence(sequence, self._segmentSize)


	def prependSequence(self, sequence):
		return self.setSequence(sequence, end=0)


	def delSequence(self, start=0, end=None):
		self.setSequence('', start, end)


	def save(self):
		if self._sequence:
			pickle.dump( zlib.compress(self._sequence), open(self._segmentName, "wb") )

			with tarfile.open(self._archivePath, "a") as tar:
				tar.add(self._segmentName)

			self._sequence = None
			os.remove(self._segmentName)
