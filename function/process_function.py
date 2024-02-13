from statistics import mean, stdev
import scipy.stats as stats
import math


# Se preprocesan los datos inicialmente y luego se determinan las presiones y las incertidumbres
def data_process(data_csv, vref, nivconf, interpolat, values):
    data_out = {}  # Inicializacion variable de guardado de datos del csv procesado
    # --------------Procesamiento de los datos en bruto--------------
    data = []  # Inicializacion variable de guardado de datos del csv procesado
    data_csv.pop(-1)  # Se elimina ultima fila con el caracter #
    # Determinaciòn tipo de formato
    if data_csv[3][0] == '>T':
        format = 'B'
    else:
        format = 'A'
    # Calculo de presion para diferentes formatos de datos
    if format == 'A':
        for i in range(len(data_csv)):
            data_buffer = []  # Reinicio variable de guardado
            # Procesamiento de los datos de la fila extraida.
            data_csv[i].pop(-1)  # Se elimina el ultimo elemento con el caracter <
            data_csv[i].pop(0)  # Se elimina el primer elemento con el caracter M, V, X o Y
            for j in range(len(data_csv[i])):
                data_buffer.append(float(data_csv[i][j].replace(',', '.')))  # Conversion de string a float.
            data.append(data_buffer)
        # ----------------Procesamiento de las presiones y Posicion----------------
        # Agrego la posicion X e Y a los datos
        data_out.update({'Posicion X': data[0][0], 'Posicion Y': data[1][0]})
        # Calculo de las presiones
        for i in range(1, int(len(data) / 2)):
            # Se utiliza la estrategia de que los valores de las tomas vienen en pares
            # Valor de referencia del sensor analizado.
            numbsenor = int(data[2 * i][0])
            V0 = vref["V{}".format(numbsenor)]  # Extraigo del diccionario el valor de referencia.
            # Calculo las presiones para la toma indicada.
            # Inicializo la variable donde guardo las presiones.
            pressure = []
            for j in range(1, len(data[2])):
                Vout = data[i * 2][j]
                Vs = data[i * 2 + 1][j]
                value = (((Vout - V0) / (Vs * 0.2)) * 1000)
                value = float('%.4f' % value)  # Reduccion a 4 cifras
                pressure.append(value)
            # Guardado de datos en variable de salida y en variable local
            data_out.update({"Presion-Sensor {}".format(numbsenor): pressure})  # Agregado de datos de presiones
    else:
        # Agrego la posicion X e Y a los datos
        data_out.update({'Posicion X': float(data_csv[0][1]), 'Posicion Y': float(data_csv[1][1])})
        data_csv.pop(1)  # Se elimina la segunda fila con dato de la posicion Y
        data_csv.pop(0)  # Se elimina la primera fila con dato de la posicion X
        # Determinacion de los numero de sensores usados
        header = []
        for i in range(3, len(data_csv[0]) - 1):
            header.append(int(data_csv[0][i].replace("toma_", "")))
        data_csv.pop(0)  # Se elimina el encabezado
        # Calculo del tiempo en segundos
        buffer_data = []
        for i in range(len(data_csv)):
            time_value = float(data_csv[i][1])
            buffer_data.append(round(time_value * 1e-6, 4))
        data_out.update({"Tiempo medicion": buffer_data})  # Agregado de datos de presiones
        del (time_value)
        # Basado en la estructura de datos a procesar se obtiene la presion de cada sensor con numero respectivo
        count = 0  # Contador utilizado para determinar numero de sensor
        for i in range(3, len(data_csv[0]) - 1):
            # Valor de referencia del sensor analizado.
            numbsenor = header[count]
            V0 = vref["V{}".format(numbsenor)]  # Extraigo del diccionario el valor de referencia.
            # Se suma el contador ya que se definio el "numbsenor"
            count += 1
            # Calculo las presiones para el sensor indicado.
            # Inicializo la variable donde guardo las presiones.
            pressure = []
            for j in range(len(data_csv)):
                Vout = float(data_csv[j][i].replace(',', '.'))
                Vs = float(data_csv[j][2].replace(',', '.'))
                value = (((Vout - V0) / (Vs * 0.2)) * 1000) * (1)  # PRESION MODIFICADA <<<--------
                value = float('%.4f' % value)  # Reduccion a 4 cifras
                pressure.append(value)
            # Guardado de datos en variable de salida y en variable local
            data_out.update({"Presion-Sensor {}".format(numbsenor): pressure})  # Agregado de datos de presiones
    # --------------Calculo de la incertidumbre--------------
    # Se determina el numero de tomas de los keys del diccionario "data_out"
    pressure_list = [k for k in list(data_out.keys()) if 'Presion-Sensor' in k]
    crit = 10  # Criterio de contribucion dominante. Se eligio 10 veces superior.
    for i in pressure_list:
        # Extraigo datos numericos.
        data_raw = data_out[i]
        # Numero de toma. Se obtiene del key del diccionario
        numb_probe = i.replace('Presion-Sensor ','')
        # Calculo de incertidumbre.
        # Numero de muestras.
        sample = len(data_raw)
        data_out.update({"Muestras-{}".format(numb_probe): sample})
        # Estimado de la medicion
        averange = mean(data_raw)
        data_out.update({"Promedio-{}".format(numb_probe):averange})
        if sample > 1:
            # Desviación típica experimental.
            typea = stdev(data_raw) / (sample ** 0.5)
            data_out.update({"TipoA-{}".format(numb_probe): typea})
            # Componente Tipo B debido a la calibración del sensor de presion.
            typeb = averange * 0.015 / (3 ** 0.5)
            data_out.update({"TipobB-presion-{}".format(numb_probe): typeb})
            # Incertidumbre combinada.
            ucomb = (typea ** 2 + typeb ** 2) ** 0.5
            data_out.update({"Incertidumbre Combinada-{}".format(numb_probe): ucomb})
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
                # Guardado datos
                data_out.update({"Coeficiente-expansion-{})".format(numb_probe): k})
                data_out.update({"Tipo-distribucion-{}".format(numb_probe): distrib})
            elif typea / typeb < 1 / crit:
                k = (3 ** 0.5) * nivconf  # Distribucion rectangular k=raiz(3)*p
                distrib = 'Rectangular'
                # Guardado datos
                data_out.update({"Coeficiente-expansion-{})".format(numb_probe): k})
                data_out.update({"Tipo-distribucion-{}".format(numb_probe): distrib})
            else:
                k = stats.norm.ppf((1 + nivconf) / 2)  # Cumple teorema limite central. Distribución Normal.
                distrib = 'Normal TCLimite'
                # Guardado datos
                data_out.update({"Coeficiente-expansion-{})".format(numb_probe): k})
                data_out.update({"Tipo-distribucion-{}".format(numb_probe): distrib})
            # Incertidumbre expandida
            uexpand = k * ucomb
            data_out.update({"Uexpandida ({}%)-{}".format(nivconf * 100, numb_probe): uexpand})

            # Reduccion de cifras. OMITIDO POR AHORA
            # averange = float('%.2f' % averange)
            # uexpand = float('%.4f' % uexpand)
            # k = float('%.4f' % k)
        else:
            # En mediciones de un solo valor no es posible calcular la incertidumbre. Se aplica N/A a todos los datos
            data_out.update({"Tipo A-{}".format(numb_probe): 'N/A'})
            data_out.update({"Tipo B-presion-{}".format(numb_probe): 'N/A'})
            data_out.update({"Incertidumbre Combinada-{}".format(numb_probe): 'N/A'})
            data_out.update({"Coeficiente-expansion-{})".format(numb_probe): 'N/A'})
            data_out.update({"Tipo-distribucion-{}".format(numb_probe): 'N/A'})
            data_out.update({"Uexpandida ({}%)-{}".format(nivconf * 100, numb_probe): 'N/A'})

    # --------------Calculo de los coeficientes del traverser--------------
    # Informacion sobre el tipo de sonda
    probe_type = values['-TYPEPROBE-']
    # Lista con el numero de toma asignado para cada agujero generado por el usuario.
    relat_hole_tap = [values['-NUM1-'], values['-NUM2-'], values['-NUM3-'], values['-NUM4-'], values['-NUM5-'],
                      values['-NUM6-'], values['-NUM7-']]
    relat_hole_tap = [x for x in relat_hole_tap if x != '']  # Elimino los valores vacios o agujeros no validos.

    # Calculo de los coeficientes del traverser para una sonda de 2 agujeros y parametros de flujo
    if probe_type == '2 agujeros':
        # Se relaciona el valor de la toma de presion respecto al agujero definido. Agujero: Toma.
        hole_data = {'hole 1': data_out["Promedio-{}".format(relat_hole_tap[0])],
                     'hole 2': data_out["Promedio-{}".format(relat_hole_tap[1])]}
        data_out.update(hole_data)  # Agregado de valores de presion de cada agujero
        # --------- Calculo de coeficientes ---------
        q = 7.35  # DEBE INGRESARSE MANUALMENTE. A IMPLEMENTAR
        cpangle = (hole_data['hole 2'] - hole_data['hole 1']) / q
        # --------- Interpolacion de parametros de Flujo ---------
        try:
            angle = round(float(interpolat["Angulo-Interp"](cpangle)), 1)
        except Exception as e:
            print(e)
            angle = 0  # Ante error deja valor nulo
        # --------- Guardado de datos ---------
        data_out.update({"Cpangulo": cpangle, "Angulo": angle})



    # Calculo de los coeficientes del traverser para una sonda de 3 agujeros.
    if probe_type == '3 agujeros':
        # Se relaciona el valor de la toma de presion respecto al agujero definido. Agujero: Toma.
        hole_data = {'hole 1': data_out["Promedio-{}".format(relat_hole_tap[0])],
                     'hole 2': data_out["Promedio-{}".format(relat_hole_tap[1])],
                     'hole 3': data_out["Promedio-{}".format(relat_hole_tap[2])]}
        data_out.update(hole_data)  # Agregado de valores de presion de cada agujero
        # Calculo de coeficientes
        pss = mean([hole_data['hole 2'], hole_data['hole 3']])
        cpangle = (hole_data['hole 3'] - hole_data['hole 2']) / (hole_data['hole 1'] - pss)
        # --------- Interpolacion de parametros de Flujo ---------
        try:
            angle = round(float(interpolat["Angulo-Interp"](cpangle)), 1)
            cpest = round(float(interpolat["Cpestatico-Interp"](cpangle)), 4)
            cptot = round(float(interpolat["Cptotal-Interp"](cpangle)), 4)
        except Exception as e:
            print(e)
            angle = 0  # Ante error deja valor nulo
            cpest = 0  # Ante error deja valor nulo
            cptot = 0  # Ante error deja valor nulo
        # --------- Calculo de coeficientes ---------
        pest = pss - (hole_data['hole 1'] - pss) * cpest
        ptot = hole_data['hole 1'] - (hole_data['hole 1'] - pss) * cptot
        density = float(values["-DENSITY_VALUE-"])  # Unidades en SI
        V = ((2 / density) * (hole_data['hole 1'] - pss) * (1 + cpest - cptot)) ** 0.5
        Vx = (V * math.cos(angle * math.pi / 180))
        Vy = V * math.sin(angle * math.pi / 180)
        data_out.update({'Angulo': angle, "Cpangulo": cpangle, "Cpestatico": cpest, "Cptotal": cptot,
                         'Presion estatica': pest, 'Presion total': ptot, 'Velocidad': V, 'Vx': Vx, 'Vy': Vy})

    # Calculo de los coeficientes del traverser para una sonda de 5 agujeros.
    if probe_type == '5 agujeros':
        # Se relaciona el valor de la toma de presion respecto al agujero definido. Agujero: Toma.
        hole_data = {'hole 1': data_out["Promedio-{}".format(relat_hole_tap[0])],
                     'hole 2': data_out["Promedio-{}".format(relat_hole_tap[1])],
                     'hole 3': data_out["Promedio-{}".format(relat_hole_tap[2])],
                     'hole 4': data_out["Promedio-{}".format(relat_hole_tap[3])],
                     'hole 5': data_out["Promedio-{}".format(relat_hole_tap[4])]}
        data_out.update(hole_data)  # Agregado de valores de presion de cada agujero
        # Determinacion del agujero con la maxima presion. Se usa para analisis de grandes angulos de flujo.
        max_hole = max(hole_data, key=hole_data.get)
        # Analisis discriminado para grande y bajos angulos de calibracion
        if values['-MULTIZONE-'] == 'Utilizado':
            # Grandes angulos de flujo
            if max_hole == 'hole 1':
                # Calculo de coeficientes de calibracion para cuando el agujero 1 tiene la mayor presion. Bajos angulos
                pss = mean([hole_data['hole 2'], hole_data['hole 3'], hole_data['hole 4'], hole_data['hole 5']])
                denom = hole_data['hole 1'] - pss
                cpalpha = (hole_data['hole 4'] - hole_data['hole 2']) / denom
                cpbeta = (hole_data['hole 5'] - hole_data['hole 3']) / denom
                zone = 'Zona 1'
                # Guardado de coeficientes
                data_out.update({"Cpalfa": cpalpha, "Cpbeta": cpbeta, "Zonamax": zone})
            elif max_hole == 'hole 2':
                # Calculo de coeficientes de calibracion para cuando el agujero 2 tiene
                # la mayor presion. Agujero 4 en perdida.
                pss = mean([hole_data['hole 1'], hole_data['hole 3'], hole_data['hole 5']])
                denom = hole_data['hole 2'] - pss
                cpalpha = (hole_data['hole 1'] - hole_data['hole 2']) / denom
                cpbeta = (hole_data['hole 5'] - hole_data['hole 3']) / denom
                zone = 'Zona 2'
                # Guardado de coeficientes
                data_out.update({"Cpalfa": cpalpha, "Cpbeta": cpbeta, "Zonamax": zone})
            elif max_hole == 'hole 3':
                # Calculo de coeficientes de calibracion para cuando el agujero 3 tiene
                # la mayor presion. Agujero 5 en perdida.
                pss = mean([hole_data['hole 1'], hole_data['hole 2'], hole_data['hole 4']])
                denom = hole_data['hole 3'] - pss
                cpalpha = (hole_data['hole 4'] - hole_data['hole 2']) / denom
                cpbeta = (hole_data['hole 1'] - hole_data['hole 3']) / denom
                zone = 'Zona 3'
                # Guardado de coeficientes
                data_out.update({"Cpalfa": cpalpha, "Cpbeta": cpbeta, "Zonamax": zone})
            elif max_hole == 'hole 4':
                # Calculo de coeficientes de calibracion para cuando el agujero 4 tiene
                # la mayor presion. Agujero 2 en perdida.
                pss = mean([hole_data['hole 1'], hole_data['hole 3'], hole_data['hole 5']])
                denom = hole_data['hole 4'] - pss
                cpalpha = (hole_data['hole 4'] - hole_data['hole 1']) / denom
                cpbeta = (hole_data['hole 5'] - hole_data['hole 3']) / denom
                zone = 'Zona 4'
                # Guardado de coeficientes
                data_out.update({"Cpalfa": cpalpha, "Cpbeta": cpbeta, "Zonamax": zone})
            elif max_hole == 'hole 5':
                # Calculo de coeficientes de calibracion para cuando el agujero 5 tiene
                # la mayor presion. Agujero 3 en perdida.
                pss = mean([hole_data['hole 1'], hole_data['hole 2'], hole_data['hole 4']])
                denom = hole_data['hole 5'] - pss
                cpalpha = (hole_data['hole 4'] - hole_data['hole 2']) / denom
                cpbeta = (hole_data['hole 5'] - hole_data['hole 1']) / denom
                zone = 'Zona 5'
                # Guardado de coeficientes
                data_out.update({"Cpalfa": cpalpha, "Cpbeta": cpbeta, "Zonamax": zone})
        else:
            # Bajos angulos de calibracion
            # Calculo de coeficientes.
            pss = mean([hole_data['hole 2'], hole_data['hole 3'], hole_data['hole 4'], hole_data['hole 5']])
            denom = hole_data['hole 1'] - pss
            cpalpha = (hole_data['hole 4'] - hole_data['hole 2']) / denom
            cpbeta = (hole_data['hole 5'] - hole_data['hole 3']) / denom
            zone = 'N/A '
            data_out.update({"Cpalfa": cpalpha, "Cpbeta": cpbeta, "Zonamax": zone})

        # --------- Interpolacion de parametros de Flujo ---------
        try:
            alpha = round(float(interpolat["Alfa-Interp"](cpalpha, cpbeta)[0]), 1)
            beta = round(float(interpolat['Beta-Interp'](cpalpha, cpbeta)[0]), 1)
            cpest = round(float(interpolat["Cpestatico-Interp"](cpalpha, cpbeta)[0]), 4)
            cptot = round(float(interpolat["Cptotal-Interp"](cpalpha, cpbeta)[0]), 4)
        except Exception as e:
            print(e)
            alpha = 0  # Ante error deja valor nulo
            beta = 0  # Ante error deja valor nulo
            cpest = 0  # Ante error deja valor nulo
            cptot = 0  # Ante error deja valor nulo
        # --------- Calculo de coeficientes ---------
        # Si se analiza multizona las ecuaciones cambian. La P1 y PSS cambia dependiendo de max_hole.
        if values['-MULTIZONE-'] == 'Utilizado':
            if max_hole == 'hole 1':
                Pi = hole_data["hole 1"]
                pss = mean([hole_data['hole 2'], hole_data['hole 3'], hole_data['hole 4'], hole_data['hole 5']])
            elif max_hole == 'hole 2':
                Pi = hole_data["hole 2"]
                pss = mean([hole_data['hole 1'], hole_data['hole 3'], hole_data['hole 5']])
            elif max_hole == 'hole 3':
                Pi = hole_data["hole 3"]
                pss = mean([hole_data['hole 1'], hole_data['hole 2'], hole_data['hole 4']])
            elif max_hole == 'hole 4':
                Pi = hole_data["hole 4"]
                pss = mean([hole_data['hole 1'], hole_data['hole 3'], hole_data['hole 5']])
            elif max_hole == 'hole 5':
                Pi = hole_data["hole 5"]
                pss = mean([hole_data['hole 1'], hole_data['hole 2'], hole_data['hole 4']])
        else:
            Pi = hole_data["hole 1"]
            pss = mean([hole_data['hole 2'], hole_data['hole 3'], hole_data['hole 4'], hole_data['hole 5']])

        pest = pss - (Pi - pss) * cpest
        ptot = Pi - (Pi - pss) * cptot
        density = float(values["-DENSITY_VALUE-"])  # Unidades en SI
        V = ((2 / density) * (Pi - pss) * (1 + cpest - cptot)) ** 0.5
        Vx = (V * math.cos(alpha * math.pi / 180)) * math.cos(beta * math.pi / 180)
        Vy = V * math.sin(alpha * math.pi / 180)
        Vz = (V * math.cos(alpha * math.pi / 180)) * math.sin(beta * math.pi / 180)
        # --------- Guardado de coeficientes ---------
        data_out.update({'Alfa': alpha, 'Beta': beta, "Cpestatico": cpest, "Cptotal": cptot,
                         'Presion estatica': pest, 'Presion total': ptot, 'Velocidad': V,
             'Vx': Vx, 'Vy': Vy, 'Vz': Vz})

    # Calculo de los coeficientes de calibracion para una sonda de 7 agujeros. REFORMAR EL CALCULO
    if probe_type == '7 agujeros':
        # Se relaciona el valor de la toma de presion respecto al agujero definido. Agujero: Toma.
        hole_data = {'hole 1': data_out["Promedio-{}".format(relat_hole_tap[0])],
                     'hole 2': data_out["Promedio-{}".format(relat_hole_tap[1])],
                     'hole 3': data_out["Promedio-{}".format(relat_hole_tap[2])],
                     'hole 4': data_out["Promedio-{}".format(relat_hole_tap[3])],
                     'hole 5': data_out["Promedio-{}".format(relat_hole_tap[4])],
                     'hole 6': data_out["Promedio-{}".format(relat_hole_tap[5])],
                     'hole 7': data_out["Promedio-{}".format(relat_hole_tap[6])]}
        data_out.update(hole_data)  # Agregado de valores de presion de cada agujero
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
                cpb = (hole_data['hole 7'] - hole_data['hole 4']) / denom
                cpc = (hole_data['hole 6'] - hole_data['hole 3']) / denom
                # Coeficientes alfa y beta
                cpalpha = cpa + ((cpb - cpc) / 2)
                cpbeta = (cpb + cpc) / (3 ** 0.5)
                zone = 'Zona 1'
                # Guardado de coeficientes
                data_out.update({"Cpa": cpa, "Cpb": cpb, "Cpc": cpc, "Cpalfa": cpalpha, "Cpbeta": cpbeta,
                                 "Zonamax": zone})
            elif max_hole == 'hole 2':
                # Calculo de coeficientes de calibracion para cuando el agujero 2 tiene
                # la mayor presion. Agujeros 4, 5 y 6 en perdida.
                denom = (hole_data['hole 2'] - 0.5 * (hole_data['hole 3'] + hole_data['hole 7']))
                cprad = (hole_data['hole 2'] - hole_data['hole 1']) / denom
                cptan = (hole_data['hole 7'] - hole_data['hole 3']) / denom
                zone = 'Zona 2'
                # Guardado de coeficientes
                data_out.update({"Cpalfa": cprad, "Cpbeta": cptan, "Zonamax": zone})
            elif max_hole == 'hole 3':
                # Calculo de coeficientes de calibracion para cuando el agujero 3 tiene
                # la mayor presion. Agujeros 5, 6 y 7 en perdida.
                denom = (hole_data['hole 3'] - 0.5 * (hole_data['hole 2'] + hole_data['hole 4']))
                cprad = (hole_data['hole 3'] - hole_data['hole 1']) / denom
                cptan = (hole_data['hole 2'] - hole_data['hole 4']) / denom
                zone = 'Zona 3'
                # Guardado de coeficientes
                data_out.update({"Cpalfa": cprad, "Cpbeta": cptan, "Zonamax": zone})
            elif max_hole == 'hole 4':
                # Calculo de coeficientes de calibracion para cuando el agujero 4 tiene
                # la mayor presion. Agujeros 2, 6 y 7 en perdida.
                denom = (hole_data['hole 4'] - 0.5 * (hole_data['hole 3'] + hole_data['hole 5']))
                cprad = (hole_data['hole 4'] - hole_data['hole 1']) / denom
                cptan = (hole_data['hole 3'] - hole_data['hole 5']) / denom
                zone = 'Zona 4'
                # Guardado de coeficientes
                data_out.update({"Cpalfa": cprad, "Cpbeta": cptan, "Zonamax": zone})
            elif max_hole == 'hole 5':
                # Calculo de coeficientes de calibracion para cuando el agujero 5 tiene
                # la mayor presion. Agujeros 2, 3 y 7 en perdida.
                denom = (hole_data['hole 5'] - 0.5 * (hole_data['hole 4'] + hole_data['hole 6']))
                cprad = (hole_data['hole 5'] - hole_data['hole 1']) / denom
                cptan = (hole_data['hole 4'] - hole_data['hole 6']) / denom
                zone = 'Zona 5'
                # Guardado de coeficientes
                data_out.update({"Cpalfa": cprad, "Cpbeta": cptan, "Zonamax": zone})
            elif max_hole == 'hole 6':
                # Calculo de coeficientes de calibracion para cuando el agujero 6 tiene
                # la mayor presion. Agujeros 2, 3 y 4 en perdida.
                denom = (hole_data['hole 6'] - 0.5 * (hole_data['hole 5'] + hole_data['hole 7']))
                cprad = (hole_data['hole 6'] - hole_data['hole 1']) / denom
                cptan = (hole_data['hole 5'] - hole_data['hole 7']) / denom
                zone = 'Zona 6'
                # Guardado de coeficientes
                data_out.update({"Cpalfa": cprad, "Cpbeta": cptan, "Zonamax": zone})
            elif max_hole == 'hole 7':
                # Calculo de coeficientes de calibracion para cuando el agujero 7 tiene
                # la mayor presion. Agujeros 3, 4 y 5 en perdida.
                denom = (hole_data['hole 7'] - 0.5 * (hole_data['hole 6'] + hole_data['hole 2']))
                cprad = (hole_data['hole 7'] - hole_data['hole 1']) / denom
                cptan = (hole_data['hole 6'] - hole_data['hole 2']) / denom
                zone = 'Zona 7'
                # Guardado de coeficientes
                data_out.update({"Cpalfa": cprad, "Cpbeta": cptan, "Zonamax": zone})
            # El paper determina otra nomenclatura para los coeficientes cuando se analiza en forma sectorial.
            # Se toma la direccion radial como alfa y la tangencial como beta. No deberia haber diferencia.
            if cprad:
                cpalpha = cprad
                cpbeta = cptan
        else:
            # Bajos angulos de calibracion
            # Calculo de coeficientes.
            pss = mean([hole_data['hole 2'], hole_data['hole 3'], hole_data['hole 4'], hole_data['hole 5'],
                        hole_data['hole 6'], hole_data['hole 7']])
            denom = hole_data['hole 1'] - pss
            # Coeficientes a, b y c
            cpa = (hole_data['hole 5'] - hole_data['hole 2']) / denom
            cpb = (hole_data['hole 7'] - hole_data['hole 4']) / denom
            cpc = (hole_data['hole 6'] - hole_data['hole 3']) / denom
            # Coeficientes alfa y beta
            cpalpha = cpa + ((cpb - cpc) / 2)
            cpbeta = (cpb + cpc) / (3 ** 0.5)
            zone = 'N/A '
            data_out.update(
                {"Cpa": cpa, "Cpb": cpb, "Cpc": cpc, "Cpalfa": cpalpha, "Cpbeta": cpbeta, "Zonamax": zone})

    return data_out

