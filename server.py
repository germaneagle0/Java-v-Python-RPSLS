from socket import *
import threading
from enum import Enum
import sqlite3

class Result(Enum):
  DRAW = 1
  PLAYER1 = 2
  PLAYER2 = 3
  NO_RESULT = 4
class State(Enum):
  WAITING_FOR_CONNECTION = 1
  WAITING_FOR_SECOND_PLAYER = 2
  WAITING_FOR_MOVES = 3
  GAME_OVER = 4
class Moves(Enum):
  Scissors = 1
  Paper = 2
  Rock = 3
  Lizard = 4
  Spock = 5
  No_Move = 6
class handlerServer(threading.Thread):
  def __init__(self, PORT, HOST):
    super(handlerServer, self).__init__()
    self.active = True
    self.HOST = HOST
    self.PORT = PORT
    self.resetVariables()
    
  def determineResult(self):
    if (self.firstPlayerMove == self.secondPlayerMove):
      return Result.DRAW
    if (self.firstPlayerMove == Moves.Scissors):
      if (self.secondPlayerMove == Moves.Paper or self.secondPlayerMove == Moves.Lizard):
        return Result.PLAYER1
      return Result.PLAYER2
    if (self.firstPlayerMove == Moves.Paper):
      if (self.secondPlayerMove == Moves.Rock or self.secondPlayerMove == Moves.Spock):
        return Result.PLAYER1
      return Result.PLAYER2
    if (self.firstPlayerMove == Moves.Rock):
      if (self.secondPlayerMove == Moves.Lizard or self.secondPlayerMove == Moves.Scissors):
        return Result.PLAYER1
      return Result.PLAYER2
    if (self.firstPlayerMove == Moves.Lizard):
      if (self.secondPlayerMove == Moves.Spock or self.secondPlayerMove == Moves.Paper):
        return Result.PLAYER1
      return Result.PLAYER2
    if (self.firstPlayerMove == Moves.Spock):
      if (self.secondPlayerMove == Moves.Scissors or self.secondPlayerMove == Moves.Rock):
        return Result.PLAYER1
      return Result.PLAYER2
    
  def versus(self):
    return f"{self.firstPlayerMove.name} x {self.secondPlayerMove.name}"
  
  def resetVariables(self):
    self.state = State.WAITING_FOR_CONNECTION
    self.firstPlayerIP = ''
    self.secondPlayerIP = ''
    self.firstPlayerMove = Moves.No_Move
    self.secondPlayerMove = Moves.No_Move
    self.result = Result.NO_RESULT
    self.firstPlayerReceived = False
    self.secondPlayerReceived = False
  
  def createBanco(self):
    try:
        sqliteConnection = sqlite3.connect('banco_de_dados.db')
        c = sqliteConnection.cursor() 
        c.execute("""create table if not exists resultados (
                     rodada integer primary key autoincrement ,
                     player1 text,
                     player2 text,
                     resultado text)""")
        sqliteConnection.commit()
        c.close()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
  
  def saveResult(self):
    self.createBanco()
    try:
        sqliteConnection = sqlite3.connect('banco_de_dados.db')
        c = sqliteConnection.cursor() 
        data = [(self.firstPlayerIP, self.secondPlayerIP , self.result.name)]
        insertstring = "INSERT INTO resultados (player1, player2, resultado) VALUES (?, ?, ?)"
        c.executemany(insertstring, data)
        sqliteConnection.commit()
        c.close()
    except sqlite3.Error as error:
        print("Error while inserting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
    
    
  def getResults(self, addr):
    self.createBanco()
    text = ''
    try:
      sqliteConnection = sqlite3.connect('banco_de_dados.db')
      c = sqliteConnection.cursor() 
      c.execute("select * from resultados where player1 = '"+str(addr)+"' or player2 = '"+str(addr)+"'")
      lista = c.fetchall()
      for (item) in lista:
        text = f"{text} || {item[0]} - {item[1]} vs {item[2]} - Result {item[3]}"
      c.close()
    except sqlite3.Error as error:
      print("Error while inserting to sqlite", error)
    finally:
      if sqliteConnection:
          sqliteConnection.close()
      return text
  def handleRequest(self, conn):
    messagem = str(conn.recv(1024).decode()).lower()
    dados = messagem.split('-')
    addr = dados[0] ## id do cliente
    messagem = dados[1]
    
    if (messagem == 'results'):
      conn.sendall(self.getResults(addr).encode())
      return
    
    if (messagem == 'exit'):
      if (self.state == State.WAITING_FOR_CONNECTION):
        conn.sendall("Server - Disconnected\n".encode())
        self.active = False
        return
      if (self.state == State.GAME_OVER):
        self.state=State.WAITING_FOR_CONNECTION
        self.resetVariables()
      elif (self.firstPlayerIP == addr):
        if (self.secondPlayerIP == ''):
          self.state=State.WAITING_FOR_CONNECTION
          self.resetVariables()
          conn.sendall("Server - Disconnected\n".encode())
        else: 
          self.state=State.GAME_OVER
        return
      elif (self.secondPlayerIP == addr):
        self.state=State.GAME_OVER
      else:
        conn.sendall(f"{addr} please wait for game to finish\n".encode())
      
    if self.state == State.WAITING_FOR_CONNECTION:
      if messagem == "connect":
        self.firstPlayerIP = addr
        self.state = State.WAITING_FOR_SECOND_PLAYER
        conn.send(f"{addr} connected as player 1\n".encode())
      else:
        conn.send(f"{addr} to connect, send message 'connect'\n".encode())
    
    if self.state == State.WAITING_FOR_SECOND_PLAYER:
      if addr != self.firstPlayerIP:
        if messagem == "connect":
          self.secondPlayerIP = addr
          self.state = State.WAITING_FOR_MOVES
          conn.send(f"{addr} connected as player 2\n".encode())
          return
        else:
          conn.send(f"{addr} to connect, send message 'connect'\n".encode())
      else:
        conn.send(f"{addr} waiting for player 2 to enter\n".encode())
      
    if self.state == State.WAITING_FOR_MOVES:
      if addr == self.firstPlayerIP:
        if self.firstPlayerMove != Moves.No_Move:
          conn.send("waiting for player 2\n".encode())
        elif (messagem == "scissors") or (messagem == "paper") or (messagem == "rock") or (messagem == "lizard") or (messagem == "spock"):
          self.firstPlayerMove = Moves[messagem.capitalize()]
          print(f"Server - {addr} played {self.firstPlayerMove.name}")
          if (self.secondPlayerMove != Moves.No_Move):
            self.result = self.determineResult()
            self.saveResult()
            print(f"Server - Result {self.firstPlayerIP} vs {self.secondPlayerIP} \n\t{self.versus()} \n\t{self.result.name}")
            self.state = State.GAME_OVER
          conn.send(f"move received by {addr}\n".encode())
        else:
          conn.send(f"invalid move by {addr}\n".encode())     
      elif addr == self.secondPlayerIP:
        if self.secondPlayerMove != Moves.No_Move:
          conn.send("waiting for player 1\n".encode())
        elif (messagem == "scissors") or (messagem == "paper") or (messagem == "rock") or (messagem == "lizard") or (messagem == "spock"):
          self.secondPlayerMove = Moves[messagem.capitalize()]
          print(f"Server - {addr} played {self.secondPlayerMove.name}")
          if (self.firstPlayerMove != Moves.No_Move):
            self.result = self.determineResult()
            self.saveResult()
            print(f"Server - Result {self.firstPlayerIP} vs {self.secondPlayerIP} \n\t{self.versus()}\n\t{self.result.name}")
            self.state = State.GAME_OVER
          conn.send(f"move received by {addr}\n".encode())
        else:
          conn.send(f"invalid move by {addr}\n".encode())
      else:
        conn.send(f"{addr} you are not a player\n".encode())

    elif self.state == State.GAME_OVER:
      if (messagem == "get"):
        if addr == self.firstPlayerIP:
          self.firstPlayerReceived = True
          if self.result == Result.DRAW:
            conn.send((f"{addr} draw ({self.versus()})\n").encode())
          elif self.result == Result.PLAYER1:
            conn.send((f"{addr} you won ({self.versus()})\n").encode())
          elif self.result == Result.PLAYER2:
            conn.send((f"{addr} you lost ({self.versus()})\n").encode())
          else:
            conn.send(f"{addr} server exiting\n".encode())
        elif addr == self.secondPlayerIP:
          self.secondPlayerReceived = True
          if self.result == Result.DRAW:
            conn.send((f"{addr} draw ({self.versus()})\n").encode())
          elif self.result == Result.PLAYER1:
            conn.send((f"{addr} you lost ({self.versus()})\n").encode())
          elif self.result == Result.PLAYER2:
            conn.send((f"{addr} you won ({self.versus()})\n").encode())
          else:
            conn.send(f"{addr} server exiting\n".encode())
        else:
          conn.send(f"{addr} you are not a player\n".encode())
        if (self.firstPlayerReceived and self.secondPlayerReceived):
          self.resetVariables()
      else:
        conn.send(f"{addr} to get result, send message 'get'\n".encode())
  
  def run(self):
    print("Server - Recebendo mensagens no PORT " + str(self.PORT))
    while self.active:
      try:  
        with socket(AF_INET, SOCK_STREAM) as s:
          s.bind((self.HOST, self.PORT))
          s.listen()
          conn, addr = s.accept()
          with conn:
            # print(f'Server - Connected by {addr[0]}, port {addr[1]}')
            self.handleRequest(conn)
      except Exception as e:
        print("Server - Error ao receber mensagens no PORT " + str(self.PORT))
        print(e.args)
    print("Server - Fim")

  def shutdown(self):
    self.active = False
