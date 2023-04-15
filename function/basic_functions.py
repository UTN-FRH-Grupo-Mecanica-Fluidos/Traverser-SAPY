from function.layout_functions import *
from subprocess import check_output
import PySimpleGUI as sg
import csv
import matplotlib.pyplot as plt


# Funciòn para determinar que los valores ingresados en la seccion "Relacion Agujeros: Tomas" sean correctos
def ref_aguj_toma_ok(values):
    # Tipo de sonda seleccionada
    num_tomas = values['-NUMTOMAS-']
    flag = 0  # Variable para determinar que es posible guardar la configuracion
    # Verifiacion de completitud de los datos ingresados
    data_conf = []
    if num_tomas == '2 agujeros':
        data_conf = [values['-NUMTOMAS-'], values['-NUM1-'], values['-NUM2-'], values['-NUMPS-'], values['-NUMPT-']]
        # Se busca posibles valores vacios
        for i in range(len(data_conf)):
            if data_conf[i] == '' and flag == 0:
                error_popup('Uno o mas agujeros no tienen la toma de presion definida')
                flag = 1
                break  # Corta el "for" cuando encuentra un error.
        # Se usa el elemento SET para determinar si hay tomas repetidas
        if len(set(data_conf)) != 5 and flag == 0:
            error_popup('Una toma de presion es usada en mas de un agujero')
            flag = 1
    elif num_tomas == '3 agujeros':
        data_conf = [values['-NUMTOMAS-'], values['-NUM1-'], values['-NUM2-'], values['-NUM3-'], values['-NUMPS-'],
                     values['-NUMPT-']]
        # Se busca posibles valores vacios
        for i in range(len(data_conf)):
            if data_conf[i] == '' and flag == 0:
                error_popup('Uno o mas agujeros no tienen la toma de presion definida')
                flag = 1
                break  # Corta el "for" cuando encuentra un error.
        # Se usa el elemento SET para determinar si hay tomas repetidas
        if len(set(data_conf)) != 6 and flag == 0:
            error_popup('Una toma de presion es usada en mas de un agujero')
            flag = 1
    elif num_tomas == '5 agujeros':
        # Se usa el elemento SET para determinar si hay tomas repetidas
        data_conf = [values['-NUMTOMAS-'], values['-NUM1-'], values['-NUM2-'], values['-NUM3-'], values['-NUM4-'],
                     values['-NUM5-'], values['-NUMPS-'], values['-NUMPT-']]
        # Se busca posibles valores vacios
        for i in range(len(data_conf)):
            if data_conf[i] == '' and flag == 0:
                error_popup('Uno o mas agujeros no tienen la toma de presion definida')
                flag = 1
                break  # Corta el "for" cuando encuentra un error.
        if len(set(data_conf)) != 8 and flag == 0:
            error_popup('Una toma de presion es usada en mas de un agujero')
            flag = 1
    elif num_tomas == '7 agujeros':
        data_conf = [values['-NUMTOMAS-'], values['-NUM1-'], values['-NUM2-'], values['-NUM3-'], values['-NUM4-'],
                     values['-NUM5-'], values['-NUM6-'], values['-NUM7-'], values['-NUMPS-'], values['-NUMPT-']]
        # Se busca posibles valores vacios
        for i in range(len(data_conf)):
            if data_conf[i] == '' and flag == 0:
                error_popup('Uno o mas agujeros no tienen la toma de presion definida')
                flag = 1
                break  # Corta el "for" cuando encuentra un error.
        # Se usa el elemento SET para determinar si hay tomas repetidas
        if len(set(data_conf)) != 10 and flag == 0:
            error_popup('Una toma de presion es usada en mas de un agujero')
            flag = 1
    else:
        error_popup('No se selecciono ningun tipo de sonda')
        flag = 1
    return flag, data_conf


# La funcion toma el listado de archivos de calibracion y los organiza de menor a mayor en funcion de alfa y beta
def sort_files_calib(calibr_files_in):
    # Se extrae del nombre del archivo de calibracion los valores de alfa y beta.
    alfa_buffer = []
    beta_buffer = []
    list_buffer = []
    for i in range(len(calibr_files_in)):
        # Se usa el caracter "_" para dividir el nombre del archivo.
        buffer = calibr_files_in[i].split('_')
        alfa_buffer.append(int(buffer[2]))
        beta_buffer.append(int(buffer[4]))
        list_buffer.append(int(i))
    # Usando las funciones SORTED y ZIP se organiza de menor a mayor alfa y beta al mismo tiempo.
    # Se usa la variable "ist" para determinar el orden nuevo del listado de archivos de calibracion.
    # Web eplicativa: https://es.stackoverflow.com/questions/443252/c%C3%B3mo-ordenar-dos-listas-al-mismo-tiempo-en-python
    file_list = []
    for alfa_buffer, beta_buffer, list_buffer in sorted(zip(alfa_buffer, beta_buffer, list_buffer)):
        file_list.append(list_buffer)
    # Usando la variables "list" se organiza la lista de archivos de calibracion de menor a mayor.
    calibr_files_out = []
    for i in range(len(calibr_files_in)):
        calibr_files_out.append(calibr_files_in[file_list[i]])
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
    # Calculo el valor promedio de voltaje de cada toma del archivo seleccionado.
    for i in range(int(len(data_row) / 2)):
        numbsenor = data_row[2 * i][1]  # Se utiliza la estrategia de que los valores vienen en pares
        values = data_row[i * 2][2:-1]  # Se extraen los valores de los voltajes.
        values = [float(i.replace(',', '.')) for i in values]  # Convierto valores de la lista a flotacion.
        averang = sum(values) / len(values)  # Calculo el promedio de Vout.
        averang = float('%.6f' % averang)  # Reducir el numero de cifras a 6
        vref["V{}".format(numbsenor)] = averang  # Modifico valor del diccionario para la toma especifica.
    return vref


# -------------------------Guardados de archivos CSV-------------------------
def save_csv_pressure(save_pressure, path, seplist, decsep):
    # Determinacion de la longitud mas larga de las listas de valores.
    # Puede existir mediciones con numeros diferentes de muestras y es necesario determinar la mayor.
    long = 0
    for i in range(len(save_pressure)):
        if long < len(save_pressure[i]):
            long = len(save_pressure[i])
    # Grabado de los datos obtenidos.
    with open(path + '/presiones.csv', "w", newline='') as f:
        writer = csv.writer(f, delimiter=seplist)
        for i in range(long):
            buffer = []  # Reinicio de la variable. Guarda temporalmente los datos antes de pasarlo al CSV.
            for j in range(len(save_pressure)):
                try:
                    buffer.append(save_pressure[j][i])  # transpone los datos de las listas.
                except Exception as e:
                    print(e)
                    buffer.append('')  # Cuando las longitudes de datos son diferentes se agregan espacios vacios.
            if i > 1:  # Evita que se hagan reemplazos en los encabezados de los archivos.
                # Convierto los decimales al formato elegido.
                buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
            writer.writerow(buffer)
        f.close()  # Cerrado del archivo CSV


def save_csv_incert(save_uncert, conf_level, path, seplist, decsep):
    with open(path + '/incertidumbre.csv', "w", newline='') as f:
        writer = csv.writer(f, delimiter=seplist)
        # Encabezado de las filas.
        column = ['', 'Promedio', 'Uexpandida ({}%)'.format(conf_level * 100), 'Numero de muestras',
                  'Distribución final', 'Coeficiente de expansion']
        for i in range(len(save_uncert[0])):
            buffer = []  # Reinicio de la variable. Guarda temporalmente los datos antes de pasarlo al CSV.
            for j in range(len(save_uncert)):
                buffer.append(save_uncert[j][i])  # transpone los datos de las listas.
            if i > 0:  # Evita que se hagan reemplazos en los encabezados de los archivos.
                # Convierto los decimales al formato elegido.
                buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
            buffer.insert(0, column[i])  # Inserto el encabezado de las filas.
            writer.writerow(buffer)
        # Escritura de nota de archivos de incertidumbre.
        writer.writerow([])
        writer.writerow(
            ['Importante: El analisis de incertidumbre realizado solo incluye incertidumbre por repetividad (Tipo A)'])
        writer.writerow(
            ['y la incertidumbre debido a la calibracion del instrumento (Tipo B), se debe realizar un analisis'])
        writer.writerow(['de otras fuentes de incertidumbre.'])
        f.close()  # Cerrado del archivo CSV


def save_csv_calibr(data_calib, path, seplist, decsep, values):
    with open(path + '/calibracion.csv', "w", newline='') as f:
        writer = csv.writer(f, delimiter=seplist)
        # Encabezado de las filas.
        column = ['', 'Promedio']
        # Informacion del tipo de sonda
        writer.writerow(['Tipo de sonda: ', values['-NUMTOMAS-']])
        # Informacion si se utiliza el analisis sectorizado
        if values['-NUMTOMAS-'] == '2 agujeros' or values['-NUMTOMAS-'] == '3 agujeros':
            # Sonda de 2 y 3 agujeros no tiene analisis sectorizado.
            writer.writerow(['Analisis Sectorizado: ', 'No Aplica'])
        else:
            if values['-HIGH ANGLE-']:
                writer.writerow(['Analisis Sectorizado: ', 'Utilizado'])
            elif not values['-HIGH ANGLE-']:
                writer.writerow(['Analisis Sectorizado: ', 'No utilizado'])

        # Guardado de datos
        for i in range(len(data_calib[0])):
            buffer = []  # Reinicio de la variable. Guarda temporalmente los datos antes de pasarlo al CSV.
            for j in range(len(data_calib)):
                buffer.append(data_calib[j][i])  # transpone los datos de las listas.
            if i > 0:  # Evita que se hagan reemplazos en los encabezados de los archivos.
                # Convierto los decimales al formato elegido.
                buffer = [str(buffer[i]).replace('.', decsep) for i in range(len(buffer))]
            buffer.insert(0, column[i])  # Inserto el encabezado de las filas.
            writer.writerow(buffer)
        # Escritura de nota de archivos de incertidumbre.
        # SE DEBE REFORMAR LA NOTA PARA EL CALCULO DE LOS COEFICIENTES.
        writer.writerow([])
        writer.writerow(
            ['Importante: El analisis de incertidumbre realizado solo incluye incertidumbre por repetividad (Tipo A)'])
        writer.writerow(
            ['y la incertidumbre debido a la calibracion del instrumento (Tipo B), se debe realizar un analisis'])
        writer.writerow(['de otras fuentes de incertidumbre.'])
        f.close()  # Cerrado del archivo CSV


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