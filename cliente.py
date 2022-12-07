from socket import *
import threading
import random
from time import sleep
import sqlite3

SLEEP_TIME = 0.1
LIMITE_JOGOS = 15

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
    self.numero_jogos = 0
    self.status = 0
    self.player = 0
  
  def extractFromString(self, str):
    str_paratheses = str[str.find("(")+1:str.find(")")].split(" x ")
    my_play = str_paratheses[0]
    op_play = str_paratheses[1]
    if (self.player == 2):
      swap = my_play
      my_play = op_play
      op_play = swap
    result = 1 # 1 = empate, 2 = ganhei, 3 = perdi
    if ("you won" in str):
      result = 2
    if ("you lost" in str):
      result = 3
    self.saveResult(my_play, op_play, result)
    return result
  
  def createBanco(self):
    try:
        sqliteConnection = sqlite3.connect('banco_de_dados.db')
        c = sqliteConnection.cursor() 
        c.execute("""create table if not exists cliente_dados (
                     rodada integer primary key autoincrement ,
                     my_play text,
                     op_play text,
                     resultado integer)""")
        sqliteConnection.commit()
        c.close()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
  
  def saveResult(self, my_play, op_play, resultado):
    self.createBanco()
    try:
        sqliteConnection = sqlite3.connect('banco_de_dados.db')
        c = sqliteConnection.cursor() 
        data = [(my_play, op_play, resultado)]
        insertstring = "INSERT INTO cliente_dados (my_play, op_play, resultado) VALUES (?, ?, ?)"
        c.executemany(insertstring, data)
        sqliteConnection.commit()
        c.close()
    except sqlite3.Error as error:
        print("Error while inserting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
  
  # Estrategia, ver o mais frequente das ultimas, jogar o oposto, so se rodadas > 5
  def heuristica(self):
    self.createBanco()
    text = ''
    plays = [0,0,0,0,0]
    amount = 0
    try:
      sqliteConnection = sqlite3.connect('banco_de_dados.db')
      c = sqliteConnection.cursor() 
      c.execute("select * from cliente_dados")
      lista = c.fetchall()
      for (item) in lista:
        amount += 1
        op_play = item[2]
        if (op_play == 'Rock'):
          plays[0] += 1
        if (op_play == 'Paper'):
          plays[1] += 1
        if (op_play == 'Scissors'):
          plays[2] += 1
        if (op_play == 'Lizard'):
          plays[3] += 1
        if (op_play == 'Spock'):
          plays[4] += 1
        text = f"{text} || {item[0]} - {item[1]} vs {item[2]} - {item[3]}!"
      c.close()
    except sqlite3.Error as error:
      print("Error while inserting to sqlite", error)
    finally:
      if sqliteConnection:
          sqliteConnection.close()
    if (amount > 5):
      indice = plays.index(max(plays))
      if (indice == 0): # case rock
        possibilities = ['Paper', 'Spock']
      if (indice == 1): # case paper
        possibilities = ['Scissors', 'Lizard']
      if (indice == 2): # case scissors
        possibilities = ['Rock', 'Spock']
      if (indice == 3): # case lizard
        possibilities = ['Rock', 'Scissors']
      if (indice == 4): # case spock
        possibilities = ['Paper', 'Lizard']
      random_number = random.randint(0, 1)
      return possibilities[random_number]
    else:
      random_number = random.randint(1, 5)
      if (random_number == 1):
        return 'Paper'
      if (random_number == 2):
        return 'Scissors'
      if (random_number == 3):
        return 'Lizard'
      if (random_number == 4):
        return 'Spock'
      if (random_number == 5):
        return 'Rock'
  
  def sendMessage(self, s):
    s.connect((self.HOST, self.PORT))
    if self.status == 0:
      data = "connect"
      s.sendall(f"{self.clientID}-{data}".encode())
      resposta = s.recv(1024).decode().replace('\n', '')
      if ("connected as player" in resposta):
        self.status = 1
        return
    if self.status == 1:
      data = self.heuristica()
      s.sendall(f"{self.clientID}-{data}".encode())
      resposta = s.recv(1024).decode().replace('\n', '')
      if ("to get result, send message 'get'" in resposta):
        self.status = 2
        if ('1' in resposta):
          self.player = 1
        else:
          self.player = 2
        return
    if self.status == 2:
      data = 'get'
      s.sendall(f"{self.clientID}-{data}".encode())
      resposta = s.recv(1024).decode().replace('\n', '')
      resp = self.extractFromString(resposta)
      if (resp != 1):
        self.printResumo()
        self.numero_jogos += 1
      self.status = 0
  
  def printResults(self):
    self.createBanco()
    try:
      win = 0
      lose = 0
      draw = 0
      sqliteConnection = sqlite3.connect('banco_de_dados.db')
      c = sqliteConnection.cursor() 
      c.execute("select * from cliente_dados")
      lista = c.fetchall()
      i = 0
      print("\nFim do Jogo! Apresentando as partidas realizadas:")
      for (item) in lista:
        i+=1
        if (item[3] == 2):
          win += 1
        elif (item[3] == 3):
          lose += 1
        else:
          draw += 1
        print(f"\nPartida {i} - {item[1]} x {item[2]} - Result {'Empate' if item[3] == 1 else ('Vitoria' if item[3] == 2 else 'Derrota')}", end="")
      c.close()
    except sqlite3.Error as error:
      print("Error while inserting to sqlite", error)
    finally:
      if sqliteConnection:
          sqliteConnection.close()
    points = win - lose
    total = win + lose + draw
    print("\n" + f"{'Vitorioso!' if points > 0 else 'Derrotado!' if points < 0 else 'Empatado!'}")
    print(f"\nVitorias: {round(100*win/(total),2)}% \nDerrotas: {round(100*lose/total, 2)}% \nEmpates: {round(100*draw/total, 2)}%")
    
  def clearBanco(self):
    self.createBanco()
    try:
      sqliteConnection = sqlite3.connect('banco_de_dados.db')
      c = sqliteConnection.cursor() 
      c.execute("delete from cliente_dados")
      sqliteConnection.commit()
    except sqlite3.Error as error:
      print("Error while inserting to sqlite", error)
    finally:
      if sqliteConnection:
          sqliteConnection.close()
  
  def printResumo(self):
    self.createBanco()
    try:
      win = 0
      lose = 0
      draw = 0
      sqliteConnection = sqlite3.connect('banco_de_dados.db')
      c = sqliteConnection.cursor() 
      c.execute("select * from cliente_dados")
      lista = c.fetchall()
      i = 0
      for (item) in lista:
        i+=1
        if (item[3] == 2):
          win += 1
        elif (item[3] == 3):
          lose += 1
        else:
          draw += 1
      c.close()
    except sqlite3.Error as error:
      print("Error while inserting to sqlite", error)
    finally:
      if sqliteConnection:
          sqliteConnection.close()
    total = win + lose + draw
    print(f"\nRodada {win + lose} - Vitorias: {round(100*win/(total),2)}% | Derrotas: {round(100*lose/total,2)}% | Empates: {round(100*draw/total,2)}%", end="")
  
  def run(self):
    self.clearBanco()
    print(f"Cliente {self.clientID} ativado")
    while self.numero_jogos < LIMITE_JOGOS:
      try:
        sleep(SLEEP_TIME)
        with socket(AF_INET, SOCK_STREAM) as s:
          self.sendMessage(s)
          
      except Exception as e:
        if (self.numero_jogos < LIMITE_JOGOS):
          print(".", end="")
          sleep(1)
    self.printResults()
if __name__ == "__main__":
  cliente = handlerClient(PORT=12000, HOST="172.15.3.50", ID=f"python_gamer{str(getRandomNumber())}")
  cliente.start()
  cliente.join()
  print("Ending!")
  
