# RockPaperScissorLizardSpock

Utilizando Sockets, podemos communicar entre linguagens de programação diferentes. Nao precisa nem de um tutorial pois, qualquer erro de sintae o servidor deixara claro o que precisa fazer. Mas para já saberem o fluxo esperado:

1. Rode game.py
  a. Vai iniciar o servidor em python
2. Rode cliente.py
  a. Vai iniciar o seu cliente em python
3. Rode cliente.java
  a. Vai iniciar o seu cliente em java
4. Para conectar ao servidor
  a. Escreva "connect"
  b. So quando tiver dois connectados que poderá competir entre si
5. Escolha uma jogada
  a. Escolha entre: 'Rock', 'Paper', 'Scissors', 'Lizard' e 'Spock'
6. Apos ambos jogadores escolherem sua respectiva jogada
  a. Escreva "get" para obter o resultado
  b. Após ambos jogadores olharem o resultado, a connexão é rompida. Volta ao passo 1.

Observação:
- O seu nome é aleatorio
- A qualquer momento, se escrever 'exit' terminará o cliente, além disso pode inclusive terminar o servidor dependendo do contexto em que usa.
