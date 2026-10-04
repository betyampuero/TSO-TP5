"""
UNJu - Facultad de Ingeniería
Teoría de Sistemas Operativos (TSO) - Ciclo Lectivo 2026
Cátedra: Ing. María Fernanda Vázquez - JTP: Ing. Fabio D. Argañaraz

Ejercicio Práctico N° 2: El Problema del Oso y las Abejas
Bibliografía de Referencia:
- Silberschatz: Cap. 6.6 (Problemas clásicos de sincronización)
- Stallings: Cap. 5.4 (Sincronización con semáforos)
"""

import sys
import threading
import time
import random

# Configuración UTF-8 para consola Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

M = 10                  # Capacidad del tarro de miel
NUM_ABEJAS = 5          # Número de abejas obreras
tarro_miel = 0          # Variable compartida
simulacion_activa = True

# Mecanismos de sincronización
mutex = threading.Lock()
sem_oso = threading.Semaphore(0)
sem_tarro_disponible = threading.Semaphore(1)

def abeja(id_abeja):
    global tarro_miel, simulacion_activa
    while simulacion_activa:
        time.sleep(random.uniform(0.05, 0.2))
        
        # 1. Esperar a que el tarro esté disponible para juntar miel
        sem_tarro_disponible.acquire()
        
        # 2. Entrar en exclusión mutua para modificar la variable compartida
        mutex.acquire()
        
        if not simulacion_activa:
            mutex.release()
            sem_tarro_disponible.release()
            break
            
        tarro_miel += 1
        print(f"🐝 Abeja {id_abeja} aportó miel. Tarro: {tarro_miel}/{M}")
        
        if tarro_miel == M:
            print(f"🐝 Abeja {id_abeja} llenó el tarro! Llama al oso... 🐻")
            mutex.release()
            # Despertar al oso (NO liberamos sem_tarro_disponible hasta que el oso coma)
            sem_oso.release()
        else:
            mutex.release()
            # Si el tarro no está lleno, permitimos que otra abeja continúe
            sem_tarro_disponible.release()

def oso(max_tarros=2):
    global tarro_miel, simulacion_activa
    tarros_comidos = 0
    while tarros_comidos < max_tarros:
        # 1. Esperar pasivamente a que las abejas llenen el tarro
        sem_oso.acquire()
        
        # 2. Comer la miel
        print("🐻 El oso se despierta y se come toda la miel!")
        tarro_miel = 0
        tarros_comidos += 1
        print(f"🐻 El oso comió {tarros_comidos}/{max_tarros} tarro(s) y vuelve a dormir.")
        
        time.sleep(0.1)
        
        # 3. Avisar a las abejas que el tarro está vacío y disponible
        sem_tarro_disponible.release()
        
    simulacion_activa = False
    # Liberar semáforos por si hay abejas esperando al finalizar
    sem_tarro_disponible.release()

if __name__ == "__main__":
    print("=" * 60)
    print(" Iniciando Simulación: El Oso y las Abejas (UNJu FI)")
    print("=" * 60)
    
    hilos_abejas = []
    for i in range(NUM_ABEJAS):
        t = threading.Thread(target=abeja, args=(i + 1,))
        hilos_abejas.append(t)
        t.start()
        
    hilo_oso = threading.Thread(target=oso, args=(2,))
    hilo_oso.start()
    
    hilo_oso.join()
    for t in hilos_abejas:
        t.join()
        
    print("=" * 60)
    print(" Simulación finalizada exitosamente.")
    print("=" * 60)
