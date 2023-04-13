import PySimpleGUI as sg
import random

# --------------------------------------------------- LAYOUT ---------------------------------------------------
# Layout Theme
sg.theme('SystemDefaultForReal')

# ---------------------------- PRUEBA LAYOUT ----------------------------

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
    sg.Text('No Aplica', key='-MULTIZONE-', enable_events=True, justification='c', background_color='white', relief='groove',
            expand_x = True)]]

# Frame archivo de calibracion
arch_calib = [[sg.Input(key='-CALIBFILE-', enable_events=True, expand_x=True),
               sg.FileBrowse(button_text='Buscar', file_types=(('Archivo CSV', '.csv'),))],
              [sg.Column(col_a1, element_justification='left'), sg.Column(col_a2, element_justification='left')]]
arch_calib_frame = [
    [sg.Frame('Ingresar archivo de calibracion', arch_calib, vertical_alignment='center', title_location='nw')]]


# Generacion de 2 ventanas (windows)
# La primera es el programa principal, la segunda es para ventanas de avisos de progreso.
window1 = sg.Window("Traverser XY – SAPY - Version 1.0 (alfa)", arch_calib_frame, resizable=False, icon=None,
                    finalize=True)
window2 = None  # Ventana de progreso


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

    # Salida del programa
    if event == "Salir" or event == sg.WIN_CLOSED:
        break
