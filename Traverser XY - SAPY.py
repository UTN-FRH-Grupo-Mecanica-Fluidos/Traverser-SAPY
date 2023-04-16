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

            # Actualiza la imagen del numero de agujeros junto con sus referencias.
            # Deshabilita o habilita los COMBO dependiendo del tipo de sonda elegida y se reemplaza el valor
            # que tenia previamente por uno nulo [] cuando se deshabilita.
            if probe_type == '2 agujeros':
                window['-IMAGENSONDA-'].update(source=dos_agujeros, subsample=3)
                window['-IMAGENSONDA-'].TooltipObject.text = 'Sonda de 2 agujeros'
                window['-NUM1-'].update(disabled=False)
                window['-NUM2-'].update(disabled=False)
                window['-NUM3-'].update(disabled=True, value=[])
                window['-NUM4-'].update(disabled=True, value=[])
                window['-NUM5-'].update(disabled=True, value=[])
                window['-NUM6-'].update(disabled=True, value=[])
                window['-NUM7-'].update(disabled=True, value=[])
                window['-MINALPHA-'].update('{}'.format(min(angle)))
                window['-MAXALPHA-'].update('{}'.format(max(angle)))
                window['-MINBETA-'].update('{}'.format('-'))
                window['-MAXBETA-'].update('{}'.format('-'))
                window['-TYPEPROBE-'].update('{}'.format(probe_type))
                window['-MULTIZONE-'].update('{}'.format(sect_calc))
            elif probe_type == '3 agujeros':
                window['-IMAGENSONDA-'].update(source=tres_agujeros, subsample=3)
                window['-IMAGENSONDA-'].TooltipObject.text = 'Sonda de 3 agujeros'
                window['-NUM1-'].update(disabled=False)
                window['-NUM2-'].update(disabled=False)
                window['-NUM3-'].update(disabled=False)
                window['-NUM4-'].update(disabled=True, value=[])
                window['-NUM5-'].update(disabled=True, value=[])
                window['-NUM6-'].update(disabled=True, value=[])
                window['-NUM7-'].update(disabled=True, value=[])
                window['-MINALPHA-'].update('{}'.format(min(angle)))
                window['-MAXALPHA-'].update('{}'.format(max(angle)))
                window['-MINBETA-'].update('{}'.format('-'))
                window['-MAXBETA-'].update('{}'.format('-'))
                window['-TYPEPROBE-'].update('{}'.format(probe_type))
                window['-MULTIZONE-'].update('{}'.format(sect_calc))
            elif probe_type == '5 agujeros':
                window['-IMAGENSONDA-'].update(source=cinco_agujeros, subsample=3)
                window['-IMAGENSONDA-'].TooltipObject.text = 'Sonda de 5 agujeros'
                window['-NUM1-'].update(disabled=False)
                window['-NUM2-'].update(disabled=False)
                window['-NUM3-'].update(disabled=False)
                window['-NUM4-'].update(disabled=False)
                window['-NUM5-'].update(disabled=False)
                window['-NUM6-'].update(disabled=True, value=[])
                window['-NUM7-'].update(disabled=True, value=[])
                window['-MINALPHA-'].update('{}'.format(min(alpha)))
                window['-MAXALPHA-'].update('{}'.format(max(alpha)))
                window['-MINBETA-'].update('{}'.format(min(beta)))
                window['-MAXBETA-'].update('{}'.format(max(beta)))
                window['-TYPEPROBE-'].update('{}'.format(probe_type))
                window['-MULTIZONE-'].update('{}'.format(sect_calc))
            elif probe_type == '7 agujeros':
                window['-IMAGENSONDA-'].update(source=siete_agujeros, subsample=3)
                window['-IMAGENSONDA-'].TooltipObject.text = 'Sonda de 7 agujeros'
                window['-NUM1-'].update(disabled=False)
                window['-NUM2-'].update(disabled=False)
                window['-NUM3-'].update(disabled=False)
                window['-NUM4-'].update(disabled=False)
                window['-NUM5-'].update(disabled=False)
                window['-NUM6-'].update(disabled=False)
                window['-NUM7-'].update(disabled=False)
                window['-MINALPHA-'].update('{}'.format(min(alpha)))
                window['-MAXALPHA-'].update('{}'.format(max(alpha)))
                window['-MINBETA-'].update('{}'.format(min(beta)))
                window['-MAXBETA-'].update('{}'.format(max(beta)))
                window['-TYPEPROBE-'].update('{}'.format(probe_type))
                window['-MULTIZONE-'].update('{}'.format(sect_calc))

    # Evento de seleccion de carpeta de trabajo
    if event == '-FOLDER-':
        # Guardado de la ubicacion de la carpeta de trabajo del traverser
        path_folder = values['-FOLDER-']
        # Se busca si la carpeta existe sino devuelve un listado vacio y actualiza la barra de estatus.
        try:
            file_list = os.listdir(path_folder)
        except Exception as e:
            print(e)
            file_list = []
            window['-STATUS-'].update('No hay archivos del traverser')
        # Busca en la carpeta de trabajo los archivos que sean solo CSV.
        fnames = [f for f in file_list if os.path.isfile(os.path.join(path_folder, f)) and f.lower().endswith(".csv")]
        # Elimina del analisis los archivos de salida.
        if "presiones.csv" in fnames:
            fnames.remove("presiones.csv")
        if "incertidumbre.csv" in file_list:
            fnames.remove("incertidumbre.csv")
        if "traverser-velocidades.csv" in file_list:
            fnames.remove("calibracion.csv")
        # Clasificacion de los archivos CSV en los del traverser y cero
        traverser_files = []
        zero_files = []
        for clasif_names in fnames:
            if "XY_SapySync_X" in clasif_names:
                traverser_files.append(clasif_names)
            else:
                zero_files.append(clasif_names)
        # Se realiza la actualizacion del layout dependiendo de si se encontraron archivos de calibracion o no
        if not traverser_files:
            # Como no hay archivos del traverser se desactivan los botones de configuracion de sonda y se eliminan
            # los valores de las listas de tomas de los COMBO en la sección "relación Agujero: Toma de presion".
            window['-STATUS-'].update('No hay archivos de calibracion')
            window['-CARGCONF-'].update(disabled=True)
            window['-GUARDCONF-'].update(disabled=True)
            window['-NUM1-'].update(values=[])
            window['-NUM2-'].update(values=[])
            window['-NUM3-'].update(values=[])
            window['-NUM4-'].update(values=[])
            window['-NUM5-'].update(values=[])
            window['-NUM6-'].update(values=[])
            window['-NUM7-'].update(values=[])
        else:
            # Se organiza los archivos de menor a mayor en funcion del X y el Y. Se recurre a una funcion.
            traverser_files = sort_files_travers(traverser_files)
            numb_files_travers = len(traverser_files)
            window['-STATUS-'].update('Se encontraron {} archivos del traverser'.format(numb_files_travers))
            # Se analiza las tomas que se usaron tomando un archivo del traverser al azar. Se actualizan los listados
            # de la seccion "Agujeros: Toma de Presion"
            num_tomas_list = list_tomas(os.path.join(path_folder, random.choice(traverser_files)))
            window['-CARGCONF-'].update(disabled=False)
            window['-GUARDCONF-'].update(disabled=False)
            window['-NUM1-'].update(values=num_tomas_list)
            window['-NUM2-'].update(values=num_tomas_list)
            window['-NUM3-'].update(values=num_tomas_list)
            window['-NUM4-'].update(values=num_tomas_list)
            window['-NUM5-'].update(values=num_tomas_list)
            window['-NUM6-'].update(values=num_tomas_list)
            window['-NUM7-'].update(values=num_tomas_list)
        # Se realiza la actualizacion del layout dependiendo de si se encontraron CSV's para el autozero.
        if not zero_files:
            window['-CERO-'].update(values=[])
            window['-CERO-'].update(value='No hay archivos CSV')
        else:
            window['-CERO-'].update(values=zero_files)

    # Evento de guardado de la configuracion de la sonda.
    if event == '-GUARDCONF-':
        # Determinacion de que los datos ingresados por layout no tengan tomas repetidas
        # o no se hallan ingresado valores. Se utiliza una funcion.
        flag, data_conf = ref_aguj_toma_ok(values, probe_type)
        # Si esta correcto se prosigue con el guardado de un archivo de extension "*.conf"
        if flag == 0:
            save_file = sg.popup_get_file('Guardar archivo de configuracion',
                                          file_types=(('Archivo de configuracion', '*.conf'),), no_window=True,
                                          save_as=True, keep_on_top=True)  # Elegir el icono
            # Verificar que se puede guardar el archivo. Evita el error por poner cancelar al guardar.
            if save_file != '':
                with open(save_file, "w", newline='') as f:
                    save_file = csv.writer(f, delimiter=',')
                    save_file.writerow(data_conf)

    # Evento de carga de la configuracion de la sonda proveniente de un archivo *.conf
    if event == '-CARGCONF-':
        flag = 0  # Variable para determinar que es posible cargar la configuracion
        # Seleccionar archivo de configuracion
        load_file = sg.popup_get_file('Cargar archivo de configuracion',
                                      file_types=(('Archivo de configuracion', '*.conf'),), no_window=True,
                                      save_as=False, keep_on_top=True)  # Elegir el icono
        # Verifica que se selecciono un archivo. Evita error por poner cancelar al cargar.
        if load_file != '':
            # Lectura del archivo de configuracion
            with open(os.path.join(path_folder, load_file)) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                # Extraigo todas las filas
                data_row = []  # Incializacion variable donde se guardan los datos en bruto del CSV.
                for csv_row in csv_reader:
                    conf_carg = csv_row
            # Analisis del archivo de configuracion. Si el tipo de sonda de la configuracion es diferente al
            # del utilizado por el archivos de calibracion cargado, se advierte. Se cargan los valores
            # en la seccion "Relacion Agujero: Toma de presion".
            if not probe_type == conf_carg[0]:
                error_popup(
                    'El archivo de configuracion no coincide con el numero de tomas de la calibracion \n'
                    'No olvidar cargar el archivo de calibracion previmamente')
            # elif probe_type == '-':
            #     error_popup('No se cargo aun el archivo de calibracion')
            else:
                if conf_carg[0] == '2 agujeros':
                    # El numero de tomas de presion definidos en el archivo de configuracion deberia ser coherente
                    # con el tipo de sonda
                    if len(conf_carg) != 3:
                        error_popup('El archivo de configuracion tiene un numero de tomas incorrecto')
                        flag = 1
                    # Las tomas de presion definidas en el archivo de configuracion deben ser igual a las utilizadas
                    # en la calibracion
                    for i in conf_carg[1:]:
                        if i not in num_tomas_list:
                            error_popup('El archivo de configuracion tiene tomas de presiòn\n'
                                        'no utilizadas en la calibracion')
                            flag = 1
                    if flag == 0:
                        # Modificacion de la seccion "relacion Agujero: Toma de presion" y carga de los valores.
                        window['-NUM1-'].update(value=conf_carg[1])
                        window['-NUM2-'].update(value=conf_carg[2])
                elif conf_carg[0] == '3 agujeros':
                    # El numero de tomas de presion definidos en el archivo de configuracion deberia ser coherente
                    # con el tipo de sonda
                    if len(conf_carg) != 4:
                        error_popup('El archivo de configuracion tiene un numero de tomas incorrecto')
                        flag = 1
                    # Las tomas de presion definidas en el archivo de configuracion deben ser igual a las utilizadas
                    # en la calibracion
                    for i in conf_carg[1:]:
                        if i not in num_tomas_list:
                            error_popup('El archivo de configuracion tiene tomas de presiòn\n'
                                        'no utilizadas en la calibracion')
                            flag = 1
                    if flag == 0:
                        # Modificacion de la seccion "relacion Agujero: Toma de presion" y carga de los valores.
                        window['-NUM1-'].update(value=conf_carg[1])
                        window['-NUM2-'].update(value=conf_carg[2])
                        window['-NUM3-'].update(value=conf_carg[3])
                elif conf_carg[0] == '5 agujeros':
                    # El numero de tomas de presion definidos en el archivo de configuracion deberia ser coherente
                    # con el tipo de sonda
                    if len(conf_carg) != 6:
                        error_popup('El archivo de configuracion tiene un numero de tomas incorrecto')
                        flag = 1
                    # Las tomas de presion definidas en el archivo de configuracion deben ser igual a las utilizadas
                    # en la calibracion
                    for i in conf_carg[1:]:
                        if i not in num_tomas_list:
                            error_popup('El archivo de configuracion tiene tomas de presiòn\n'
                                        'no utilizadas en la calibracion')
                            flag = 1
                    if flag == 0:
                        # Modificacion de la seccion "relacion Agujero: Toma de presion" y carga de los valores.
                        window['-NUM1-'].update(value=conf_carg[1])
                        window['-NUM2-'].update(value=conf_carg[2])
                        window['-NUM3-'].update(value=conf_carg[3])
                        window['-NUM4-'].update(value=conf_carg[4])
                        window['-NUM5-'].update(value=conf_carg[5])
                elif conf_carg[0] == '7 agujeros':
                    # El numero de tomas de presion definidos en el archivo de configuracion deberia ser coherente
                    # con el tipo de sonda
                    if len(conf_carg) != 8:
                        error_popup('El archivo de configuracion tiene un numero de tomas incorrecto')
                        flag = 1
                    # Las tomas de presion definidas en el archivo de configuracion deben ser igual a las utilizadas
                    # en la calibracion
                    for i in conf_carg[1:]:
                        if i not in num_tomas_list:
                            error_popup('El archivo de configuracion tiene tomas de presiòn\n'
                                        'no utilizadas en la calibracion')
                            flag = 1
                    if flag == 0:
                        # Modificacion de la seccion "relacion Agujero: Toma de presion" y carga de los valores.
                        window['-NUM1-'].update(value=conf_carg[1])
                        window['-NUM2-'].update(value=conf_carg[2])
                        window['-NUM3-'].update(value=conf_carg[3])
                        window['-NUM4-'].update(value=conf_carg[4])
                        window['-NUM5-'].update(value=conf_carg[5])
                        window['-NUM6-'].update(value=conf_carg[6])
                        window['-NUM7-'].update(value=conf_carg[7])

    # Salida del programa
    if event == "Salir" or event == sg.WIN_CLOSED:
        break
