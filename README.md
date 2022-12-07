# RockPaperScissorLizardSpock

Nesse jogo podemos realizar uma competição entre bots. 

Para isso, a primeira coisa a se fazer é ligar o servidor.

- Rode game.py

Temos dois bots, um em python, cuja heurística consistem em verificar qual a tendência de um jogador. Ou seja, a que mais gosta de usar. Ele inicia aleatório até um limite (agora é 5), acima da qual começa a usar essa lógica.

O outro bot em java utiliza uma heurística apresentada nesse artigo:

Para iniciar o jogo basta rodar o

- cliente.py
- cliente.java

O jogo consiste em 15 rodadas, onde uma rodada consistem em uma partida onde não houve empate!

Essa trabalho busca apresentar como utilizando sockets, podemos communicar entre linguagens de programação diferentes.

Observação:

- No terminal onde roda game.py, observará a visão geral (jogada dos outros jogadores e resultados)
- Associado a cada processo temos um nome aleatório que o servidor usa como referência
- O servidor guarda os resultados de tudo em um banco sql
- O cliente python armazena os resultados em um banco sql
- Já o cliente java não precisa armazenar em um banco pois a heurística apenas analisa e compara com a ultima jogada.