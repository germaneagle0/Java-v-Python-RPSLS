from cliente import handlerClient
from server import handlerServer

"""
Rules:
Scissors decapitate Scissors cuts paper, 
paper covers rock, 
rock crushes lizard, 
lizard poisons Spock, 
Spock smashes scissors, 
scissors decapitates lizard, 
lizard eats paper, 
paper disproves Spock, 
Spock vaporizes rock, 
and as it always has, 
rock crushes scissors
"""

if __name__ == "__main__":
  
  server = handlerServer(PORT= 12000, HOST="172.15.3.50")
  server.start()
  server.join()
  print("Ending!")
  