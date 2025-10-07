package Servicios_procesos.Hilos.Act2;

import java.util.Random;

class ProcesadorUrgente extends Thread {
    private String pedido;

    public ProcesadorUrgente(String pedido) {
        this.pedido = pedido;
    }

    public void run() {
        Random random = new Random();
        System.out.println("Procesando pedido urgente: " + pedido);

        for (int progreso = 0; progreso <= 100; progreso += 25) {
            try {
                Thread.sleep(300 + random.nextInt(700)); // Pausa entre 300ms y 1000ms
                System.out.println("Urgente [" + pedido + "] - Progreso: " + progreso + "%");
            } catch (InterruptedException e) {
                System.out.println("Error en pedido urgente: " + pedido);
            }
        }

        System.out.println("Pedido urgente completado: " + pedido);
    }
}

class ProcesadorEstandar implements Runnable {
    private String pedido;

    public ProcesadorEstandar(String pedido) {
        this.pedido = pedido;
    }

    @Override
    public void run() {
        Random random = new Random();
        System.out.println("Procesando pedido estándar: " + pedido);

        for (int progreso = 0; progreso <= 100; progreso += 25) {
            try {
                Thread.sleep(500 + random.nextInt(1000)); // Pausa entre 500ms y 1500ms
                System.out.println("Estándar [" + pedido + "] - Progreso: " + progreso + "%");
            } catch (InterruptedException e) {
                System.out.println("Error en pedido estándar: " + pedido);
            }
        }

        System.out.println("Pedido estándar completado: " + pedido);
    }
}

public class SistemaPedidos {
    public static void main(String[] args) {
        long inicio = System.currentTimeMillis();

        // Crear procesadores
        ProcesadorUrgente urgente1 = new ProcesadorUrgente("Pedido-U1");
        ProcesadorUrgente urgente2 = new ProcesadorUrgente("Pedido-U2");

        Thread estandar1 = new Thread(new ProcesadorEstandar("Pedido-E1"));
        Thread estandar2 = new Thread(new ProcesadorEstandar("Pedido-E2"));

        // Iniciar todos los hilos
        urgente1.start();
        urgente2.start();
        estandar1.start();
        estandar2.start();

        // Esperar a que todos terminen
        try {
            urgente1.join();
            urgente2.join();
            estandar1.join();
            estandar2.join();
        } catch (InterruptedException e) {
            System.out.println("Error esperando la finalización de los pedidos.");
        }

        long fin = System.currentTimeMillis();
        long tiempoTotal = fin - inicio;

        System.out.println("\n Tiempo total de procesamiento: " + tiempoTotal + " ms");
    }
}