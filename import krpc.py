import krpc
import csv
import time

# Подключение к серверу kRPC
print("Проверка соединения с kRPC...")
conn = krpc.connect(name='Data Logger')
print("Соединение установлено.")
vessel = conn.space_center.active_vessel

# Настройка частоты записи данных
log_interval = 1.0  # Интервал записи в секундах

# Выбор системы отсчета
reference_frame = vessel.orbit.body.reference_frame  # Для орбитальной скорости

# Открытие файла для записи данных
with open('C:/kspproject/data.csv', mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['time', 'altitude', 'velocity', 'mass'])
    writer.writeheader()
    file.flush()
    
    # Получение начального времени
    start_time = conn.space_center.ut
    
    print("Ожидание включения двигателей...")
    
    # Ждем, пока двигатели не будут активированы
    while all(engine.thrust == 0 for engine in vessel.parts.engines):
        time.sleep(0.1)
    
    print("Двигатели активированы. Начинается запись данных.")
    
    try:
        while True:
            # Получение текущего времени, высоты, скорости и массы ракеты
            ut = conn.space_center.ut - start_time
            altitude = vessel.flight().mean_altitude
            velocity = vessel.velocity(reference_frame)  # Возвращает вектор скорости
            speed = (velocity[0]**2 + velocity[1]**2 + velocity[2]**2) ** 0.5  # Модуль скорости
            mass = vessel.mass
            
            # Запись данных в файл
            writer.writerow({
                'time': ut,
                'altitude': altitude,
                'velocity': speed,
                'mass': mass
            })
            print(f"Время: {ut:.2f}, Высота: {altitude:.2f}, Скорость: {speed:.2f}, Масса: {mass:.2f}")
            
            # Ожидание следующего цикла записи
            time.sleep(log_interval)
    
    except KeyboardInterrupt:
        print("Запись данных завершена.")
