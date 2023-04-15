import PySimpleGUI as sg
import csv


# -------------------------Mensajes popup-------------------------
def error_popup(message):
    sg.Window('Error', [[sg.T('{}'.format(message))],
                        [sg.B('OK', bind_return_key=True, size=(4, 1))]],
              element_justification='c', modal=True).read(close=True)


def info_popup(message):
    sg.Window('Informacion', [[sg.T('{}'.format(message))],
                              [sg.B('OK', bind_return_key=True, size=(4, 1))]],
              element_justification='c', modal=True).read(close=True)


def error_files_popup(files):
    sg.Window('Error', [[sg.T('Los siguientes archivos no pudieron procesarse:')],
                        [sg.Multiline(default_text=files, write_only=True, expand_x=True, expand_y=True,
                                      size=(30, 10))],
                        [sg.Push(), sg.B('OK', bind_return_key=True, size=(4, 1))]], resizable=True).read(close=True)


def autozero_popup(values):
    sg.Window('Resultados Autozero', [[sg.T('Se lista los valores de tension \nutilizados para el Autozero:')],
                        [sg.Multiline(default_text=values, write_only=True, expand_x=True, expand_y=True,
                                      size=(30, 10))],
                        [sg.Push(), sg.B('OK', bind_return_key=True, size=(4, 1))]], resizable=True, modal=True).read(close=True)

# -------------------------Elementos repetidos del Layout-------------------------
def combo_list(key):
    combo_element = sg.Combo(values=[], key=key, s=(3, 1), readonly=True, background_color='white',
                             enable_events=True, disabled=True)
    return combo_element


# ---------------------Determinacion del listado de tomas usadas---------------------

# Extrae de un archivo de calibracion las tomas usadas
def list_tomas(files):
    with open(files) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        # Extraigo todas las filas
        data_row = []  # Incializacion variable donde se guardan los datos en bruto del CSV.
        for csv_row in csv_reader:
            data_row.append(csv_row)
    data_row.pop(-1)  # Se elimina ultima fila con el caracter #
    # Se extraen los numeros de las tomas usadas, se omite las filas con valores de los angulos.
    tomas = []
    for i in range(2, len(data_row)):
        tomas.append(data_row[i][1])
    # Elimino los valoes repetidos
    tomas = [i for n, i in enumerate(tomas) if i not in tomas[:n]]
    return tomas