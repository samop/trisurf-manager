import argparse
import paramiko
from . import Remote
from . import trisurf
import socket
import os,sys
import tabulate
import subprocess,re
import psutil
#import http.server
#import socketserver
if sys.version_info>=(3,0):
	from urllib.parse import urlparse
	from . import WebTrisurf
else:
	from urlparse import urlparse
	from vtk import *
	
#import io

from IPython import embed

import __main__ as main

#Color definitions for terminal
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#parses Command Line Arguments and returns the list of parsed values
def ParseCLIArguments(arguments):
	parser = argparse.ArgumentParser(description='Manages (start, stop, status) multiple simulation processes of trisurf according to the configuration file.')
	parser.add_argument('proc_no', metavar='PROC_NO', nargs='*',
			    help='process number at host. If hostname is not specified, localhost is assumed. If no processes are specified all processes on all hosts are assumed.')
	action_group=parser.add_mutually_exclusive_group(required=True)
	action_group.add_argument('-c','--comment',nargs=1, help='append comment to current comment')
	action_group.add_argument('--analysis', nargs='+', help='runs analysis function defined in configuration file')
	action_group.add_argument('--delete-comment', help='delete comment',action='store_true')
	action_group.add_argument('-k','--kill','--stop','--suspend', help='stop/kill the process', action='store_true')
	action_group.add_argument('-r','--run','--start','--continue', help='start/continue process', action='store_true')
	action_group.add_argument('-s','--status',help='print status of the processes',action='store_true')
	action_group.add_argument('-v','--version', help='print version information and exit', action='store_true')
	action_group.add_argument('--web-server', type=int,metavar="PORT", nargs=1, help='EXPERIMENTAL: starts web server and never exist.')
	action_group.add_argument('--jump-to-ipython', help='loads the variables and jumps to IPython shell', action="store_true")
	action_group.add_argument('-p','--preview',help='preview last VTU shape',action='store_true')
	parser.add_argument('--force', help='if dangerous operation (killing all the processes) is requested, this flag is required to execute the operation. Otherwise, the request will be ignored.', action="store_true")
	parser.add_argument('-H', '--host', nargs='+', help='specifies which host is itended for the operation. Defauts to localhost for all operations except --status and --version, where all configured hosts are assumed.')
	parser.add_argument('--html', help='Generate HTML output', action="store_true")
	parser.add_argument('-n', nargs='+', metavar='PROC_NO', type=int, help='OBSOLETE. Specifies process numbers.')
	parser.add_argument('-R','--raw',help='print status and the rest of the information in raw format', action="store_true")
	parser.add_argument('-x','--local-only',help='do not attempt to contact remote hosts. Run all operations only on local machine',action='store_true')
	parser.add_argument('--originating-host',nargs=1,help='specify which host started the remote connections. Useful mainly fo internal functionaly of tsmgr and analyses.')
	args = parser.parse_args(arguments)
	return args


#gets version of trisurf currently running
def getTrisurfVersion():
	p = subprocess.Popen('trisurf --version', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	lines=p.stdout.readlines()
	version=re.findall(r'[0-9a-f]{7}(?:-dirty)?', lines[0].decode('ascii'))
	p.wait()
	if(len(version)):
		return version[0]
	else:
		return "unknown version"



def copyConfigAndConnect(hosts):
	print("Connecting to remote hosts and copying config files, tapes and snapshots")
	#create a list of files to be copied across all the remote hosts
	file_list=[]
	for h in hosts:
		for r in h['runs']:
			if(r.isFromSnapshot):
				file_list.append(r.snapshotFile)
			else:
				file_list.append(r.tapeFilename)
	file_list.append(main.__file__)
	for host in hosts:
		if(host['name'] !=socket.gethostname()): #if I am not the computer named in host name
			try:
				username=host['username']
			except:
				username=os.getusername() #default username is current user user's name
			try:
				port=host['port']
			except:
				port=22 #default ssh port
			rm=Remote.Connection(hostname=host['address'],username=username, port=port)
			rm.connect()
#			print ("Sendind file:"+main.__file__)
			if('remotebasepath' in host):
				remote_dir=host['remotebasepath']
			else:
				remote_dir='trisurf_simulations'
			rm.send_multiple_files_in_directory(file_list,remote_dir)
#			rm.send_file(main.__file__,'remote_control.py')
#			for run in host['runs']:
#				try:
#					rm.send_file(run.tapeFile,run.tapeFile)
#				except:
#					pass
#				try:
#					rm.send_file(run.snapshotFile,run.snapshotFile)
#				except:
#					pass
			host['_conn']= rm
	# we are connected to all hosts...
	return hosts



def getTargetRunIdxList(args):
	target_runs=list(map(int,args['proc_no']))
	if len(target_runs)==0:
		#check if obsolete -n flags have numbers
		target_runs=args['n']
		if target_runs==None:
			return None
	target_runs=list(set(target_runs))
	return target_runs



def status_processes(args,host):
	target_runs=getTargetRunIdxList(args)
	if target_runs==None:
		target_runs=list(range(1,len(host['runs'])+1))
	report=[]
#	print("was here")
	for i in target_runs:
		line=host['runs'][i-1].getStatistics()
		line.insert(0,i)
		report.append(line)
	if(args['raw']):
		print(report)
	else:
		if(args['html']):
			tablefmt='html'
		else:
			tablefmt='fancy_grid'
		print(tabulate.tabulate(report,headers=["Run no.", "Run start time", "ETA", "Status", "PID", "Path", "Comment"], tablefmt=tablefmt))
	return

def run_processes(args,host):
	target_runs=getTargetRunIdxList(args)
	if target_runs==None:
		target_runs=list(range(1,len(host['runs'])+1))
	for i in target_runs:
		host['runs'][i-1].start()
	return

def kill_processes(args,host):
	target_runs=getTargetRunIdxList(args)
	if target_runs==None:
		if args['force']==True:
			target_runs=list(range(1,len(host['runs'])+1))
		else:
			print("Not stopping all processes on the host. Run with --force flag if you are really sure to stop all simulations")
			return
	for i in target_runs:
		host['runs'][i-1].stop()
	return

def comment_processes(args,host):
	target_runs=getTargetRunIdxList(args)
	if target_runs==None:
		target_runs=list(range(1,len(host['runs'])+1))
	for i in target_runs:
		host['runs'][i-1].writeComment(args['comment'][0],'a')
	print("Comment added")
	return

def delete_comments(args,host):
	target_runs=getTargetRunIdxList(args)
	if target_runs==None:
		if args['force']==True:
			target_runs=list(range(1,len(host['runs'])+1))
		else:
			print("Not deleting comments on all posts on the host. Run with --force flag if you are really sure to delete all comments")
			return
	for i in target_runs:
		host['runs'][i-1].writeComment("")
	print("Comment deleted")
	return


def start_web_server(args,host):
	print('Server listening on port {}'.format(args['web_server'][0]))
	if sys.version_info>=(3,0):
		WebTrisurf.WebServer(port=args['web_server'][0])
	else:
		print("Cannot start WebServer in python 2.7")
	exit(0)


def analyze(args,host,a_dict, analysis,hosts):
	if len(a_dict)==0:
		print ('Error: no analyses are specified in the tsmgr.start()!')
		exit(1)
	target_runs=getTargetRunIdxList(args)
	if target_runs==None:
		target_runs=list(range(1,len(host['runs'])+1))
	for i in target_runs:

		for anal in analysis:
			if(anal not in a_dict):
				print("Analysis '"+anal+"' is not known. Available analyses: "+", ".join(a_dict.keys())+".")
				exit(0)
		for anal in analysis:
			retval=a_dict[anal](host['runs'][i-1],host=host, args=args, hosts=hosts)
			#try:
			if(retval):
				exit(0)
			#except:
			#	pass


	

def perform_action(args,host,**kwargs):
	#find which flags have been used and act upon them. -r -s -k -v -c --delete-comment are mutually exclusive, so only one of them is active
	if args['run']:
		run_processes(args,host)
	elif args['kill']:
		kill_processes(args,host)
	elif args['status']:
		status_processes(args,host)
	elif args['comment']!= None:
		comment_processes(args,host)
	elif args['delete_comment']:
		delete_comments(args,host)
	elif args['web_server']!=None:
		start_web_server(args,host)
	elif args['preview']:
		preview_vtu(args,host)
	elif args['jump_to_ipython']:
		print('Jumping to shell...')
		embed()
		exit(0)
	elif args['analysis']!= None:
		analyze(args,host,kwargs.get('analyses', {}), args['analysis'],kwargs.get('hosts',None))
		exit(0)
	else: #version requested
		print(getTrisurfVersion())
	return



def preview_vtu(args,host):
	from . import VTKRendering
	target_runs=getTargetRunIdxList(args)
	if target_runs==None:
		target_runs=list(range(1,len(host['runs'])+1))
	if host['name'] == socket.gethostname():
		for i in target_runs:
			VTKRendering.Renderer(args,host,host['runs'][i-1])
	else:
		print("VTK rendering currently works on localhost only!")
		

def getListOfHostConfigurationByHostname(hosts,host):
	rhost=[]
	for chost in hosts:
		if chost['name'] in host:
			rhost.append(chost)
	return rhost



def start(hosts,argv=sys.argv[1:], analyses={}):
	args=vars(ParseCLIArguments(argv))
	#Backward compatibility... If running just on localmode, the host specification is unnecessary. Check if only Runs are specified
	try:
		test_host=hosts[0]['name']
	except:
		print("Old syntax detected.")
		hosts=({'name':socket.gethostname(),'address':'127.0.0.1', 'runs':hosts},)

	#find the host at which the action is attended
	if args['host']==None:
		#Only status and version commands are automatically executed on all the hosts. stopping or starting  or other actions is not!
		if(args['status']==False and args['version']==False):
			hosts=getListOfHostConfigurationByHostname(hosts,socket.gethostname())
	else:
		hosts=getListOfHostConfigurationByHostname(hosts,args['host'])
	if len(hosts)==0:
		print ('Hostname "{}" does not exist in configuration file. Please check the spelling'.format(args['host'][0]))
		exit(1)
	if not args['local_only']:
			hosts=copyConfigAndConnect(hosts)
	#do local stuff:
	for host in hosts:
		if host['name'] == socket.gethostname():
			if(args['html']):
				print("Host <font color='orange'>"+host['name']+"</font> reports:")
			else:
				print("Host "+bcolors.WARNING+host['name']+bcolors.ENDC+" reports:")
			perform_action(args,host, analyses=analyses, hosts=hosts)
		elif not args['local_only']:
			if('remotebasepath' in host):
				remote_dir=host['remotebasepath']
			else:
				remote_dir='trisurf_simulations'
			#output=host['_conn'].execute('cd '+remote_dir)
			#print(remote_dir)
			#print(main.__file__)
			#print('python3 '+main.__file__+' -x '+" ".join(argv))
			output=host['_conn'].execute('cd '+remote_dir+ '; python3 '+main.__file__+' -x --originating-host ' +socket.gethostname()+" "+" ".join(argv))
			for line in output:
				print(line.replace('\n',''))


	if not args['local_only']:
		print("Closing connections to remote hosts")
		for host in hosts:
			if(host['name'] !=socket.gethostname()):
				host['_conn'].disconnect()



