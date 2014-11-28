from Segment import Segment


class Region(object):

	def __init__(self, archivePath, regionName, maxSegmentSize=1000, sequence=None):
		self._archivePath = archivePath
		self._regionName = regionName
		self._maxSegmentSize = maxSegmentSize
		self._segmentList = []
		self._lastIdx = -1

		if sequence:
			self.__createNewSegments(sequence)


	def __createNewSegments(self, sequence):
		length = len(sequence)
		nSegments = 1 + length/self._maxSegmentSize
		for i in xrange(nSegments):
			start = i*self._maxSegmentSize
			end = (i+1)*self._maxSegmentSize
			if end > length:
				end = length

			self._segmentList += [Segment(self._archivePath, self._regionName + "_seg_" + str(1+i+self._lastIdx), self._maxSegmentSize, sequence[start:end])] 
		self._lastIdx = i


	def _setPath(self, archivePath):
		self._archivePath = archivePath
		for seg in self._segmentList:
			seg._setPath(archivePath)


	def getSize(self):
		if self._segmentList:
			return self._maxSegmentSize*(len(self._segmentList)-1) + self._segmentList[-1].getSize()

		return 0


	def getName(self):
		return self._regionName


	def setMaxSegmentSize(self, size):
		if self._maxSegmentSize != size:
			sequence = self.getSequence()
			self.delAllSegments()
			self._maxSegmentSize = size
			self.__createNewSegments(sequence)


	def setPath(self, archivePath):
		if self._archivePath != archivePath:
			self._archivePath = archivePath
			for seg in self._segmentList:
				seg.setPath(archivePath)


	def delSegment(self, idx):
		if type(idx) == int:
			idx = [idx]

		nSegments = len(self._segmentList)
		idx_plus = set([i+nSegments if i < 0 else i for i in idx])

		for i in sorted(list(idx_plus), reverse=True):
			if i < nSegments:
				self._segmentList[i].delSequence()
				self._segmentList = self._segmentList[:i] + self._segmentList[(i+1):]


	def delAllSegments(self):
		for seg in self._segmentList:
			seg.delSequence()
		self._segmentList = []
		self._lastIdx = -1


	def getSequence(self, start=0, end=None):
		size = self.getSize()
		if end == None:
			end = size

		if start < 0:
			start += size
		elif start > size:
			start = size-1

		if end < 0:
			end += size
		elif end > size:
			end = size

		sequence = ""

		if end:
			segStart = start/self._maxSegmentSize
			segEnd = 1 + end/self._maxSegmentSize
			if end % self._maxSegmentSize == 0:
				segEnd -= 1

			for i in xrange(segStart, segEnd):
				s = 0
				e = self._maxSegmentSize
				if start > i*self._maxSegmentSize:
					s = start - i*self._maxSegmentSize
				if end < (i+1)*self._maxSegmentSize:
					e = end - i*self._maxSegmentSize
				sequence += self._segmentList[i].getSequence(s, e)

		return sequence


	def setSequence(self, sequence, start=0, end=None):
		size = self.getSize()
		if end == None:
			end = size

		if start < 0:
			start += size
		elif start > size:
			start = size-1

		if end < 0:
			end += size
		elif end > size:
			end = size

		seqLen = len(sequence)
		diffLen = seqLen - (end-start)
		i = -1

		if self._segmentList:
			segStart = start/self._maxSegmentSize
			segEnd = 1 + end/self._maxSegmentSize
			if end % self._maxSegmentSize == 0:
				segEnd -= 1

			for i in xrange(segStart, segEnd):
				s = 0
				e = self._maxSegmentSize

				if start > i*self._maxSegmentSize:
					s = start - i*self._maxSegmentSize

				if end < (i+1)*self._maxSegmentSize:
					e = end - i*self._maxSegmentSize

				sequence = self._segmentList[i].setSequence(sequence, s, e)

		if sequence:
			i += 1

			while sequence and i < len(self._segmentList):
				sequence = self._segmentList[i].prependSequence(sequence)
				i += 1

			if sequence:
				self.__createNewSegments(sequence)
		else:
			if diffLen < 0:
				segAdd = (start + seqLen)/self._maxSegmentSize
				for j in xrange(segAdd+1, len(self._segmentList)):
					sequence += self._segmentList[j].getSequence()

				sequence = self._segmentList[segAdd].appendSequence(sequence)

				for j in xrange(segAdd+1, len(self._segmentList)):
					sequence = self._segmentList[j].setSequence(sequence)

				for j in xrange(len(self._segmentList)-1, -1, -1):
					if self._segmentList[j].getSize() == 0:
						self.delSegment(j)
					else: break


	def appendSequence(self, sequence):
		size = self.getSize()
		self.setSequence(sequence, size, size)


	def prependSequence(self, sequence):
		self.setSequence(sequence, end=0)


	def delSequence(self, start=0, end=None):
		self.setSequence("", start, end)


	def save(self):
		for seg in self._segmentList:
			seg.save()
