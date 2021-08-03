from socket import *
from threading import *
from random import choice
import threading
import random
import sys

# costanti
PORTA = 53000
BUFSIZE = 4096
HOST = '127.0.0.1' # prima era ''
FORMAT = 'utf-8' # prima era 'utf8'

# utente

risultati = [] # risultati finali

results = {} # {dizionario} socket : punteggio_finale

indirizzi = {} # indirizzi[utente] = addr

clienti = {} # clienti[utente] = nome

threads = []

# liste per la formazione della leaderboard (classifica)
numero_risposte_giocatori = []
users_leaderboard = []

# condition variables per la coordinazione delle threads
cond = threading.Condition()

cond_leaderboard = threading.Condition()

# Server
global SERVER # HOST, PORTA
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind((HOST, PORTA))

# Ruoli
male_roles = ["Mago", "Stregone", "Apprendista Stregone", "Guerriero", "Evocatore", "Arciere", "Balestriere",
"Re", "Principe","Cavaliere"]
female_roles = ["Maga", "Strega", "Apprendista Stregone", "Guerriera", "Evocatrice", "Arciere", "Balestriere",
"Regina", "Principessa","Cavaliera", "Dama"]

# dizionario con le domande e le possibili risposte
domande = {
    "Quale protocollo controlla i pacchetti inviati?\n" : ["TCP", "UDP"],
    "Quale protocollo invia pacchetti senza controllo?\n" : ["UDP", "TCP"]
    #"Nel 3-Way Handshake, cosa risponde il server al client?\n" : ["ACK", "SYN ACK"],
    #"Nel 3-Way Handshake, cosa invia il client per stabilire una connessione?\n" : ["SYN", "ACK"],
    #"Nel 3-Way Handshake, cosa invia infine il client in risposta al server?\n" : ["SYN", "ACK"]
}

domande_errate = [
    "Domanda errata0\n","Domanda errata1\n", "Domanda errata2\n", "Domanda errata3\n" #, "Domanda errata4\n"
]

# Questa funzione sceglie un ruolo maschile o femminile in base al nome passato come parametro.
def pick_role(nome):
    ruolo = ""
    print("nome[-1]: " + nome[-1])
    # metto il .lower perchè così anche se il nome viene scritto in maiuscolo, comunque lo controllo
    if(str(nome[-1]).lower() == 'a' and not(str(nome).lower() == "luca") and not(str(nome).lower() == "andrea")): #and not nome == "luca" or not nome == "andrea"): # l'indice -1 ti fa ottenere l'ultimo carattere della stringa
        print("Female role")
        ruolo = choice(list(female_roles))
    elif(str(nome[-1]).lower() == 'o'):
        print("Male role")
        ruolo = choice(list(male_roles))
    else:
        ruolo = choice(list(male_roles))
    print("ruolo: " + ruolo)
    return ruolo

# Questa funzione serve per selezionare 3 domande, di cui 1 trabocchetto, e di inviarle all'utente.
def pick_questions(cliente_connection):
    domanda1 = choice(list(domande.keys())) # choice server per scegliere una domanda casuale dal dizionario domande
    domanda2 = choice(list(domande.keys()))
    while(domanda1 == domanda2):
        domanda2 = choice(list(domande.keys()))
    domanda3 = choice(list(domande_errate))

    questions = []
    questions.append(domanda1)
    questions.append(domanda2) 
    questions.append(domanda3)
    print("questions prima dello shuffle: " , questions)
    random.shuffle(questions) # shuffle serve per mischiare l'ordine delle domande.
    print("questions dopo lo shuffle: " , questions)
    domande_da_inviare = questions[0] + questions[1] + questions[2]
    cliente_connection.send(domande_da_inviare.encode(FORMAT))
    return evaluate_question(cliente_connection)

# Si occupa di valutare la domanda scelta dall'utente, se è corretta o errata.
def evaluate_question(utente_connection):
    evaluate = utente_connection.recv(BUFSIZE).decode(FORMAT) # domanda scelta dall'utente
    print("evaluate: " + str(evaluate))
    print("domande: " + str(domande.keys()))
    print("evaluate in domande.keys(): " + str(evaluate in domande.keys()))
    if evaluate in domande_errate: # se la domanda scelta si trova nella lista domande_errate allora elimino il giocatore.
        print("Domanda errata!")
        utente_connection.send("Domanda errata".encode(FORMAT))
        return False
    elif(evaluate in domande.keys()): # se la domande scelta dall'utente si trova nel dizionario domande allora proseguo col gioco.
        print("Domanda corretta!")
        utente_connection.send("Domanda corretta".encode(FORMAT))
        return evaluate
    else:
        print("Nè domanda corretta nè domanda errata!")
        return evaluate

# Si occupa di inviare all'utente le possibili risposte alla domanda da lui/lei scelta.
def send_question(client):#, quesito_scelto):
    # resetto le variabili a stringhe vuote.
    domanda_da_inviare = ""
    risposta1 = ""
    risposta2 = ""
    quesito_scelto = pick_questions(client)
    print("quesito_scelto: " + str(quesito_scelto))
    if(quesito_scelto == False):
        print("Domanda errata!")
        return False 
    elif(quesito_scelto == "Stop"):
        return quesito_scelto # "Stop"
    elif(quesito_scelto == "QUIT"):
        return False
    else:
        print("Domanda corretta!")
        print("Proseguendo con la domanda e le possibili risposte da inviare..")

    # aggiungo "Domanda: " alla stringa con la domanda, perchè così il client capisce che è una domanda.
    domanda_da_inviare = "Domanda: " + quesito_scelto
    print("send_question(), domanda_da_inviare: " + domanda_da_inviare)

    # metto le due possibili risposte in delle variabili.
    possibile_risposta = domande[quesito_scelto]
    risposta1 = "Risposta1: " + possibile_risposta[0] + "\n"
    risposta2 = "Risposta2: " + possibile_risposta[1] + "\n"

    print("send_question(), risposta1: " + risposta1)
    print("send_question(), risposta2: " + risposta2)

    # metto assieme la domanda e le possibili risposte e le invio all'utente.
    messaggio = domanda_da_inviare + risposta1 + risposta2
    print("messaggio: " + messaggio)
    client.send(messaggio.encode(FORMAT))

# Funzione principale che si occupa di inviare all'utente domande
def gestisci_utente(utente_connection):
    has_sent_question = send_question(utente_connection)
    if has_sent_question == False:
        print("Domanda errata eliminazione del player..")
        close_connection(utente_connection)
    elif has_sent_question == "Stop":
        msg = "Stop"
    else:
        msg = utente_connection.recv(BUFSIZE).decode(FORMAT)
    if(str(msg).startswith("Ricevuto")): # continuo ad inviare altre domande.
        gestisci_utente(utente_connection)
    elif(str(msg).startswith("Stop")): # smetto di inviare domande e passo al conteggio dei risultati.
        print("Tempo di gioco finito!!!")
        print("Assegnamento vincitori in base al loro punteggio")

        evaluate_winner(utente_connection)
        print("threads: " + str(threads))

        send_leaderboard(utente_connection) # questo o lo metto qui o dentro game_over
        game_over(utente_connection)

# Questa funzione controlla se i giocatori sono ancora online o sono usciti e restarta il gioco.
def game_over(utente_connection):

    print("threads prima check_client: " + str(threads))
    check_client(utente_connection)
    
    print("threads dopo check_client: " + str(threads))
    reset(utente_connection)

# Questa funzione riceve i punteggi dai giocatori e decreta il vincitore/perdente o il pareggio.
def evaluate_winner(utente_connection):
    global results_sorted
    print("len(risultati): %d , len(clienti): %d" % (len(risultati), len(clienti)))

    cond.acquire()
    string_punteggio = utente_connection.recv(BUFSIZE).decode(FORMAT)
    print("%s ha appena inviato un messaggio: " , str(clienti[utente_connection])) # così ottengo il nome di chi ha inviato il messaggio.
    results.update({utente_connection : int(string_punteggio)})
    print("string: " + str(string_punteggio))
    risultati.append(int(string_punteggio))
    print("risultati: " , risultati)

    # Aspetta che tutti i clients abbiano inviato i loro risultati prima di proseguire.
    if(len(risultati) < len(clienti)):
        print("Waiting for all results..")
        cond.wait()
    else:
        print("Releasing.. got all the results..")
        cond.notifyAll()
        cond.release()

    risultati.sort(reverse=True) # reverse=True serve per ordinare in modo decrescente, grande a piccolo
    print("risultati.sort(reverse=True): " , risultati)
    print("results[socket : punteggio]: " , results)
    results_sorted = dict(sorted(results.items(), key=lambda item: item[1], reverse=True)) # reverse=True per ordinarlo 
    print("results_sorted: " , results_sorted)

    # Ora devo inviare al vincitore "You Won!" ed agli altri "You Lost" oppure "Pareggio (Draw/Stalemate)"
    # draw controlla se i risultati dei giocatori sono tutti uguali e se c'è almeno più di un giocatore 
    # (altrimenti con un singolo giocatore il pareggio non avrebbe senso)
    draw = len(list(set(list(results_sorted.values())))) == 1 and len(results_sorted) > 1

    if(draw == True):
        utente_connection.send("Pareggio".encode(FORMAT))
    elif(utente_connection == list(results_sorted)[0]):
        utente_connection.send("You won!".encode(FORMAT))
        print("l'utente di indirizzo %s ha vinto " % str(indirizzi[utente_connection]))
        print("%s ha vinto!: " % str(utente_connection))
    else:
        utente_connection.send("You Lost".encode(FORMAT))
        print("%s ha perso: " % str(utente_connection))

    print("Messaggi inviati, fuori dal loop.")

# Questa funziona aspetta di ricevere un messaggio dal client, se il messaggio è "RESTART" prosegue col restart
# altrimenti se il messaggio è "QUIT" cancella il giocatore dalle liste in cui era presente.
def check_client(client_connection):
    print("trying to receive data from player..")
    data = client_connection.recv(BUFSIZE).decode(FORMAT)
    print("data: " + str(data))

    if str(data).startswith("RESTART"):
        print("Il giocatore %s è ancora online!" % str(client_connection))
        return True
    elif str(data).startswith("QUIT"):
        print("L'utente %s si è disconnesso, rimozione dell'utente dalla lista. " % 
                    (str(client_connection)))
        close_connection(client_connection)

# Questa funzione azzera alcune variabili e liste per poter far ripartire il gioco.
def reset(utente):
    print("reset function threads: " + str(threads))
    results.clear()
    risultati.clear()
    print("il dict results %s e la lista risultati %s sono stati puliti (svuotati). " % (str(results),str(risultati)))

    # invio al client RESTART per indicare possiamo riniziare!
    utente.send("RESTART".encode(FORMAT))
    numero_risposte_giocatori.clear()
    users_leaderboard.clear()
    gestisci_utente(utente)

# Questa funzione cancella l'utente dalle liste in cui era presente, chiude la connessione e interrompe il server
# se non ci sono più utenti rimasti.
def close_connection(utente_connection): 
    print("Old clients: " + str(clienti))
    print("Old addresses: " + str(indirizzi))
    del clienti[utente_connection]
    del indirizzi[utente_connection]
    print("Updated clients: " + str(clienti))
    print("Updated addresses: " + str(indirizzi))
    utente_connection.close()
    # per chiudere la thread
    #sys.exit(0)
    # se non ci sono più utenti esce.
    if(len(clienti) <= 0):
        print("Non ci sono pià clients..")
        print("Disconnessione del server..")
        #sys.exit(0)
        SERVER.close()
    else:
        # la thread va comunque chiusa.
        sys.exit(0)

# Questa funzione riceve dagli utenti le loro statistiche (risposte corrette/sbagliate) e riordina i
# loro punteggi e crea la classifica e la invia agli utenti.
def send_leaderboard(utente_connection):
    print("threads in send_leaderboard: " + str(threads))

    giocatori = [] # lista di socket perchè results ha il socket
    punteggi = []
    # clienti invece ha clienti[socket] = nome
    print("results in leaderboard: " + str(results))
    # Questo serve per aggiungere i giocatori dal dizionario results.
    for i in range(len(results_sorted.keys())):
        giocatori.append(list(results_sorted.keys())[i])
        print("giocatori: " + str(giocatori))

    for i in range(len(results_sorted.values())):
        punteggi.append(list(results_sorted.values())[i])
        print("punteggi: " + str(punteggi))

    # Questo serve per sostituire a giocatori, che inizialmente aveva i sockets, i nomi dei players.
    # perchè clienti[socket] = nome.
    for i in range(len(giocatori)):
	    print("giocatori[%d]: %s" % (i,giocatori[i]))
	    print("clienti[%s]: %s" % (giocatori[i],clienti[giocatori[i]]))
	    nome = clienti[giocatori[i]]
	    giocatori[i] = nome
	    print("giocatori[%d] %s" % (i, giocatori[i]))

    # Così ho 2 liste, quella con i nomi dei giocatori e quella con i loro punteggi
    # Giocatore[0] il suo punteggio è punteggi[0] e così via..
    print("giocatori: " + str(giocatori))
    print("punteggi: " + str(punteggi))

    lista_giocatori_punteggi = []

    for i in range(len(giocatori)):
        lista_giocatori_punteggi.append(giocatori[i] + ' : ' + str(punteggi[i]))

    # creo una stringa dalla lista "lista_giocatori_punteggi"
    messaggio = ' \n '.join(map(str, lista_giocatori_punteggi)) + ' \n' # nuova stringa = giocatore : punteggio \n giocatore : punteggio \n
    print("messaggio con giocatori e punteggi: " + str(messaggio))

    utente_connection.send(messaggio.encode(FORMAT))

    # ------------------- RISPOSTE CORRETTE E SBAGLIATE PER OGNI GIOCATORE --------------------------

    cond_leaderboard.acquire()
    msg = utente_connection.recv(BUFSIZE).decode(FORMAT)
    numero_risposte_giocatori.append(msg)
    print("numero_risposte_giocatori: " + str(numero_risposte_giocatori))
    users_leaderboard.append(str(clienti[utente_connection]))
    print("users_leaderboard: " + str(users_leaderboard))

    # Qui devo aspettare che tutti i clients abbiano inviato le loro statistiche prima di proseguire
    # con la creazione della classifica.
    if(len(numero_risposte_giocatori) < len(clienti)):
        print("Waiting for all players to send stats..")
        cond_leaderboard.wait()
    else:
        cond_leaderboard.notifyAll()
        cond_leaderboard.release()

    # creo una stringa dalla lista "numero_risposte_giocatori"
    risposte_corrette_e_sbagliate = ''.join(map(str, numero_risposte_giocatori))

    string = risposte_corrette_e_sbagliate.split('\n')
    string.remove(string[-1]) # rimuovo l'ultimo carattere che è un ''
    print("string: " + str(string))

    # list[start:end:step]

    messaggio_finale = ""

    # metto assieme in una singola stringa il nome del giocatore e le sue risposte date corrette e sbagliate.
    for i in range(len(string)):
        if(i % 2) == 0:
            if i == 0:
                messaggio_finale +=  str(users_leaderboard[i]) + "\n " + str('\n '.join(map(str, string[i:i+2]))) + "\n"
            else:
                # serve la conversione nella divisione, altrimenti verrebbe considerato un float.
                messaggio_finale +=  str(users_leaderboard[int(i/2)]) + "\n " + str('\n '.join(map(str, string[i:i+2]))) + "\n"

    print("messaggio_finale: " + str(messaggio_finale))
    utente_connection.send(str(messaggio_finale).encode(FORMAT))

    punteggi.clear() # è locale, teoricamente non servirebbe il .clear()
    lista_giocatori_punteggi.clear() # anche questa è locale alla funzione.

# Questa funzione accetta connessioni da utenti.
def accept_connections():
    while True:
        utente, addr = SERVER.accept()
        print("Connessione da %s:%s " % addr)
        msg = "Benvenuto"
        utente.send(msg.encode(FORMAT))
        utente.recv(BUFSIZE).decode(FORMAT)
        indirizzi[utente] = addr
        print("indirizzi[utente]: " , indirizzi[utente])
        nome = utente.recv(BUFSIZE).decode(FORMAT) # ricevo il nome dell'utente.
        clienti[utente] = nome
        utente.send(pick_role(nome).encode(FORMAT)) # Invio il ruolo.
        print("clienti[utente]: " , clienti[utente])
        GESTISCI_UTENTE_THREAD = Thread(target=gestisci_utente, args=(utente,))
        threads.append(GESTISCI_UTENTE_THREAD)
        print("threads: " + str(threads))
        GESTISCI_UTENTE_THREAD.start()

if __name__ == '__main__':
    SERVER.listen(5)
    print("Aspettando connessioni..")
    ACCETTA = Thread(target=accept_connections)
    ACCETTA.start()
    ACCETTA.join() 
    SERVER.close()
    print("Disconnessione dal server..")