import tarfile, os
import cPickle as pickle


from ZPObject import ZPObject
from Region import Region
from Segment import Segment


def load(archivePath):
	"""Function for loading ZPObjects from archive files."""

	#extract ZPObject from archive
	with tarfile.open(archivePath, "r") as tar:
		zp = pickle.load( tar.extractfile("head") )

	#change archivePath for ZPObject in case it is other than saved in
	#extracted instance
	zp._setPath(archivePath)
	return zp
