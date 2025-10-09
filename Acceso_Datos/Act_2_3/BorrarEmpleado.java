package Acceso_Datos.Act_2_3;

import java.io.RandomAccessFile;
import java.util.Scanner;

public class BorrarEmpleado {
    public static void main(String[] args) throws Exception {
        Scanner sc = new Scanner(System.in);
        System.out.print("ID a borrar: ");
        int id = sc.nextInt();
        sc.close();

        try (RandomAccessFile raf = new RandomAccessFile("empleados.dat", "rw")) {
            boolean encontrado = false;
            while (raf.getFilePointer() < raf.length()) {
                long posicion = raf.getFilePointer();
                Empleado emp = Empleado.leer(raf);
                if (emp.getId() == id) {
                    raf.seek(posicion);
                    raf.writeInt(-1);
                    System.out.println("Empleado borrado lógicamente.");
                    encontrado = true;
                    break;
                }
            }
            if (!encontrado) System.out.println("ID no encontrado.");
        }
    }
}