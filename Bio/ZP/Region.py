from Segment import Segment


class Region(object):

	def __init__(self, archivePath, regionName, maxSegmentSize=1000, sequence=None):
		self.archivePath = archivePath
		self.regionName = regionName
		self.maxSegmentSize = maxSegmentSize
		self.segmentList = []
		self.lastIdx = -1

		if sequence:
			self.__createNewSegments(sequence)


	def __createNewSegments(self, sequence):
		length = len(sequence)
		nSegments = 1 + length/self.maxSegmentSize
		for i in xrange(nSegments):
			start = i*self.maxSegmentSize
			end = (i+1)*self.maxSegmentSize
			if end > length:
				end = length

			self.segmentList += [Segment(self.archivePath, self.regionName + "_seg_" + str(1+i+self.lastIdx), self.maxSegmentSize, sequence[start:end])] 
		self.lastIdx = i



	def getSize(self):
		if self.segmentList:
			return self.maxSegmentSize*(len(self.segmentList)-1) + self.segmentList[-1].getSize()

		return 0


	def getName(self):
		return self.regionName


	def setMaxSegmentSize(self, size):
		if self.maxSegmentSize != size:
			sequence = self.getSequence()
			self.delAllSegments()
			self.maxSegmentSize = size
			self.__createNewSegments(sequence)


	def setPath(self, archivePath):
		if self.archivePath != archivePath:
			self.archivePath = archivePath
			for seg in self.segmentList:
				seg.setPath(archivePath)


	def delSegment(self, idx):
		if type(idx) == int:
			idx = [idx]

		nSegments = len(self.segmentList)
		idx_plus = set([i+nSegments if i < 0 else i for i in idx])

		for i in sorted(list(idx_plus), reverse=True):
			if i < nSegments:
				self.segmentList[i].delSequence()
				self.segmentList = self.segmentList[:i] + self.segmentList[(i+1):]


	def delAllSegments(self):
		for seg in self.segmentList:
			seg.delSequence()
		self.segmentList = []
		self.lastIdx = -1


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
			segStart = start/self.maxSegmentSize
			segEnd = 1 + end/self.maxSegmentSize
			if end % self.maxSegmentSize == 0:
				segEnd -= 1

			for i in xrange(segStart, segEnd):
				s = 0
				e = self.maxSegmentSize
				if start > i*self.maxSegmentSize:
					s = start - i*self.maxSegmentSize
				if end < (i+1)*self.maxSegmentSize:
					e = end - i*self.maxSegmentSize
				sequence += self.segmentList[i].getSequence(s, e)

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

		if self.segmentList:
			segStart = start/self.maxSegmentSize
			segEnd = 1 + end/self.maxSegmentSize
			if end % self.maxSegmentSize == 0:
				segEnd -= 1

			for i in xrange(segStart, segEnd):
				s = 0
				e = self.maxSegmentSize

				if start > i*self.maxSegmentSize:
					s = start - i*self.maxSegmentSize

				if end < (i+1)*self.maxSegmentSize:
					e = end - i*self.maxSegmentSize

				sequence = self.segmentList[i].setSequence(sequence, s, e)

		if sequence:
			i += 1

			while sequence and i < len(self.segmentList):
				sequence = self.segmentList[i].prependSequence(sequence)
				i += 1

			if sequence:
				self.__createNewSegments(sequence)
		else:
			if diffLen < 0:
				segAdd = (start + seqLen)/self.maxSegmentSize
				for j in xrange(segAdd+1, len(self.segmentList)):
					sequence += self.segmentList[j].getSequence()

				sequence = self.segmentList[segAdd].appendSequence(sequence)

				for j in xrange(segAdd+1, len(self.segmentList)):
					sequence = self.segmentList[j].setSequence(sequence)

				for j in xrange(len(self.segmentList)-1, -1, -1):
					if self.segmentList[j].getSize() == 0:
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
		for seg in self.segmentList:
			seg.save()
