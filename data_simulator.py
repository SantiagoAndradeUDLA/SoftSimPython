import random
import time

def get_fake_data():
    voltaje = round(random.uniform(110, 125), 2)
    corriente = round(random.uniform(0.1, 2.5), 2)
    potencia = round(voltaje * corriente, 2)
    energia = round(potencia * random.uniform(0.001, 0.005), 4)
    return {
        'voltaje': voltaje,
        'corriente': corriente,
        'potencia': potencia,
        'energia': energia
    }
