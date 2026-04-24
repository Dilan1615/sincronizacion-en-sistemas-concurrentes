from flask import Flask, render_template, request
import threading
import time
import random

app = Flask(__name__)


#PRODUCTOR CONSUMIDOR (Panaderia)

def ejecutar_panaderia():
    buffer = []
    LIMITE = 5
    condicion = threading.Condition()
    logs = []

    def productor():
        for _ in range(10):
            pan = random.randint(1, 100)

            with condicion:
                while len(buffer) == LIMITE:
                    logs.append("Panaderia llena. Esperando...")
                    condicion.wait()

                buffer.append(pan)
                logs.append(f"Pan producido: {pan}")

                condicion.notify()

            time.sleep(0.1)

    def consumidor():
        for _ in range(10):
            with condicion:
                while len(buffer) == 0:
                    logs.append("Sin pan. Cliente esperando...")
                    condicion.wait()

                pan = buffer.pop(0)
                logs.append(f"Cliente compro pan: {pan}")

                condicion.notify()

            time.sleep(0.1)

    h1 = threading.Thread(target=productor)
    h2 = threading.Thread(target=consumidor)

    h1.start()
    h2.start()
    h1.join()
    h2.join()

    return logs



# LECTORES ESCRITORES

def ejecutar_lectores():
    logs = []
    tablon = {"nota": "Nota inicial"}
    cant_lectores = {"valor": 0}

    mutex = threading.Lock()
    sem_escritor = threading.Semaphore(1)

    def lector(i):
        for _ in range(2):
            with mutex:
                cant_lectores["valor"] += 1
                if cant_lectores["valor"] == 1:
                    sem_escritor.acquire()

            logs.append(f"Lector {i} lee: {tablon['nota']}")
            time.sleep(0.1)

            with mutex:
                cant_lectores["valor"] -= 1
                if cant_lectores["valor"] == 0:
                    sem_escritor.release()

    def escritor(i):
        for _ in range(2):
            sem_escritor.acquire()
            tablon["nota"] = f"Escrito por escritor {i}"
            logs.append(f"Escritor {i} escribio")
            time.sleep(0.1)
            sem_escritor.release()

    hilos = []

    for i in range(3):
        hilos.append(threading.Thread(target=lector, args=(i+1,)))

    for i in range(2):
        hilos.append(threading.Thread(target=escritor, args=(i+1,)))

    for h in hilos:
        h.start()

    for h in hilos:
        h.join()

    return logs



# BARRERA

def ejecutar_barrera():
    logs = []
    contador = {"valor": 0}
    N = 5

    lock = threading.Lock()
    cond = threading.Condition(lock)

    def hilo(i):
        time.sleep(random.random())

        with cond:
            contador["valor"] += 1
            logs.append(f"Hilo {i} llego ({contador['valor']}/{N})")

            if contador["valor"] == N:
                logs.append("Todos llegaron, continuar")
                cond.notify_all()
            else:
                while contador["valor"] < N:
                    logs.append(f"Hilo {i} esperando")
                    cond.wait()

        logs.append(f"Hilo {i} continua")

    hilos = [threading.Thread(target=hilo, args=(i+1,)) for i in range(N)]

    for h in hilos:
        h.start()

    for h in hilos:
        h.join()

    return logs



#GIMNASIO

def ejecutar_gimnasio():
    logs = []
    semaforo = threading.Semaphore(3)

    def atleta(i):
        logs.append(f"Atleta {i} esperando")

        with semaforo:
            logs.append(f"Atleta {i} entrenando")
            time.sleep(0.5)
            logs.append(f"Atleta {i} salio")

    hilos = [threading.Thread(target=atleta, args=(i+1,)) for i in range(8)]

    for h in hilos:
        h.start()

    for h in hilos:
        h.join()

    return logs



#VENTA BOLETOS

def ejecutar_venta():
    boletos = {"valor": 0}
    lock = threading.Lock()

    N = 5
    M = 100000

    def vender():
        for _ in range(M):
            with lock:
                boletos["valor"] += 1

    hilos = [threading.Thread(target=vender) for _ in range(N)]

    for h in hilos:
        h.start()

    for h in hilos:
        h.join()

    return [
        f"Total vendidos: {boletos['valor']}",
        f"Esperado: {N*M}",
        "Correcto" if boletos["valor"] == N*M else "Error"
    ]



@app.route("/", methods=["GET", "POST"])
def index():
    resultado = []
    titulo = "Selecciona un ejercicio"

    if request.method == "POST":
        op = request.form.get("ejercicio")

        if op == "panaderia":
            titulo = "Panaderia"
            resultado = ejecutar_panaderia()

        elif op == "lectores":
            titulo = "Lectores Escritores"
            resultado = ejecutar_lectores()

        elif op == "barrera":
            titulo = "Barrera"
            resultado = ejecutar_barrera()

        elif op == "gimnasio":
            titulo = "Gimnasio"
            resultado = ejecutar_gimnasio()

        elif op == "venta":
            titulo = "Venta Boletos"
            resultado = ejecutar_venta()

    return render_template("index.html", titulo=titulo, resultado=resultado)


if __name__ == "__main__":
    app.run(debug=True)