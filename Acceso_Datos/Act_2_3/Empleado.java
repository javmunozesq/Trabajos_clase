package Acceso_Datos.Act_2_3;

import java.io.RandomAccessFile;

public class Empleado {
    public static final int TAMAÑO_REGISTRO = 52;

    private int id;
    private String apellido;
    private double salario;

    public Empleado(int id, String apellido, double salario) {
        this.id = id;
        this.apellido = String.format("%-20s", apellido).substring(0, 20); // Rellenar o recortar
        this.salario = salario;
    }

    public int getId() { return id; }
    public String getApellido() { return apellido.trim(); }
    public double getSalario() { return salario; }

    public void escribir(RandomAccessFile raf) throws Exception {
        raf.writeInt(id);
        for (int i = 0; i < 20; i++) {
            raf.writeChar(apellido.charAt(i));
        }
        raf.writeDouble(salario);
    }

    public static Empleado leer(RandomAccessFile raf) throws Exception {
        int id = raf.readInt();
        StringBuilder apellido = new StringBuilder();
        for (int i = 0; i < 20; i++) {
            apellido.append(raf.readChar());
        }
        double salario = raf.readDouble();
        return new Empleado(id, apellido.toString(), salario);
    }
}