package Acceso_Datos.Act_2_3;

import java.io.RandomAccessFile;

public class MostrarBorrados {
    public static void main(String[] args) throws Exception {
        try (RandomAccessFile raf = new RandomAccessFile("empleados.dat", "r")) {
            System.out.println("Empleados borrados:");
            while (raf.getFilePointer() < raf.length()) {
                Empleado emp = Empleado.leer(raf);
                if (emp.getId() == -1) {
                    System.out.println(emp.getApellido());
                }
            }
        }
    }
}