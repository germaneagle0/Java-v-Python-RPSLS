package RockPaperScissorsLizardSpock;
import java.net.*;
import java.io.*;
import java.text.DecimalFormat;
import java.util.Random;
import java.util.Scanner;
import java.lang.Thread;
import java.util.Vector;
import java.util.concurrent.ThreadLocalRandom;

class Dados {
    public String my_jogada;
    public String op_jogada;
    public int result;
    public Dados(String my,String op,int res) {
        my_jogada = my;
        op_jogada = op;
        result = res;
    }
}

public class Cliente {
    int sleep_time = 100;
    int limite_games = 15;
    Vector<Dados> historico;
    String HOST;
    int PORT;
    String clientID;
    Boolean active = true;
    int games_played = 0;
    int status = 0;
    int player = 0;
    String my_last_play = "";
    String op_last_play = "";
    int res_last_play = 1;
    DecimalFormat df;
    public Cliente(String host, int port, String id) {
        df = new DecimalFormat();
        df.setMaximumFractionDigits(2);

        historico = new Vector<>();
        this.HOST = host;
        this.PORT = port;
        this.clientID = id;
        System.out.println(String.format("Cliente %s ativado", id));
        Scanner scan = new Scanner(System.in);
        while (games_played < limite_games) {
            try {
                Thread.sleep(sleep_time);
                String line = obterMensagem();
                String mensagemFinal = this.clientID + '-' + line;
                Socket socket = new Socket(host, port);
                PrintStream out = new PrintStream( socket.getOutputStream() );
                BufferedReader in = new BufferedReader( new InputStreamReader( socket.getInputStream() ) );
                out.print(mensagemFinal);
                String response = in.readLine();
                lidarComResposta(response);
                in.close();
                out.close();
                socket.close();
            }
            catch(UnknownHostException u) {
                System.out.print(".");
            }
            catch(IOException i) {
                System.out.print(".");
            }
            catch (InterruptedException i) {
                System.out.print(".");
            }
        }
        int vitorias = 0;
        int derrotas = 0;
        int empates = 0;
        int i = 0;
        System.out.println("\nFim do Jogo! Apresentando as partidas realizadas:");
        for (Dados dado: historico) {
            i+=1;
            String resultado = "Empate! (Nao conta como rodada)";
            if (dado.result == 2) {
                vitorias += 1;
                resultado = "Vitoria!";
            }
            else if (dado.result == 3) {
                derrotas += 1;
                resultado = "Derrota!";
            }
            else {
                empates += 1;
            }
            System.out.print("\nPartida "+ i + " - " + dado.my_jogada + " x " + dado.op_jogada + " - " + resultado);
        }
        if (vitorias - derrotas > 0) {
            System.out.println("\nVitorioso!");
        }
        else if (vitorias - derrotas < 0) {
            System.out.println("\nDerrotado!");
        }
        else {
            System.out.println("\nEmpatados!");
        }
        System.out.println("\nVitorias: " + df.format(100*((float)vitorias / (vitorias+empates+derrotas)))+"%");
        System.out.println("Derrotas: " + df.format(100*((float)derrotas / (vitorias+empates+derrotas)))+"%");
        System.out.println("Empates: " + df.format(100*((float)empates / (vitorias+empates+derrotas)))+"%");
    }
    public String getRandomElement() {
        String[] arr = {"Rock", "Paper", "Scissors", "Lizard", "Spock"};
        return arr[ThreadLocalRandom.current().nextInt(arr.length)];
    }
    // Heuristica, se vencer, pega o elemento que do opponente
    // Se perder, pega algo que no foi pego pelos dois
    public String heuristica() {
        if (my_last_play.equals("") || res_last_play == 1) {
            return getRandomElement();
        }
        else if (res_last_play == 2) {
            return op_last_play;
        }
        else {
            String ret = my_last_play;
            while (ret.equals(my_last_play) || ret.equals(op_last_play)){
                ret = getRandomElement();
            }
            return ret;
        }
    }

    public void printResumo() {
        int vitorias = 0;
        int derrotas = 0;
        int empates = 0;
        int i = 0;
        for (Dados dado: historico) {
            i+=1;
            if (dado.result == 2) {
                vitorias += 1;
            }
            else if (dado.result == 3) {
                derrotas += 1;
            }
            else {
                empates += 1;
            }
        }
        int rodada = vitorias + derrotas;
        int total = vitorias+empates+derrotas;
        System.out.print("\nRodada " + rodada + " - ");
        System.out.print("Vitorias: " + df.format(100*((float)vitorias / (total)))+"% ");
        System.out.print("Derrotas: " + df.format(100*(float)derrotas / (total))+"% ");
        System.out.print("Empates: " + df.format(100*(float)empates / (total))+"%");
    }
    public String obterMensagem() {
        if (status == 0) {
            return "connect";
        }
        else if (status == 1) {
            return heuristica();
        }
        else {
            return "get";
        }
    }
    public void lidarComResposta(String resposta) {
        if (status == 0) {
            if (resposta.contains("connected as player")){
                status = 1;
            }
        }
        else if (status == 1) {
            if (resposta.contains("to get result, send message 'get'")) {
                status = 2;
                if (resposta.contains("1")) {
                    player = 1;
                }
                else {
                    player = 2;
                }
            }
        }
        else {
            int resp = extractFromString(resposta);
            if (resp != 1) {
                printResumo();
                games_played += 1;
            }
            status = 0;
        }
    }

    public int extractFromString(String str) {
        String[] str_parantheses = str.substring(str.indexOf("(")+1, str.indexOf(")")).split(" x ");
        String my_play = str_parantheses[0];
        String op_play = str_parantheses[1];
        if (player == 2) {
            String swap = my_play;
            my_play = op_play;
            op_play = swap;
        }
        int result = 1;
        if (str.contains("you won")) {
            result = 2;
        }
        if (str.contains("you lost")) {
            result = 3;
        }
        saveResult(my_play, op_play, result);
        return result;
    }

    public void saveResult(String my_play, String op_play, int result) {
        my_last_play = my_play;
        op_last_play = op_play;
        res_last_play = result;
        Dados d = new Dados(my_play,op_play,result);
        historico.add(d);
    }
    public static String getRandom(int max) {
        return String.valueOf((int)(Math.random() * max + 1));
    }

    public static void main(String args[])
    {
        Cliente client = new Cliente("172.15.3.50", 12000, "java_gamer".concat(getRandom(1000)));
    }
}
