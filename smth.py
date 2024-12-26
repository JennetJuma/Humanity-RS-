import matplotlib.pyplot as plt
import csv

# Константы
p0 = 101325  # стандартное атмосферное давление на уровне моря, Па
T0 = 288.16  # стандартная температура на уровне моря, К
m_air = 0.029  # молярная масса сухого воздуха, кг/моль
R = 8.31  # универсальная газовая постоянная, Дж/(моль*К)
g0 = 9.81  # ускорение свободного падения, м/с^2

# Параметры ракеты
mass_total = 142070  # Полная масса ракеты, кг
m1 = 4000  # Топливо 1 ступени, кг
m2 = 8000  # Топливо 2 ступени, кг
m3 = 79600  # Топливо 3 ступени, кг
mass_1_stage = 17500 + m1  # Масса 1 ступени с топливом, кг
mass_2_stage = 25200 + m2  # Масса 2 ступени с топливом, кг
mass_3_stage = 62600 + m3  # Масса 3 ступени с топливом, кг
M0 = mass_total - mass_1_stage - mass_2_stage - mass_3_stage

t_fuel_3 = 105  # Время работы 3 ступени, сек
t_fuel_2 = 150  # Время работы 2 ступени, сек
t_fuel_1 = 165  # Время работы 1 ступени, сек

I3 = 320  # Удельный импульс 3 ступени
I2 = 300  # Удельный импульс 2 ступени
I1 = 355  # Удельный импульс 1 ступени

# Расход топлива ступеней
net_flow_rate_stage3 = m3 / t_fuel_3  # Расход топлива 3 ступени, кг/сек
net_flow_rate_stage2 = m2 / t_fuel_2  # Расход топлива 2 ступени, кг/сек
net_flow_rate_stage1 = m1 / t_fuel_1  # Расход топлива 1 ступени, кг/сек

# Импорт данных из файла MechJeb2
data_file = 'data.csv'
time_arr = []
altitude_arr = []
velocity_arr = []
mass_arr = []

def import_data(filename):
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            time_arr.append(float(row['time']))
            altitude_arr.append(float(row['altitude']))
            velocity_arr.append(float(row['velocity']))
            mass_arr.append(float(row['mass']))

import_data(data_file)

# Расчёт массы ракеты по ступеням

def calculate_mass():
    global mass_total, mass_3_stage, mass_2_stage, mass_1_stage  # Используем глобальные переменные
    
    mass_total_arr = [0] * len(time_arr)
    mass_3_stage_arr = [0] * len(time_arr)
    mass_2_stage_arr = [0] * len(time_arr)
    mass_1_stage_arr = [0] * len(time_arr)

    mass_total_arr[0] = mass_total
    mass_3_stage_arr[0] = mass_3_stage
    mass_2_stage_arr[0] = mass_2_stage
    mass_1_stage_arr[0] = mass_1_stage

    for i in range(1, len(time_arr)):
        dt = time_arr[i] - time_arr[i - 1]

        if time_arr[i] < t_fuel_3:
            mass_total -= net_flow_rate_stage3 * dt
            mass_3_stage -= net_flow_rate_stage3 * dt
        elif t_fuel_3 <= time_arr[i] < t_fuel_3 + t_fuel_2:
            mass_total -= net_flow_rate_stage2 * dt
            mass_2_stage -= net_flow_rate_stage2 * dt
        elif t_fuel_3 + t_fuel_2 <= time_arr[i] < t_fuel_3 + t_fuel_2 + t_fuel_1:
            mass_total -= net_flow_rate_stage1 * dt
            mass_1_stage -= net_flow_rate_stage1 * dt

        mass_total_arr[i] = mass_total
        mass_3_stage_arr[i] = mass_3_stage
        mass_2_stage_arr[i] = mass_2_stage
        mass_1_stage_arr[i] = mass_1_stage

    return mass_total_arr, mass_3_stage_arr, mass_2_stage_arr, mass_1_stage_arr


mass_total_arr, mass_3_stage_arr, mass_2_stage_arr, mass_1_stage_arr = calculate_mass()

def calculate_velocity():
    velocity_simulated = [velocity_arr[0]]
    altitude_simulated = [altitude_arr[0]]
    for i in range(1, len(time_arr)):
        dt = time_arr[i] - time_arr[i - 1]
        mass = mass_total_arr[i]

        # Тяга двигателя
        if i < t_fuel_3:
            thrust = I3 * g0 * net_flow_rate_stage3
        elif t_fuel_3 <= i < t_fuel_3 + t_fuel_2:
            thrust = I2 * g0 * net_flow_rate_stage2
        elif t_fuel_3 + t_fuel_2 <= i < t_fuel_3 + t_fuel_2 + t_fuel_1:
            thrust = I1 * g0 * net_flow_rate_stage1
        else:
            thrust = 0  # После сгорания топлива тяга отсутствует

        # Изменение скорости: F = ma -> a = F/m
        acceleration = thrust / mass - g0

        # Обновляем скорость
        new_velocity = max(velocity_simulated[-1] + acceleration * dt, 0)
        velocity_simulated.append(new_velocity)

        # Расчет высоты
        new_altitude = altitude_simulated[-1] + new_velocity * dt
        altitude_simulated.append(new_altitude)

    return velocity_simulated, altitude_simulated

velocity_simulated, altitude_simulated = calculate_velocity()


# Построение графиков
plt.figure(figsize=(12, 24))

# График скорости
plt.subplot(5, 1, 1)
plt.plot(time_arr, velocity_arr, label='MechJeb Data', linestyle='--', color='blue')
plt.plot(time_arr, velocity_simulated, label='Simulated Data', linestyle='-', color='orange')
plt.title('Изменение скорости')
plt.xlabel('Время (с)')
plt.ylabel('Скорость (м/с)')
plt.legend()
plt.grid()

# График высоты
plt.subplot(5, 1, 2)
plt.plot(time_arr, altitude_arr, label='MechJeb Data', linestyle='--', color='green')
plt.plot(time_arr, altitude_simulated, label='Simulated Data', linestyle='-', color='orange')
plt.title('Изменение высоты')
plt.xlabel('Время (с)')
plt.ylabel('Высота (м)')
plt.legend()
plt.grid()

# График сравнения общей массы
plt.subplot(5, 1, 3)
plt.plot(time_arr, mass_arr, label='MechJeb Mass Data', linestyle='--', color='purple')
plt.plot(time_arr, mass_total_arr, label='Simulated Mass', linestyle='-', color='orange')
plt.title('Сравнение общей массы')
plt.xlabel('Время (с)')
plt.ylabel('Масса (кг)')
plt.legend()
plt.grid()


# График траектории
plt.subplot(5, 1, 4)
plt.plot(altitude_arr, velocity_simulated, label='Simulated Trajectory', linestyle='-', color='red')
plt.plot(altitude_arr, velocity_arr, label='MechJeb Trajectory', linestyle='--', color='blue')
plt.title('Траектория полета')
plt.xlabel('Высота (м)')
plt.ylabel('Скорость (м/с)')
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()
