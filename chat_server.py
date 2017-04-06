import socket
import threading
import sys

RMV=False

class chatServer:
	def __init__(self,host,port):
		self.clients=[]
		self.users=[]
		self.host=host
		self.port=port
		self.serverSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.names={}
		self.sockets={}

		try:
			self.serverSocket.bind((self.host,self.port))
		except:
			sys.exit()

		self.serverSocket.listen(10)

	def run(self):
		while True:
			clientSocket,clientAddr=self.serverSocket.accept()
			self.clients.append(clientSocket)

			newClient=Client(clientSocket,clientAddr,self)
			newClient.start()

	def removeClient(self, clientSocket):
		try:
			global RMV
			self.clients.remove(clientSocket)
			self.users.remove(self.sockets[clientSocket])
			RMV=True
		except:
			pass

	def addName(self, name, soc):
		self.names[name]=soc
		self.users.append(name)
		self.sockets[soc]=name


class Client(threading.Thread):
	def __init__(self,clientSocket,clientAddr,server):
		super(Client, self).__init__()
		self.clientSocket=clientSocket
		self.clientAddr=clientAddr
		self.server=server

	def list_msg(self):
		msg2='2'
		for x in self.server.users:
			msg2+=' '+x
		return msg2

	def run(self):
		lock = threading.Lock()
		while True:
			try:
				global RMV
				if RMV:
					lock.acquire()
					try:
						RMV=False
						msg2=self.list_msg()
						try:
							for client in self.server.clients:
								client.send(bytes(msg2,'UTF-8'))
						except:
							self.server.removeClient(client)
					finally:
						lock.release()

				data=self.clientSocket.recv(2048)
				if data:
					lock.acquire()
					try:
						msg=data.decode('UTF-8')
						msg2=msg
						try:
							if msg[0]=='2':
								self.server.addName(msg[1:],self.clientSocket)
								msg2=self.list_msg()
						except:
							pass

						if msg[0]=='3':
							self.server.removeClient(msg[1:])
							msg2=self.list_msg()

						if msg[0]=='1':
							try:
								i=1
								while msg[i] != ' ':
									i+=1
								receiver=self.server.names[msg[1:i]]
								msg='1'+msg[i+1:]
								receiver.send(bytes(msg,'UTF-8'))
							except:
								self.server.removeClient(receiver)

						else:#send to everyon
							try:
								for client in self.server.clients:
									client.send(bytes(msg2,'UTF-8'))
							except:
								self.server.removeClient(client)
					finally:
						lock.release()
				else:
					self.server.removeClient(self.clientSocket)
					break
			except:
				self.server.removeClient(self.clientSocket)
				break



server = chatServer('',12345)
server.run()
