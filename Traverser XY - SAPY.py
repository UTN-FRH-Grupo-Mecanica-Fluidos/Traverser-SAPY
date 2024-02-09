import os
import random
import base64
from scipy import interpolate

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

# Ventana de calculo de densidad
def density_calc():
    layout_density = [[sg.T("Presion Atmosferica Absoluta [Pa]")],
                      [sg.I("", justification="center", k="-ATM_PRESSURE-", s=8),
                       sg.T("±", visible = False), sg.I("0", justification="center", k="-ATM_PRESSURE_UNCERT-",
                            s=8, visible = False, tooltip="No Implementado")],
                      [sg.T("Temperatura [ºC]")],
                      [sg.I("", justification="center", k="-TEMP-", s=5,), sg.T("±", visible = False),
                       sg.I("0", justification="center", k="-TEMP_UNCERT-", s=5, visible = False,
                            tooltip="No Implementado")],
                      [sg.T("Humedad Relativa [%]")],
                      [sg.I("", justification="center", k="-REL_HUMIDITY-",s=5), sg.T("±", visible = False),
                       sg.I("0", justification="center", k="-REL_HUMIDITY_UNCERT-", s=5, visible = False,
                            tooltip="No Implementado")],
                      [sg.B("Aceptar", k="-ACCEPT_DENSITY-", pad=(8,8)), sg.B("Cancelar", k="-CANCEL_DENSITY-")]]
    return sg.Window("Calculo densidad del aire", layout_density, resizable=False, icon=icon_bytes,
                    finalize=True, keep_on_top = True, disable_close = True)


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
col_b2 = [[sg.T("Densidad [Kg/m3]", justification="left"), sg.B("Calcular", s=12, k="-CALC_DENSITY-")],
          [sg.I('1.225', s=7, justification="center", p=(0, 8), k="-DENSITY_VALUE-", pad = (2,0))],
          [sg.Text('Nivel de confianza:'), sg.Combo(values=['68%', '95%', '99%'], key='-NIVCONF-',
                                                    default_value=['95%'], s=(5, 1), readonly=True,
                                                    background_color='white')],
          [sg.Button('Procesar', key='-PROCESS-', enable_events=True, font=("Arial", 11), size=(9, 1),
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
graf = [[sg.Listbox(values=['Seleccione archivo traverser'], key='-PLOT LIST-', size=(35, 16), enable_events=True,
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
              sg.Frame('Graficos del Mapeo', graf_button, vertical_alignment='center', font=("Arial", 13, 'bold'),
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
# probe_type = '-'
# sect_calc = '-'


while True:
    # Se utiliza el sistema multi-window. Se utiliza una segunda ventana.
    window, event, values = sg.read_all_windows()

    print('event:', event)
    print('values:', values)

    # -------------------------Ventana de calculo de densidad-------------------------
    # Abrir ventana de calculo
    if event == "-CALC_DENSITY-":
        window2 = density_calc()

    # Cancelar Ingreso
    if event == "-CANCEL_DENSITY-":
        window2.close()

    # Se calcula la densidad
    if event == "-ACCEPT_DENSITY-":
        # Verificar si los valores ingresados son numericos.
        try:
            pressure = float(values["-ATM_PRESSURE-"])
            if 90000 <= pressure <= 105000:
                temperature = float(values["-TEMP-"])
                relative_humidity = float(values["-REL_HUMIDITY-"])
                if 0 <= relative_humidity <= 100:
                    density = air_density(pressure, relative_humidity, temperature)
                    window1["-DENSITY_VALUE-"].update(value=round(density, 4))  # Se redondea a 4 cifras
                    window2.close()
                else:
                    sg.popup_ok("La humedad relativa debe tener un valor entre 0-100%.", keep_on_top=True)
            else:
                sg.popup_ok("La Presion tiene un valor anormal.", keep_on_top=True)
        except Exception as e:
            print(e)
            sg.popup_ok("Se deben ingresar valores numericos", keep_on_top=True)


    # -------------------------Window Principal-------------------------
    # Evento de carga de archivo de calibracion
    if event == '-CALIBFILE-':
        can_process_calib = True
        # ---------Carga de los datos del archivo de calibracion---------
        try:
            raw_data = []  # Reinicio de la variable donde se guardan los datos del CSV.
            # Lee el archivo de calibracion y determina si inicia como "Tipo de sonda: ," o' "Tipo de sonda: ;"
            with open(values['-CALIBFILE-'], 'r') as file:
                first_line = file.readline()
            if "Tipo de sonda: ," in first_line:
                # Carga de datos para un formato de separacion de columnas del tipo ","
                with open(values['-CALIBFILE-']) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    # Extraigo todas las filas del archivo y se lo procesa.
                    for csv_row in csv_reader:
                        raw_data.append(csv_row)
            else:
                # Carga de datos para un formato de separacion de columnas del tipo ";"
                with open(values['-CALIBFILE-']) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=';')
                    # Extraigo todas las filas de un archivo y se lo procesa.
                    for csv_row in csv_reader:
                        raw_data.append(csv_row)
                # Convierto en float los valores. Cambio "," a ".". Se usa "nested list comprehensions" para procesar
                raw_data = [[l.replace(',', '.') for l in i] for i in raw_data]
            del first_line  # Borrado de variables innecesarias

            # Se determina el tipo de sonda y si el calculo de los coeficientes de calibracion
            # fue realizado en forma "Multi-Zona"
            probe_type = raw_data[0][1]
            sect_calc = raw_data[1][1]
            calib_data = raw_data  # La informacion de calibracion pasa a otra variable
            del calib_data[0:3]  # Se elimina primera linea con el tipo de sonda y la segunda

            # Se realiza una conversion a float y se redondea los valores durante la carga de valores.
            # Angulos 1 cifra significativa. Coeficientes 4 cifras significativas
            if probe_type == '2 agujeros':
                # ---------- Carga de datos de la calibracion para 2 agujeros ----------
                angle = [round(float(calib_data[i][0]), 1) for i in range(len(calib_data))]
                cpangle = [round(float(calib_data[i][1]), 4) for i in range(len(calib_data))]
                # ---------- Carga de funciones de interpolacion ----------
                sorted_lists = sorted(zip(cpangle, angle), key=lambda x: x[0])  # Acomodo la lista en forma incremental para el interpolador
                angle_sort, cpangle_sort = zip(*sorted_lists)
                angle_interp = interpolate.CubicSpline(cpangle_sort, angle_sort)  # Interpolacion por "Cubic splines"
                # ---------- Guardado de datos en variable de diccionario ----------
                data_calibr = {'Angulo': angle, "Cpangulo": cpangle, "Angulo-Interp": angle_interp}

                # Actualiza la imagen del numero de agujeros junto con sus referencias.
                # Deshabilita o habilita los COMBO dependiendo del tipo de sonda elegida y se reemplaza el valor
                # que tenia previamente por uno nulo [] cuando se deshabilita.
                # Evento de seleccion de carpeta de trabajo
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
                # ---------- Carga de datos de la calibracion para 3 agujeros ----------
                angle = [round(float(calib_data[i][0]), 1) for i in range(len(calib_data))]
                cpangle = [round(float(calib_data[i][1]), 4) for i in range(len(calib_data))]
                cpestat = [round(float(calib_data[i][2]), 4) for i in range(len(calib_data))]
                cptotal = [round(float(calib_data[i][3]), 4) for i in range(len(calib_data))]
                # ---------- Carga de funciones de interpolacion ----------
                sorted_lists = sorted(zip(cpangle, angle, cpestat, cptotal), key=lambda x: x[0])  # Acomodo la lista en forma incremental para el interpolador
                cpangle_sort, angle_sort, cpestat_sort, cptotal_sort = zip(*sorted_lists)
                angle_interp = interpolate.CubicSpline(cpangle_sort, angle_sort)  # Interpolacion por "Cubic splines"
                cpestat_interp = interpolate.CubicSpline(cpangle_sort, cpestat_sort)  # Interpolacion por "Cubic splines"
                cptotal_interp = interpolate.CubicSpline(cpangle_sort, cptotal_sort)  # Interpolacion por "Cubic splines"
                # ---------- Guardado de datos en variable de diccionario ----------
                data_calibr = {'Angulo': angle, "Cpangulo": cpangle, "Cpestatico": cpestat, "Cptotal": cptotal,
                               "Angulo-Interp": angle_interp, "Cpestatico-Interp": cpestat_interp,
                               "Cptotal-Interp": cptotal_interp}
                # ---------- Modificacion de la ventana con datos cargados ----------
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

            elif probe_type == '5 agujeros' or probe_type == '7 agujeros':
                # ---------- Carga de datos de la calibracion para 5 y 7 agujeros ----------
                alpha = [round(float(calib_data[i][0]), 1) for i in range(len(calib_data))]
                beta = [round(float(calib_data[i][1]), 1) for i in range(len(calib_data))]
                cpalpha = [round(float(calib_data[i][2]), 4) for i in range(len(calib_data))]
                cpbeta = [round(float(calib_data[i][3]), 4) for i in range(len(calib_data))]
                cpestat = [round(float(calib_data[i][4]), 4) for i in range(len(calib_data))]
                cptotal = [round(float(calib_data[i][5]), 4) for i in range(len(calib_data))]
                max_zone = [calib_data[i][13] for i in range(len(calib_data))]
                # ---------- Carga de funciones de interpolacion ----------
                alfa_interp = interpolate.SmoothBivariateSpline(cpalpha, cpbeta, alpha, w=None, kx=3, ky=3, s=None,
                                                                eps=1e-16)
                beta_interp = interpolate.SmoothBivariateSpline(cpalpha, cpbeta, beta, w=None, kx=3, ky=3, s=None,
                                                                eps=1e-16)
                cpestat_interp = interpolate.SmoothBivariateSpline(cpalpha, cpbeta, cpestat, w=None, kx=3, ky=3, s=None,
                                                                   eps=1e-16)
                cptotal_interp = interpolate.SmoothBivariateSpline(cpalpha, cpbeta, cptotal, w=None, kx=3, ky=3, s=None,
                                                                   eps=1e-16)
                # ---------- Guardado de datos en variable de diccionario ----------
                data_calibr = {'Alfa': alpha, "Beta": beta, "Cpalfa": cpalpha, "Cpbeta": cpbeta, "Cpestatico": cpestat,
                               "Cptotal": cptotal, "Alfa-Interp": alfa_interp, "Beta-Interp": beta_interp,
                               "Cpestatico-Interp": cpestat_interp, "Cptotal-Interp": cptotal_interp}
                # ---------- Modificacion de la ventana con datos cargados ----------
                if probe_type == '5 agujeros':
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
        # Clasificacion de los archivos CSV en los del traverser y cero
        traverser_files = []
        zero_files = []
        for clasif_names in fnames:
            # Si el archivo empieza como "XY_SapySync_X" se lo considera del traverser
            if clasif_names.startswith("XY_SapySync_X"):
                traverser_files.append(clasif_names)
            else:
                zero_files.append(clasif_names)
        # Se realiza la actualizacion del layout dependiendo de si se encontraron archivos de calibracion o no
        if not traverser_files:
            # Como no hay archivos del traverser se desactivan los botones de configuracion de sonda y se eliminan
            # los valores de las listas de tomas de los COMBO en la sección "relación Agujero: Toma de presion".
            window['-STATUS-'].update('No hay archivos del traverser')
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
        num_tomas = window['-TYPEPROBE-'].get()
        flag, data_conf = ref_aguj_toma_ok(values, num_tomas)
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
            if not window['-TYPEPROBE-'].get() == conf_carg[0]:
                error_popup(
                    'El tipo de sonda indicado en el archivo de configuracion no coincide con el de la calibracion ingresada \n'
                    'No olvidar cargar el archivo de calibracion previamente')
            else:
                if conf_carg[0] == '2 agujeros':
                    # El numero de tomas de presion definidos en el archivo de configuracion deberia ser coherente
                    # con el tipo de sonda
                    if len(conf_carg) != 3:
                        error_popup('El archivo de configuracion tiene un numero de sensores incorrecto')
                        flag = 1
                    # Las tomas de presion definidas en el archivo de configuracion deben ser igual a las utilizadas
                    # en la calibracion
                    for i in conf_carg[1:]:
                        if i not in num_tomas_list:
                            error_popup('El archivo de configuracion tiene numeros de sensor de presion\n'
                                        'no utilizados por el traverser')
                            flag = 1
                    if flag == 0:
                        # Modificacion de la seccion "relacion Agujero: Toma de presion" y carga de los valores.
                        window['-NUM1-'].update(value=conf_carg[1])
                        window['-NUM2-'].update(value=conf_carg[2])
                elif conf_carg[0] == '3 agujeros':
                    # El numero de tomas de presion definidos en el archivo de configuracion deberia ser coherente
                    # con el tipo de sonda
                    if len(conf_carg) != 4:
                        error_popup('El archivo de configuracion tiene un numero de sensores incorrecto')
                        flag = 1
                    # Las tomas de presion definidas en el archivo de configuracion deben ser igual a las utilizadas
                    # en la calibracion
                    for i in conf_carg[1:]:
                        if i not in num_tomas_list:
                            error_popup('El archivo de configuracion tiene numeros de sensor de presion\n'
                                        'no utilizados por el traverser')
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
                        error_popup('El archivo de configuracion tiene un numero de sensores incorrecto')
                        flag = 1
                    # Las tomas de presion definidas en el archivo de configuracion deben ser igual a las utilizadas
                    # en la calibracion
                    for i in conf_carg[1:]:
                        if i not in num_tomas_list:
                            error_popup('El archivo de configuracion tiene numeros de sensor de presion\n'
                                        'no utilizados por el traverser')
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
                        error_popup('El archivo de configuracion tiene un numero de sensores incorrecto')
                        flag = 1
                    # Las tomas de presion definidas en el archivo de configuracion deben ser igual a las utilizadas
                    # en la calibracion
                    for i in conf_carg[1:]:
                        if i not in num_tomas_list:
                            error_popup('El archivo de configuracion tiene numeros de sensor de presion\n'
                                        'no utilizados por el traverser')
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

    # Procesamiento de las presiones medidas, la incertidumbre de las presiones
    # y ... (calibracion de la sonda junto con sus incertidumbres)
    if event == '-PROCESS-':
        can_process = True  # Flag de que no existen errores.
        # Ingreso de datos desde la interfaz grafica
        # Se incluye el tipo de sonda dentro de la variable "values". Facilita el codigo en las funciones.
        values.update({'-TYPEPROBE-': window['-TYPEPROBE-'].get()})
        values.update({'-MULTIZONE-': window['-MULTIZONE-'].get()})
        # Nombre de la carpeta de trabajo
        path_folder = values['-FOLDER-']
        # Nombre del archivo del cero referencia
        cero_file = values['-CERO-']
        # Formato de salida CSV
        if values[0]:
            option = 0
        elif values[1]:
            option = 1
        else:
            option = 2
        seplist, decsep = format_csv(option)
        # Nivel de Confianza. Se eligio 68.27%, 95% y 99%. Los que se suelen usar.
        conf_level = values['-NIVCONF-']
        if conf_level == '68%':
            conf_level = float(0.6827)
        elif conf_level == '95%':
            conf_level = float(0.95)
        elif conf_level == '99%':
            conf_level = float(0.99)

        # Comprobacióm de errores
        #  La carpeta no existe
        if not os.path.exists(path_folder):
            error_popup('La carpeta seleccionada no existe')
            can_process = False
        else:
            # No hay archivos del traverser en la carpeta. Para evitar errores debe estar dentro del "if".
            if traverser_files == [] and can_process:
                error_popup('No hay archivos del traverser en la carpeta')
                can_process = False
        #  No se selecciono el archivo de referencia del cero
        if (cero_file == '' or cero_file == 'No hay archivos CSV') and can_process:
            error_popup('No se selecciono el archivo de referencia')
            can_process = False
        # Verificacion de la configuracion de la relacion Agujero: Toma de Presion
        if can_process:
            # Determinacion de que los datos ingresados por layout no tengan tomas repetidas
            # o no se halla ingresado ningun valor.
            num_tomas = window['-TYPEPROBE-'].get()
            flag, data_conf = ref_aguj_toma_ok(values, num_tomas)
            if flag == 1:
                can_process = False

        #  Verificacion de valor numerico en la densidad
        if can_process:
            try:
                float(values["-DENSITY_VALUE-"])
            except Exception as e:
                print(e)
                error_popup('El valor de densidad es incorrecto')
                can_process = False

        # Calculo de los voltajes de referencia. Ante falla da aviso.
        if can_process:  # Si no hubo errores se continua. Similar a can_process==True.
            try:  # Prueba procesar el archivo sino genera mensaje de error.
                path_cero = path_folder + '/' + cero_file
                vref = reference_voltage(path_cero)
                # Listado de los valores de voltaje del autozero. Se activa for el checkbox.
                if values['-INFO AUTOZERO-'] and can_process:
                    values_vref = []
                    for sensor_volt, value in vref.items():
                        values_vref.append(str(sensor_volt) + ': {}'.format(round(value, 4)))
                    autozero_popup('\n'.join(values_vref))
            except Exception as e:
                print(e)
                vref = []  # Evita tomar valores de una instancia anterior
                # Aviso de cero no procesable
                error_popup('El archivo del Autozero no es procesable')
                can_process = False

        # Creacion/verificacion de la carpeta "Resultados".
        save_path_folder = path_folder + '/Resultados'  # Linea para cambiar el nombre de la carpeta de salida
        if not os.path.isdir(save_path_folder):
            try:
                # Prueba generar la cerpeta "Resultados".
                os.mkdir(save_path_folder)
            except Exception as e:
                print(e)
                # Aviso la carpeta de salida no pudo crearse
                error_popup('No se pudo crear la carpeta "Resultados"')
                can_process = False

        # Si no hay errores se inicia el calculo
        if can_process:
            # Armado listado de archivos de calibracion. Se arma el PATH completo
            file_path_list = []
            for i in traverser_files:
                file_path_list.append(path_folder + '/' + i)

            # Procesamiento de los archivos
            save_data = []  # Inicializo variable donde se guardan los datos.
            error_files_list = []  # Inicializo variable donde se guardan los archivos con fallas.
            # Barra de progreso del calculo
            window2 = sg.Window('Procesando', [[sg.Text('Procesando ... 0%', key='-PROGRESS VALUE-')], [
                sg.ProgressBar(len(file_path_list), orientation='horizontal', style='xpnative', size=(20, 20),
                               k='-PROGRESS-')]], finalize=True)

            for i in range(len(file_path_list)):
                data = []  # Reinicio de la variable donde se guardan los datos del CSV.
                # Actualizacion barra de progreso
                window2['-PROGRESS-'].update(current_count=i)
                window2['-PROGRESS VALUE-'].update('Procesando ... {}%'.format(int(((i+1)/len(file_path_list))*100)))
                # Se abre cada archivo que figura en el listado.
                with open(file_path_list[i]) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=';')
                    # Extraigo todas las filas de un archivo y se lo procesa.
                    for csv_row in csv_reader:
                        data.append(csv_row)
                    try:
                        # Procesamiento de los datos
                        data_calc = data_process(data, vref, conf_level, data_calibr, values)
                        # Union de los datos procesados de cada archivo.
                        save_data.append(data_calc)
                    except Exception as e:
                        print(e)
                        error_files_list.append(file_path_list[i])
            # Se cierra la ventana de progreso
            window2.close()

            # Prevención de error cuando todos los archivos fallan en procesarse.
            if len(save_data) == 0:
                info_popup('No se llego a procesar ningun archivo')
            else:
                # Guardado de los archivos
                # Ventana de aviso de guardado de archivos
                window2 = sg.Window('', [[sg.Text('Guardando archivos CSV')]], no_titlebar=True, background_color='grey',
                                    finalize=True)
                # Path de guardado de resultados
                try:
                    save_csv_pressure(save_data, save_path_folder, seplist, decsep)
                    save_csv_uncert(save_data, conf_level, save_path_folder, seplist, decsep)
                    save_csv_trav(save_data, save_path_folder, seplist, decsep, values)
                    info_popup('Los archivos de salida se guardaron con exito')
                except Exception as e:
                    print(e)
                    info_popup('Existen problemas en el guardado de los archivos de salida')
                    error_files_list.append(file_path_list[i])
                #  Se cierra la ventana de aviso de guardado de archivos
                window2.close()

            # Informa los archivos que no pudieron procesarse
            if error_files_list:
                error_files_popup('\n'.join(error_files_list))

    # Evento de carga de archivo de calibracion para luego graficarlo.
    # Este evento DEBE estar luego del evento '-PROCESS-' para que la carga automatica del archivo de calibracion
    # luego de procesar funcione
    if event == '-GRAFARCH-':
        can_process_plot = True  # Flag para determinar que el archivo cargado es valido para graficar
        # ---------Carga de los datos del archivo de calibracion---------
        try:
            raw_data = []  # Reinicio de la variable donde se guardan los datos del CSV.
            # Lee el archivo de calibracion y determina si inicia como "Tipo de sonda: ," o' "Tipo de sonda: ;"
            with open(values['-GRAFARCH-'], 'r') as file:
                first_line = file.readline()
            if "Tipo de sonda: ," in first_line:
                # Carga de datos para un formato de separacion de columnas del tipo ","
                with open(values['-GRAFARCH-']) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    # Extraigo todas las filas del archivo y se lo procesa.
                    for csv_row in csv_reader:
                        raw_data.append(csv_row)
            else:
                # Carga de datos para un formato de separacion de columnas del tipo ";"
                with open(values['-GRAFARCH-']) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=';')
                    # Extraigo todas las filas de un archivo y se lo procesa.
                    for csv_row in csv_reader:
                        raw_data.append(csv_row)
                # Convierto en float los valores. Cambio "," a ".". Se usa "nested list comprehensions" para procesar
                raw_data = [[l.replace(',', '.') for l in i] for i in raw_data]
            del first_line  # Borrado de variables innecesarias
            # Se determina el tipo de sonda y si el calculo de los coeficientes de calibracion
            # fue realizado en forma "sectorial"
            probe_type = raw_data[0][1]
            sect_calc = raw_data[1][1]
            # Se elininan los datos de las dos primeras filas
            raw_data = raw_data[2:]

            # Extracion de los datos (ChatGPT)
            # Encabezado
            headers = raw_data[0]
            # Usando los encabezados como keys inicio el diccionario con listas vacias
            graph_data = {header: [] for header in headers}
            # Agrego los datos de cada columna a su key correspondiente
            for row in raw_data[1:]:
                for header, value in zip(headers, row):
                    graph_data[header].append(value)
            # Agregado del tipo de sonda y analisis sectorizado
            graph_data.update({"Tipo de sonda": probe_type, "Analisis Sectorizado": sect_calc})
        except Exception as e:
            # Si el archivo fallo en procesarse se advierte y "resetea" la seccion "Graficos"
            print(e)
            error_popup('El archivo de calibracion no es procesable')
            can_process_plot = False
            window['-PLOT LIST-'].update(values=['Seleccione archivo calibracion'])
            window['-GRAFICAR-'].update(disabled=True)
            window['-GUARDGRAF-'].update(disabled=True)
        # Actualizacion del listado de funciones disponibles para graficar y carga de los datos necesarios para graficar.
        if can_process_plot:
            window['-GRAFICAR-'].update(disabled=False)
            window['-GUARDGRAF-'].update(disabled=False)
            # Se realiza una conversion a float y se redondea los valores durante la carga de valores.
            # Angulos 1 cifra significativa. Coeficientes 4 cifras significativas
            if probe_type == '2 agujeros':
                plot_list = ['CpAngulo=F(Angulo)']  # Graficos disponibles
                window['-PLOT LIST-'].update(values=plot_list)
            elif probe_type == '3 agujeros':
                plot_list = ['CpAngulo=F(Angulo)', 'CpEstatico=F(Angulo)',
                             'CpTotal=F(Angulo)']  # Graficos disponibles
                window['-PLOT LIST-'].update(values=plot_list)
            elif probe_type == '5 agujeros' or probe_type == '7 agujeros':
                plot_list = ['CpAlfa=F(Alfa,Beta)', 'CpBeta=F(Alfa,Beta)', 'CpEstatico=F(Alfa,Beta)',
                             'CpTotal=F(Alfa,Beta)', 'Alfa=F(CpAlfa,CpBeta)', 'Beta=F(CpAlfa,CpBeta)',
                             "Datos=f(angulo) - VTK", "Datos=f(Cp) - VTK"]
                # Se agrega la funcion de Analisis Sectorizado si la calibracion tiene este tipo de analisis.
                if sect_calc == 'Utilizado':
                    plot_list += ['Analisis Sectorial']
                window['-PLOT LIST-'].update(values=plot_list)
            else:
                # No deberia ocurrir nunca pero se lo agrega por seguridad.
                error_popup('El archivo de calibracion no es procesable')


    # Salida del programa
    if event == "Salir" or event == sg.WIN_CLOSED:
        break

