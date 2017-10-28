"""
Binary data in the file are compressed when the VTKFile element is of the form

 <VTKFile ... compressor="vtkZLibDataCompressor">

The data corresponding to a data array are stored in a set of blocks which are each compressed using the zlib library. The block structure allows semi-random access without decompressing all data. In uncompressed form all the blocks have the same size except possibly the last block which might be smaller. The data for one array begin with a header of the form

 [#blocks][#u-size][#p-size][#c-size-1][#c-size-2]...[#c-size-#blocks][DATA]

Each token is an integer value whose type is specified by "header_type" at the top of the file (UInt32 if no type specified). The token meanings are:

 [#blocks] = Number of blocks
 [#u-size] = Block size before compression
 [#p-size] = Size of last partial block (zero if it not needed)
 [#c-size-i] = Size in bytes of block i after compression

The [DATA] portion stores contiguously every block appended together. The offset from the beginning of the data section to the beginning of a block is computed by summing the compressed block sizes from preceding blocks according to the header. 


Usage example:
compressvtkfile('timestep_000099.vtu')
"""

import xml.etree.ElementTree as ET
import struct
import base64
import zlib

def element2binary(element, pack_type):
	t=element.text.split()
	if(pack_type=='q' or pack_type=='B'): #Int64 or UInt8
		s=[int(i) for i in t]
	elif(pack_type=='d'): #double
		s=[float(i) for i in t]	
	else:
		print("wrong type")
		exit(1)

	if(pack_type in 'qd'):
		mult=8
	else:
		mult=1

	#if(pack_type=='q'): #reduce integer to int32
	#	mult=4
	#	pack_type='L'
	#	element.set('type','UInt32')	
	b=struct.pack(pack_type*len(s),*s)
	#blen=struct.pack('I',mult*len(s))
	cmprs=zlib.compress(b,6)
	sizes=[1,len(b),len(b),len(cmprs)]
	header=struct.pack('I'*4,*sizes)
	element.text=base64.b64encode(header).decode('ascii')+base64.b64encode(cmprs).decode('ascii')
	element.set('format','binary')	
	
def compressvtkfile(filename):
	try:
		tree = ET.parse(filename)
	except:
		print("Error reading snapshot file")

	iterator=tree.iter()

	for element in iterator:
		#UInt8, Int64, Float64
		if element.get('type')=='UnstructuredGrid':
			element.set('compressor','vtkZLibDataCompressor')
		if element.get('type')=='Int64':
			element2binary(element,'q')

		if element.get('type')=='UInt8':
			element2binary(element,'B')
		if element.get('type')=='Float64':
			element2binary(element,'d')

	tree.write("test.vtu")

	#now compress the trisurf part:
	with open('test.vtu', 'r') as file:
		c=file.read()
	i=c.find('<trisurf ')
	j=c.find('>',i)
	k=c.find('</trisurf>',j)
	cs=c[j+1:k]
	fields=c[i:j+1].split()
	fields=[s.replace('false','true') for s in fields]
	starttag=' '.join(fields)
	cmprs=zlib.compress(cs.encode('ascii'),6)
	cmprs=base64.b64encode(cmprs)
	cc=c[0:i]+starttag+cmprs.decode('ascii')+c[k:]
	with open('test1.vtu', 'w') as file:
		file.write(cc)

