package Acceso_Datos.Act_2_3;

import java.io.RandomAccessFile;
import java.util.Scanner;

public class InsertarEmpleado {
    public static void main(String[] args) throws Exception {
        Scanner sc = new Scanner(System.in);
        System.out.print("ID: ");
        int id = sc.nextInt();
        sc.nextLine();
        System.out.print("Apellido: ");
        String apellido = sc.nextLine();
        System.out.print("Salario: ");
        double salario = sc.nextDouble();
        sc.close();

        try (RandomAccessFile raf = new RandomAccessFile("empleados.dat", "rw")) {
            boolean existe = false;
            while (raf.getFilePointer() < raf.length()) {
                Empleado emp = Empleado.leer(raf);
                if (emp.getId() == id) {
                    existe = true;
                    break;
                }
            }
            if (existe) {
                System.out.println("El ID ya existe.");
            } else {
                raf.seek(raf.length());
                new Empleado(id, apellido, salario).escribir(raf);
                System.out.println("Empleado insertado.");
            }
        }
    }
}