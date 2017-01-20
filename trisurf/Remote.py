import paramiko
import os.path

class Connection:
	def __init__(self, hostname, port=22, username=None, password=None):
		self.hostname=hostname
		self.port=port
		if(username!=None):
			self.username=username
		else:
			self.username=''
		if(password!=None):
			self.password=password
		else:
			self.password=''
		self.ssh=paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.connected=False
		return
	
	def connect(self, Timeout=5):
		if(not self.connected):
#			try:
			print("Trying to connect to: "+self.username+"@"+self.hostname+":"+str(self.port)+".")
			self.ssh.connect(self.hostname, username=self.username, password=self.password, port=self.port, timeout=Timeout)
			self.connected=True
#			except:
#				print("Error establishing connection with "+self.username+"@"+self.hostname+":"+str(self.port)+".")
#				exit(1)
		else:
			print("Already connected!")
		return

	def disconnect(self):
		if(self.connected):
			self.ssh.close()
		else:
			print("Cannot disconect. Already disconnected.")
		self.connected=False

	def execute(self,command):
		if(self.connected):
			try:
				stdin,stdout,stderr=self.ssh.exec_command(command)
				output=stdout.readlines()
				errors=stderr.readlines()
			#	print(errors)
				return(output)
			except:
				print("Cannot execute remote commands")
		else:
			print("Cannot execute remote commands. Connect first.")

	def send_file(self, local, remote):
		pass
#		sftp=self.ssh.open_sftp()
#		sftp.put(local,remote)
#		sftp.close()

	def receive_file(self,remote,local):
		pass
#		sftp=self.ssh.open_sftp()
#		sftp.get(remote,local)
#		sftp.close()

	def mkdir_remote(self,directory):
		sftp=self.ssh.open_sftp()
		sftp.mkdir(directory)
		sftp.close()

	def mkdir_p(self,sftp, remote_directory):
		"""Change to this directory, recursively making new folders if needed.
		Returns True if any folders were created. Recursive algorithm."""
		if remote_directory == '/':
			# absolute path so change directory to root
			sftp.chdir('/')
			return
		if remote_directory == '':
			# top-level relative directory must exist
			return
		try:
			sftp.chdir(remote_directory) # sub-directory exists
		except IOError:
			dirname, basename = os.path.split(remote_directory.rstrip('/'))
			self.mkdir_p(sftp, dirname) # make parent directories
			sftp.mkdir(basename) # sub-directory missing, so created it
			sftp.chdir(basename)
		return True
	
	def send_multiple_files_in_directory(self,local_files,directory):
		pass
