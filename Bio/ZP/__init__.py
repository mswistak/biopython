import tarfile, os
import cPickle as pickle


from ZPObject import ZPObject
from Region import Region
from Segment import Segment


def load(archivePath):
	with tarfile.open(archivePath, "r") as tar:
		zp = pickle.load( tar.extractfile("head") )

	zp._setPath(archivePath)
	return zp
