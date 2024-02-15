class ExamException(Exception):
    pass


class CSVTimeSeriesFile:

    def __init__(self, name):
        self.nome_file = name
        try:  # Provo ad aprire il file e a leggere una riga
            self.file_aperto = open(self.nome_file, 'r')
            self.file_aperto.readline()
        except:  # Se non si può aprire il file
            raise ExamException('Non è possibile aprire "{}"'.format(self.nome_file))

    def get_data(self):
        lista_valori = []
        tutte_le_date = []  # Lista con date per controllare se ci sono doppie
        for line in self.file_aperto:
            line = line.strip() # Pulisco
            try:
                elementi_riga = line.split(',') # Divido riga in [data, passeggeri]
                elementi_riga[1]  # Verifico che ci sia almeno un secondo elemento
            except:
                continue  # Ignoro la riga, il for riparte subito con quella dopo

            mese = -1 # Valori di default (verranno modificati)
            anno = -1
            passeggeri = -1.0  # (float altrimenti is_integer dà errore)
            
# CHECK DATA, PASSEGGERI
            
            if elementi_riga[0] != 'date':  # Se NON sto leggendo intestazione
                data = elementi_riga[0]
                valutabile = True  # (Default) flag: una riga è idonea a essere valutata
                
# Formato data
                try:  # Verifico se la data è valida ("ANNO-MESE" dove entrambi sono numeri)
                    anno_e_mese = data.split('-')  # Divido data in [anno, mese]
                    anno = anno_e_mese[0]  # Estraggo l'anno (str) da [anno, mese]
                    anno = float(anno)
                    mese = anno_e_mese[1]  # Estraggo il mese (str) da [anno, mese]
                    mese = float(mese)
                except:  # Data non valida: ignoro la riga
                    valutabile = False
                    
# Anno intero
                if valutabile is True and float(anno).is_integer() is False:
                    # L'anno non è intero
                    valutabile = False
                elif valutabile is True: # L'anno è intero
                    anno = int(anno)

# Mese intero
                if valutabile is True and float(mese).is_integer() is False:
                    # Il mese non è intero
                    valutabile = False
                elif valutabile is True: # Il mese è intero
                    mese = int(mese)
                    
# Mese tra 1 e 12
                if valutabile is True and int(mese) not in range(1, 13): # (13 escluso)
                    valutabile = False
                    
# Anno positivo
                if valutabile is True and int(anno) < 0:
                    valutabile = False
                    
# Pass. è numero
                try:  # Se valore passeggeri è convertibile a float
                    passeggeri = float(elementi_riga[1])
                except:
                    valutabile = False
                    
# Pass. positivo non nullo
                if valutabile is True and passeggeri <= 0:
                    valutabile = False
                    
# Pass. intero
                if valutabile is True and passeggeri.is_integer() is False:
                    # Passeggeri frazionati
                    valutabile = False
                    
# Valuto la riga
                if valutabile is True: # Riga valutabile
                    lista_valori.append(['{}-{}'.format(anno, mese),int(passeggeri)])
                    if data in tutte_le_date:  # La data è già presente, quindi è doppia
                        raise ExamException('La data {} è doppia'.format(data))
                    else:  # La data è unica (non doppia)
                        tutte_le_date.append(data)

                else: # Se la riga non è valutabile
                    pass # Non faccio nulla; il for riparte con la riga successiva

# Date in ordine
        for (i, elem) in enumerate(tutte_le_date):  # Controllo date fuori ordine
            if i == 0:  # Parto dal secondo elemento
                pass
            else:
                elem_prec = tutte_le_date[i-1]
                elem = elem.split('-') # elem = [anno, mese]
                elem_prec = elem_prec.split('-')
                if elem[0] == elem_prec[0] and elem[1] < elem_prec[1]: # No ordine mesi
                    raise ExamException('I mesi {} e {} dell anno {} non sono in ordine'
                                        .format(elem[1], elem_prec[1], elem[0]))
                if elem[0] < elem_prec[0]: # No ordine anni
                    raise ExamException('Gli anni {} e {} non sono in ordine'
                                        .format(elem[0], elem_prec[0]))

        return lista_valori


def compute_increments(time_series, first_year, last_year):
    if len(time_series) == 0:  # La lista di valori validi è vuota
        raise ExamException('Il file sorgente è vuoto o non contiene valori validi')
        
# CHECK VALORI first e last year
    
# Formato first
    try:  # Controllo se first_year è un numero
        first_year = float(first_year)
    except:
        raise ExamException('L estremo inferiore {} non è un numero'.format(first_year))
        
# Formato last
    try:  # Controllo se last_year è un numero
        last_year = float(last_year)
    except:
        raise ExamException('L estremo superiore {} non è un numero'.format(last_year))
        
# First intero
    if first_year.is_integer() is False:
        raise ExamException('L estremo inferiore {} non è intero'.format(first_year))
    else:
        first_year = int(first_year)
        
# Last intero
    if last_year.is_integer() is False:
        raise ExamException('L estremo superiore {} non è intero'.format(last_year))
    else:
        last_year = int(last_year)

# Smonto time_series e creo lista di anni e di passeggeri
    lista_anni = []
    lista_passeggeri = []
    for element in time_series: # Scorro ogni [data, pass] di time_series
        anno_e_mese = element[0].split('-') # Divido str "data" in [anno, mese]
        anno = int(anno_e_mese[0])
        passeggeri = element[1]

        lista_anni.append(anno) # Lista [anno1, anno2, anno3, ...]
        lista_passeggeri.append(passeggeri) # Lista [pass_anno1, pass_anno2, pass_anno3, ...]

    anno_min = min(lista_anni)
    anno_max = max(lista_anni)

# CHECK SENSO first e last year
    
    if first_year > last_year: # Ordine estremi sbagliato: li inverto
        tmp = first_year
        first_year = last_year
        last_year = tmp
    if first_year == last_year: # Lunghezza intervallo insufficiente
        raise ExamException('L intervallo inserito comprende un solo anno')

    if first_year < anno_min: # Primo anno troppo piccolo
        raise ExamException('Il primo anno inserito è minore all anno minimo')
    if last_year > anno_max: # Ultimo anno troppo grande
        raise ExamException('L ultimo anno inserito è maggiore dell anno massimo')

# Dizionario dei valori medi

    anni_vuoti = []  # Lista che conterrà gli anni senza valori
    dict_val_medi = {}
    anno_corrente = anno_min # Parto dal primo anno in cui ho valori
    conta = 0  # Indice della lista
    while anno_corrente <= anno_max: # Scorro tutti gli anni dal min al max
        somma_per_anno = 0
        nr_per_anno = 0
        while lista_anni[conta] == anno_corrente: #Finchè ho valori dell'anno corrente
            somma_per_anno += lista_passeggeri[conta]
            nr_per_anno += 1  # Nr valori di quest'anno
            conta += 1
            if conta == len(lista_anni): # L'indice n non esiste: l'ultimo è n-1
                break  # Altrimenti indice fuori range, errore while
        try:
            val_medio = somma_per_anno / nr_per_anno
            dict_val_medi[anno_corrente] = val_medio
        except ZeroDivisionError: # Se per un anno non ci sono valori
            anni_vuoti.append(anno_corrente)
        anno_corrente += 1 # Valuto l'anno successivo

# Dizionario delle differenze (finale)

    calcolabile = True # Flag per capire se ci sono ancora anni nell'intervallo
    dict_differenze = {}
    for i in range(first_year, last_year):
        if i not in anni_vuoti:  # Se l'anno di partenza ha dei valori (se no i++ nel for)
            b = i + 1  # Estremo superiore dell'intervallo dei due anni
            while b in anni_vuoti:
                b += 1 # Se l'estremo sup non ha valori, lo aumento di +1
                if b > last_year: # Se supero l'intervallo considerato
                    calcolabile = False
                    break 
            if calcolabile is False:
                break
            dicitura = '{}-{}'.format(i, b) # str 'ANNO1-ANNO2'
            diff = dict_val_medi[b] - dict_val_medi[i]
            dict_differenze[dicitura] = diff # Compilo per l'anno corrente

    return dict_differenze
    