import threading
import time
import random


# =========================
# UTILIDAD PARA MEDIR TIEMPO
# =========================

def medir(nombre, funcion):
    inicio = time.perf_counter()
    resultado = funcion()
    fin = time.perf_counter()
    tiempo = fin - inicio

    print(f"{nombre}: {tiempo:.4f} segundos")
    return resultado, tiempo


# =========================
# 1. VENTA DE BOLETOS
# =========================

def venta_secuencial():
    boletos = 0
    n_hilos = 5
    m_ventas = 1_000_000

    for _ in range(n_hilos):
        for _ in range(m_ventas):
            boletos += 1

    return boletos


def venta_concurrente():
    boletos = {"valor": 0}
    lock = threading.Lock()

    n_hilos = 5
    m_ventas = 1_000_000

    def vender():
        for _ in range(m_ventas):
            with lock:
                boletos["valor"] += 1

    hilos = [threading.Thread(target=vender) for _ in range(n_hilos)]

    for h in hilos:
        h.start()

    for h in hilos:
        h.join()

    return boletos["valor"]


# =========================
# 2. GIMNASIO
# =========================

def gimnasio_secuencial():
    for i in range(8):
        print(f"Atleta {i + 1} entrenando secuencialmente")
        time.sleep(0.2)


def gimnasio_concurrente():
    semaforo = threading.Semaphore(3)

    def atleta(i):
        print(f"Atleta {i + 1} espera su turno")

        with semaforo:
            print(f"Atleta {i + 1} entrenando")
            time.sleep(0.2)
            print(f"Atleta {i + 1} salio")

    hilos = [threading.Thread(target=atleta, args=(i,)) for i in range(8)]

    for h in hilos:
        h.start()

    for h in hilos:
        h.join()


# =========================
# 3. PANADERIA
# PRODUCTOR - CONSUMIDOR
# =========================

def panaderia_secuencial():
    vitrina = []

    for i in range(10):
        pan = f"Pan {i + 1}"
        vitrina.append(pan)
        print(f"Producido: {pan}")

    for i in range(10):
        pan = vitrina.pop(0)
        print(f"Consumido: {pan}")


def panaderia_concurrente():
    vitrina = []
    limite = 5
    condicion = threading.Condition()

    def productor():
        for i in range(10):
            pan = f"Pan {i + 1}"

            with condicion:
                while len(vitrina) == limite:
                    condicion.wait()

                vitrina.append(pan)
                print(f"Producido: {pan}")
                condicion.notify()

            time.sleep(0.1)

    def consumidor():
        for _ in range(10):
            with condicion:
                while len(vitrina) == 0:
                    condicion.wait()

                pan = vitrina.pop(0)
                print(f"Consumido: {pan}")
                condicion.notify()

            time.sleep(0.1)

    h1 = threading.Thread(target=productor)
    h2 = threading.Thread(target=consumidor)

    h1.start()
    h2.start()

    h1.join()
    h2.join()


# =========================
# 4. LECTORES ESCRITORES
# =========================

def lectores_escritores_secuencial():
    tablon = "Nota inicial"

    for i in range(3):
        print(f"Lector {i + 1} lee: {tablon}")
        time.sleep(0.2)

    for i in range(2):
        tablon = f"Nota escrita por escritor {i + 1}"
        print(f"Escritor {i + 1} escribio: {tablon}")
        time.sleep(0.2)


def lectores_escritores_concurrente():
    cant_lectores = {"valor": 0}
    tablon = {"nota": "Nota inicial"}

    mutex_lectores = threading.Lock()
    sem_escritor = threading.Semaphore(1)

    def lector(id_lector):
        for _ in range(2):
            with mutex_lectores:
                cant_lectores["valor"] += 1

                if cant_lectores["valor"] == 1:
                    sem_escritor.acquire()

            print(f"Lector {id_lector} lee: {tablon['nota']}")
            time.sleep(0.2)

            with mutex_lectores:
                cant_lectores["valor"] -= 1

                if cant_lectores["valor"] == 0:
                    sem_escritor.release()

            time.sleep(0.1)

    def escritor(id_escritor):
        for _ in range(2):
            sem_escritor.acquire()

            tablon["nota"] = f"Nota escrita por escritor {id_escritor}"
            print(f"Escritor {id_escritor} escribio: {tablon['nota']}")
            time.sleep(0.2)

            sem_escritor.release()
            time.sleep(0.1)

    hilos = []

    for i in range(3):
        hilos.append(threading.Thread(target=lector, args=(i + 1,)))

    for i in range(2):
        hilos.append(threading.Thread(target=escritor, args=(i + 1,)))

    for h in hilos:
        h.start()

    for h in hilos:
        h.join()


# =========================
# 5. BARRERA DE SINCRONIZACION
# =========================

def barrera_secuencial():
    for i in range(5):
        print(f"Hilo simulado {i + 1} fase 1")
        time.sleep(0.2)

    print("Todos llegaron a la barrera")

    for i in range(5):
        print(f"Hilo simulado {i + 1} fase 2")
        time.sleep(0.2)


def barrera_concurrente():
    contador = {"valor": 0}
    n_total = 5

    lock = threading.Lock()
    condicion = threading.Condition(lock)

    def tarea(id_hilo):
        print(f"Hilo {id_hilo} fase 1")
        time.sleep(random.random())

        with condicion:
            contador["valor"] += 1
            print(f"Hilo {id_hilo} llego a la barrera ({contador['valor']}/{n_total})")

            if contador["valor"] == n_total:
                print("Todos llegaron. Se despiertan los hilos")
                condicion.notify_all()
            else:
                while contador["valor"] < n_total:
                    condicion.wait()

        print(f"Hilo {id_hilo} fase 2")

    hilos = [threading.Thread(target=tarea, args=(i + 1,)) for i in range(n_total)]

    for h in hilos:
        h.start()

    for h in hilos:
        h.join()


# =========================
# EJECUCION GENERAL
# =========================

print("\n========== COMPARACION SECUENCIAL VS CONCURRENTE ==========\n")

print("\n--- 1. VENTA DE BOLETOS ---")
res_seq, t_seq = medir("Secuencial", venta_secuencial)
res_conc, t_conc = medir("Concurrente", venta_concurrente)
print(f"Resultado secuencial: {res_seq}")
print(f"Resultado concurrente: {res_conc}")

print("\n--- 2. GIMNASIO ---")
_, t_seq = medir("Secuencial", gimnasio_secuencial)
_, t_conc = medir("Concurrente", gimnasio_concurrente)

print("\n--- 3. PANADERIA ---")
_, t_seq = medir("Secuencial", panaderia_secuencial)
_, t_conc = medir("Concurrente", panaderia_concurrente)

print("\n--- 4. LECTORES ESCRITORES ---")
_, t_seq = medir("Secuencial", lectores_escritores_secuencial)
_, t_conc = medir("Concurrente", lectores_escritores_concurrente)

print("\n--- 5. BARRERA ---")
_, t_seq = medir("Secuencial", barrera_secuencial)
_, t_conc = medir("Concurrente", barrera_concurrente)

print("\n========== FIN DE LA COMPARACION ==========")