package Acceso_Datos.Act_2_3;

import java.io.RandomAccessFile;
import java.util.Scanner;

public class ConsultarEmpleado {
    public static void main(String[] args) throws Exception {
        Scanner sc = new Scanner(System.in);
        System.out.print("Introduce el ID del empleado: ");
        int idBuscado = sc.nextInt();
        sc.close();

        try (RandomAccessFile raf = new RandomAccessFile("empleados.dat", "r")) {
            boolean encontrado = false;
            while (raf.getFilePointer() < raf.length()) {
                Empleado emp = Empleado.leer(raf);
                if (emp.getId() == idBuscado) {
                    System.out.println("Empleado encontrado: " + emp.getApellido() + ", Salario: " + emp.getSalario());
                    encontrado = true;
                    break;
                }
            }
            if (!encontrado) System.out.println("Empleado no encontrado.");
        }
    }
}