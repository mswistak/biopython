import tarfile, zlib, os
import cPickle as pickle


class Segment(object):
	"""
	Object which stores sequences up to a given length. Allows performing
	basic operations on sequences.
	"""

	def __init__(self, archivePath, segmentName, maxSegmentSize, sequence):
		"""Create Segment object."""

		self._archivePath = str(archivePath)
		self._segmentName = str(segmentName)
		self._maxSegmentSize = int(maxSegmentSize)
		self._sequence = str(sequence)
		self._segmentSize = len(self._sequence)


	def _setPath(self, archivePath):
		"""Change archivePath. Private method used only after loading
		a ZPObject to ensure that sequences will be extracted from the
		appropriate archive even if it has been renamed or moved in the
		filesystem."""

		self._archivePath = str(archivePath)


	def setPath(self, archivePath):
		"""Change archivePath. Results in removal of file containing
		the sequence from old archive and from the filesystem. Sequence
		will be stored as an attribute in the Segment object until save
		command is invoked."""

		#if sequence is saved in the filesystem
		#and archivePath is different than before
		if self._sequence == None and self._archivePath != archivePath:
			#keep sequence explicitly in Segment instance
			self._sequence = self.getSequence()

			#extract file containing sequence from archive
			with tarfile.open(self._archivePath, "r") as tar:
				tar.extract(self._segmentName)

			#remove extracted file from filesystem
			os.remove(self._segmentName)

		#change archivePath
		self._archivePath = str(archivePath)


	def getSize(self):
		"""Get current length of sequence contained in Segment."""

		return self._segmentSize


	def getMaxSize(self):
		"""Get maximal allowed size for Segment."""

		return self._maxSegmentSize


	def getSequence(self, start=0, end=None):
		"""Access sequence (or subsequence) kept in Segment."""

		#if end is not specified,
		#set it to the last character in sequence
		if end == None:
			end = self._segmentSize

		#if sequence is stored explicitly in Segment instance
		if self._sequence != None:
			return self._sequence[start:end]

		#if sequence is stored in the archive
		else:
			#access archive
			with tarfile.open(self._archivePath, "r") as tar:
				#load and decompress sequence
				sequence = zlib.decompress( \
					pickle.load( \
					tar.extractfile(self._segmentName) \
							) )

			return sequence[start:end]


	def setSequence(self, newSeq, start=0, end=None):
		"""Change sequence (or subsequence) kept in Segment. Results in
		removal of file containing the sequence from archive and from
		the filesystem. Sequence will be stored as an attribute in the
		Segment object until save command is invoked. In case changed
		sequence is longer than maximal Segment size, this fuction returns
		the suffix which sticked out (it may be an empty string)."""

		#if end is not specified,
		#set it to the last character in sequence
		if end == None:
			end = self._segmentSize

		#get current sequence
		seq = self.getSequence()
		
		#if sequence is stored in the archive
		if self._sequence == None:
			#access archive
			with tarfile.open(self._archivePath, "r") as tar:
				#extract file containing sequence from archive
				tar.extract(self._segmentName)

			#remove extracted file from filesystem
			os.remove(self._segmentName)

		#prepare new sequence
		seq = seq[:start] + newSeq + seq[end:]

		#if sequence is longer than specified limit
		if len(seq) > self._maxSegmentSize:
			#saved new trimmed sequence
			self._sequence = seq[:self._maxSegmentSize]

		#if sequence length is within specified limit
		else:
			#save whole new sequence
			self._sequence = seq

		#update current segment size
		self._segmentSize = len(self._sequence)

		#return excesive sequence
		return seq[self._segmentSize:]


	def appendSequence(self, sequence):
		"""Convenience function for appending sequences. See setSequence
		for details."""

		return self.setSequence(sequence, self._segmentSize)


	def prependSequence(self, sequence):
		"""Convenience function for prepending sequences. See setSequence
		for details."""

		return self.setSequence(sequence, end=0)


	def delSequence(self, start=0, end=None):
		"""Convenience function for deleting sequences. See setSequence
		for details. It does not return any excesive sequence."""

		self.setSequence('', start, end)


	def save(self):
		"""Save the sequence contained in Segment to the archive."""

		#if sequence is not already in the archive
		if self._sequence:
			#compress and save sequence to a file
			pickle.dump( \
				zlib.compress(self._sequence), \
				open(self._segmentName, "wb") \
				)

			#add saved sequence file to the archive
			with tarfile.open(self._archivePath, "a") as tar:
				tar.add(self._segmentName)

			#update status of sequence attribute
			#it no longer  stores sequence explicitly
			self._sequence = None

			#remove unnecessary file in filesystem
			os.remove(self._segmentName)
