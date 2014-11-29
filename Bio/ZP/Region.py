from Segment import Segment


class Region(object):
	"""
	Object which stores long sequences in Segments of given length. Allows
	performing basic operations on sequences.
	"""

	def __init__(self, archivePath, regionName, maxSegmentSize=1000, sequence=None):
		"""Create Region object."""

		self._archivePath = str(archivePath)
		self._regionName = str(regionName)
		self._maxSegmentSize = int(maxSegmentSize)
		self._segmentList = []
		self._lastIdx = -1

		#if sequence is not empty, create new Segments
		if sequence:
			self.__createNewSegments(sequence)


	def __createNewSegments(self, sequence):
		"""Private method for creating new Segments and adding them to
		the list of Segments"""

		#convert sequence to string
		sequence = str(sequence)

		#how many Segments should be created
		length = len(sequence)
		nSegments = 1 + length/self._maxSegmentSize

		for i in xrange(nSegments):
			#basic sequence bounds for i-th Segment
			start = i*self._maxSegmentSize
			end = (i+1)*self._maxSegmentSize

			#if bounds exceeds sequence length
			if end > length:
				end = length

			#add new Segment to the list
			self._segmentList += \
				[ Segment( \
					self._archivePath, \
					self._regionName + "_seg_" + \
						str(1+i+self._lastIdx), \
					self._maxSegmentSize, \
					sequence[start:end]) \
				]

		#update index of last added element in Segment list
		self._lastIdx = i


	def _setPath(self, archivePath):
		"""Change archivePath for Region and all Segments consisting it.
		Private meth d used only after loading a ZPObject to ensure that
		sequences will be extracted from the appropriate archive even if
		it has been renamed or moved in the filesystem."""

		self._archivePath = archivePath
		for seg in self._segmentList:
			seg._setPath(archivePath)


	def getSize(self):
		"""Get current size of Region."""

		#if Region contains any Segments
		if self._segmentList:
			#calculate how long the sequence should be given list length
			#ask only the last Segmetn for accurate length
			return self._maxSegmentSize*(len(self._segmentList)-1) \
				+ self._segmentList[-1].getSize()

		return 0


	def getName(self):
		"""Get the name of the Region."""

		return self._regionName


	def setMaxSegmentSize(self, size):
		"""Change maximal allowed Segment size. Setting new size will
		trigger deleting all Segments and creating new with different
		size."""

		try:
			#ensure that size is a number
			size = int(size)
		except ValueError:
			raise ValueError("Given size is not a number: %s" % size)

		#if new size is different than before
		if self._maxSegmentSize != size:
			#temporarily save whole sequence and del all Segments
			sequence = self.getSequence()
			self.delAllSegments()

			#change maximal Segment size and create new Segments
			self._maxSegmentSize = size
			self.__createNewSegments(sequence)


	def setPath(self, archivePath):
		"""Change archivePath. Results in removal of files containing
		the sequence from old archive and from the filesystem. Sequence
		will be stored as attributes in the Segment objects until save
		command is invoked."""

		#if sequence is saved in the filesystem
		#and archivePath is different than before
		if self._archivePath != archivePath:
			#update archivePath for Region and all Segments
			self._archivePath = archivePath
			for seg in self._segmentList:
				seg.setPath(archivePath)


	def delSegment(self, idx):
		"""Delete Segments under specified index (list of indexes).
		Results in removal of files containing sequences of specified
		Segments from the archive."""

		#enclose single index to list
		if type(idx) == int:
			idx = [idx]

		#convert negative indexes to positive indexes
		nSegments = len(self._segmentList)
		idx_plus = set([i+nSegments if i < 0 else i for i in idx])

		#delete sequences from specified Segments
		#delete specified Segments from the last to the first
		for i in sorted(list(idx_plus), reverse=True):
			if i < nSegments:
				self._segmentList[i].delSequence()
				self._segmentList = self._segmentList[:i] + self._segmentList[(i+1):]


	def delAllSegments(self):
		"""Delete all Segments in Region. Results in removal of all files
		containing Region sequence from the archive."""

		#delete sequences of all Segments
		for seg in self._segmentList:
			seg.delSequence()

		#update Region attributes
		self._segmentList = []
		self._lastIdx = -1


	def getSequence(self, start=0, end=None):
		"""Access sequence (or subsequence) of the Region."""

		size = self.getSize()

		#if end is not specified,
		#set it to the last character in sequence
		if end == None:
			end = size

		#if start is a negative index, convert it to positive
		if start < 0:
			start += size
		#if start exceeds length, set it to the end of sequence
		elif start > size:
			start = size-1

		#if end is a negative index, convert it to positive
		if end < 0:
			end += size
		#if end exceeds length, set it to the size of sequence
		elif end > size:
			end = size

		#initialize output sequence
		sequence = ""

		#if there are any Segments
		if self._segmentList:
			#get starting and ending Segment
			segStart = start/self._maxSegmentSize
			segEnd = 1 + end/self._maxSegmentSize

			#if end points at the last character in Segment,
			#correct ending Segment
			if end % self._maxSegmentSize == 0:
				segEnd -= 1

			#get sequences from appropriate Segments
			for i in xrange(segStart, segEnd):
				#basic assignment of start and end of Segment
				s = 0
				e = self._maxSegmentSize

				#if sequence start is after Segment start
				if start > i*self._maxSegmentSize:
					s = start - i*self._maxSegmentSize

				#if sequence end is before Segment end
				if end < (i+1)*self._maxSegmentSize:
					e = end - i*self._maxSegmentSize

				#append sequence from i-th Segment to result
				sequence += self._segmentList[i].getSequence(s, e)

		return sequence


	def setSequence(self, sequence, start=0, end=None):
		"""Change sequence (or subsequence) of Region. Results in
		rearangements in existing Segments coupled with removal of
		files containing the sequence from archive and from the
		filesystem. Sequence will be stored as an attribute in the
		Segments object until save command is invoked. May also result
		in removal or creation of Segments."""

		size = self.getSize()

		#if end is not specified,
		#set it to the last character in sequence
		if end == None:
			end = size

		#if start is a negative index, convert it to positive
		if start < 0:
			start += size
		#if start exceeds length, set it to the end of sequence
		elif start > size:
			start = size-1

		#if end is a negative index, convert it to positive
		if end < 0:
			end += size
		#if end exceeds length, set it to the size of sequence
		elif end > size:
			end = size

		seqLen = len(sequence)
		diffLen = seqLen - (end-start)
		i = -1

		#if there are any Segments
		if self._segmentList:
			#get starting and ending Segment
			segStart = start/self._maxSegmentSize
			segEnd = 1 + end/self._maxSegmentSize

			#if end points at the last character in Segment,
			#correct ending Segment
			if end % self._maxSegmentSize == 0:
				segEnd -= 1

			#change sequences from appropriate Segments
			for i in xrange(segStart, segEnd):
				#basic assignment of start and end of Segment
				s = 0
				e = self._maxSegmentSize

				#if sequence start is after Segment start
				if start > i*self._maxSegmentSize:
					s = start - i*self._maxSegmentSize

				#if sequence end is before Segment end
				if end < (i+1)*self._maxSegmentSize:
					e = end - i*self._maxSegmentSize

				#set sequence from i-th Segment to given
				#sequence is updated to didn't fit into i-th Segment
				sequence = self._segmentList[i].setSequence(sequence, s, e)

		#if there is any sequence left to add ie. given sequence was
		#longer than previous and it exceeded specified Segments
		if sequence:
			i += 1

			#add excesive sequence to next Segments (always at the
			#beginning) until there is no sequence to add or there
			#are no Segments left
			while sequence and i < len(self._segmentList):
				sequence = self._segmentList[i].prependSequence(sequence)
				i += 1

			#if there is sequence to add and no Segments with
			#with available space, create new Segments
			if sequence:
				self.__createNewSegments(sequence)

		#if there is no more sequence to add ie. given sequence was
		#shorter than or equal to previous one
		else:
			#if length of substitute is less than length of original
			if diffLen < 0:
				#get Segment in which the substituted sequence ends
				segAdd = (start + seqLen)/self._maxSegmentSize

				#get sequences from all Segments after substitute's end
				for j in xrange(segAdd+1, len(self._segmentList)):
					sequence += self._segmentList[j].getSequence()

				#append sequence to the Segment where substitute ends
				sequence = self._segmentList[segAdd].appendSequence(sequence)

				#set sequence of next Segments to what's left
				for j in xrange(segAdd+1, len(self._segmentList)):
					sequence = self._segmentList[j].setSequence(sequence)

				#delete empty Segments going from the end of the list
				for j in xrange(len(self._segmentList)-1, -1, -1):
					if self._segmentList[j].getSize() == 0:
						self.delSegment(j)
					else: break


	def appendSequence(self, sequence):
		"""Convenience function for appending sequences. See setSequence
		for details."""

		size = self.getSize()
		self.setSequence(sequence, size, size)


	def prependSequence(self, sequence):
		"""Convenience function for prepending sequences. See setSequence
		for details."""

		self.setSequence(sequence, end=0)


	def delSequence(self, start=0, end=None):
		"""Convenience function for deleting sequences. See setSequence
		for details."""

		self.setSequence("", start, end)


	def save(self):
		"""Save the sequence of the Region to the archive."""

		for seg in self._segmentList:
			seg.save()
