from ctypes import *

TS_SUCCESS=0
TS_FAIL=1

TS_ID_FILAMENT=1

TS_COORD_CARTESIAN=0
TS_COORD_SPHERICAL=1
TS_COORD_CYLINDRICAL=2


class ts_coord(Structure):
	_fields_=[
		("e1", c_double),
		("e2", c_double),
		("e3", c_double),
		("coord_type", c_uint)
		]
class ts_vertex(Structure):
	pass
class ts_bond(Structure):
	pass
class ts_triangle(Structure):
	pass
class ts_cell(Structure):
	pass
class ts_poly(Structure):
	pass
class ts_cluster(Structure):
	pass
ts_vertex._fields_=[
		('idx',c_uint),
		('x',c_double),
		('y',c_double),
		('z',c_double),
		('neigh_no',c_uint),
		('neigh', POINTER(POINTER(ts_vertex))),
		('bond_length', POINTER(c_double)),
		('bond_length_dual',POINTER(c_double)),
		('curvature', c_double),
		('energy', c_double),
		('energy_h',c_double),
		('tristar_no', c_uint),
		('tristar', POINTER(POINTER(ts_triangle))),
		('bond_no',c_uint),
		('bond',POINTER(POINTER(ts_bond))),
		('cell',POINTER(ts_cell)),
		('xk',c_double),
		('c',c_double),
		('id', c_uint),
		('projArea',c_double),
		('relR', c_double),
		('solAngle', c_double),
		('grafted_poly', POINTER(ts_poly)),
		('cluster',POINTER(ts_cluster)),
		]
class ts_vertex_list(Structure):
	_fields_=[('n',c_uint), ('vtx',POINTER(POINTER(ts_vertex)))]

ts_bond._fields_=[('idx',c_uint),
		('vtx1', POINTER(ts_vertex)),
		('vtx2', POINTER(ts_vertex)),
		('bond_length',c_double),
		('bond_length_dual',c_double),
		('tainted', c_char),
		('energy',c_double),
		('x',c_double),
		('y',c_double),
		('z',c_double),
	]
class ts_bond_list(Structure):
	_fields_=[('n', c_uint),('bond',POINTER(POINTER(ts_bond)))]

ts_triangle._fields_=[
		('idx',c_uint),
		('vertex', POINTER(ts_vertex)*3),
		('neigh_no',c_uint),
		('neigh', POINTER(POINTER(ts_triangle))),
		('xnorm', c_double),
		('ynorm', c_double),
		('znorm', c_double),
		('area', c_double),
		('volume', c_double),
	]

class ts_triangle_list(Structure):
	_fields_=[('n',c_uint),('tria', POINTER(POINTER(ts_triangle)))]


ts_cell._fields_=[
	('idx', c_uint),
	('vertex', POINTER(POINTER(ts_vertex))),
	('nvertex', c_uint),
	]		

class ts_cell_list(Structure):
	_fields_=[
		('ncmax', c_uint*3),
		('cellno', c_uint),
		('cell',POINTER(POINTER(ts_cell))),
		('dcell', c_double),
		('shift', c_double),
		('max_occupancy', c_double),
		('dmin_interspecies', c_double)
	]

class ts_spharm(Structure):
	_fields_=[
		('l',c_uint),
		('ulm', POINTER(POINTER(c_double))),
	#	('ulmComplex', POINTER(POINTER(gsl_complex))), #poisci!!!!
		('ulmComplex', POINTER(POINTER(c_double))), #temporary solution
		('sumUlm2', POINTER(POINTER(c_double))),
		('N', c_uint),
		('co',POINTER(POINTER(c_double))),
		('Ylmi', POINTER(POINTER(c_double))),
		]

ts_poly._fields_=[
		('vlist', POINTER(ts_vertex_list)),
		('blist', POINTER(ts_bond_list)),
		('grafted_vtx',POINTER(ts_vertex)),
		('k', c_double),
	]

class ts_poly_list(Structure):
	_fields_=[('n',c_uint),('poly',POINTER(POINTER(ts_poly)))]

class ts_tape(Structure):
	_fields_=[
		('nshell',c_long),
		('ncxmax',c_long),
		('ncymax',c_long),
		('nczmax',c_long),
		('npoly',c_long),
		('nmono',c_long),
		('internal_poly',c_long),
		('nfil',c_long),
		('nfono', c_long),
		('R_nucleus',c_long),
		('R_nucleusX',c_double),
		('R_nucleusY',c_double),
		('R_nucleusZ',c_double),
		('pswitch',c_long),
		('constvolswitch',c_long),
		('constareaswitch',c_long),
		('constvolprecision',c_double),
		('multiprocessing',c_char_p),
		('brezveze0',c_long),
		('brezveze1',c_long),
		('brezveze2',c_long),
		('xk0',c_double),
		('dmax',c_double),
		('dmin_interspecies',c_double),
		('stepsize',c_double),
		('kspring',c_double),
		('xi',c_double),
		('pressure',c_double),
		('iterations',c_long),
		('inititer',c_long),
		('mcsweeps',c_long),
		('quiet',c_long),
		('shc',c_long),
		('number_of_vertice_with_c0',c_long),
		('c0', c_double),
		('w', c_double),
		('F', c_double),
	]
		

class ts_vesicle(Structure):
	_fields_=[
		('vlist', POINTER(ts_vertex_list)),
		('blist', POINTER(ts_bond_list)),
		('tlist', POINTER(ts_triangle_list)),
		('clist', POINTER(ts_cell_list)),
		('nshell', c_uint),
		('bending_rigidity',c_double),
		('dmax',c_double),
		('stepsize',c_double),
		('cm', c_double*3),
		('volume', c_double),
		('sphHarmonics',POINTER(ts_spharm)),
		('poly_list', POINTER(ts_poly_list)),
		('filament_list', POINTER(ts_poly_list)),
		('spring_constant', c_double),
		('pressure', c_double),
		('pswitch', c_int),
		('tape', POINTER(ts_tape)),
		('R_nucleus', c_double),
		('R_nucleusX', c_double),
		('R_nucleusY', c_double),
		('R_nucleusZ', c_double),
		('nucleus_center', c_double *3 ),
		('area', c_double),
	]

ts_cluster._fields_=[('nvtx',c_uint),('idx',c_uint),('vtx', POINTER(POINTER(ts_vertex)))]

class ts_cluster_list(Structure):
	_fields_=[('n',c_uint),('poly',POINTER(POINTER(ts_cluster)))]

