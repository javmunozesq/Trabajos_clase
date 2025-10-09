package Acceso_Datos.Act_2_1;

import java.io.Serializable;

public class Alumno implements Serializable {
    private int nia;
    private String nombre;
    private String apellidos;
    private char sexo;
    private String ciclo;
    private String curso;
    private String grupo;

    public Alumno(int nia, String nombre, String apellidos, char sexo, String ciclo, String curso, String grupo) {
        this.nia = nia;
        this.nombre = nombre;
        this.apellidos = apellidos;
        this.sexo = sexo;
        this.ciclo = ciclo;
        this.curso = curso;
        this.grupo = grupo;
    }

    public String toString() {
        return "NIA: " + nia + ", Nombre: " + nombre + ", Apellidos: " + apellidos +
               ", Sexo: " + sexo + ", Ciclo: " + ciclo + ", Curso: " + curso + ", Grupo: " + grupo;
    }
}