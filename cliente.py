from socket import *
import threading
import random
def getRandomNumber():
  return random.randint(1, 1000)
  
  

class handlerClient(threading.Thread):
  def __init__(self, PORT, HOST, ID):
    super(handlerClient, self).__init__()
    self.active = True
    self.HOST = HOST
    self.PORT = PORT
    if ('-' in ID):
      self.ID = ID.replace('-', '')
    self.clientID = str(ID)
    
  def run(self):
    print(f"Cliente {self.clientID} ativado")
    while self.active:
      try:
        with socket(AF_INET, SOCK_STREAM) as s:
          data = input("> ")
          if ('-' in data):
            print("Mensagem invalida!")
            continue
          if (data == 'exit'):
            self.active = False
          s.connect((self.HOST, self.PORT))
          s.sendall(f"{self.clientID}-{data}".encode())
          resposta = s.recv(1024).decode()
          print(f"{resposta}")
          
      except Exception as e:
        if (self.active):
          print("Erro ao enviar mensagem: " + str(e.args))
          data = input("Exit? (y/n) \n> ")
          if (data == 'y'):
            self.active = False
          
if __name__ == "__main__":
  cliente = handlerClient(PORT=12000, HOST="172.15.3.50", ID=f"gamer{str(getRandomNumber())}")
  cliente.start()
  cliente.join()
  print("Ending!")
  