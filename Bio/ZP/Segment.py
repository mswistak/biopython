import tarfile, zlib, os
import cPickle as pickle


class Segment(object):

	def __init__(self, archivePath, segmentName, maxSegmentSize, sequence):
		self.archivePath = archivePath
		self.segmentName = segmentName
		self.maxSegmentSize = maxSegmentSize
		self.sequence = sequence
		self.segmentSize = len(sequence)


	def setPath(self, archivePath):
		if self.sequence == None:
			self.sequence = self.getSequence()

			with tarfile.open(self.archivePath, "r") as tar:
				tar.extract(self.segmentName)
			os.remove(self.segmentName)

		self.archivePath = archivePath


	def getSize(self):
		return self.segmentSize


	def getMaxSize(self):
		return self.maxSegmentSize


	def getSequence(self, start=0, end=None):
		if end == None:
			end = self.segmentSize

		if self.sequence != None:
			return self.sequence[start:end]
		else:
			with tarfile.open(self.archivePath, "r") as tar:
				sequence = zlib.decompress( pickle.load( tar.extractfile(self.segmentName) ) )

			return sequence[start:end]


	def setSequence(self, newSeq, start=0, end=None):
		if end == None:
			end = self.segmentSize
		seq = self.getSequence()
		
		if self.sequence == None:
			with tarfile.open(self.archivePath, "r") as tar:
				tar.extract(self.segmentName)
			os.remove(self.segmentName)

		seq = seq[:start] + newSeq + seq[end:]

		if len(seq) > self.maxSegmentSize:
			self.sequence = seq[:self.maxSegmentSize]
		else:
			self.sequence = seq
		self.segmentSize = len(self.sequence)

		return seq[self.segmentSize:]


	def appendSequence(self, sequence):
		return self.setSequence(sequence, self.segmentSize)


	def prependSequence(self, sequence):
		return self.setSequence(sequence, end=0)


	def delSequence(self, start=0, end=None):
		self.setSequence('', start, end)


	def save(self):
		if self.sequence:
			pickle.dump( zlib.compress(self.sequence), open(self.segmentName, "wb") )

			with tarfile.open(self.archivePath, "a") as tar:
				tar.add(self.segmentName)

			self.sequence = None
			os.remove(self.segmentName)
