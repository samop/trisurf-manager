#!/usr/bin/python3
from trisurf import trisurf
from trisurf import tsmgr




#Ok... Configure your keys:
#ssh-keygen
#and copy them to all the remote hosts
#ssh-copy-id -i ./ssh/id_rsa.pub username@remotehost

run2=trisurf.Runner(tape='tape')
run2.setMaindir(("N","k","V","Np","Nm"),("nshell","xk0","constvolswitch","npoly","nmono"))
run2.setSubdir("run1")

run3=trisurf.Runner(tape='tape')
run3.setMaindir(("N","k","V","Np","Nm"),("nshell","xk0","constvolswitch","npoly","nmono"))
run3.setSubdir("run2")


Runs=[run2, run3]

#this is how analyses are defined
def analyze(run, **kwargs):
	host=kwargs.get('host', None)
	print("Demo analysis")
	print("Analysis on host "+host['name']+" for run "+run.Dir.fullpath()+" completed")
	print("here comes info on the run variable:")
	print(run)
	print("here comes info on the host variable:")
	print(host)
	print("here comes info on the hosts variable:")
	print(kwargs.get('hosts',None))
	print("here comes info on the args variable:")
	print(kwargs.get('args',None))

def testWebAnalysis(run, **kwargs):
	print("Simulations are located in "+run.Dir.fullpath())
	print("\n\nStatistics file:")
	print(run.Statistics.readText())

hosts=({'name':'natalie','address':'kabinet.penic.eu', 'runs':Runs, 'username':'samo', 'remotebasepath':'simulations-test/subdir/subdir'},
	{'name':'Hestia','address':'127.0.0.1', 'runs':Runs, 'username':'samo'})
analyses={'analysis1':analyze,'webReport':testWebAnalysis}

tsmgr.start(hosts, analyses=analyses)
