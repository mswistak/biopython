import sys

sys.path.append("../Bio")

import ZP


zp = ZP.load("ZP/bar.zp")


print "region dictionary:\n", zp.getRegionsDict()
print
print "region sizes:\n", zp.getRegionSizes()
print "segment max size:", zp.getMaxSegmentSize()
print "segment composition:"
tmp = [(reg.getName(), \
	[s.getSize() for s in reg._segmentList]) \
	for reg in zp.getRegionsIterator()]
print
print "change segment size to 200"
zp.setMaxSegmentSize(200)
print "segment composition:"
tmp = [(reg.getName(), \
	[s.getSize() for s in reg._segmentList]) \
	for reg in zp.getRegionsIterator()]
for i in tmp: print i
print
print "change segment size to 50"
zp.setMaxSegmentSize(50)
print "segment composition:"
tmp = [(reg.getName(), \
	[s.getSize() for s in reg._segmentList]) \
	for reg in zp.getRegionsIterator()]
for i in tmp: print i
print
print "sequences:"
tmp = [(reg.getName(), \
	zp.getSequence(reg.getName())) \
	for reg in zp.getRegionsIterator()]
for i in tmp: print i
print
seq1 = zp.getSequence("reg1")
seq2 = zp.getSequence("reg2")
seq3 = zp.getSequence("reg3")
seq4 = zp.getSequence("reg4")
print "reg1", seq1
print "reg1", [seg.getSize() for seg in zp.getRegion("reg1")._segmentList]
print "set sequence[145:221] to HDSUIFHSHFIUN in region reg1"
zp.setSequence("HDSUIFHSHFIUN", "reg1", 145, 221)
print "reg1", zp.getSequence("reg1")
print "reg1", [seg.getSize() for seg in zp.getRegion("reg1")._segmentList]
print "is the result the same as expected with concatenation?"
print seq1[:145]+"HDSUIFHSHFIUN"+seq1[221:] == zp.getSequence("reg1")
print
print "reg2", seq2
print "reg2", [seg.getSize() for seg in zp.getRegion("reg2")._segmentList]
print "append sequence FDSIOFHSFIJSDFNSIUNODF to region reg2"
zp.appendSequence("FDSIOFHSFIJSDFNSIUNODF", "reg2")
print "reg2", zp.getSequence("reg2")
print "reg2", [seg.getSize() for seg in zp.getRegion("reg2")._segmentList]
print "is the result the same as expected with concatenation?"
print seq2+"FDSIOFHSFIJSDFNSIUNODF" == zp.getSequence("reg2")
print
print "reg3", seq3
print "reg3", [seg.getSize() for seg in zp.getRegion("reg3")._segmentList]
print "prepend sequence UISDHUFHKSFUDSSIFHUSHDIHFSIBUBSFBI to region reg3"
zp.prependSequence("UISDHUFHKSFUDSSIFHUSHDIHFSIBUBSFBI", "reg3")
print "reg3", zp.getSequence("reg3")
print "reg3", [seg.getSize() for seg in zp.getRegion("reg3")._segmentList]
print "is the result the same as expected with concatenation?"
print "UISDHUFHKSFUDSSIFHUSHDIHFSIBUBSFBI"+seq3 == zp.getSequence("reg3")
print
print "reg4", seq4
print "reg4", [seg.getSize() for seg in zp.getRegion("reg4")._segmentList]
print "delete sequence[200:312] from region reg4"
zp.delSequence("reg4", 200, 312)
print "reg4", zp.getSequence("reg4")
print "reg4", [seg.getSize() for seg in zp.getRegion("reg4")._segmentList]
print "is the result the same as expected?"
print seq4[:200]+seq4[312:] == zp.getSequence("reg4")
print
print "save ZPObject"
zp.save()
print "load object into new variable"
zp2 = ZP.load("ZP/bar.zp")
print "compare if regions in both instance are identical"
print "are sequences identical?"
print [(reg, zp.getSequence(reg) == zp2.getSequence(reg)) for reg in zp.getRegionNames()]
print "are segment compositions identical?"
print [(reg, \
	[seg1.getSize() for seg1 in zp.getRegion(reg)._segmentList] == \
	[seg2.getSize() for seg2 in zp2.getRegion(reg)._segmentList]) \
	for reg in zp.getRegionNames()]
#tmp = [(reg, zp.getRegion(reg)._segmentList, zp2.getRegion(reg)._segmentList) \
#	for reg in zp.getRegionNames()]
#for i in tmp:
#	for j in i:
#		print j
#	print

print
print "archivePath for ZPObject:", zp.getPath()
print "archivePath for Regions:\n", \
	[reg._archivePath for reg in zp.getRegionsIterator()]
print "archivePath for Segments:"
tmp = [(reg.getName(), [seg._archivePath for seg in reg._segmentList]) \
	for reg in zp.getRegionsIterator()]
for i in tmp: print i
print
print "change archivePath to foo.zp"
zp.setPath("ZP/foo.zp")
print "archivePath for ZPObject:", zp.getPath()
print "archivePath for Regions:\n", \
	[reg._archivePath for reg in zp.getRegionsIterator()]
print "archivePath for Segments:"
tmp = [(reg.getName(), [seg._archivePath for seg in reg._segmentList]) \
	for reg in zp.getRegionsIterator()]
for i in tmp: print i
print 
print "create new ZPObject from scratch"
zp3 = ZP.ZPObject("ZP/bar.zp", maxSegmentSize=100)
print "zp3 archivePath:", zp3.getPath()
print "zp3 maxSegmentSize:", zp3.getMaxSegmentSize()
print "zp3 regionsDict:", zp3.getRegionsDict()
print "create new region reg1"
r = ZP.Region("", "reg1", 10, seq1)
print "r archivePath:", r._archivePath
print "r maxSegmentSize:", r._maxSegmentSize
print "r sequence:", r.getSequence()
print "r segment composition:\n", [seg.getSize() for seg in r._segmentList]
print "add created region to zp3 using addRegion"
zp3.addRegion(r)
print "zp3 regionsDict:", zp3.getRegionsDict()
print "create new region reg2"
r = ZP.Region("", "reg2", 25, seq2)
print "r archivePath:", r._archivePath
print "r maxSegmentSize:", r._maxSegmentSize
print "r sequence:", r.getSequence()
print "r segment composition:\n", [seg.getSize() for seg in r._segmentList]
print "add created region to zp3 using updateRegion"
zp3.updateRegion(r)
print "zp3 regionsDict:", zp3.getRegionsDict()
print "create 3 more regions using createRegion"
zp3.createRegion("reg3", seq3)
zp3.createRegion("reg4", seq4)
zp3.createRegion("reg5")
print "zp3 regionsDict:", zp3.getRegionsDict()
print "zp3 regionSizes:", zp3.getRegionSizes()
print "archivePath for ZPObject:", zp3.getPath()
print "archivePath for Regions:", \
	[reg._archivePath for reg in zp3.getRegionsIterator()]
print "archivePath for Segments:"
tmp = [(reg.getName(), [seg._archivePath for seg in reg._segmentList]) \
	for reg in zp.getRegionsIterator()]
for i in tmp: print i
print "segment composition of regions"
tmp = [(reg.getName(), \
	[seg.getSize() for seg in reg._segmentList]) \
	for reg in zp3.getRegionsIterator()]
for i in tmp: print i
print "delete region reg5"
zp3.delRegion("reg5")
print "segment composition of regions"
tmp = [(reg.getName(), \
	[seg.getSize() for seg in reg._segmentList]) \
	for reg in zp3.getRegionsIterator()]
for i in tmp: print i
print "save constructed ZPObject"
zp3.save()
