//Hecho por Javier Muñoz Esqueta
//El programa consiste en un monitor de procesos en el que puede introducir cualquier comando del sistema operativo
//y se ejecutará mostrando su salida en tiempo real. Además, permite finalizar el proceso manualmente y muestra métricas al finalizar.

package Servicios_procesos.Procesos.Monitor_Procesos;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Scanner;

public class Monitor {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Introduce el comando a ejecutar: ");
        String commandLine = scanner.nextLine();

        String os = System.getProperty("os.name").toLowerCase();
        String[] command;

        //Mejora para poder ejecutar todos los comandos en Windows y Linux/macOS

        // Si es Windows, envolvemos con cmd.exe /c
        if (os.contains("win")) {
            command = new String[]{"cmd.exe", "/c", commandLine};
        } else {
            // En Linux/macOS basta con dividir el comando
            command = commandLine.split(" ");
        }

        ProcessBuilder pb = new ProcessBuilder(command);
        pb.redirectErrorStream(true); // combinar salida estándar y error

        long startTime = 0;

        try {
            final Process process = pb.start();
            startTime = System.currentTimeMillis();

            // Hilo para leer la salida en tiempo real
            Thread outputThread = new Thread(() -> {
                try (BufferedReader reader = new BufferedReader(
                        new InputStreamReader(process.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        System.out.println(line);
                    }
                } catch (IOException e) {
                    System.err.println("Error leyendo la salida del proceso: " + e.getMessage());
                }
            });
            outputThread.start();

            // Hilo para permitir finalización manual
            Thread killerThread = new Thread(() -> {
                System.out.println("\nPulsa ENTER si deseas finalizar el proceso manualmente...");
                scanner.nextLine(); // espera ENTER
                process.destroy();
                System.out.println("Proceso finalizado manualmente.");
            });
            killerThread.start();

            // Esperar a que termine el proceso
            int exitCode = process.waitFor();
            long endTime = System.currentTimeMillis();

            // Esperar a que los hilos terminen
            outputThread.join();
            killerThread.interrupt(); // si el proceso ya terminó, interrumpimos el killerThread

            // Métricas
            double totalSeconds = (endTime - startTime) / 1000.0;
            System.out.println("\n===== RESULTADOS =====");
            System.out.println("Código de salida: " + exitCode);
            System.out.printf("Tiempo total: %.3f segundos%n", totalSeconds);

        } catch (IOException e) {
            System.err.println("Error al ejecutar el comando: " + e.getMessage());
        } catch (InterruptedException e) {
            System.err.println("La espera del proceso fue interrumpida: " + e.getMessage());
            Thread.currentThread().interrupt();
        } finally {
            scanner.close();
        }
    }
}