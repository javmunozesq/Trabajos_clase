import java.io.*;
import java.util.Scanner;

public class FicheroAleatorio {
    private static final String FILENAME = "empleados.dat";
    private static final int RECORD_SIZE = 36; // bytes
    private static final int APELLIDO_CHARS = 10;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int opcion;
        do {
            System.out.println("............................................................");
            System.out.println(". 1 Crear fichero directo.");
            System.out.println(". 2 Visualizar todos (huecos y borrados).");
            System.out.println(". 3 Visualizar registros (sin huecos y sin los borrados).");
            System.out.println(". 4 Consultar registro.");
            System.out.println(". 5 Insertar n registros");
            System.out.println(". 6 Subir salario a un empleado.");
            System.out.println(". 7 Borrar un registro.");
            System.out.println(". 0 Salir.");
            System.out.println("............................................................");
            System.out.print("TECLEA OPERACIÓN: ");
            opcion = sc.nextInt();
            sc.nextLine();
            try {
                switch (opcion) {
                    case 1 -> crearFichero();
                    case 2 -> visualizarTodos();
                    case 3 -> visualizarSinHuecos();
                    case 4 -> consultarRegistro(sc);
                    case 5 -> insertarRegistros(sc);
                    case 6 -> subirSalario(sc);
                    case 7 -> borrarRegistro(sc);
                    case 0 -> System.out.println("Saliendo...");
                    default -> System.out.println("Opción no válida.");
                }
            } catch (IOException e) {
                System.out.println("Error E/S: " + e.getMessage());
            }
            System.out.println();
        } while (opcion != 0);
        sc.close();
    }

    // Crear fichero con los 7 empleados iniciales
    private static void crearFichero() throws IOException {
        String apellido[] = {"FERNANDEZ","GIL","LOPEZ","RAMOS", "SEVILLA","CASILLA", "REY"};
        int dep[] = {10, 20, 10, 10, 30, 30, 20};
        Double salario[] = {1000.45, 2400.60, 3000.0, 1500.56,2200.0, 1435.87, 2000.0};

        try (RandomAccessFile raf = new RandomAccessFile(FILENAME, "rw")) {
            raf.setLength(0); // borrar contenido anterior
            for (int i = 0; i < apellido.length; i++) {
                int numEmpleado = i + 1; // nunca será 0
                raf.writeInt(numEmpleado);
                writeFixedString(raf, apellido[i], APELLIDO_CHARS);
                raf.writeInt(dep[i]);
                raf.writeDouble(salario[i]);
            }
        }
        System.out.println("Fichero creado con 7 empleados.");
    }

    // Visualizar todos los registros (incluye huecos con numEmpleado == 0)
    private static void visualizarTodos() throws IOException {
        try (RandomAccessFile raf = new RandomAccessFile(FILENAME, "r")) {
            long totalReg = raf.length() / RECORD_SIZE;
            if (totalReg == 0) {
                System.out.println("Fichero vacío.");
                return;
            }
            System.out.printf("%-8s %-12s %-6s %s%n", "NUM", "APELLIDO", "DEP", "SALARIO");
            for (int i = 0; i < totalReg; i++) {
                raf.seek(i * RECORD_SIZE);
                int num = raf.readInt();
                String ap = readFixedString(raf, APELLIDO_CHARS).trim();
                int dep = raf.readInt();
                double sal = raf.readDouble();
                System.out.printf("%-8d %-12s %-6d %.2f%n", num, ap, dep, sal);
            }
        }
    }

    // Visualizar solo registros ocupados (numEmpleado != 0)
    private static void visualizarSinHuecos() throws IOException {
        try (RandomAccessFile raf = new RandomAccessFile(FILENAME, "r")) {
            long totalReg = raf.length() / RECORD_SIZE;
            if (totalReg == 0) {
                System.out.println("Fichero vacío.");
                return;
            }
            System.out.printf("%-8s %-12s %-6s %s%n", "NUM", "APELLIDO", "DEP", "SALARIO");
            for (int i = 0; i < totalReg; i++) {
                raf.seek(i * RECORD_SIZE);
                int num = raf.readInt();
                String ap = readFixedString(raf, APELLIDO_CHARS).trim();
                int dep = raf.readInt();
                double sal = raf.readDouble();
                if (num != 0) {
                    System.out.printf("%-8d %-12s %-6d %.2f%n", num, ap, dep, sal);
                }
            }
        }
    }

    // Consultar un registro por número (num >=1)
    private static void consultarRegistro(Scanner sc) throws IOException {
        System.out.print("Introduce número de registro a consultar: ");
        int num = sc.nextInt();
        if (num <= 0) {
            System.out.println("Número de empleado inválido (no puede ser 0 ni negativo).");
            return;
        }
        long pos = (long)(num - 1) * RECORD_SIZE;
        try (RandomAccessFile raf = new RandomAccessFile(FILENAME, "r")) {
            if (pos >= raf.length()) {
                System.out.println("NO EXISTE: posición fuera del fichero.");
                return;
            }
            raf.seek(pos);
            int numEmp = raf.readInt();
            String ap = readFixedString(raf, APELLIDO_CHARS).trim();
            int dep = raf.readInt();
            double sal = raf.readDouble();
            if (numEmp == 0) {
                System.out.println("NO EXISTE: registro borrado o hueco.");
            } else {
                System.out.printf("NUM: %d  APELLIDO: %s  DEP: %d  SALARIO: %.2f%n", numEmp, ap, dep, sal);
            }
        }
    }

    // Insertar varios registros; comprueba si ya existe (numEmpleado != 0 => ya existe)
    private static void insertarRegistros(Scanner sc) throws IOException {
        System.out.print("¿Cuántos registros quieres insertar? ");
        int n = sc.nextInt();
        sc.nextLine();
        try (RandomAccessFile raf = new RandomAccessFile(FILENAME, "rw")) {
            for (int i = 0; i < n; i++) {
                System.out.println("Registro " + (i+1) + ":");
                System.out.print("Introduce número de empleado (entero, distinto de 0): ");
                int num = sc.nextInt();
                sc.nextLine();
                if (num <= 0) {
                    System.out.println("Número inválido. Se salta este registro.");
                    continue;
                }
                long pos = (long)(num - 1) * RECORD_SIZE;
                // ampliar fichero si es necesario
                if (pos > raf.length()) {
                    // rellenar con registros vacíos hasta llegar
                    long registrosActuales = raf.length() / RECORD_SIZE;
                    raf.seek(raf.length());
                    for (long r = registrosActuales; r < (num - 1); r++) {
                        raf.writeInt(0); // numEmpleado = 0
                        writeFixedString(raf, "", APELLIDO_CHARS);
                        raf.writeInt(0);
                        raf.writeDouble(0.0);
                    }
                }
                raf.seek(pos);
                int existente = 0;
                if (pos < raf.length()) {
                    existente = raf.readInt();
                }
                if (existente != 0) {
                  String apExistente = readFixedString(raf, APELLIDO_CHARS).trim();
                  int depExistente = raf.readInt();
                  double salExistente = raf.readDouble();
                  System.out.printf("Ya existe: NUM=%d, APELLIDO=%s, DEP=%d, SALARIO=%.2f%n", existente, apExistente, depExistente, salExistente);

                    // avanzar lectura para no romper el flujo si seguimos leyendo en este archivo
                } else {
                    System.out.print("Apellido: ");
                    String apellido = sc.nextLine().trim();
                    System.out.print("Departamento (entero): ");
                    int dep = sc.nextInt();
                    System.out.print("Salario (double): ");
                    double sal = sc.nextDouble();
                    sc.nextLine();
                    raf.seek(pos);
                    raf.writeInt(num);
                    writeFixedString(raf, apellido, APELLIDO_CHARS);
                    raf.writeInt(dep);
                    raf.writeDouble(sal);
                    System.out.println("Registro insertado.");
                }
            }
        }
    }

    // Subir salario: se accede al registro, se lee salario, se calcula nuevo y se reescribe sobrescribiendo la double
    private static void subirSalario(Scanner sc) throws IOException {
        System.out.print("Introduce número de empleado a subir salario: ");
        int num = sc.nextInt();
        if (num <= 0) {
            System.out.println("Número inválido.");
            return;
        }
        System.out.print("Introduce incremento (por ejemplo 200 o 10% -> escribe 10%): ");
        sc.nextLine();
        String incStr = sc.nextLine().trim();
        boolean porcentaje = incStr.endsWith("%");
        double incremento = 0.0;
        if (porcentaje) {
            try {
                incremento = Double.parseDouble(incStr.substring(0, incStr.length() - 1));
            } catch (NumberFormatException e) {
                System.out.println("Formato de porcentaje inválido.");
                return;
            }
        } else {
            try {
                incremento = Double.parseDouble(incStr);
            } catch (NumberFormatException e) {
                System.out.println("Formato de incremento inválido.");
                return;
            }
        }

        long pos = (long)(num - 1) * RECORD_SIZE;
        try (RandomAccessFile raf = new RandomAccessFile(FILENAME, "rw")) {
            if (pos >= raf.length()) {
                System.out.println("NO EXISTE: posición fuera del fichero.");
                return;
            }
            raf.seek(pos);
            int numEmp = raf.readInt();
            String ap = readFixedString(raf, APELLIDO_CHARS).trim();
            int dep = raf.readInt();
            double sal = raf.readDouble();
            if (numEmp == 0) {
                System.out.println("NO EXISTE: registro borrado o hueco.");
                return;
            }
            double nuevoSal = sal;
            if (porcentaje) {
                nuevoSal = sal + sal * (incremento / 100.0);
            } else {
                nuevoSal = sal + incremento;
            }
            // posicionarse 8 bytes hacia atrás para sobrescribir el double
            raf.seek(pos + 4 + (APELLIDO_CHARS * 2) + 4); // int + apellido + int => offset del double
            raf.writeDouble(nuevoSal);
            System.out.printf("Salario actualizado de %.2f a %.2f para empleado %d (%s)%n", sal, nuevoSal, numEmp, ap);
        }
    }

    // Borrar registro: asigna numEmpleado = 0 (marca como hueco)
    private static void borrarRegistro(Scanner sc) throws IOException {
        System.out.print("Introduce número de registro a borrar: ");
        int num = sc.nextInt();
        if (num <= 0) {
            System.out.println("Número inválido.");
            return;
        }
        long pos = (long)(num - 1) * RECORD_SIZE;
        try (RandomAccessFile raf = new RandomAccessFile(FILENAME, "rw")) {
            if (pos >= raf.length()) {
                System.out.println("NO EXISTE: posición fuera del fichero.");
                return;
            }
            raf.seek(pos);
            int numEmp = raf.readInt();
            if (numEmp == 0) {
                System.out.println("Registro ya vacío.");
                return;
            }
            raf.seek(pos);
            raf.writeInt(0); // marcar como borrado/hueco
            System.out.println("Registro borrado (marcado con numEmpleado = 0).");
        }
    }

    // Escribe apellido como cadena fija de APELLIDO_CHARS caracteres (2 bytes por char)
    private static void writeFixedString(RandomAccessFile raf, String s, int length) throws IOException {
        StringBuilder sb = new StringBuilder(s == null ? "" : s);
        if (sb.length() > length) {
            sb.setLength(length);
        } else {
            while (sb.length() < length) {
                sb.append(' ');
            }
        }
        // writeChar escribe 2 bytes por char (UTF-16 BE surrogate handling), se ajusta al enunciado
        for (int i = 0; i < length; i++) {
            raf.writeChar(sb.charAt(i));
        }
    }

    // Lee una cadena fija de length chars
    private static String readFixedString(RandomAccessFile raf, int length) throws IOException {
        StringBuilder sb = new StringBuilder(length);
        for (int i = 0; i < length; i++) {
            char c = raf.readChar();
            sb.append(c);
        }
        return sb.toString();
    }
}