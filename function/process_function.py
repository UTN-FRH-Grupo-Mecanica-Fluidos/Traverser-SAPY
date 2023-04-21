from statistics import mean, stdev
import scipy.stats as stats

# Se preprocesan los datos inicialmente y luego se determinan las presiones y las incertidumbres
def data_process(data_csv, vref, nivconf, values):
    # --------------Procesamiento de los datos en bruto--------------
    data = []  # Inicializacion variable de guardado de datos del csv procesado
    data_csv.pop(-1)  # Se elimina ultima fila con el caracter #
    for i in range(len(data_csv)):
        data_buffer = []  # Reinicio variable de guardado
        # Procesamiento de los datos de la fila extraida.
        data_csv[i].pop(-1)  # Se elimina el ultimo elemento con el caracter <
        data_csv[i].pop(0)  # Se elimina el primer elemento con el caracter M, V, A o B
        for j in range(len(data_csv[i])):
            data_buffer.append(float(data_csv[i][j].replace(',', '.')))  # Conversion de string a float.
        data.append(data_buffer)
    # ----------------Procesamiento de las presiones y angulos----------------
    data_pressure = []  # Inicializo la variable de salida.
    # Agrego X e Y al archivo de presion y encabezado
    x_posit = ['Posicion X']  # Encabezado alfa
    x_posit += data[0]  # Agregado datos alfa
    y_posit = ['Posicion Y']  # Encabezado beta
    y_posit += data[1]  # Agregado datos beta
    data_pressure.append(x_posit)  # Agregado de X
    data_pressure.append(y_posit)  # Agregado de Y
    # Calculo de las presiones
    for i in range(1, int(len(data) / 2)):  # Se utiliza la estrategia de que los valores de las tomas vienen en pares
        # Valor de referencia del sensor analizado.
        numbsenor = int(data[2 * i][0])
        V0 = vref["V{}".format(numbsenor)]  # Extraigo del diccionario el valor de referencia.
        # Calculo las presiones para la toma indicada.
        # Inicializo la variable donde guardo las presiones junto con el nombre de archivo y el numero de toma.
        pressure = ["Toma {}".format(numbsenor)]
        for j in range(1, len(data[2])):
            Vout = data[i * 2][j]
            Vs = data[i * 2 + 1][j]
            value = (((Vout - V0) / (Vs * 0.2)) * 1000)
            value = float('%.4f' % value)  # Reduccion a 4 cifras
            pressure.append(value)
        data_pressure.append(pressure)  # Agregado de datos de presiones
    # --------------Calculo de la incertidumbre--------------
    data_uncert = []  # Inicializo la variable de salida.
    crit = 10  # Criterio de contribucion dominante. Se eligio 10 veces superior.
    for i in range(len(data_pressure)):
        # Genero encabezado de los datos
        uncert = [data_pressure[i][0]]  # Inicializo la variable buffer.
        # Extraigo datos numericos.
        data_raw = data_pressure[i][1:]
        # Calculo de incertidumbre.
        sample = len(data_raw)  # Numero de muestras.
        averange = mean(data_raw)  # Estimado de la medicion.
        if sample > 1:
            typea = stdev(data_raw) / (sample ** 0.5)  # Desviación típica experimental.
            # Se diferencia el calculo del componente Tipo B para los diferentes sensores.
            # VER QUE INCERTIDUMBRE TIPO B SE COLOCARA PARA POSICION DEL TRAVERSER
            if data_pressure[i][0] == 'Alfa' or data_pressure[i][0] == 'Beta':
                typeb = averange * 0.00 / (3 ** 0.5)  # Componente Tipo B debido a la posicion del traverser.
            else:
                typeb = averange * 0.015 / (
                        3 ** 0.5)  # Componente Tipo B debido a la calibración del sensor de presion.
            ucomb = (typea ** 2 + typeb ** 2) ** 0.5  # Incertidumbre combinada.
            # Analisis de la contribucion dominante para la determinacion de la incertidumbre expandida.
            # El siguiente codigo evita la division por cero.
            try:
                rel_tipe = typea / typeb
            except Exception as e:
                print(e)
                rel_tipe = 1e10
            # Analisis del tipo de distribucion
            if rel_tipe > crit:
                k = stats.t.ppf((1 + nivconf) / 2, sample - 1)  # t student doble cola. t.ppf(alfa, gl)
                distrib = 't-student con {} GL'.format(sample - 1)
            elif typea / typeb < 1 / crit:
                k = (3 ** 0.5) * nivconf  # Distribucion rectangular k=raiz(3)*p
                distrib = 'Rectangular'
            else:
                k = stats.norm.ppf((1 + nivconf) / 2)  # Cumple teorema limite central. Distribución Normal.
                distrib = 'Normal TCLimite'
            uexpand = k * ucomb  # Incertidumbre expandida
            # Reduccion de cifras
            averange = float('%.2f' % averange)
            uexpand = float('%.4f' % uexpand)
            k = float('%.4f' % k)
        else:
            # En mediciones de un solo valor no es posible calcular la incertidumbre
            averange = float('%.2f' % averange)
            uexpand = 'N/A'
            distrib = 'N/A'
            k = 'N/A'
        # Organizo los datos calculados
        uncert.extend([averange, uexpand, sample, distrib, k])
        data_uncert.append(uncert)
    # --------------Calculo de los coeficientes del traverser--------------
    # Informacion sobre el tipo de sonda
    probe_type = values['-TYPEPROBE-']
    # Lista con el numero de toma asignado para cada agujero generado por el usuario.
    relat_hole_tap = [values['-NUM1-'], values['-NUM2-'], values['-NUM3-'], values['-NUM4-'], values['-NUM5-'],
                      values['-NUM6-'], values['-NUM7-']]
    relat_hole_tap = [x for x in relat_hole_tap if x != '']  # Elimino los valores vacios o agujeros no validos.
    # Busco la organizacion que poseen los datos respecto al numero de toma. EJ: X Y Toma a Toma b
    header_data = [data_uncert[i][0] for i in range(len(data_uncert))]
    # Se determina la relacion entre el "numero de agujero-numero de toma-ubicacion del numero de toma en los datos".
    relat_hole_tap_data = []
    for i in range(len(relat_hole_tap)):
        relat_hole_tap_data.append(int(header_data.index('Toma {}'.format(relat_hole_tap[i]))))

    # # Calculo de los coeficientes del traverser para una sonda de 2 agujeros.
    # if probe_type == '2 agujeros':
    #     # Se relaciona el valor de la toma de presion respecto al agujero definido. Agujero: Toma.
    #     hole_data = {'hole 1': data_uncert[relat_hole_tap_data[0]][1], 'hole 2': data_uncert[relat_hole_tap_data[1]][1],
    #                  'pestatic': data_uncert[relat_hole_tap_data[2]][1],
    #                  'ptotal': data_uncert[relat_hole_tap_data[3]][1]}
    #     # Calculo de coeficientes
    #     q = hole_data['ptotal'] - hole_data['pestatic']
    #     cpangle = (hole_data['hole 2'] - hole_data['hole 1']) / q
    #     # Discriminacion en funcion del angulo definido para la calibracion.
    #     if values['-ALPHA PLANE-']:
    #         data_coef = [['Angulo', data_uncert[0][1]], ['Cpangulo', cpangle]]
    #     if values['-BETA PLANE-']:
    #         data_coef = [['Angulo', data_uncert[1][1]], ['Cpangulo', cpangle]]

    # Calculo de los coeficientes del traverser para una sonda de 3 agujeros.
    if probe_type == '3 agujeros':
        # Se relaciona el valor de la toma de presion respecto al agujero definido. Agujero: Toma.
        hole_data = {'hole 1': data_uncert[relat_hole_tap_data[0]][1], 'hole 2': data_uncert[relat_hole_tap_data[1]][1],
                     'hole 3': data_uncert[relat_hole_tap_data[2]][1]}
        # Calculo de coeficientes
        pss = mean([hole_data['hole 2'], hole_data['hole 3']])
        denom = hole_data['hole 1'] - pss
        cpangle = (hole_data['hole 3'] - hole_data['hole 2']) / denom
        # Discriminacion en funcion del angulo definido para la calibracion.
        if values['-ALPHA PLANE-']:
            data_coef = [['Angulo', data_uncert[0][1]], ['Cpangulo', cpangle]]
        if values['-BETA PLANE-']:
            data_coef = [['Angulo', data_uncert[1][1]], ['Cpangulo', cpangle]]

    # Calculo de los coeficientes del traverser para una sonda de 5 agujeros.
    if probe_type == '5 agujeros':
        # Se relaciona el valor de la toma de presion respecto al agujero definido. Agujero: Toma.
        hole_data = {'hole 1': data_uncert[relat_hole_tap_data[0]][1], 'hole 2': data_uncert[relat_hole_tap_data[1]][1],
                     'hole 3': data_uncert[relat_hole_tap_data[2]][1], 'hole 4': data_uncert[relat_hole_tap_data[3]][1],
                     'hole 5': data_uncert[relat_hole_tap_data[4]][1]}
        # Determinacion del agujero con la maxima presion. Se usa para analisis de grandes angulos de flujo.
        max_hole = max(hole_data, key=hole_data.get)
        # Analisis discriminado para grande y bajos angulos de calibracion
        if values['-MULTIZONE-'] == 'Utilizado':
            # Grandes angulos de flujo
            if max_hole == 'hole 1':
                # Calculo de coeficientes de calibracion para cuando el agujero 1 tiene la mayor presion. Bajos angulos
                pss = mean([hole_data['hole 2'], hole_data['hole 3'], hole_data['hole 4'], hole_data['hole 5']])
                denom = hole_data['hole 1'] - pss
                cpalfa = (hole_data['hole 4'] - hole_data['hole 2']) / denom
                cpbeta = (hole_data['hole 3'] - hole_data['hole 5']) / denom
                zone = 'Zona 1'
            elif max_hole == 'hole 2':
                # Calculo de coeficientes de calibracion para cuando el agujero 2 tiene
                # la mayor presion. Agujero 4 en perdida.
                pss = mean([hole_data['hole 1'], hole_data['hole 3'], hole_data['hole 5']])
                denom = hole_data['hole 2'] - pss
                cpalfa = (hole_data['hole 1'] - hole_data['hole 2']) / denom
                cpbeta = (hole_data['hole 3'] - hole_data['hole 5']) / denom
                zone = 'Zona 2'
            elif max_hole == 'hole 3':
                # Calculo de coeficientes de calibracion para cuando el agujero 3 tiene
                # la mayor presion. Agujero 5 en perdida.
                pss = mean([hole_data['hole 1'], hole_data['hole 2'], hole_data['hole 4']])
                denom = hole_data['hole 3'] - pss
                cpalfa = (hole_data['hole 4'] - hole_data['hole 2']) / denom
                cpbeta = (hole_data['hole 3'] - hole_data['hole 1']) / denom
                zone = 'Zona 3'
            elif max_hole == 'hole 4':
                # Calculo de coeficientes de calibracion para cuando el agujero 4 tiene
                # la mayor presion. Agujero 2 en perdida.
                pss = mean([hole_data['hole 1'], hole_data['hole 3'], hole_data['hole 5']])
                denom = hole_data['hole 4'] - pss
                cpalfa = (hole_data['hole 4'] - hole_data['hole 1']) / denom
                cpbeta = (hole_data['hole 3'] - hole_data['hole 5']) / denom
                zone = 'Zona 4'
            elif max_hole == 'hole 5':
                # Calculo de coeficientes de calibracion para cuando el agujero 5 tiene
                # la mayor presion. Agujero 3 en perdida.
                pss = mean([hole_data['hole 1'], hole_data['hole 2'], hole_data['hole 4']])
                denom = hole_data['hole 5'] - pss
                cpalfa = (hole_data['hole 4'] - hole_data['hole 2']) / denom
                cpbeta = (hole_data['hole 1'] - hole_data['hole 5']) / denom
                zone = 'Zona 5'
            data_coef = [['X', data_uncert[0][1]], ['Y', data_uncert[1][1]], ['Cpalfa', cpalfa],
                          ['Cpbeta', cpbeta], ['Zona maxima presion', zone]]
        else:
            # Bajos angulos de calibracion
            # Calculo de coeficientes.
            pss = mean([hole_data['hole 2'], hole_data['hole 3'], hole_data['hole 4'], hole_data['hole 5']])
            denom = hole_data['hole 1'] - pss
            cpalfa = (hole_data['hole 4'] - hole_data['hole 2']) / denom
            cpbeta = (hole_data['hole 3'] - hole_data['hole 5']) / denom
            zone = 'N/A '
            data_coef = [['X', data_uncert[0][1]], ['Y', data_uncert[1][1]], ['Cpalfa', cpalfa],
                          ['Cpbeta', cpbeta], ['Zona maxima presion', zone]]

    # Calculo de los coeficientes de calibracion para una sonda de 7 agujeros.
    if probe_type == '7 agujeros':
        # Se relaciona el valor de la toma de presion respecto al agujero definido. Agujero: Toma.
        hole_data = {'hole 1': data_uncert[relat_hole_tap_data[0]][1], 'hole 2': data_uncert[relat_hole_tap_data[1]][1],
                     'hole 3': data_uncert[relat_hole_tap_data[2]][1], 'hole 4': data_uncert[relat_hole_tap_data[3]][1],
                     'hole 5': data_uncert[relat_hole_tap_data[4]][1], 'hole 6': data_uncert[relat_hole_tap_data[5]][1],
                     'hole 7': data_uncert[relat_hole_tap_data[6]][1]}
        # Determinacion del agujero con la maxima presion. Se usa para analisis de grandes angulos de flujo.
        max_hole = max(hole_data, key=hole_data.get)
        # Analisis discriminado para grande y bajos angulos de calibracion
        if values['-MULTIZONE-']:
            # Grandes angulos de calibracion
            if max_hole == 'hole 1':
                # Calculo de coeficientes de calibracion para cuando el agujero 1 tiene la mayor presion. Bajos angulos
                pss = mean([hole_data['hole 2'], hole_data['hole 3'], hole_data['hole 4'], hole_data['hole 5'],
                            hole_data['hole 6'], hole_data['hole 7']])
                denom = hole_data['hole 1'] - pss
                # Coeficientes a, b y c
                cpa = (hole_data['hole 5'] - hole_data['hole 2']) / denom
                cpb = (hole_data['hole 4'] - hole_data['hole 7']) / denom
                cpc = (hole_data['hole 3'] - hole_data['hole 6']) / denom
                # Coeficientes alfa y beta
                cpalfa = cpa + ((cpb - cpc) / denom)
                cpbeta = (cpb + cpc) / (3 ** 0.5)
                zone = 'Zona 1'
            elif max_hole == 'hole 2':
                # Calculo de coeficientes de calibracion para cuando el agujero 2 tiene
                # la mayor presion. Agujeros 4, 5 y 6 en perdida.
                denom = (hole_data['hole 2'] - 0.5 * (hole_data['hole 3'] + hole_data['hole 7']))
                cprad = (hole_data['hole 2'] - hole_data['hole 1']) / denom
                cptan = (hole_data['hole 7'] - hole_data['hole 3']) / denom
                zone = 'Zona 2'
            elif max_hole == 'hole 3':
                # Calculo de coeficientes de calibracion para cuando el agujero 3 tiene
                # la mayor presion. Agujeros 5, 6 y 7 en perdida.
                denom = (hole_data['hole 3'] - 0.5 * (hole_data['hole 2'] + hole_data['hole 4']))
                cprad = (hole_data['hole 3'] - hole_data['hole 1']) / denom
                cptan = (hole_data['hole 2'] - hole_data['hole 4']) / denom
                zone = 'Zona 3'
            elif max_hole == 'hole 4':
                # Calculo de coeficientes de calibracion para cuando el agujero 4 tiene
                # la mayor presion. Agujeros 2, 6 y 7 en perdida.
                denom = (hole_data['hole 4'] - 0.5 * (hole_data['hole 3'] + hole_data['hole 5']))
                cprad = (hole_data['hole 4'] - hole_data['hole 1']) / denom
                cptan = (hole_data['hole 3'] - hole_data['hole 5']) / denom
                zone = 'Zona 4'
            elif max_hole == 'hole 5':
                # Calculo de coeficientes de calibracion para cuando el agujero 5 tiene
                # la mayor presion. Agujeros 2, 3 y 7 en perdida.
                denom = (hole_data['hole 5'] - 0.5 * (hole_data['hole 4'] + hole_data['hole 6']))
                cprad = (hole_data['hole 5'] - hole_data['hole 1']) / denom
                cptan = (hole_data['hole 4'] - hole_data['hole 6']) / denom
                zone = 'Zona 5'
            elif max_hole == 'hole 6':
                # Calculo de coeficientes de calibracion para cuando el agujero 6 tiene
                # la mayor presion. Agujeros 2, 3 y 4 en perdida.
                denom = (hole_data['hole 6'] - 0.5 * (hole_data['hole 5'] + hole_data['hole 7']))
                cprad = (hole_data['hole 6'] - hole_data['hole 1']) / denom
                cptan = (hole_data['hole 5'] - hole_data['hole 7']) / denom
                zone = 'Zona 6'
            elif max_hole == 'hole 7':
                # Calculo de coeficientes de calibracion para cuando el agujero 7 tiene
                # la mayor presion. Agujeros 3, 4 y 5 en perdida.
                denom = (hole_data['hole 7'] - 0.5 * (hole_data['hole 6'] + hole_data['hole 2']))
                cprad = (hole_data['hole 7'] - hole_data['hole 1']) / denom
                cptan = (hole_data['hole 6'] - hole_data['hole 2']) / denom
                zone = 'Zona 7'
            # El paper determina otra nomenclatura para los coeficientes cuando se analiza en forma sectorial.
            # Se toma la direccion radial como alfa y la tangencial como beta. No deberia haber diferencia.
            if cprad:
                cpalfa = cprad
                cpbeta = cptan
            data_coef = [['X', data_uncert[0][1]], ['Y', data_uncert[1][1]], ['Cpalfa', cpalfa],
                          ['Cpbeta', cpbeta], ['Zona maxima presion', zone]]
        else:
            # Bajos angulos de calibracion
            # Calculo de coeficientes.
            pss = mean([hole_data['hole 2'], hole_data['hole 3'], hole_data['hole 4'], hole_data['hole 5'],
                        hole_data['hole 6'], hole_data['hole 7']])
            denom = hole_data['hole 1'] - pss
            # Coeficientes a, b y c
            cpa = (hole_data['hole 5'] - hole_data['hole 2']) / denom
            cpb = (hole_data['hole 4'] - hole_data['hole 7']) / denom
            cpc = (hole_data['hole 3'] - hole_data['hole 6']) / denom
            # Coeficientes alfa y beta
            cpalfa = cpa + ((cpb - cpc) / denom)
            cpbeta = (cpb + cpc) / (3 ** 0.5)
            cpest = (pss - hole_data['pestatic']) / denom
            cptot = (hole_data['hole 1'] - hole_data['ptotal']) / denom
            zone = 'N/A '
            data_coef = [['X', data_uncert[0][1]], ['Y', data_uncert[1][1]], ['Cpalfa', cpalfa],
                          ['Cpbeta', cpbeta], ['Zona maxima presion', zone]]

    # Carga de funciones de interpolacion


    return data_pressure, data_uncert, data_coef