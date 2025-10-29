package Servicios_procesos.Hilos.Banco;

import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

class CuentaBancariaSegura {
    private int id;
    private double saldo;
    private final Lock lock = new ReentrantLock();

    public CuentaBancariaSegura(int id, double saldoInicial) {
        this.id = id;
        this.saldo = saldoInicial;
    }

    public int getId() { return id; }
    public double getSaldo() { return saldo; }

    // Solución a la condición de carrera
    public void transferirConSincronizacion(CuentaBancariaSegura destino, double monto) {
        lock.lock();
        try {
            if (saldo >= monto) {
                try { Thread.sleep(100); } catch (InterruptedException e) {}
                saldo -= monto;
                destino.saldo += monto;
                System.out.println(Thread.currentThread().getName() + " ✅ Transferencia sincronizada: $" + monto);
            } else {
                System.out.println(Thread.currentThread().getName() + " ❌ Fondos insuficientes");
            }
        } finally {
            lock.unlock();
        }
    }

    // Solución al deadlock
    public void transferirSinDeadlock(CuentaBancariaSegura destino, double monto) {
        Lock primero = this.id < destino.id ? this.lock : destino.lock;
        Lock segundo = this.id < destino.id ? destino.lock : this.lock;

        primero.lock();
        try {
            segundo.lock();
            try {
                if (saldo >= monto) {
                    saldo -= monto;
                    destino.saldo += monto;
                    System.out.println(Thread.currentThread().getName() + " ✅ Transferencia sin deadlock: $" + monto);
                }
            } finally {
                segundo.unlock();
            }
        } finally {
            primero.unlock();
        }
    }

    // Sección crítica completamente protegida
    public void transferirSeccionCriticaCompleta(CuentaBancariaSegura destino, double monto) {
        lock.lock();
        destino.lock.lock();
        try {
            if (saldo >= monto) {
                saldo -= monto;
                destino.saldo += monto;
                System.out.println(Thread.currentThread().getName() + " ✅ Transferencia protegida: $" + monto);
            }
        } finally {
            destino.lock.unlock();
            lock.unlock();
        }
    }
}

class ClienteSincronizado extends Thread {
    private CuentaBancariaSegura origen, destino;
    private double monto;

    public ClienteSincronizado(String nombre, CuentaBancariaSegura origen, CuentaBancariaSegura destino, double monto) {
        super(nombre);
        this.origen = origen;
        this.destino = destino;
        this.monto = monto;
    }

    public void run() {
        origen.transferirConSincronizacion(destino, monto);
    }
}

class ClienteSinDeadlock extends Thread {
    private CuentaBancariaSegura origen, destino;
    private double monto;

    public ClienteSinDeadlock(String nombre, CuentaBancariaSegura origen, CuentaBancariaSegura destino, double monto) {
        super(nombre);
        this.origen = origen;
        this.destino = destino;
        this.monto = monto;
    }

    public void run() {
        origen.transferirSinDeadlock(destino, monto);
    }
}

class ClienteSeccionCriticaCompleta extends Thread {
    private CuentaBancariaSegura origen, destino;
    private double monto;

    public ClienteSeccionCriticaCompleta(String nombre, CuentaBancariaSegura origen, CuentaBancariaSegura destino, double monto) {
        super(nombre);
        this.origen = origen;
        this.destino = destino;
        this.monto = monto;
    }

    public void run() {
        origen.transferirSeccionCriticaCompleta(destino, monto);
    }
}



class SistemaBancarioSeguro {
    public static void main(String[] args) {
        System.out.println("✅ SISTEMA BANCARIO CONCURRENTE - CON SOLUCIONES\n");

        // Test sincronización
        CuentaBancariaSegura cuenta1 = new CuentaBancariaSegura(1, 100);
        CuentaBancariaSegura cuenta2 = new CuentaBancariaSegura(2, 0);
        Thread[] hilosSync = new Thread[15];
        for (int i = 0; i < 15; i++) {
            hilosSync[i] = new ClienteSincronizado("Sync-" + i, cuenta1, cuenta2, 10);
            hilosSync[i].start();
        }
        for (Thread hilo : hilosSync) {
            try { hilo.join(); } catch (InterruptedException e) {}
        }
        System.out.println("🔒 Saldo total sincronizado: $" + (cuenta1.getSaldo() + cuenta2.getSaldo()));

        // Test sin deadlock
        CuentaBancariaSegura cuentaA = new CuentaBancariaSegura(3, 1000);
        CuentaBancariaSegura cuentaB = new CuentaBancariaSegura(4, 1000);
        Thread hiloA = new ClienteSinDeadlock("Deadlock-Free-A", cuentaA, cuentaB, 100);
        Thread hiloB = new ClienteSinDeadlock("Deadlock-Free-B", cuentaB, cuentaA, 150);
        hiloA.start();
        hiloB.start();
        try {
            hiloA.join();
            hiloB.join();
        } catch (InterruptedException e) {}

        // Test sección crítica completa
        CuentaBancariaSegura cuentaSC1 = new CuentaBancariaSegura(5, 200);
        CuentaBancariaSegura cuentaSC2 = new CuentaBancariaSegura(6, 0);
        Thread[] hilosSC = new Thread[5];
        for (int i = 0; i < 5; i++) {
            hilosSC[i] = new ClienteSeccionCriticaCompleta("SC-" + i, cuentaSC1, cuentaSC2, 50);
            hilosSC[i].start();
        }
        for (Thread hilo : hilosSC) {
            try { hilo.join(); } catch (InterruptedException e) {}
        }
        System.out.println("🔒 Saldo total protegido: $" + (cuentaSC1.getSaldo() + cuentaSC2.getSaldo()));
    }
}