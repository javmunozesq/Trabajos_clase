package Acceso_Datos.Act_2_3;

import java.io.RandomAccessFile;
import java.util.Scanner;

public class ModificarSalario {
    public static void main(String[] args) throws Exception {
        Scanner sc = new Scanner(System.in);
        System.out.print("ID: ");
        int id = sc.nextInt();
        System.out.print("Nuevo salario: ");
        double nuevoSalario = sc.nextDouble();
        sc.close();

        try (RandomAccessFile raf = new RandomAccessFile("empleados.dat", "rw")) {
            boolean encontrado = false;
            while (raf.getFilePointer() < raf.length()) {
                long posicion = raf.getFilePointer();
                Empleado emp = Empleado.leer(raf);
                if (emp.getId() == id) {
                    raf.seek(posicion + 4 + 40); // Saltar ID y apellido
                    raf.writeDouble(nuevoSalario);
                    System.out.println("Salario modificado para " + emp.getApellido());
                    encontrado = true;
                    break;
                }
            }
            if (!encontrado) System.out.println("ID no encontrado.");
        }
    }
}