/*  Hecho por Javier Muñoz
Este programa simula la descarga concurrente de varios archivos usando hilos indicando al final
si se descargaron correctamente y el tiempo de ejecución
*/

import java.util.Random;

class DescargaArchivo extends Thread {
    private String nombreArchivo;
    private boolean descargadoCorrectamente = false;

    public DescargaArchivo(String nombreArchivo) {
        this.nombreArchivo = nombreArchivo;
    }

    public boolean isDescargadoCorrectamente() {
        return descargadoCorrectamente;
    }

    public void run() {
        Random random = new Random();
        System.out.println("Iniciando descarga de " + nombreArchivo);

        for (int progreso = 0; progreso <= 100; progreso += 25) {
            try {
                Thread.sleep(500 + random.nextInt(1000)); // Pausa aleatoria entre 500ms y 1500ms
                System.out.println(nombreArchivo + " - Progreso: " + progreso + "%");
            } catch (InterruptedException e) {
                System.out.println("Error en la descarga de " + nombreArchivo);
                return;
            }
        }

        descargadoCorrectamente = true;
        System.out.println("Descarga completada de " + nombreArchivo);
    }
}

public class SimuladorDescargas {
    public static void main(String[] args) {
        long inicio = System.currentTimeMillis();

        DescargaArchivo archivo1 = new DescargaArchivo("archivo1.zip");
        DescargaArchivo archivo2 = new DescargaArchivo("archivo2.pdf");
        DescargaArchivo archivo3 = new DescargaArchivo("archivo3.jpg");

        archivo1.start();
        archivo2.start();
        archivo3.start();

        try {
            archivo1.join();
            archivo2.join();
            archivo3.join();
        } catch (InterruptedException e) {
            System.out.println("Error esperando la finalización de los hilos.");
        }

        long fin = System.currentTimeMillis();
        long tiempoTotal = fin - inicio;

        System.out.println("\n Resultados de descarga:");
        System.out.println("archivo1.zip: " + (archivo1.isDescargadoCorrectamente() ? " Completado" : " Fallido"));
        System.out.println("archivo2.pdf: " + (archivo2.isDescargadoCorrectamente() ? " Completado" : " Fallido"));
        System.out.println("archivo3.jpg: " + (archivo3.isDescargadoCorrectamente() ? " Completado" : " Fallido"));

        System.out.println("\nTiempo total de ejecución: " + tiempoTotal + " ms");
    }
}