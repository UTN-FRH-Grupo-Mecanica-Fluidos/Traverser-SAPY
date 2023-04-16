import os
import random
import base64

# Carga imagenes del layout e icono
from image.image_agujeros import *
from image.logo import *
from image.icono import *

# Cargar funciones
from function.basic_functions import *
from function.layout_functions import *
from function.process_function import *


# ----------Carga de Icono----------
icon_bytes = base64.b64decode(icon)

# --------------------------------------------------- LAYOUT ---------------------------------------------------
# Layout Theme
sg.theme('SystemDefaultForReal')

# -----------------------------------Columna Izquierda-----------------------------------
# Frame archivo de calibracion
# Informacion min-max de alfa y beta y Analisis Multi-Zona
col_a1 = [[sg.Text('α (Alfa): '), sg.Text('-',key='-MINALPHA-',enable_events=True,justification='c',
                                              background_color='white', relief='groove',s=5),
               sg.Text('/'), sg.Text('-', key='-MAXALPHA-', enable_events=True, justification='c',
                                     background_color='white', relief='groove', s=5)],
              [sg.Text('β (Beta):'),
               sg.Text('-', key='-MINBETA-', enable_events=True, justification='c', background_color='white',
                       relief='groove', s=5), sg.Text('/'),
               sg.Text('-', key='-MAXBETA-', enable_events=True, justification='c', background_color='white',
                       relief='groove', s=5)]]
col_a2 = [[sg.Text('Analisis Multi-Zona')], [
    sg.Text('No Aplica', key='-MULTIZONE-', enable_events=True, justification='c', background_color='white',
            relief='groove', expand_x=True)]]
arch_calib = [[sg.Input(key='-CALIBFILE-', enable_events=True, expand_x=True),
               sg.FileBrowse(button_text='Buscar', file_types=(('Archivo CSV', '.csv'),))],
              [sg.Column(col_a1, element_justification='left'), sg.Column(col_a2, element_justification='left')]]
arch_calib_frame = [sg.Frame('Ingresar archivo de calibracion', arch_calib, expand_x=True, title_location='nw')]

# Frame carpeta de trabajo (Traverser)
folder_traverser = [
    [sg.Input(key='-FOLDER-', enable_events=True, expand_x=True), sg.FolderBrowse(button_text='Buscar')],
    [sg.StatusBar('No hay archivos del traverser', justification='left', size=(50, 1), expand_x=True, key='-STATUS-')]]
frame_traverser = [
    sg.Frame('Ingresar carpeta de trabajo (Traverser)', folder_traverser, title_location='nw', expand_x=True)]

# Frame de la referencia del cero (autozero)
autozero = [[sg.Combo(values=[], default_value='No hay archivos CSV', key='-CERO-', enable_events=True, expand_x=True)],
            [sg.Checkbox('Informar el resultado del autozero', key='-INFO AUTOZERO-')]]
frame_autozero = [
    sg.Frame('Elegir archivo de referencia del cero (Autozero)', autozero, vertical_alignment='center', pad=(0, (8, 4)),
             expand_x=True)]

# Frame formato CSV
format_CSV = [[sg.Radio("Automatico (solo Windows)", "grupo-CSV")],
              [sg.Radio("Separador de listas: COMA - Simbolo decimal: PUNTO", "grupo-CSV", default=True)],
              [sg.Radio("Separador de listas: PUNTO Y COMA - Simbolo decimal: COMA", "grupo-CSV")]]
frame_format_CSV = [
    sg.Frame('Formato de salida del CSV', format_CSV, vertical_alignment='center', expand_y=True, expand_x=True,
             pad=(0, (4, 4)))]

# Logo, nivel de confianza, boton procesar y salir
col_b1 = [[sg.Image(source=logo, subsample=3, tooltip='Laboratorio de Aerodinamica y Fluidos')]]
col_b2 = [[sg.Text('Nivel de confianza:'),
           sg.Combo(values=['68%', '95%', '99%'], key='-NIVCONF-', default_value=['95%'], s=(5, 1), readonly=True,
                    background_color='white')], [
              sg.Button('Procesar', key='-PROCESS-', enable_events=True, font=("Arial", 11), size=(9, 1),
                        pad=(10, (10, 5))), sg.Button('Salir', font=("Arial", 11), size=(9, 1), pad=(10, (10, 5))),
              sg.Push()]]
last_row = [sg.Column(col_b1, vertical_alignment='middle'), sg.Column(col_b2, vertical_alignment='center')]

# Columna Izquierda Final
col_izq = [arch_calib_frame, frame_traverser, frame_autozero, frame_format_CSV, last_row]

# -----------------------------------Columna Derecha-----------------------------------
# Imagen Agujeros - Carga de configuracion de sonda
col_c1 = [[sg.Image(source=sin_agujeros, subsample=3, tooltip='Sonda no definida', key='-IMAGENSONDA-')],
          [sg.Push(), sg.Text("Vista Frontal", justification='center', font=("Arial", 9, 'bold')), sg.Push()]]
col_c2 = [[sg.Text("Configuracion", justification='center', font=("Arial", 14, 'underline'))], [
    sg.Button('Cargar', key='-CARGCONF-', enable_events=True, font=("Arial", 14), size=(7, 1), pad=((0, 0), (7, 7)),
              disabled=True)], [
              sg.Button('Guardar', key='-GUARDCONF-', enable_events=True, font=("Arial", 14), size=(7, 1),
                        pad=((0, 0), (7, 7)), disabled=True)]]
conf_sonda = [sg.Push(), sg.Column(col_c1),
              sg.Column(col_c2, element_justification='center', vertical_alignment='middle'), sg.Push()]

# Informacion sobre el tipo de sonda
tipo_sonda = [sg.Push(), sg.Text("Tipo de sonda:", justification='center', font=("Arial", 15)),
              sg.Text('-', key='-TYPEPROBE-', size=(10, 1), enable_events=True, justification='c',
                      background_color='white', font=("Arial", 15), relief='groove'), sg.Push()]

# Frame relacion Agujeros/Toma
col_d1 = [[sg.Text("1:", justification='right')], [sg.Text("2:", justification='right')],
          [sg.Text("3:", justification='right')]]
col_d2 = [[combo_list('-NUM1-')], [combo_list('-NUM2-')], [combo_list('-NUM3-')]]
col_d3 = [[sg.Text("4:", justification='right')], [sg.Text("5:", justification='right')],
          [sg.Text("6:", justification='right')]]
col_d4 = [[combo_list('-NUM4-')], [combo_list('-NUM5-')], [combo_list('-NUM6-')]]
col_d5 = [[sg.Text("7:", justification='right')]]
col_d6 = [[combo_list('-NUM7-')]]
agujero_toma = [[sg.Column(col_d1), sg.Column(col_d2), sg.Column(col_d3), sg.Column(col_d4),
                 sg.Column(col_d5, vertical_alignment='top'), sg.Column(col_d6, vertical_alignment='top')]]
agujero_toma_frame = [sg.Push(),
                      sg.Frame('Definir relacion Agujero: Toma de Presion', agujero_toma, vertical_alignment='center',
                               expand_y=True), sg.Push()]

# Frame Graficos de Calibracion
# Seleccion Graficos (listado)
graf = [[sg.Listbox(values=['Seleccione archivo calibracion'], key='-PLOT LIST-', size=(35, 16), enable_events=True,
                    select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED)]]
# Frame graficos, Boton graficar y guardar
col_e1 = [
    [sg.Frame('Graficos', graf, vertical_alignment='center', font=("Arial", 12), title_location='n', size=(210, 120))]]
col_e2 = [[sg.Button('Graficar', key='-GRAFICAR-', size=(8, 1), pad=((0, 0), (7, 7)), disabled=True)],
          [sg.Button('Guardar', key='-GUARDGRAF-', size=(8, 1), pad=((0, 0), (7, 7)), disabled=True)]]
graf_button = [[sg.Input(key='-GRAFARCH-', enable_events=True, size=(33, 1)),
                sg.FileBrowse(button_text='Buscar', file_types=(('Archivo CSV', '.csv'),))],
               [sg.Column(col_e1), sg.Column(col_e2)]]
graf_calib = [sg.Push(),
              sg.Frame('Graficos de calibracion', graf_button, vertical_alignment='center', font=("Arial", 13, 'bold'),
                       title_location='nw'), sg.Push()]

# Columna Derecha Final
col_der = [conf_sonda, tipo_sonda, agujero_toma_frame, graf_calib]

# ----------------------------------- Layout Final -----------------------------------
layout = [[sg.Column(col_izq, vertical_alignment='top'), sg.Column(col_der)]]


# Generacion de 2 ventanas (windows)
# La primera es el programa principal, la segunda es para ventanas de avisos de progreso.
window1 = sg.Window("Traverser XY – SAPY - Version 1.0 (alfa)", layout, resizable=False, icon=icon_bytes,
                    finalize=True)
window2 = None  # Ventana de progreso

# Inicio de variables. Es para evitar errores durante la ejecucion, por inexistencia de esta.
probe_type = '-'


while True:
    # Se utiliza el sistema multi-window. Se utiliza una segunda ventana.
    window, event, values = sg.read_all_windows()
    print('event:', event)
    print('values:', values)

    # Borrar para testeo unicamente
    if event == "-MINALPHA-":
        window['-MINALPHA-'].update('{}'.format(round(random.uniform(-20,20), 1)))
        window['-MAXALPHA-'].update('{}'.format(round(random.uniform(-20, 20), 1)))
        window['-MINBETA-'].update('{}'.format(round(random.uniform(-20, 20), 1)))
        window['-MAXBETA-'].update('{}'.format(round(random.uniform(-20, 20), 1)))

    # Evento de carga de archivo de calibracion
    if event == '-CALIBFILE-':
        can_process_calib = True
        # ---------Carga de los datos del archivo de calibracion---------
        try:
            raw_data = []  # Reinicio de la variable donde se guardan los datos del CSV.
            # Carga de datos para un formato de separacion de columnas del tipo ","
            with open(values['-CALIBFILE-']) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                # Extraigo todas las filas del archivo y se lo procesa.
                for csv_row in csv_reader:
                    raw_data.append(csv_row)
            # Si el numero de columnas de la primera linea es menor a 2, es debido a que el separador
            # de columnas del CSV es ";".
            if len(raw_data[0]) <= 1:
                # Se vuelve a cargar el archivo con el delimitador ";" y se cambia los
                # decimales de "," a "." para poder procesarlo.
                raw_data = []  # Reinicio de la variable donde se guardan los datos del CSV.
                with open(values['-CALIBFILE-']) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=';')
                    # Extraigo todas las filas de un archivo y se lo procesa.
                    for csv_row in csv_reader:
                        raw_data.append(csv_row)
                    # Convierto en float los valores. Cambio "," a ".". Se usa "nested list comprehensions" para procesar
                    raw_data = [[l.replace(',', '.') for l in i] for i in raw_data]
            # Se determina el tipo de sonda y si el calculo de los coeficientes de calibracion
            # fue realizado en forma "Multi-Zona"
            probe_type = raw_data[0][1]
            sect_calc = raw_data[1][1]
            # Eliminar informacion extra.
            calib_data = [raw_data[i] for i in range(0, 4)]  # Se elimina el pie de nota
            del calib_data[2][0]  # Se elimina primer elemento del encabezado
            del calib_data[3][0]  # Se elimina primer elemento de los datos de los coeficientes
            del calib_data[0:2]  # Se elimina primera linea con el tipo de sonda y la segunda
        except Exception as e:
            # Si el archivo fallo en procesarse se advierte
            print(e)
            error_popup('El archivo de calibracion no es procesable')
            window['-MINALPHA-'].update('{}'.format('-'))
            window['-MAXALPHA-'].update('{}'.format('-'))
            window['-MINBETA-'].update('{}'.format('-'))
            window['-MAXBETA-'].update('{}'.format('-'))
            window['-MAXBETA-'].update('{}'.format('-'))
            window['-TYPEPROBE-'].update('{}'.format('-'))
            window['-MULTIZONE-'].update('{}'.format('-'))
            window['-IMAGENSONDA-'].update(source=sin_agujeros, subsample=3)
            window['-IMAGENSONDA-'].TooltipObject.text = 'Sonda no definida'
            window['-NUM1-'].update(disabled=True, value=[])
            window['-NUM2-'].update(disabled=True, value=[])
            window['-NUM3-'].update(disabled=True, value=[])
            window['-NUM4-'].update(disabled=True, value=[])
            window['-NUM5-'].update(disabled=True, value=[])
            window['-NUM6-'].update(disabled=True, value=[])
            window['-NUM7-'].update(disabled=True, value=[])
            can_process_calib = False
        # Como el archivo de calibracion es valido se cargan los datos y se actualiza los datos en el layout
        if can_process_calib:
            # Se realiza una conversion a float y se redondea los valores durante la carga de valores.
            # Angulos 1 cifra significativa. Coeficientes 4 cifras significativas
            if probe_type == '2 agujeros':
                # Carga de datos de la calibracion para 2 agujeros
                angle = []
                cpangle = []
                for i in range(int(len(calib_data[1]) / 2)):
                    # Los coeficientes vienen en paquetes de 2 datos por angulo
                    angle.append(round(float(calib_data[1][2 * i + 0]), 1))
                    cpangle.append(round(float(calib_data[1][2 * i + 1]), 4))
                # asfa
            elif probe_type == '3 agujeros':
                # Carga de datos de la calibracion para 3 agujeros
                angle = []
                cpangle = []
                cpestat = []
                cptotal = []
                for i in range(int(len(calib_data[1]) / 4)):
                    # Los coeficientes vienen en paquetes de 4 datos por angulo
                    angle.append(round(float(calib_data[1][4 * i + 0]), 1))
                    cpangle.append(round(float(calib_data[1][4 * i + 1]), 4))
                    cpestat.append(round(float(calib_data[1][4 * i + 2]), 4))
                    cptotal.append(round(float(calib_data[1][4 * i + 3]), 4))
            elif probe_type == '5 agujeros' or probe_type == '7 agujeros':
                # Carga de datos de la calibracion para 5 y 7 agujeros. Tienen los mismos coeficientes.
                alpha = []
                beta = []
                cpalpha = []
                cpbeta = []
                cpestat = []
                cptotal = []
                max_zone = []
                for i in range(int(len(calib_data[1]) / 7)):
                    # Los coeficientes vienen en paquetes de 7 datos por angulo. Los datos del "max_zone" se cargan
                    # aunque no sea sectorizado el analisis
                    alpha.append(round(float(calib_data[1][7 * i + 0]), 1))
                    beta.append(round(float(calib_data[1][7 * i + 1]), 1))
                    cpalpha.append(round(float(calib_data[1][7 * i + 2]), 4))
                    cpbeta.append(round(float(calib_data[1][7 * i + 3]), 4))
                    cpestat.append(round(float(calib_data[1][7 * i + 4]), 4))
                    cptotal.append(round(float(calib_data[1][7 * i + 5]), 4))
                    max_zone.append(calib_data[1][7 * i + 6])
            else:
                # Sino falla durante la carga del archivo pero el dato del tipo de sonda es erroneo
                # se filta en esta estancia. Se actualiza el layout de la misma forma que fallara la carga.
                window['-MINALPHA-'].update('{}'.format('-'))
                window['-MAXALPHA-'].update('{}'.format('-'))
                window['-MINBETA-'].update('{}'.format('-'))
                window['-MAXBETA-'].update('{}'.format('-'))
                window['-MAXBETA-'].update('{}'.format('-'))
                window['-TYPEPROBE-'].update('{}'.format('-'))
                window['-MULTIZONE-'].update('{}'.format('-'))
                window['-IMAGENSONDA-'].update(source=sin_agujeros, subsample=3)
                window['-IMAGENSONDA-'].TooltipObject.text = 'Sonda no definida'
                window['-NUM1-'].update(disabled=True, value=[])
                window['-NUM2-'].update(disabled=True, value=[])
                window['-NUM3-'].update(disabled=True, value=[])
                window['-NUM4-'].update(disabled=True, value=[])
                window['-NUM5-'].update(disabled=True, value=[])
                window['-NUM6-'].update(disabled=True, value=[])
                window['-NUM7-'].update(disabled=True, value=[])
                error_popup('El archivo de calibracion no es procesable')
    # Salida del programa
    if event == "Salir" or event == sg.WIN_CLOSED:
        break
