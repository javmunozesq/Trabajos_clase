package Acceso_Datos.Act_2_1;

import java.io.FileInputStream;
import java.io.ObjectInputStream;

public class LeerAlumnos {
    public static void main(String[] args) {
        try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream("alumno.dat"))) {
            Alumno alumno = (Alumno) ois.readObject();
            System.out.println("Alumno leído del fichero:");
            System.out.println(alumno);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}