from socket import *
import threading
import tkinter as tk
from tkinter import PhotoImage, messagebox
from threading import *
import re
from time import sleep
import sys
from tkinter.font import BOLD

# costanti
BUFSIZE = 4096
FORMAT = 'utf-8' # prima era 'utf8'
HOST = '127.0.0.1'
PORT = 53000

ADDR = (HOST, PORT)

# timer
TOT_GAME_SECONDS = 30
FINISHED_TIME = 0
start_timer = False
game_timer = TOT_GAME_SECONDS

# Nome e Ruolo
your_name = ""
ruolo = ""

# punteggio e statistiche di gioco
punteggio = 0
corrette = 0
sbagliate = 0 
scelta_domanda_errata = False

# threads
threads = []

timer_threads = []

# cliente
cliente = socket(AF_INET ,SOCK_STREAM)
cliente.connect(ADDR)

# Interfaccia grafica tkinter
root = tk.Tk()
root.title("Quiz")

top_answers_frame = tk.Frame(root)
top_answers_frame.pack_forget()

question_label_text = tk.StringVar()
question_label_text.set("") # text iniziale del label
question_label = tk.Label(top_answers_frame, textvariable=question_label_text)
question_label.config(state=tk.ACTIVE)
question_label.pack()

answer_button_text = tk.StringVar() # per poter cambiare il testo del pulsante
answer_button_text.set("") # text iniziale del pulsante
answer_button = tk.Button(top_answers_frame, textvariable=answer_button_text, command=lambda : scelta(risposta1,cliente), height= 5, width=10, bg='#567', fg='White')
answer_button.pack(side=tk.LEFT, pady=10)
answer_button.config(state=tk.NORMAL)

answer_button2_text = tk.StringVar() # per poter cambiare il testo del pulsante
answer_button2_text.set("")
answer_button2 = tk.Button(top_answers_frame, textvariable=answer_button2_text, command=lambda : scelta(risposta2,cliente), height= 5, width=10, bg='#567', fg='White')
answer_button2.pack(side=tk.RIGHT, pady=10)
answer_button2.config(state=tk.NORMAL)

# ---------------------------------------------------------------------------------------------------

top_welcome_frame= tk.Frame(root)
lbl_name = tk.Label(top_welcome_frame, text = "Name:")
lbl_name.pack(side=tk.LEFT)
ent_name = tk.Entry(top_welcome_frame)
ent_name.pack(side=tk.LEFT)
btn_connect = tk.Button(top_welcome_frame, text="Connect", command= lambda : threading._start_new_thread(connect, ()))#command=lambda : connect()) 
btn_connect.pack(side=tk.LEFT)

top_welcome_frame.pack(side=tk.TOP)

# ---------------------------------------------------------------------------------------------------

leaderboard_frame = tk.Frame(root)
lbl_classifica = tk.Label(leaderboard_frame, text="Classifica", font = "Helvetica 9 bold")
lbl_leaderboard_text = tk.StringVar()
lbl_leaderboard = tk.Label(leaderboard_frame, text = "Nome | Punteggio | Risposte Corrette | Risposte errate")

lbl_classifica.pack_forget()
lbl_leaderboard.pack_forget()
leaderboard_frame.pack_forget()

# ---------------------------------------------------------------------------------------------------

top_message_frame = tk.Frame(root)
lbl_line = tk.Label(top_message_frame, text="***********************************************************").pack()
lbl_choose_question = tk.Label(top_message_frame, text="Scegli la domanda")
lbl_choose_question.pack()

btn_question1_text = tk.StringVar()
btn_question2_text = tk.StringVar()
btn_question3_text = tk.StringVar()

btn_question1 = tk.Button(top_message_frame, textvariable=btn_question1_text, command=lambda : question_choice(domanda1, cliente)) 
btn_question2 = tk.Button(top_message_frame, textvariable=btn_question2_text, command=lambda : question_choice(domanda2, cliente)) 
btn_question3 = tk.Button(top_message_frame, textvariable=btn_question3_text, command=lambda : question_choice(domanda3, cliente)) 

btn_question1_text.set("")
btn_question2_text.set("")
btn_question3_text.set("")

btn_question1.pack() 
btn_question2.pack() 
btn_question3.pack()

lbl_line_server = tk.Label(top_message_frame, text="***********************************************************")
lbl_line_server.pack()
top_message_frame.pack_forget()

# ---------------------------------------------------------------------------------------------------

top_frame = tk.Frame(root)
top_left_frame = tk.Frame(top_frame, highlightbackground="green", highlightcolor="green", highlightthickness=1)
lbl_your_name = tk.Label(top_left_frame, text="Your name: " + your_name, font = "Helvetica 13 bold")
lbl_your_name.grid(row=0, column=0, padx=5, pady=8)
top_left_frame.pack(side=tk.LEFT, padx=(10, 10))


top_right_frame = tk.Frame(top_frame, highlightbackground="green", highlightcolor="green", highlightthickness=1)
lbl_game_round = tk.Label(top_right_frame, text="Timer", foreground="blue", font = "Helvetica 14 bold")
lbl_timer = tk.Label(top_right_frame, text=" ", font = "Helvetica 24 bold", foreground="black")
lbl_game_round.grid(row=0, column=0, padx=5, pady=5)
lbl_timer.grid(row=1, column=0, padx=5, pady=5)
top_right_frame.pack(side=tk.RIGHT, padx=(10, 10))

top_frame.pack_forget()

# ---------------------------------------------------------------------------------------------------

middle_frame = tk.Frame(root)

lbl_line = tk.Label(middle_frame, text="***********************************************************").pack()
lbl_line = tk.Label(middle_frame, text="**** GAME LOG ****", font = "Helvetica 13 bold", foreground="blue").pack()
lbl_line = tk.Label(middle_frame, text="***********************************************************").pack()

round_frame = tk.Frame(middle_frame)
lbl_your_answer = tk.Label(round_frame, text="Your answer: " + "None", font = "Helvetica 13 bold")
lbl_your_answer.pack()
lbl_punteggio = tk.Label(round_frame, text="Punteggio: " + str(punteggio))
lbl_punteggio.pack()
lbl_role = tk.Label(round_frame, text="Ruolo: ", foreground="black", font = "Helvetica 9")
lbl_role.pack()
btn_restart = tk.Button(round_frame, text="RESTART", command=lambda : reset(cliente)) 
btn_restart.pack_forget()
btn_quit = tk.Button(round_frame, text="QUIT", command=lambda : quit(cliente)) 
btn_quit.pack_forget()
round_frame.pack(side=tk.TOP)

final_frame = tk.Frame(middle_frame)
lbl_line = tk.Label(final_frame, text="***********************************************************").pack()
lbl_final_result = tk.Label(final_frame, text=" ", font = "Helvetica 13 bold", foreground="blue")
lbl_final_result.pack()
lbl_line = tk.Label(final_frame, text="***********************************************************").pack()
final_frame.pack(side=tk.TOP)

middle_frame.pack_forget()

# ---------------------------------------------------------------------------------------------------

# il client controlla la sua risposta con questo dizionario, il client passa la key a questo
# dizionario e gli viene restituita il valore (ovvero la risposta) se questa (la risposta) 
# combacia con la risposta data dall'utente allora aumenta il punteggio.
risposte_corrette = {
    "Quale protocollo controlla i pacchetti inviati?\n" : "TCP",
    "Quale protocollo invia pacchetti senza controllo?\n" : "UDP"
    #"Nel 3-Way Handshake, cosa risponde il server al client?\n" : "SYN ACK",
    #"Nel 3-Way Handshake, cosa invia il client per stabilire una connessione?\n" : "SYN",
    #"Nel 3-Way Handshake, cosa invia infine il client in risposta al server?\n" : "ACK"
}

# funzione molto basica per determinare se un nome è maschile o femminile
# metto il .lower perchè così anche se viene scritto in maiuscolo, comunque viene controllato.
def male(name):
    return str(name[-1]).lower() == 'o' or str(name).lower() == "luca" or str(name).lower() == "andrea" and not str(name[-1]).lower() == 'a'

# Questa funzione permette di ricevere le 3 domande (di cui 1 trabocchetto) dal server.
# E setta il testo dei pulsanti delle domande.
def recv_initial_questions(client_connection):
    global domanda1, domanda2, domanda3
    domanda1 = ""
    domanda2 = ""
    domanda3 = ""

    disable_buttons(True) # 2 pulsanti disabilitati
    disable_initial_questions(False) # 3 pulsanti attivi (normali)
    
    msg = client_connection.recv(BUFSIZE).decode(FORMAT)
    print("domande: " + str(msg))

    domande = []
    domande.clear()
    msg_split = msg.split('\n')
    domande.append(msg_split[0])
    domande.append(msg_split[1])
    domande.append(msg_split[2])
    print("domande: " , domande)
    print("domande[0]: " , domande[0])
    print("domande[1]: " , domande[1])
    print("domande[2]: " , domande[2])

    domanda1 = str(domande[0])
    domanda2 = str(domande[1])
    domanda3 = str(domande[2])

    btn_question1_text.set(domanda1)
    btn_question2_text.set(domanda2)
    btn_question3_text.set(domanda3)

# Questa funzione si occupa di ricevere la domanda scelta dall'utente
# e le possibili risposte ad essa dal server.
def receive_questions(client):
    disable_buttons(False)
    global domanda
    global risposta1, risposta2
    msg = client.recv(BUFSIZE).decode(FORMAT)
    print("msg: " + msg)
    string = msg.split('\n')
    print("string: " , string)
    print("string[0]: " , string[0]) # domanda
    print("string[1]: " + string[1]) # risposta1
    print("string[2]: " + string[2]) # risposta2

    domanda = string[0].split(':', 1)[1]
    risposta1 = string[1].split(':', 1)[1]
    risposta2 = string[2].split(':', 1)[1]
    print("[domanda:] " + domanda)
    print("[risposta1:] " + risposta1)
    print("[risposta2:] " + risposta2)

    question_label_text.set(domanda)
    answer_button_text.set(risposta1)
    answer_button2_text.set(risposta2)

# Questa funzione si occupa di disabilitare i 2 pulsanti delle risposte da scegliere.
def disable_buttons(todo):
    if todo == True:
        answer_button.config(state=tk.DISABLED)
        answer_button2.config(state=tk.DISABLED)
    else:
        answer_button.config(state=tk.NORMAL)
        answer_button2.config(state=tk.NORMAL)

# Questa funzione si occupa di disabilitare i 3 pulsanti delle 3 domande da poter scegliere.
def disable_initial_questions(todo):
    if todo == True:
        btn_question1.config(state=tk.DISABLED)
        btn_question2.config(state=tk.DISABLED)
        btn_question3.config(state=tk.DISABLED)
    else:
        btn_question1.config(state=tk.NORMAL)
        btn_question2.config(state=tk.NORMAL)
        btn_question3.config(state=tk.NORMAL)

# Questa funzione serve per quando l'utente clicca uno dei due pulsanti delle risposte.
# Se ha cliccato la risposta giusta, il suo punteggio incrementerà di 1, altrimenti diminuirà di 1.
def scelta(arg, client):
    global punteggio
    global start_timer
    global corrette, sbagliate
    disable_buttons(True)

    print("start_timer: " + str(start_timer))
    if(start_timer == False): 
        print("Starting timer..")
        TIMER_THREAD = Thread(target=timer, args=(start_timer, client))
        TIMER_THREAD.start()
        timer_threads.append(TIMER_THREAD)
        print("timer_threads: " + str(timer_threads))
        start_timer = True

    msg = "Ricevuto"
    client.send(msg.encode(FORMAT))

    x = domanda + '\n'
    print("x: " + x)
    print(x[1:]) # rimuovo il primo carattere (perchè c'è uno spazio di troppo.)
    x = x[1:]
    print("x: " + x)
    arg = arg[1:] # rimuovo uno spazio di troppo da arg

    # stampo la risposta di x , ovvero della domanda e stampo il valore di arg, risposta data dall'utente.
    print("risposte_corrette[x]: " +  risposte_corrette[x])
    print("arg: " + arg)

    print("punteggio prima della risposta: %d" % punteggio)

    if(risposte_corrette[x] == arg):
        print("Risposta corretta!")
        punteggio += 1
        corrette += 1 # conteggio delle risposte corrette
        print("Conteggio delle risposte corrette: %d" % corrette)
        lbl_punteggio["text"] = "Punteggio: " + str(punteggio)
        print("Nuovo punteggio: %d" % punteggio)
        lbl_your_answer["text"] = "Your answer: " + str(arg) + " \nCORRETTA"
        recv_initial_questions(client)
    else:
        print("Risposta errata!")
        punteggio -= 1
        lbl_punteggio["text"] = "Punteggio: " + str(punteggio)
        sbagliate += 1 # conteggio delle risposte sbagliate
        print("Conteggio delle risposte sbagliate: %d" % sbagliate)
        print("Nuovo punteggio: %d" % punteggio)
        lbl_your_answer["text"] = "Your answer: " + str(arg) + " \nSBAGLIATA" 
        recv_initial_questions(client) 

# Questa funzione viene chiamata la prima volta che si clicca su uno dei due pulsanti della risposta.
def timer(counter_started, client):
    global game_timer, start_timer
    print("start_timer: " + str(counter_started))
    print("game_timer = " + str(game_timer))
    if(counter_started == False):
        lbl_timer["text"] = str(game_timer)
        while game_timer > FINISHED_TIME and scelta_domanda_errata == False:
            game_timer -= 1
            lbl_timer["text"] = str(game_timer)
            print("game timer: " + str(game_timer) + "s")
            sleep(1)
        disable_buttons(True)
        disable_initial_questions(True)
        start_timer = True
        print("Game Finished!")
        global punteggio_finale
        punteggio_finale = punteggio
        print("punteggio_finale: " + str(punteggio_finale))
        if start_timer == True and scelta_domanda_errata == False:
            print("start_timer: " + str(start_timer))
            print("Gioco finito!")
            print("def: scelta = punteggio_finale: " + str(punteggio_finale))
            # Invio al server il fatto che il timer ha finito e quindi può smettere di inviare
            # domanda e può prendere il punteggio_finale e paragonarlo agli altri.
            client.send("Stop".encode(FORMAT))
            client.send(str(punteggio_finale).encode(FORMAT))
            end_game(client)

# Questa funzione aspetta dal server il risultato, ovvero se vincitore/perdente o pareggio
# e poi chiama leaderboard per poter creare la classifica.
def end_game(client_connection):
    print("end_game threads: " + str(threads))
    disable_buttons(True) 
    print("In attesa dei risultati..")
    final_result = client_connection.recv(BUFSIZE).decode(FORMAT)
    print("final_result: " + str(final_result))
    lbl_final_result["text"] = str(final_result)
    btn_restart.pack(side=tk.LEFT)
    btn_quit.pack(side=tk.RIGHT)
    btn_restart.config(state=tk.NORMAL)
    btn_quit.config(state=tk.NORMAL)

    leadarboard(client_connection)

    print("end_game threads: " + str(threads))
    print("In attesa che il giocatore prema RESTART o QUIT..")

# Questa funzione azzera alcune variabili e liste per poter far ripartire il gioco.
def reset(client):
    global corrette, sbagliate
    print("reset _ threads: " + str(threads))
    btn_restart.config(state=tk.DISABLED)
    btn_quit.config(state=tk.DISABLED)
    global start_timer, punteggio, punteggio_finale, game_timer
    start_timer = False
    punteggio = 0
    punteggio_finale = 0
    game_timer = TOT_GAME_SECONDS
    lbl_final_result["text"] = ""
    lbl_punteggio["text"] = "Punteggio: " + str(punteggio) # str(0)
    print("Restart: set start_timer: %s, punteggio: %d , punteggio_finale: %d, game_timer: %d secs rimanenti" % (str(start_timer) , punteggio , punteggio_finale, game_timer))
    print("Restarting the game..")
    # cancello labels classifica: 
    for i in range(len(labels_list)):
        labels_list[i].destroy()
    # comunque pulisco labels_list
    print("labels_list: " + str(labels_list))
    labels_list.clear()
    print("labels_list.clear() " , labels_list)
    corrette = 0 # conteggio risposte corrette azzerato
    sbagliate = 0 # conteggio sbagliate corrette azzerato
    client.send("RESTART".encode(FORMAT))

    # prima di questo mi faccio inviare dal server: RESTART per avere il via.

    print("Waiting for server to send RESTART when all players are ready!")
    # anche senza dover aspettare gli altri players
    msg = client.recv(BUFSIZE).decode(FORMAT)
    if(str(msg).startswith("RESTART")):
        receive_channel(client)

# Questa funzione serve per poter informare al server che il client sta per uscire..
def quit(client):
    client.send("QUIT".encode(FORMAT))
    client.close()
    #root.quit()
    sys.exit(0)

# Questa funzione viene chiamata quando si preme il pulsante di una delle 3 domande.
# Se il giocatore ha scelto la domanda trabocchetto viene eliminato dal gioco!
def question_choice(question_picked, client):
    global scelta_domanda_errata
    disable_initial_questions(True)
    question_picked = question_picked + '\n' 
    client.send(question_picked.encode(FORMAT))

    msg = client.recv(BUFSIZE).decode(FORMAT)
    if(str(msg).startswith("Domanda errata")):
        scelta_domanda_errata = True
        print("Domanda errata, hai perso!")
        disable_buttons(True)
        if(male(your_name) == True):
            lbl_final_result["text"] = "Domanda Errata\n Eliminato!" # in base al nome
        else:
            lbl_final_result["text"] = "Domanda Errata\n Eliminata!" # in base al nome
        lbl_final_result.after(3000, lambda : lbl_final_result.config(text = "Exiting.."))

        print("Exiting..")
        root.after(5000, lambda : quit(client))
        #root.after(5000, lambda : root.quit())
    else:
        print("question_choice(): chiamo receive_questions()")
        receive_questions(client)

# Questa è la funzione principale che chiama recv_initial_questions()
def receive_channel(client):
    recv_initial_questions(client)

# Questa funzione riceve dal server la classifica con i punteggi e i conteggi delle risposte date da
# tutti i giocatori corrette e sbagliate.
# E crea la classifica!
def leadarboard(client_connection):
    global labels_list
    print("In attesa che il server invii la classifica..")
    msg = client_connection.recv(BUFSIZE).decode(FORMAT)
    print("msg: " + str(msg))
    string = re.split(r"[\n\:]+", msg)
    giocatori = []
    punteggi = []
    print("string: " + str(string))
    for i in range(len(string) - 1): # - 1 per rimuovere l'ultimo carattere che è un ''
        if (i % 2) == 0: # se l'indice è pari
            print("string[# pari] = " + str(string[i]))
            giocatori.append(string[i])
            print("giocatori: " + str(giocatori))
        else: # se l'indice è dispari
            print("string[# dispari] = " + str(string[i]))
            punteggi.append(string[i])
            print("punteggi: " + str(punteggi))

    print("Fuori dal loop della classifica (leaderboard)")
    print("giocatori: " + str(giocatori))
    print("punteggi: " + str(punteggi))
    
    leaderboard_frame.pack(side=tk.TOP)
    lbl_classifica.pack(side=tk.TOP)
    lbl_leaderboard.pack()

    labels_list = [] # lista dei labels

    # numero risposte corrette e sbagliate da inviare al server.
    risposte_date = str(corrette) + "\n "  + str(sbagliate) + "\n"
    client_connection.send(risposte_date.encode(FORMAT))

    print("In attesa dal server del numero di risposte corrette e sbagliate di ciascun giocatore..")
    number_of_answers = client_connection.recv(BUFSIZE).decode(FORMAT)
    lista_number_of_answers = str(number_of_answers).split('\n')
    print("lista_number_of_answers: " + str(lista_number_of_answers))
    lista_number_of_answers.remove(lista_number_of_answers[-1]) # eliminiamo il '' (che era l'ultimo carattere)

    # rimuovo gli spazi non necessari nelle stringhe della lista per far sì che trovi un match (delle stringhe che combaciano).
    for i in range(len(lista_number_of_answers)):
        print("prima: " + str(lista_number_of_answers))
        lista_number_of_answers[i] = lista_number_of_answers[i].replace(" ", "") # .replace per rimuovere gli spazi
        print("dopo: " + str(lista_number_of_answers))

    for i in range(len(giocatori)):
        giocatori[i] = str(giocatori[i]).replace(" ", "")
        print("giocatori: " + str(giocatori))

    # qui trovo gli elementi in comune tra le due liste
    common_elements_in_lists = set(lista_number_of_answers).intersection(giocatori)
    # altro modo: common_elements_in_lists = [value for value in lista_number_of_answers if value in giocatori]
    print("common_elements_in_lists: " + str(common_elements_in_lists))
    print("giocatori: " + str(giocatori))

    # riordinare gli elementi comuni in base alla lista giocatori (che ha l'ordine giusto)
    common_elements_in_lists = sorted(common_elements_in_lists, key = giocatori.index)
    print("common_elements_in_lists: " + str(common_elements_in_lists))

    # qui trovo a quali indici si trovono questi elementi in comune.
    indices_lista_number_of_answers = [lista_number_of_answers.index(x) for x in common_elements_in_lists]
    indices_giocatori = [giocatori.index(x) for x in common_elements_in_lists]
    print("indices_lista_number_of_answers: " + str(indices_lista_number_of_answers))
    print("indices_giocatori: " + str(indices_giocatori))

    # essenzialmente lista_number_of_answers[indices_lista_number_of_answers[i] + 1] : mi da le risposte corrette
    # lista_number_of_answers[indices_lista_number_of_answers[i] + 2] : mi da le risposte errate
    for i in range(len(giocatori)):
        if(lista_number_of_answers[indices_lista_number_of_answers[i]] == giocatori[indices_giocatori[i]]):
            labels_list.append(create_label(leaderboard_frame, str(giocatori[i]) + " | " + str(punteggi[i] + " | " + str(lista_number_of_answers[indices_lista_number_of_answers[i] + 1] + " | " + str(lista_number_of_answers[indices_lista_number_of_answers[i] + 2])))))

        labels_list[i].pack()    

    giocatori.clear() # sono tutte liste locali alla funzione, forse non servirebbe fare il .clear()
    punteggi.clear()
    lista_number_of_answers.clear()

# Questa funzione permette di creare un label tkinter
def create_label(parent_frame, text):
    label = tk.Label(parent_frame, text=text)
    return label

# Questa funzione permette di "renderizzare" alcuni frame e modifica il testo di alcuni labels. (nome e ruolo)
def update_gui(): 
    top_message_frame.pack(side=tk.TOP)
    top_answers_frame.pack()
    top_frame.pack()
    middle_frame.pack()
    lbl_your_name["text"] = "Your name: " + your_name
    lbl_role["text"] = "Ruolo: " + ruolo 

# Questa funzione viene chiamata quando il pulsante "Connect" viene premuto.
def connect():
    global your_name, ruolo, cliente
    if(len(ent_name.get())) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="You must enter a name")
    else:
        your_name = ent_name.get()
        print("your_name: " + your_name)

        lbl_name.config(state=tk.DISABLED) 
        ent_name.config(state=tk.DISABLED)
        btn_connect.config(state=tk.DISABLED)

    print(cliente.recv(BUFSIZE).decode(FORMAT))
    msg = "Connesso da %s:%s " % ADDR
    cliente.send(msg.encode(FORMAT))
    cliente.send(your_name.encode(FORMAT))
    ruolo = cliente.recv(BUFSIZE).decode(FORMAT) # riceve il ruolo
    print("Ruolo: " + ruolo)
    update_gui()
    receive_thread = Thread(target=receive_channel, args=(cliente,))
    threads.append(receive_thread)
    receive_thread.start()

if __name__ == '__main__':
    root.mainloop()