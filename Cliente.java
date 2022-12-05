package RockPaperScissorsLizardSpock;
import java.net.*;
import java.io.*;
import java.util.Random;
import java.util.Scanner;

public class Cliente {
    String HOST;
    int PORT;
    String clientID;
    Boolean active = true;
    public Cliente(String host, int port, String id) {
        this.HOST = host;
        this.PORT = port;
        this.clientID = id;
        System.out.println(String.format("Cliente %s ativado", id));
        String line = "";
        Scanner scan = new Scanner(System.in);
        while (!line.equals("exit")) {
            try {
                while(true) {
                    System.out.print("> ");
                    line = scan.nextLine();
                    if (!line.contains("-")) {
                        break;
                    }
                    System.out.println("Mensagem invalida, tente novamente!");
                }
                String mensagemFinal = this.clientID + '-' + line;
                Socket socket = new Socket(host, port);
                PrintStream out = new PrintStream( socket.getOutputStream() );
                BufferedReader in = new BufferedReader( new InputStreamReader( socket.getInputStream() ) );
                out.print(mensagemFinal);
                String response = in.readLine();
                System.out.println(response);
                in.close();
                out.close();
                socket.close();
            }
            catch(UnknownHostException u) {
                System.out.println("Erro ao enviar mensagem: ");
                System.out.println(u);
                System.out.print("Exit? (y/n) >");
                String response = scan.nextLine();
                if (response.equals("y")){
                    line = "exit";
                }
            }
            catch(IOException i) {
                System.out.println("Erro ao enviar mensagem: ");
                System.out.println(i);
                System.out.print("Exit? (y/n) >");
                String response = scan.nextLine();
                if (response.equals("y")){
                    line = "exit";
                }
            }
        }
    }

    public static String getRandom(int max) {
        return String.valueOf((int)(Math.random() * max + 1));
    }

    public static void main(String args[])
    {
        Cliente client = new Cliente("172.15.3.50", 12000, "java_gamer".concat(getRandom(1000)));
    }
}
