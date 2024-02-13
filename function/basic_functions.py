from function.layout_functions import *
from subprocess import check_output
from math import exp
import vtkmodules.all as vtk
import datetime
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
    key_list = ['Posicion X', 'Posicion Y']
    # Si existe la variable tiempo se incorpora
    if 'Tiempo medicion' in list(save_pressure[0].keys()):
        key_list.extend(['Tiempo medicion'])
    # Agregado de los sensores en la lista. Se analiza los keys del primer diccionario unicamente.
    key_list.extend([k for k in list(save_pressure[0].keys()) if 'Presion-Sensor' in k])
    key_list.sort()
    # Grabado de los datos obtenidos.
    date_file_name = datetime.datetime.now().strftime("%H-%M-%S_%d-%m-%Y")  # Hora y dia de guardado. Utilizado para guardado de los archivos CSV
    save_file_name = path + '/presiones_{}.csv'.format(date_file_name)
    with open(save_file_name, "w", newline='') as f:
        writer = csv.writer(f, delimiter=seplist)
        # Guardado de encabezado y mejoramiento de nombres.
        header = key_list
        header = [s.replace('Posicion X', 'Posicion X[mm]') for s in header]
        header = [s.replace('Posicion Y', 'Posicion Y[mm]') for s in header]
        header = [s.replace('Presion-Sensor', 'Presion Sensor[Pa] - ') for s in header]
        writer.writerow(header)  # Encabezado de datos
        key_list = key_list[2:]  # Listado de keys que tienen un listado de valores. En general presiones
        # Se toma el primer elemento de "key_list" para determinar la longitud de la listas de presiones o tiempo
        for i in range(len(save_pressure)):
            for j in range(len(save_pressure[i][key_list[1]])):
                buffer = [save_pressure[i]['Posicion X'], save_pressure[i]['Posicion Y']]
                buffer.extend([save_pressure[i][k][j] for k in key_list])
                buffer = [str(data).replace('.', decsep) for data in buffer]
                writer.writerow(buffer)
    f.close()  # Cerrado del archivo CSV

def save_csv_uncert(save_uncert, conf_level, path, seplist, decsep):
    # Armado del listado de keys de diccionario. Se toma el primer punto analizado como referencia
    # Angulo
    key_list = ["Posicion X", "Posicion Y"]
    # Numero de muestras
    key_list.extend([l for l in list(save_uncert[1].keys()) if 'Muestras-' in l])
    # Promedio de presiones de cada sensor
    key_list.extend([l for l in list(save_uncert[1].keys()) if 'Promedio-' in l])
    # Incertidumbre Tipo A
    key_list.extend([l for l in list(save_uncert[1].keys()) if 'Tipo A-' in l])
    # Incertidumbre Tipo B del instrumento. 1.5 %
    key_list.extend([l for l in list(save_uncert[1].keys()) if 'Tipo B-presion-' in l])
    # Incertidumbre Combinada
    key_list.extend([l for l in list(save_uncert[1].keys()) if 'Incertidumbre Combinada-' in l])
    # Coeficiente de expansion
    key_list.extend([l for l in list(save_uncert[1].keys()) if 'Coeficiente-expansion-' in l])
    # Tipo de distribución
    key_list.extend([l for l in list(save_uncert[1].keys()) if 'Tipo-distribucion-' in l])
    # Incertidumbre Expandida
    key_list.extend([l for l in list(save_uncert[1].keys()) if 'Uexpandida' in l])

    # Grabado de los datos obtenidos y apertura del archivo a guardar los datos de incertidumbre.
    date_file_name = datetime.datetime.now().strftime("%H-%M-%S_%d-%m-%Y")  # Hora y dia de guardado. Utilizado para guardado de los archivos CSV
    save_file_name = path + '/incertidumbre_{}.csv'.format(date_file_name)
    with open(save_file_name, "w", newline='') as f:
        writer = csv.writer(f, delimiter=seplist)
        # Guardado del encabezado y mejoramiento de los nombres
        header = key_list
        header = [s.replace('Posicion X', 'Posicion X[mm]') for s in header]
        header = [s.replace('Posicion Y', 'Posicion Y[mm]') for s in header]
        header = [s.replace('Muestras-', 'Nº Muestras[] ') for s in header]
        header = [s.replace('Promedio-', 'Promedio[Pa] ') for s in header]
        header = [s.replace('Tipo A-', 'Tipo A - ') for s in header]
        header = [s.replace('Tipo B-presion-', 'Tipo B(presion) - ') for s in header]
        header = [s.replace('Incertidumbre Combinada-', 'Incertidumbre Combinada ') for s in header]
        header = [s.replace('Coeficiente-expansion-', 'Coeficiente expansion ') for s in header]
        header = [s.replace('Tipo-distribucion-', 'Tipo distribucion ') for s in header]
        header = [s.replace('Uexpandida ({}%)-'.format(conf_level * 100), 'Uexpandida ({}%) - '.format(conf_level * 100)) for s in header]
        writer.writerow(header)
        for i in range(len(save_uncert)):
            buffer = [save_uncert[i][l] for l in key_list]
            # Convierto los decimales al formato elegido.
            buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
            writer.writerow(buffer)
        # Escritura de nota de archivos de incertidumbre.
        writer.writerow([])
        writer.writerow(
            ['Importante: El analisis de incertidumbre realizado solo incluye incertidumbre por repetividad (Tipo A)'])
        writer.writerow(
            ['y la incertidumbre debido a la calibracion del instrumento (Tipo B), se debe realizar un analisis'])
        writer.writerow(['de otras fuentes de incertidumbre.'])
    f.close()  # Cerrado del archivo CSV


def save_csv_trav(data_calib, path, seplist, decsep, values):
    date_file_name = datetime.datetime.now().strftime("%H-%M-%S_%d-%m-%Y")  # Hora y dia de guardado. Utilizado para guardado de los archivos CSV
    save_file_name = path +'/traverser_{}.csv'.format(date_file_name)
    # Grabado de los datos obtenidos.
    with open(save_file_name, "w", newline='') as f:
        writer = csv.writer(f, delimiter=seplist)
        # Encabezado de las filas.
        # Informacion del tipo de sonda
        writer.writerow(['Tipo de sonda: ', values['-TYPEPROBE-']])

        # Se preparan las lista de keys del diccionario y los encabezados para el archivo de salida.
        # Guardado de los datos de los coeficientes
        if values['-TYPEPROBE-'] == '2 agujeros':
            #  Informacion si se utiliza el analisis sectorizado
            writer.writerow(['Analisis Sectorizado: ', 'No Aplica'])
            # Guardado del valor de densidad utilizado
            writer.writerow(['Densidad [Kg/m3]: ', values["-DENSITY_VALUE-"]])
            key_list = ["Posicion X", "Posicion Y", 'hole 1', 'hole 2', "Cpangulo", "Angulo"]
            header = ['Posicion X[mm]', 'Posicion Y[mm]', "Agujero 1 [Pa]", "Agujero 2 [Pa]", "Cp Angulo []", 'Angulo [º]']

        elif values['-TYPEPROBE-'] == '3 agujeros':
            # Informacion si se utiliza el analisis sectorizado
            writer.writerow(['Analisis Sectorizado: ', 'No Aplica'])
            # Guardado del valor de densidad utilizado
            writer.writerow(['Densidad [Kg/m3]: ', values["-DENSITY_VALUE-"]])
            key_list = ["Posicion X", "Posicion Y", 'hole 1', 'hole 2', 'hole 3', "Cpangulo", "Cpestatico", "Cptotal",
                        "Angulo", 'Presion estatica', 'Presion total','Velocidad',"Vx", "Vy"]
            header = ['Posicion X[mm]', 'Posicion Y[mm]', "Agujero 1 [Pa]", "Agujero 2 [Pa]", "Agujero 3 [Pa]",
                      "Cp Angulo []", "Cp Estatico []", "Cp Total []", 'Angulo [º]', 'Presion estatica [Pa]',
                      "Presion total [Pa]", 'Velocidad [m/seg]', 'Velocidad X [m/seg]', 'Velocidad Y [m/seg]']

        elif values['-TYPEPROBE-'] == '5 agujeros':
            #  Informacion si se utiliza el analisis sectorizado
            if values['-MULTIZONE-'] == 'Utilizado':
                writer.writerow(['Analisis Sectorizado: ', 'Utilizado'])
            else:
                writer.writerow(['Analisis Sectorizado: ', 'No utilizado'])
            # Guardado del valor de densidad utilizado
            writer.writerow(['Densidad [Kg/m3]: ', values["-DENSITY_VALUE-"]])
            # Encabezado de los datos
            key_list = ["Posicion X", "Posicion Y", 'hole 1', 'hole 2', 'hole 3', "hole 4", "hole 5", "Cpalfa",
                        'Cpbeta', "Cpestatico", "Cptotal", 'Zonamax', 'Alfa', 'Beta', 'Presion estatica',
                        "Presion total", 'Velocidad', "Vx", "Vy", "Vz"]
            header = ['Posicion X[mm]', 'Posicion Y[mm]', "Agujero 1 [Pa]", "Agujero 2 [Pa]", "Agujero 3 [Pa]",
                      "Agujero 4 [Pa]", "Agujero 5 [Pa]", "Cp Alfa []", "Cp Beta []", "Cp Estatico []", "Cp Total []",
                       "Zona Maxima",'Alfa [º]', 'Beta [º]', 'Presion estatica [Pa]', "Presion total [Pa]",
                      'Velocidad [m/seg]', 'Velocidad X [m/seg]', 'Velocidad Y [m/seg]', 'Velocidad Z [m/seg]']

        elif values['-TYPEPROBE-'] == '7 agujeros':
            # Informacion si se utiliza el analisis sectorizado
            if values['-MULTIZONE-'] == 'Utilizado':
                writer.writerow(['Analisis Sectorizado: ', 'Utilizado'])
            elif not values['-HIGH ANGLE-']:
                writer.writerow(['Analisis Sectorizado: ', 'No utilizado'])
            # Guardado del valor de densidad utilizado
            writer.writerow(['Densidad [Kg/m3]: ', values["-DENSITY_VALUE-"]])


        # Guardado de encabezado y datos
        writer.writerow(header)
        for i in range(len(data_calib)):
            buffer = [data_calib[i][l] for l in key_list]
            # Convierto los decimales al formato elegido.
            buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
            writer.writerow(buffer)
        f.close()  # Cerrado del archivo CSV


# -------------------------Funciones de Graficacion y Guardado de Graficos-------------------------
def plot_2d(x, y, conf, save, path):
    # Armado de grafico
    plt.figure()
    plt.xlabel(conf['xlabel'])
    plt.ylabel(conf['ylabel'])
    plt.title(conf['title'], fontdict={'size': 14}, pad=20)
    plt.grid(visible=None, which='major', axis='both')
    plt.plot(x, y, linestyle='-', marker='o')
    if save:
        # Hora y dia de guardado. Utilizado para guardado del grafico
        date_file_name = datetime.datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
        save_file_name = path + conf["save_name"].replace("_.jpg", "_{}.jpg".format(date_file_name))
        plt.savefig(save_file_name)
    else:
        plt.show()


def plot_3d(x, y, z, conf, save, path):
    # Armado de grafico
    fig3 = plt.figure()
    ax = fig3.add_subplot(111, projection='3d')
    surf = ax.plot_trisurf(x, y, z, cmap='gist_rainbow', linewidth=1, antialiased=False, rasterized=True)
    plt.colorbar(surf, shrink=1, aspect=10)
    plt.title(conf['title'], fontdict={'fontsize': 20}, loc='center', pad=None)
    plt.xlabel(conf['xlabel'])
    plt.ylabel(conf['ylabel'])
    if save:
        # Hora y dia de guardado. Utilizado para guardado del grafico
        date_file_name = datetime.datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
        save_file_name = path + conf["save_name"].replace("_.jpg", "_{}.jpg".format(date_file_name))
        # Grabado del grafico
        plt.savefig(save_file_name)
    else:
        plt.show()


def plot_vtk(data, file_name):
    # Crear estructura VTK PolyData.
    points = vtk.vtkPoints()
    vertices = vtk.vtkCellArray()
    scalars_posx = vtk.vtkFloatArray()
    scalars_posx.SetName("Posicion X")  # Definir el nombre del escalar
    scalars_posy = vtk.vtkFloatArray()
    scalars_posy.SetName("Posicion Y")  # Definir el nombre del escalar
    scalars_alfa = vtk.vtkFloatArray()
    scalars_alfa.SetName("Alfa")  # Definir el nombre del escalar
    scalars_beta = vtk.vtkFloatArray()
    scalars_beta.SetName("Beta")  # Definir el nombre del escalar
    scalars_cpalfa = vtk.vtkFloatArray()
    scalars_cpalfa.SetName("Cpalfa")  # Definir el nombre del escalar
    scalars_cpbeta = vtk.vtkFloatArray()
    scalars_cpbeta.SetName("Cpbeta")  # Definir el nombre del escalar
    scalars_cpestatica = vtk.vtkFloatArray()
    scalars_cpestatica.SetName("Cpestatica")  # Definir el nombre del escalar
    scalars_cptotal = vtk.vtkFloatArray()
    scalars_cptotal.SetName("Cptotal")  # Definir el nombre del escalar
    scalars_hole1 = vtk.vtkFloatArray()
    scalars_hole1.SetName("Agujero 1")  # Definir el nombre del escalar
    scalars_hole2 = vtk.vtkFloatArray()
    scalars_hole2.SetName("Agujero 2")  # Definir el nombre del escalar
    scalars_hole3 = vtk.vtkFloatArray()
    scalars_hole3.SetName("Agujero 3")  # Definir el nombre del escalar
    scalars_hole4 = vtk.vtkFloatArray()
    scalars_hole4.SetName("Agujero 4")  # Definir el nombre del escalar
    scalars_hole5 = vtk.vtkFloatArray()
    scalars_hole5.SetName("Agujero 5")  # Definir el nombre del escalar
    scalars_presion_est = vtk.vtkFloatArray()
    scalars_presion_est.SetName("Presion Estatica")  # Definir el nombre del escalar
    scalars_presion_tot = vtk.vtkFloatArray()
    scalars_presion_tot.SetName("Presion Total")  # Definir el nombre del escalar
    scalars_vel = vtk.vtkFloatArray()
    scalars_vel.SetName("Velocidad")  # Definir el nombre del escalar
    scalars_velx = vtk.vtkFloatArray()
    scalars_velx.SetName("Velocidad X")  # Definir el nombre del escalar
    scalars_vely = vtk.vtkFloatArray()
    scalars_vely.SetName("Velocidad Y")  # Definir el nombre del escalar
    scalars_velz = vtk.vtkFloatArray()
    scalars_velz.SetName("Velocidad Z")  # Definir el nombre del escalar
    # En caso de sonda 7 agujeros
    if data['Tipo de sonda'] == '7 agujeros':
        scalars_hole6 = vtk.vtkFloatArray()
        scalars_hole6.SetName("Agujero 6")  # Definir el nombre del escalar
        scalars_hole7 = vtk.vtkFloatArray()
        scalars_hole7.SetName("Agujero 7")  # Definir el nombre del escalar

    for i in range(len(data['Posicion Y[mm]'])):
        # Los puntos del plano depende del tipo de grafico seleccionado
        x = float(data['Posicion X[mm]'][i].replace(",", "."))
        y = float(data['Posicion Y[mm]'][i].replace(",", "."))
        z = 0.0  # Se define en forma predefinida como "0"
        # Descarga de datos para incorporarlos al VTK
        posx = float(data['Posicion X[mm]'][i].replace(",", "."))
        posy = float(data['Posicion Y[mm]'][i].replace(",", "."))
        alfa = float(data['Alfa [º]'][i].replace(",", "."))
        beta = float(data['Beta [º]'][i].replace(",", "."))
        cpalfa = float(data['Cp Alfa []'][i].replace(",", "."))
        cpbeta = float(data['Cp Beta []'][i].replace(",", "."))
        cpestatica = float(data['Cp Estatico []'][i].replace(",", "."))
        cptotal = float(data['Cp Total []'][i].replace(",", "."))
        # Tema agujeros ver de un sistema de reconocimiento para diferentes agujeros, siempre 5 o 7
        hole1 = float(data['Agujero 1 [Pa]'][i].replace(",", "."))
        hole2 = float(data['Agujero 2 [Pa]'][i].replace(",", "."))
        hole3 = float(data['Agujero 3 [Pa]'][i].replace(",", "."))
        hole4 = float(data['Agujero 4 [Pa]'][i].replace(",", "."))
        hole5 = float(data['Agujero 5 [Pa]'][i].replace(",", "."))
        presion_est = float(data['Presion estatica [Pa]'][i].replace(",", "."))
        presion_tot = float(data['Presion total [Pa]'][i].replace(",", "."))
        vel = float(data['Velocidad [m/seg]'][i].replace(",", "."))
        velx = float(data['Velocidad X [m/seg]'][i].replace(",", "."))
        vely = float(data['Velocidad Y [m/seg]'][i].replace(",", "."))
        velz = float(data['Velocidad Z [m/seg]'][i].replace(",", "."))
        # En caso de sonda 7 agujeros
        if data['Tipo de sonda'] == '7 agujeros':
            hole6 = float(data['Agujero 6 [Pa]'][i].replace(",", "."))
            hole7 = float(data['Agujero 7 [Pa]'][i].replace(",", "."))

        point_id = points.InsertNextPoint(x, y, z)
        vertices.InsertNextCell(1, [point_id])

        # Generar escalares en formato VTK
        scalars_posx.InsertNextValue(posx)
        scalars_posy.InsertNextValue(posy)
        scalars_alfa.InsertNextValue(alfa)
        scalars_beta.InsertNextValue(beta)
        scalars_cpalfa.InsertNextValue(cpalfa)
        scalars_cpbeta.InsertNextValue(cpbeta)
        scalars_cpestatica.InsertNextValue(cpestatica)
        scalars_cptotal.InsertNextValue(cptotal)
        scalars_hole1.InsertNextValue(hole1)
        scalars_hole2.InsertNextValue(hole2)
        scalars_hole3.InsertNextValue(hole3)
        scalars_hole4.InsertNextValue(hole4)
        scalars_hole5.InsertNextValue(hole5)
        scalars_presion_est.InsertNextValue(presion_est)
        scalars_presion_tot.InsertNextValue(presion_tot)
        scalars_vel.InsertNextValue(vel)
        scalars_velx.InsertNextValue(velx)
        scalars_vely.InsertNextValue(vely)
        scalars_velz.InsertNextValue(velz)
        # En caso de sonda 7 agujeros
        if data['Tipo de sonda'] == '7 agujeros':
            scalars_hole6.InsertNextValue(hole6)
            scalars_hole7.InsertNextValue(hole7)

    # Crear un objeto "PolyData" y definir puntos, vetices e incluir los escalares
    poly_data = vtk.vtkPolyData()
    poly_data.SetPoints(points)
    poly_data.SetVerts(vertices)

    poly_data.GetPointData().AddArray(scalars_posx)
    poly_data.GetPointData().AddArray(scalars_posy)
    poly_data.GetPointData().AddArray(scalars_alfa)
    poly_data.GetPointData().AddArray(scalars_beta)
    poly_data.GetPointData().AddArray(scalars_cpalfa)
    poly_data.GetPointData().AddArray(scalars_cpbeta)
    poly_data.GetPointData().AddArray(scalars_cpestatica)
    poly_data.GetPointData().AddArray(scalars_cptotal)
    poly_data.GetPointData().AddArray(scalars_hole1)
    poly_data.GetPointData().AddArray(scalars_hole2)
    poly_data.GetPointData().AddArray(scalars_hole3)
    poly_data.GetPointData().AddArray(scalars_hole4)
    poly_data.GetPointData().AddArray(scalars_hole5)
    poly_data.GetPointData().AddArray(scalars_presion_est)
    poly_data.GetPointData().AddArray(scalars_presion_tot)
    poly_data.GetPointData().AddArray(scalars_vel)
    poly_data.GetPointData().AddArray(scalars_velx)
    poly_data.GetPointData().AddArray(scalars_vely)
    poly_data.GetPointData().AddArray(scalars_velz)
    if data['Tipo de sonda'] == '7 agujeros':
        poly_data.GetPointData().AddArray(scalars_hole6)
        poly_data.GetPointData().AddArray(scalars_hole7)

    # Aplicar "Delaunay 2D triangulation".
    delaunay = vtk.vtkDelaunay2D()
    delaunay.SetInputData(poly_data)
    delaunay.Update()

    # Hora y dia de guardado. Utilizado para guardado del archivo VTK
    date_file_name = datetime.datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
    # Grabado del grafico
    file_name = file_name.replace("_.vtk", "_{}.vtk".format(date_file_name))

    # Guardar el conjunto de datos VTK a un archivo VTK
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(delaunay.GetOutput())
    writer.Write()

# Developed by P