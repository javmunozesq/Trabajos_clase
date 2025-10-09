package Acceso_Datos.Act_2_1;

import java.io.FileOutputStream;
import java.io.ObjectOutputStream;

public class EscribirAlumnos {
    public static void main(String[] args) {
        Alumno alumno = new Alumno(1006, "Elena", "Moreno Sánchez", 'F', "ASIR", "1º", "D");

        try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("alumno.dat"))) {
            oos.writeObject(alumno);
            System.out.println("Fichero alumno.dat creado correctamente.");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}