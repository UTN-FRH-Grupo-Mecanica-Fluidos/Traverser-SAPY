from function.layout_functions import *
from subprocess import check_output
from math import exp
import PySimpleGUI as sg
import csv
import matplotlib.pyplot as plt


# Funciòn para determinar que los valores ingresados en la seccion "Relacion Agujeros: Tomas" sean correctos
def ref_aguj_toma_ok(values, num):
    # Tipo de sonda seleccionada
    num_tomas = num
    flag = 0  # Variable para determinar que es posible guardar la configuracion
    # Verifiacion de completitud de los datos ingresados
    data_conf = []
    if num_tomas == '2 agujeros':
        data_conf = [num_tomas, values['-NUM1-'], values['-NUM2-']]
        # Se busca posibles valores vacios
        for i in range(len(data_conf)):
            if data_conf[i] == '' and flag == 0:
                error_popup('Uno o mas agujeros no tienen los sensores de presion definidos')
                flag = 1
                break  # Corta el "for" cuando encuentra un error.
        # Se usa el elemento SET para determinar si hay tomas repetidas
        if len(set(data_conf)) != 3 and flag == 0:
            error_popup('Un sensor de presion es usado en mas de un agujero')
            flag = 1
    elif num_tomas == '3 agujeros':
        data_conf = [num_tomas, values['-NUM1-'], values['-NUM2-'], values['-NUM3-']]
        # Se busca posibles valores vacios
        for i in range(len(data_conf)):
            if data_conf[i] == '' and flag == 0:
                error_popup('Uno o mas agujeros no tienen los sensores de presion definidos')
                flag = 1
                break  # Corta el "for" cuando encuentra un error.
        # Se usa el elemento SET para determinar si hay tomas repetidas
        if len(set(data_conf)) != 4 and flag == 0:
            error_popup('Un sensor de presion es usado en mas de un agujero')
            flag = 1
    elif num_tomas == '5 agujeros':
        # Se usa el elemento SET para determinar si hay tomas repetidas
        data_conf = [num_tomas, values['-NUM1-'], values['-NUM2-'], values['-NUM3-'], values['-NUM4-'],
                     values['-NUM5-']]
        # Se busca posibles valores vacios
        for i in range(len(data_conf)):
            if data_conf[i] == '' and flag == 0:
                error_popup('Uno o mas agujeros no tienen los sensores de presion definidos')
                flag = 1
                break  # Corta el "for" cuando encuentra un error.
        if len(set(data_conf)) != 6 and flag == 0:
            error_popup('Un sensor de presion es usado en mas de un agujero')
            flag = 1
    elif num_tomas == '7 agujeros':
        data_conf = [num_tomas, values['-NUM1-'], values['-NUM2-'], values['-NUM3-'], values['-NUM4-'],
                     values['-NUM5-'], values['-NUM6-'], values['-NUM7-']]
        # Se busca posibles valores vacios
        for i in range(len(data_conf)):
            if data_conf[i] == '' and flag == 0:
                error_popup('Uno o mas agujeros no tienen los sensores de presion definidos')
                flag = 1
                break  # Corta el "for" cuando encuentra un error.
        # Se usa el elemento SET para determinar si hay tomas repetidas
        if len(set(data_conf)) != 8 and flag == 0:
            error_popup('Un sensor de presion es usado en mas de un agujero')
            flag = 1
    else:
        error_popup('El tipo de sonda es erroneo')
        flag = 1
    return flag, data_conf


# -------------------------Funciones de manejo del listado de archivos-------------------------

# La funcion toma el listado de archivos de calibracion y los organiza de menor a mayor en funcion de alfa y beta
def sort_files_travers(travers_files_in):
    # Se extrae del nombre de los archivo del traverser los valores de X e Y.
    x_buffer = []
    y_buffer = []
    list_buffer = []
    for i in range(len(travers_files_in)):
        # Se usa el caracter "_" para dividir el nombre del archivo.
        buffer = travers_files_in[i].split('_')
        # Si el archivo es similar al traverser pero tiene estructura de nombre diferente se elimina
        x_buffer.append(int(buffer[3]))
        y_buffer.append(int(buffer[5]))
        list_buffer.append(int(i))

    # Usando las funciones SORTED y ZIP se organiza de menor a mayor X e Y al mismo tiempo.
    # Se usa la variable "ist" para determinar el orden nuevo del listado de archivos de calibracion.
    # Web eplicativa: https://es.stackoverflow.com/questions/443252/c%C3%B3mo-ordenar-dos-listas-al-mismo-tiempo-en-python
    file_list = []
    for x_buffer, y_buffer, list_buffer in sorted(zip(x_buffer, y_buffer, list_buffer)):
        file_list.append(list_buffer)
    # Usando la variables "list" se organiza la lista de archivos del traverser de menor a mayor.
    calibr_files_out = []
    for i in range(len(travers_files_in)):
        calibr_files_out.append(travers_files_in[file_list[i]])
    return calibr_files_out


# -------------------------Funciones de procesamiento-------------------------
def format_csv(option):
    # La opcion "0" lee el formato de "separacion de listas" y el "simbolo decimal" del registro de windows.
    if option == 0:
        # Envia el comando al CMD y luego se aisla el valor del parametro.
        salida = check_output('Reg Query "HKEY_CURRENT_USER\Control Panel\International" /v sList',
                              shell=True)
        salida = salida.decode("utf-8").split("\n")
        seplist = salida[2].replace('    sList    REG_SZ    ', '').replace('\r', '')
        salida = check_output('Reg Query "HKEY_CURRENT_USER\Control Panel\International" /v sDecimal',
                              shell=True)
        salida = salida.decode("utf-8").split("\n")
        decsep = salida[2].replace('    sDecimal    REG_SZ    ', '').replace('\r', '')
        error_popup('Según el registro del sistema el separdor de LISTAS es "{}"'.format(seplist) +
                    ' y el simbolo DECIMAL es "{}"'.format(seplist))
    elif option == 1:
        seplist = ','
        decsep = '.'
    elif option == 2:
        seplist = ';'
        decsep = ','
    else:
        sg.popup('Algo raro paso en la eleccion del formato de salida del CSV', title='Error',
                 keep_on_top=True)
        seplist = ''
        decsep = ''
    return seplist, decsep


# Determinacion del voltaje de referencia de cada toma del instrumento.
def reference_voltage(path):
    # Diccionario por defecto de los voltajes de referencia de las tomas. Maximo SAPY 32 tomas.
    vref = {}
    for i in range(1, 33):
        vref["V{}".format(i)] = 1
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        # Extraigo todas las filas
        data_row = []  # Incializacion variable donde se guardan los datos en bruto del CSV.
        for csv_row in csv_reader:
            data_row.append(csv_row)
    data_row.pop(-1)  # Se elimina ultima fila con el caracter #
    # Determinaciòn tipo de formato
    if data_row[3][0] == '>T':
        format = 'B'
    else:
        format = 'A'
    # Calculo de las presiones de referencia para diferentes formatos de datos
    if format == 'A':
        # Calculo el valor promedio de voltaje de cada toma del archivo seleccionado.
        for i in range(int(len(data_row) / 2)):
            numbsenor = data_row[2 * i][1]  # Se utiliza la estrategia de que los valores vienen en pares
            values = data_row[i * 2][2:-1]  # Se extraen los valores de los voltajes.
            values = [float(i.replace(',', '.')) for i in values]  # Convierto valores de la lista a flotacion.
            averang = sum(values) / len(values)  # Calculo el promedio de Vout.
            averang = float('%.6f' % averang)  # Reducir el numero de cifras a 6
            vref["V{}".format(numbsenor)] = averang  # Modifico valor del diccionario para la toma especifica.
    elif 'B':
        data_row.pop(1)  # Se elimina la segunda fila con dato de la posicion Y
        data_row.pop(0)  # Se elimina la primera fila con dato de la posicion X
        # Determinacion de los numero de sensores usados
        header = []
        for i in range(3, len(data_row[0]) - 1):
            header.append(int(data_row[0][i].replace("toma_", "")))
        data_row.pop(0)  # Se elimina el encabezado
        count = 0  # Contador utilizado para determinar numero de sensor procesado
        for i in range(3, len(data_row[0]) - 1):
            # Valor de referencia del sensor analizado.
            numbsenor = header[count]
            # Se suma el contador ya que se definio el "numbsenor"
            count += 1
            values = []
            for j in range(len(data_row)):
                values.append(float(data_row[j][i].replace(',', '.')))
            averang = sum(values) / len(values)  # Calculo el promedio de Vout.
            averang = float('%.6f' % averang)  # Reducir el numero de cifras a 6
            vref["V{}".format(numbsenor)] = averang  # Modifico valor del diccionario para la toma especifica.
    return vref


def air_density(total_pressure, relative_humidity, temperature):
    # Basado en el calculo del wikipedia.
    # https://en.wikipedia.org/wiki/Density_of_air

    # Constantes utilizadas
    rair = 287.058  # Constante de los gases para el aire seco [J/(kg·K]
    rvapor = 461.495  # Constante de los gases para el aire seco [J/(kg·K]

    # Convertir temperatura de Celcius a Kelvin.
    absolute_temperature = temperature + 273.15

    # Calcular la presion de vapor de saturacion a una cierta temperatura [HPa].
    saturation_pressure = 6.1078 * exp((17.5 * temperature) / (237.3 + temperature))
    saturation_pressure = saturation_pressure * 100  # Convertir a Pascal
    # Calculo de la presion parcial de vapor en el aire. Se convierte la humedad relativa a porcentual.
    vapor_pressure = (relative_humidity/100) * saturation_pressure

    # Calculo de la presion parcial del aire seco. Es la presion total menos la presion parcial del vapor de agua.
    dry_air_pressure = total_pressure - vapor_pressure

    # Calculo de la densidad del aire (ρ)
    air_density = (dry_air_pressure / (rair * absolute_temperature)) + (vapor_pressure / (rvapor * absolute_temperature))

    return air_density

# -------------------------Guardado de archivos CSV-------------------------
def save_csv_pressure(save_pressure, path, seplist, decsep):
    # Listado de variables a guardar.
    header_list = ['Posicion X', 'Posicion Y']
    # Si existe la variable tiempo se incorpora
    if 'Tiempo medicion' in list(save_pressure[0].keys()):
        header_list.extend(['Tiempo medicion'])
    # Agregado de los sensores en la lista. Se analiza los keys del primer diccionario unicamente.
    header_list.extend([k for k in list(save_pressure[0].keys()) if 'Presion-Sensor' in k])
    header_list.sort()
    buffer = []  # Guardado de variable buffer
    # Grabado de los datos obtenidos.
    with open(path + '/presiones.csv', "w", newline='') as f:
        writer = csv.writer(f, delimiter=seplist)
        writer.writerow(["Valores de Presion de los sensores en Pascales"])  # Nota del tipo de archivo
        writer.writerow(header_list)  # Encabezado de datos
        key_list = header_list[2:]  # Listado de keys que tienen un listado de valores. En general presiones y el tiempo
        # Se toma el primer elemento de "key_list" para determinar la longitud de la listas de presiones o tiempo
        for i in range(len(save_pressure)):
            for j in range(len(save_pressure[i][key_list[1]])):
                buffer = [save_pressure[i]['Posicion X'], save_pressure[i]['Posicion Y']]
                buffer.extend([save_pressure[i][k][j] for k in key_list])
                buffer = [str(data).replace('.', decsep) for data in buffer]
                writer.writerow(buffer)
    f.close()  # Cerrado del archivo CSV

def save_csv_uncert(save_uncert, conf_level, path, seplist, decsep):
    # Encabezado
    header = [l for l in list(save_uncert[0].keys()) if 'Presion-Sensor' in l]
    header.insert(0, '')  # Se inserta el primer espacio en el encabezado
    # Listado de variables a guardar. Se analiza los keys del primer diccionario unicamente.
    sample_list = [l for l in list(save_uncert[0].keys()) if 'Muestras-' in l]  # Listado de Tomas - Muestras
    sample_list.sort()
    averange_list = [l for l in list(save_uncert[0].keys()) if 'Promedio-' in l]  # Listado de Tomas - Promedio
    averange_list.sort()
    exp_list = [l for l in list(save_uncert[0].keys()) if 'Uexpandida ' in l]  # Listado de Tomas - Uexpandida
    exp_list.sort()
    k_list = [l for l in list(save_uncert[0].keys()) if 'Coeficiente-expansion-' in l]  # Listado de Tomas - K
    k_list.sort()
    distrib_list = [l for l in list(save_uncert[0].keys()) if 'Tipo-distribucion-' in l]  # Listado de Tomas - Promedio
    distrib_list.sort()

    # Grabado de los datos obtenidos.
    with open(path + '/incertidumbre.csv', "w", newline='') as f:
        writer = csv.writer(f, delimiter=seplist)
        for i in range(len(save_uncert)):
            buffer = []  # Reinicio de la variable. Guarda temporalmente los datos antes de pasarlo al CSV.
            x_posit = str(save_uncert[i]['Posicion X']).replace('.', decsep)
            writer.writerow(['Posicion X', x_posit])  # Guardado del punto X
            y_posit = str(save_uncert[i]['Posicion Y']).replace('.', decsep)
            writer.writerow(['Posicion Y', y_posit])  # Guardado del punto Y
            writer.writerow(header)  # Guardado del encabezado
            # ---Guardado de Muestras---
            buffer = [save_uncert[i][l] for l in sample_list]
            # Convierto los decimales al formato elegido.
            buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
            buffer.insert(0, 'Numero de muestras')
            writer.writerow(buffer)
            # ---Guardado de Promedios---
            buffer = [save_uncert[i][l] for l in averange_list]
            # Convierto los decimales al formato elegido.
            buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
            buffer.insert(0, 'Promedio')
            writer.writerow(buffer)
            # ---Guardado de Uexpandida---
            buffer = [save_uncert[i][l] for l in exp_list]
            # Convierto los decimales al formato elegido.
            buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
            buffer.insert(0, 'Uexpandida ({}%)'.format(conf_level * 100))
            writer.writerow(buffer)
            # ---Guardado del Coeficiente de expansion---
            buffer = [save_uncert[i][l] for l in k_list]
            # Convierto los decimales al formato elegido.
            buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
            buffer.insert(0, 'Coeficiente de expansion')
            writer.writerow(buffer)
            # ---Guardado del Tipo de distribucion---
            buffer = [save_uncert[i][l] for l in distrib_list]
            # Convierto los decimales al formato elegido.
            buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
            buffer.insert(0, 'Tipo de distribucion')
            writer.writerow(buffer)
            writer.writerow(['##########' for i in range(len(header))])  # Division entre puntos del traverser
        # Escritura de nota de archivos de incertidumbre.
        writer.writerow([])
        writer.writerow(
            ['Importante: El analisis de incertidumbre realizado solo incluye incertidumbre por repetividad (Tipo A)'])
        writer.writerow(
            ['y la incertidumbre debido a la calibracion del instrumento (Tipo B), se debe realizar un analisis'])
        writer.writerow(['de otras fuentes de incertidumbre.'])
    f.close()  # Cerrado del archivo CSV


def save_csv_trav(data_calib, path, seplist, decsep, values):
    # Grabado de los datos obtenidos.
    with open(path + '/traverser.csv', "w", newline='') as f:
        writer = csv.writer(f, delimiter=seplist)
        # Nota del tipo de archivo
        writer.writerow(["Datos utilizados en el procesamiento del traverser"])
        # Informacion del tipo de sonda
        writer.writerow(['Tipo de sonda: ', values['-TYPEPROBE-']])
        # Informacion si se utiliza el analisis sectorizado
        if values['-TYPEPROBE-'] == '2 agujeros' or values['-TYPEPROBE-'] == '3 agujeros':
            # Sonda de 2 y 3 agujeros no tiene analisis sectorizado.
            writer.writerow(['Analisis Sectorizado: ', 'No Aplica'])
        else:
            if values['-MULTIZONE-'] == 'Utilizado':
                writer.writerow(['Analisis Sectorizado: ', 'Utilizado'])
            else:
                writer.writerow(['Analisis Sectorizado: ', 'No utilizado'])
        # Guardado del valor de densidad utilizado
        writer.writerow(['Densidad [Kg/m3]: ', values["-DENSITY_VALUE-"]])

        # Guardado de los datos de los coeficientes
        if values['-TYPEPROBE-'] == '2 agujeros':
            None
        elif values['-TYPEPROBE-'] == '3 agujeros':
            None
        elif values['-TYPEPROBE-'] == '5 agujeros':
            # Encabezado de los datos
            header_list = ['Posicion X', 'Posicion Y', "Agujero 1 [Pa]", "Agujero 2 [Pa]", "Agujero 3 [Pa]",
                           "Agujero 4 [Pa]", "Agujero 5 [Pa]", "Cp Alfa []", "Cp Beta []", "Zona Maxima", 'Alfa [º]',
                           'Beta [º]', 'Presion estatica [Pa]', "Presion total [Pa]",'Velocidad [m/seg]',
                           'Velocidad X [m/seg]', 'Velocidad Y [m/seg]', 'Velocidad Z [m/seg]']
            writer.writerow(header_list)
            for i in range(len(data_calib)):
                # Listado de Keys a guardar.
                key_list = ['Posicion X','Posicion Y', "hole 1", "hole 2", "hole 3", "hole 4", "hole 5", "Cpalfa",
                            'Cpbeta','Zonamax', 'Alfa', 'Beta', 'Presion estatica', "Presion total",'Velocidad',
                            "Vx", "Vy", "Vz"]
                buffer = [data_calib[i][j] for j in key_list]  # Armo lista de valores con "key_list"
                buffer = [str(data).replace('.', decsep) for data in buffer]  # Conversion a formato de salida CSV
                writer.writerow(buffer)
        elif values['-TYPEPROBE-'] == '7 agujeros':
            None
    f.close()  # Cerrado del archivo CSV

# ELIMINAR FUNCION
# def save_csv_flow(data_flow, path, seplist, decsep, values):
#     # Encabezado
#     header = ['', 'Promedio']
#     with open(path + '/traverser-velocidades.csv', "w", newline='') as f:
#         writer = csv.writer(f, delimiter=seplist)
#         # Informacion del tipo de sonda
#         writer.writerow(['Tipo de sonda: ', values['-TYPEPROBE-']])
#         # Informacion si se utiliza el analisis sectorizado
#         if values['-TYPEPROBE-'] == '2 agujeros' or values['-TYPEPROBE-'] == '3 agujeros':
#             # Sonda de 2 y 3 agujeros no tiene analisis sectorizado.
#             writer.writerow(['Analisis Sectorizado: ', 'No Aplica'])
#         else:
#             if values['-MULTIZONE-'] == 'Utilizado':
#                 writer.writerow(['Analisis Sectorizado: ', 'Utilizado'])
#                 writer.writerow(['##########', '##########'])  # Division entre puntos del traverser
#             else:
#                 writer.writerow(['Analisis Sectorizado: ', 'No utilizado'])
#                 writer.writerow(['##########', '##########'])  # Division entre puntos del traverser
#         for i in range(len(data_flow)):
#             buffer = []  # Reinicio de la variable. Guarda temporalmente los datos antes de pasarlo al CSV.
#             if values['-TYPEPROBE-'] == '2 agujeros':
#                 None
#             if values['-TYPEPROBE-'] == '3 agujeros':
#                 None
#             if values['-TYPEPROBE-'] == '5 agujeros' or values['-TYPEPROBE-'] == '7 agujeros':
#                 x_posit = str(data_flow[i]['Posicion X']).replace('.', decsep)
#                 writer.writerow(['Posicion X', x_posit])  # Guardado del punto X
#                 y_posit = str(data_flow[i]['Posicion Y']).replace('.', decsep)
#                 writer.writerow(['Posicion Y', y_posit])  # Guardado del punto Y
#                 writer.writerow(header)  # Guardado del encabezado
#                 # ---Guardado de Alfa---
#                 buffer = ['Alfa', str(data_flow[i]['Alfa'])]
#                 # Convierto los decimales al formato elegido.
#                 buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
#                 writer.writerow(buffer)
#                 # ---Guardado de Beta---
#                 buffer = ['Beta', data_flow[i]['Beta']]
#                 # Convierto los decimales al formato elegido.
#                 buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
#                 writer.writerow(buffer)
#                 # ---Guardado de Presion estatica---
#                 buffer = ['Presion estatica', data_flow[i]['Presion estatica']]
#                 # Convierto los decimales al formato elegido.
#                 buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
#                 writer.writerow(buffer)
#                 # ---Guardado de Presion total---
#                 buffer = ['Presion total', data_flow[i]['Presion total']]
#                 # Convierto los decimales al formato elegido.
#                 buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
#                 writer.writerow(buffer)
#                 # ---Guardado de Velocidad---
#                 buffer = ['Velocidad', data_flow[i]['Velocidad']]
#                 # Convierto los decimales al formato elegido.
#                 buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
#                 writer.writerow(buffer)
#                 # ---Guardado de Velocidad en X---
#                 buffer = ['Velocidad X', data_flow[i]['Vx']]
#                 # Convierto los decimales al formato elegido.
#                 buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
#                 writer.writerow(buffer)
#                 # ---Guardado de Velocidad en Y---
#                 buffer = ['Velocidad Y', data_flow[i]['Vy']]
#                 # Convierto los decimales al formato elegido.
#                 buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
#                 writer.writerow(buffer)
#                 # ---Guardado de Velocidad en X---
#                 buffer = ['Velocidad Z', data_flow[i]['Vz']]
#                 # Convierto los decimales al formato elegido.
#                 buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
#                 writer.writerow(buffer)
#                 writer.writerow(['##########', '##########'])  # Division entre puntos del traverser
#     f.close()  # Cerrado del archivo CSV


# -------------------------Funciones de Graficacion y Guardado de Graficos-------------------------
def plot_2d(x, y, conf, save):
    # Armado de grafico
    plt.figure()
    plt.xlabel(conf['xlabel'])
    plt.ylabel(conf['ylabel'])
    plt.title(conf['title'], fontdict={'size': 14}, pad=20)
    plt.grid(visible=None, which='major', axis='both')
    plt.plot(x, y, linestyle='-', marker='o')
    if save:
        plt.savefig(conf['save_name'])
    else:
        plt.show()


def plot_3d(x, y, z, conf, save):
    # Armado de grafico
    fig3 = plt.figure()
    ax = fig3.add_subplot(111, projection='3d')
    surf = ax.plot_trisurf(x, y, z, cmap='gist_rainbow', linewidth=1, antialiased=False, rasterized=True)
    plt.colorbar(surf, shrink=1, aspect=10)
    plt.title(conf['title'], fontdict={'fontsize': 20}, loc='center', pad=None)
    plt.xlabel(conf['xlabel'])
    plt.ylabel(conf['ylabel'])
    if save:
        plt.savefig(conf['save_name'])
    else:
        plt.show()
