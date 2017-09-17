from . import trisurf


def analysis(*args):
	"""Decorator for adding the analysis functions to function lists"""
	def analysis_decorator(analysis_function):
		trisurf._analysis_list[analysis_name]=analysis_function
		def wrapper(*args, **kwargs):
			analysis_function(*args,**kwargs)
		return wrapper
	if len(args) == 1 and callable(args[0]): #no arguments
		analysis_name=args[0].__name__
		return analysis_decorator(args[0])
	else:
		analysis_name=args[0]
		return analysis_decorator


@analysis
def demo(run, **kwargs):
	host=kwargs.get('host', None)
	print("Demo analysis")
	print("Analysis on host "+host['name']+" for run "+run.Dir.fullpath()+" completed")
	print("here comes info on the run variable:")
	print(run)
	print("here comes info on the host variable:")
	print(host)
	print("here comes info on the args variable:")
	print(kwargs.get('args',None))


# can be wrapped to specify scalar_field)
@analysis('plotrunningavginteractive')
def plotrunningavginteractive(run, scalar_field='vertices_idx', **kwargs):
	import matplotlib.pyplot as plt
	from trisurf import VTKRendering as vtk
	import math
	from multiprocessing import Process
	table=trisurf.Statistics(run.Dir.fullpath(),filename='poststat.csv').getTable()
	def running_avg(col):
		import numpy as np
		avg=[]	
		for i in range(0,len(col)):
			avg.append(np.average(col[:-i]))
		return avg
	def spawned_viewer(n):
		vtk.Renderer(kwargs.get('args', None),kwargs.get('host',None),run, timestep=n,scalar_field=scalar_field)

	fig=plt.figure(1)
	ra=running_avg(table['hbar'])
	l=len(table['hbar'])
	plt.plot(ra)
	plt.title('Running average')
	plt.ylabel('1/n sum_i=niter^n(hbar_i)')
	plt.xlabel('n')
	def onclick(event):
		#print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' % (event.button, event.x, event.y, event.xdata, event.ydata))
		p=Process(target=spawned_viewer, args=(l-math.floor(event.xdata)-1,))
		p.start()
	cid = fig.canvas.mpl_connect('button_press_event', onclick)
	plt.show()
	plt.close(1)


# -------------------------------
# these functions should be wrapped
# -------------------------------
@analysis('plotColumnFromPostProcess')
def plotColumnFromPostProcess(run, filename='poststat.csv', column='hbar', **kwargs):
	import matplotlib.pyplot as plt

	def smooth(y, box_pts):
		import numpy as np
		box = np.ones(box_pts)/box_pts
		y_smooth = np.convolve(y, box, mode='same')
		return y_smooth
	table=trisurf.Statistics(run.Dir.fullpath(),filename=filename).getTable()
	plt.plot(table[column], '.')
	plt.title(run.Dir.fullpath())
	plt.xlabel('Iteration')
	plt.ylabel(column)
	smooth_window=10
	smoothed=smooth(table[column],smooth_window)
	plt.plot(tuple(range(int(smooth_window/2),len(smoothed)-int(smooth_window/2))),smoothed[int(smooth_window/2):-int(smooth_window/2)])
	plt.show()
	print
	#if return False or no return statement, the analysis will continue with next running instance in the list. if return True, the analysis will stop after this run.
	return False


