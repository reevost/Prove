import logging
import os
import random
import sys

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# tutorial
# https://medium.com/python4you/creating-telegram-bot-and-deploying-it-on-heroku-471de1d96554

# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
giocatori = 0; chat_ids=[]; pool_ruoli=[]; day = 1; chat_names =[]; chat_roles=[]; guard_flag=False; status_chat=[]; win_flag=False; mer_flag=False; grup_id=0
pray = {}; m_ind=-1; g_ind=-1; pyro_flag=False; pyro_list=[]; lovers=[]; deadlist=[]; arch="notte"; book={}; cri_flag=False; play_count=0; chat_roles_iniz=[]
# Settings game
ruoli = {"Lupo": "Sei un Lupo: \nOgni notte, potrai decidere di mangiare qualcuno e di giorno dovrai confondere gli altri e non farti linciare! Se almeno la metà dei giocatori in partita sono lupi, la partita finisce e vincete. " ,
         "Contadino" : "Sei un Contadino: \nIl tuo ruolo è semplice: sopravvivere. Ogni giorno, avrai l'occasione di linciare i lupi! Vota con attenzione!",
         "Meretrice":"Sei la Meretrice: \nCome meretrice, avrai la possibilità di visitare altri giocatori ogni notte. Nel caso sfortunato in cui tu visitassi un lupo, verrai uccisa. Se visiti il giocatore che i lupi stanno sbranando, verrete uccisi insieme. Però, se scegli un giocatore, e i lupi scelgono di venire a casa tua, sopravviverai! Non eri a casa, dopotutto...",
         "Cupido": "Sei Cupido: \nA Inizio partita, sceglie due giocatori. Dopo diventa a tutti gli effetti un normale contadino. Questi due diventeranno follemente innamorati e se uno dei due muore, l'altro morirà.",
         "Guardia":"Sei la Guardia: \nSei un contadino che ogni notte protegge una persona a sua scelta. Durante la notte (dalla seconda in poi) prima della fase dei lupi mannari, la guardia dovrà scegliere un giocatore da proteggere Se quella persona viene poi scelta anche dai lupi mannari come vittima, non muore e nella fase della notte nessuno viene sbranato. La guardia può proteggere se stessa una volta sola.",
         "Veggente":"Sei il Veggente. \nOgni notte, potrai scegliere un giocatore e conoscere il suo ruolo.",
         "Becchino":"Sei il Becchino. \nOgni notte, scavi le tombe per ogni persona morta dall'ultima volta che l'hai fatto. Visto che sei fuori tutta la notte, I lupi non possono trovarti a casa, a meno che tu non abbia nulla da fare, in quel caso resterai a casa.. Però i lupi potrebbero vederti mentre scavi tombe, in base a quante ne hai scavate, e ucciderti. ",
         "Criceto Mannaro":"Sei il Criceto mannaro. \nAi fini del termine della partita e per il becchino è considerato un umano. Se è visto nella notte dal Veggente, muore insieme allo sbranato. Il criceto mannaro non appartiene a nessuna fazione: gioca solo per se stesso. Il criceto mannaro non può essere sbranato dai lupi mannari: se è scelto durante la notte, non è sbranato nessuno. Il criceto mannaro è l’unico vincitore se è ancora vivo quando la partita termina.",
         "Piromane":"sei il Piromane. \nOgni notte, puoi scegliere una casa di un giocatore e cospargerla di benzina o accendere la miccia e bruciare tutte le case scelte in precedenza, ma ricorda che hai una miccia sola. Vinci se sei l'ultimo sopravvissuto.",
         "Marco":"Sei Marco. \nParti come umano. Se sopravvive alla prima notte, assume immediatamente il ruolo di lupo, a tutti gli effetti."
         }


# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)

def start_handler(update, context):
    global giocatori, chat_ids, pool_ruoli, day, chat_names, chat_roles, guard_flag, status_chat, pray, m_ind, g_ind, pyro_flag, pyro_list, lovers, arch, book, win_flag, cri_flag, mer_flag, grup_id, play_count, chat_roles_iniz, deadlist
    giocatori = 0; chat_ids = []; pool_ruoli = []; day = 1; chat_names = []; chat_roles = []; guard_flag = False; status_chat = []; win_flag = False; mer_flag = False; grup_id = 0
    pray = {}; m_ind = -1; g_ind = -1; pyro_flag = False; pyro_list = []; lovers = []; deadlist = []; arch = "notte"; book = {}; cri_flag = False; play_count = 0; chat_roles_iniz = []
    pool_ruoli = list(ruoli.keys())
    logger.info("User {} started bot".format(update.effective_user["id"]))
    update.message.reply_text("Benvenuti in una nuova partita di Lupus in Tabula!\nClicca /aggiungimi per aggiungerti alla partita che inizierà a breve. \nAppena siete tutti pronti uno clicchi /inizio. ")
    grup_id = update.message.chat.id

def descrizione_handler(update, context):
    dd = "/crea fa partire una nuova partita\n/inizio distribuisce i ruoli ai giocatori che si sono già inseriti in una partita, sarebbe da fare dopo che tutti i partecipanti hanno fatto aggiungimi\n/aggiungimi ti permette di aggiungerti a una partita creata, sarebbe ideale da fare subito dopo crea, subito prima di inizio\n/notte fa iniziare la notte, va cliccata dopo inizio e dopo le i ballottaggi delle giornate\n/giorno analizza le risposte della notte e prepara le votazioni\n/votare permette di controllare i voti e scegliere chi portare al ballottaggio\n/ballottaggio permette di avere i feedback del ballottaggio"
    update.message.reply_text(dd)


def aggiungimi_handler(update, context):
    global giocatori, chat_ids, chat_names, chat_names, chat_roles, grup_id
    giocatori +=1
    chat_id=update.effective_user["id"]
    logger.info("User {} aggiunto con chat_id {}".format(update.effective_user["id"], chat_id))
    user = update.message.from_user
    chat_name = user['first_name']+" "+str(giocatori)
    context.bot.send_message(chat_id, "{} sei stato aggiunto, quando si saranno tutti aggiunti ti manderò il tuo ruolo".format(chat_name))
    update.message.reply_text("Aggiunto giocatore numero "+str(giocatori))
    chat_ids += [chat_id]
    chat_names += [chat_name]

def inizio_handler(update, context):
    global giocatori, chat_ids, pool_ruoli, chat_names, chat_roles, status_chat, grup_id, chat_roles_iniz
    status_chat = ["vivo" for i in range(giocatori)]
    # print(status_chat)
    # sistemo i ruoli in modo che siano giocatori - n_lupi
    n_lupi = giocatori//8 #lupi da aggiungere
    if giocatori < len(pool_ruoli)+n_lupi:
        pool_ruoli.remove("Lupo")
        n_lupi+=1
        pool_ruoli.remove("Contadino")
        pool_ruoli = random.sample(pool_ruoli, giocatori-n_lupi)
    #endfor
    pool_ruoli += ["Lupo" for i in range(n_lupi)]
    n_contadini = giocatori - len(pool_ruoli)- n_lupi #contadini da aggiungere
    n_contadini *= n_contadini>0
    # print("pool", pool_ruoli)
    # print(giocatori, n_contadini, n_lupi)
    pool_ruoli += ["Contadino" for i in range(n_contadini)]
    logger.info("User {} starta con chat_id {}".format(update.effective_user["id"], update.effective_user["id"]))
    # active_roles = []
    for ids in chat_ids:
        role = random.choice(pool_ruoli)
        pool_ruoli.remove(role)
        chat_roles += [role]

        logger.info("User {} aggiunto con ruolo {}".format(ids, role))
        context.bot.send_message(ids, ruoli[role])
    #endfor
    chat_roles_iniz = chat_roles[:]
    update.message.reply_text("Ruoli distribuiti. Che scenda la /notte!")


def button(update, context):
    global guard_flag, pray, m_ind, g_ind, pyro_flag, pyro_list, lovers, deadlist, arch, book, cri_flag, mer_flag, grup_id, play_count
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    rr = chat_ids.index(query.message.chat.id)  # indice di chi sceglie
    choice = chat_ids.index(int(query.data))  # indice della scelta
    #print("indice di chi sceglie", rr)
    #print("indice scelto", choice)

    query.edit_message_text(text="Hai scelto: {}".format(chat_names[choice]))

    if arch=="notte":
        if chat_roles[rr] == "Lupo":
            logger.info("utente {} entra in Lupo".format(rr))
            if choice in pray.keys():
                pray[choice] += 1
            else:
                pray[choice] = 1
        elif chat_roles[rr] == "Meretrice":
            logger.info("utente {} entra in Meretrice".format(rr))
            m_ind = choice
            if chat_roles[m_ind]=="Lupo":
                mer_flag=True
        elif chat_roles[rr] == "Guardia":
            logger.info("utente {} entra in Guardia".format(rr))
            if rr == choice:
                guard_flag = True
            g_ind = choice
        elif chat_roles[rr] == "Veggente":
            logger.info("utente {} entra in Veggente".format(rr))
            if chat_roles[choice] == "Lupo":
                context.bot.send_message(chat_ids[rr], 'L\'identità di {} è: lupo'.format(chat_names[choice]))
            else:
                context.bot.send_message(chat_ids[rr], 'L\'identità di {} è: contadino'.format(chat_names[choice]))
            if chat_roles[choice]=="Criceto Mannaro":
                cri_flag=True
        elif chat_roles[rr] == "Becchino":
            logger.info("utente {} entra in Becchino".format(rr))
            if chat_roles[choice] == "Lupo":
                context.bot.send_message(chat_ids[rr], 'L\'identità di {} è: lupo'.format(chat_names[choice]))
            else:
                context.bot.send_message(chat_ids[rr], 'L\'identità di {} è: contadino'.format(chat_names[choice]))
        elif chat_roles[rr] == "Piromane":
            logger.info("utente {} entra in Piromane".format(rr))
            if choice == rr:
                pyro_flag=True
            else:
                pyro_list += [choice]
        elif chat_roles[rr] == "Cupido":
            logger.info("utente {} entra in Cupido".format(rr))
            lovers += [choice]
        else:
            logger.info("error_role")
    elif arch=="giorno1" or arch=="giorno2":
        if choice in book.keys():
            book[choice] += 1
        else:
            book[choice] = 1
        context.bot.send_message(grup_id, '{} ha votato {}'.format(chat_names[rr], chat_names[choice]))
    play_count -= 1
    if play_count == 0 and arch=="notte":
        context.bot.send_message(grup_id, "hanno fatto tutti, potete passare al /giorno")
    elif play_count == 0 and arch=="giorno1":
        context.bot.send_message(grup_id, "hanno fatto tutti, potete passare a /votare")
    elif play_count == 0 and arch=="giorno2":
        context.bot.send_message(grup_id, "hanno fatto tutti, ecco i risultati del /ballottaggio")

def notte_handler(update, context):
    global day, chat_ids, pool_ruoli, chat_names, chat_roles, guard_flag, status_chat, pray, m_ind, g_ind, pyro_flag, pyro_list, lovers, deadlist, arch, grup_id, play_count
    lupus = []; contadin =[]; pray = {}; arch="notte"; play_count=0
    if "Meretrice" in chat_roles:
        m_ind = chat_roles.index("Meretrice")
    if "Guardia" in chat_roles:
        g_ind = chat_roles.index("Guardia")
    update.message.reply_text("La notte è giunta. Fate le vostre scelte, nella speranza di vedere la luce del /giorno")
    for num in [ind for ind in range(giocatori) if status_chat[ind]=="vivo"]:
        rr = chat_roles[num] # ruoli
        if rr == "Lupo":
            lupus += [num]
            play_count +=1
        elif rr == "Meretrice":
            indic = list(range(giocatori))
            keyboard = [[InlineKeyboardButton(chat_names[i], callback_data=chat_ids[i])] for i in indic if status_chat[i]=="vivo"]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_ids[num], 'Scegli in che casa passare la notte:', reply_markup=reply_markup)
            play_count += 1
        elif rr == "Guardia":
            indic = list(range(giocatori))
            if guard_flag==True:
                indic.remove(num)
            keyboard = [[InlineKeyboardButton(chat_names[i], callback_data=chat_ids[i])] for i in indic if status_chat[i]=="vivo"]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_ids[num], 'Scegli chi proteggere questa notte:', reply_markup=reply_markup)
            play_count += 1
        elif rr == "Veggente":
            indic = list(range(giocatori))
            indic.remove(num)
            keyboard = [[InlineKeyboardButton(chat_names[i], callback_data=chat_ids[i])] for i in indic if status_chat[i]=="vivo"]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_ids[num], 'Scegli di chi guardare l\' identità:', reply_markup=reply_markup)
            play_count += 1
        elif rr == "Becchino" and len(deadlist) != 0:
            indic = list(range(giocatori))
            keyboard = [[InlineKeyboardButton(chat_names[i], callback_data=chat_ids[i])] for i in indic if status_chat[i]=="morto"]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_ids[num], 'Scegli di chi guardare l\' identità:', reply_markup=reply_markup)
            play_count += 1
        elif rr == "Piromane":
            indic = list(range(giocatori))
            nam = chat_names[:]
            nam[num] = "Fuocoooo"
            keyboard = [[InlineKeyboardButton(nam[i], callback_data=chat_ids[i])] for i in indic if status_chat[i]=="vivo"]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_ids[num], 'Scegli se andare a spargere benzina nelle case altrui o stare a casa tua per accendere la miccia e dare fuoco a tutte le case cosparse di benzina:', reply_markup=reply_markup)
            play_count += 1
        elif rr == "Cupido":
            indic = list(range(giocatori))
            keyboard = [[InlineKeyboardButton(chat_names[i], callback_data=chat_ids[i])] for i in indic]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_ids[num], 'Scegli il primo innamorato:', reply_markup=reply_markup)
            context.bot.send_message(chat_ids[num], 'Scegli il secondo innamorato:', reply_markup=reply_markup)
            play_count += 2
        else:
            contadin += [num]
    #endfor
    for c_ind in contadin:
        context.bot.send_message(chat_ids[c_ind], "Buonanotte, e in bocca al lupo")
    #endfor

    lupus_names=""
    for ii in lupus:
        lupus_names += chat_names[ii]
        lupus_names += " \n "
    #endfo
    lupus_names = lupus_names[:-3]

    for l_ind in lupus:
        context.bot.send_message(chat_ids[l_ind], "I lupi questa partita sono:\n "+lupus_names)
        if bool(len(pray.keys()))==True:
            context.bot.send_message(chat_ids[l_ind], "Fin\'ora le prede votate sono:\n ")
            for ii in pray.keys():
                context.bot.send_message(chat_ids[l_ind], "{} con {} voti\n ".format(chat_names[ii],pray[ii]))
        indic = list(range(giocatori))
        indic.remove(l_ind)
        keyboard = [[InlineKeyboardButton(chat_names[i], callback_data=chat_ids[i])] for i in indic if status_chat[i] == "vivo"]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_ids[l_ind], 'Vota chi vorresti sbranarti questa notte, il contadino con più voti sarà il prescelto, a parità di voti sarà scelto casualmente tra i bersagli con più voti:', reply_markup=reply_markup)
    #endfor

def giorno_handler(update, context):
    global day, chat_ids, pool_ruoli, chat_names, chat_roles, status_chat, pray, m_ind, g_ind, pyro_list, pyro_flag, lovers, deadlist, arch, book, win_flag, cri_flag, mer_flag, grup_id, play_count, chat_roles_iniz
    deadman = random.choice([kk for kk in pray.keys() if pray[kk]==max(pray.values())])
    becc_flag = False; play_count=0
    if "Becchino" in chat_roles and status_chat[chat_roles.index("Becchino")]=="vivo":
        if random.randint(1,8) < len(deadlist):
            deadlist += [chat_roles.index("Becchino")]; status_chat[chat_roles.index("Becchino")]="morto" # becchino sgamato
            becc_flag = True
        elif len(deadlist)==0 and chat_roles.index("Becchino")==deadman:
            deadlist += [chat_roles.index("Becchino")]; status_chat[chat_roles.index("Becchino")]="morto"
            becc_flag = True
    deadlist = []
    if cri_flag:
        cri_flag=False
        crind = chat_roles.index("Criceto Mannaro")
        deadlist += [crind];  status_chat[crind]="morto"
    if mer_flag:
        mer_flag=False
        merind = chat_roles.index("Meretrice")
        deadlist += [merind];  status_chat[merind]="morto"
    if g_ind!=deadman:
        if m_ind==deadman:
            deadlist += [chat_roles.index("Meretrice")]; status_chat[chat_roles.index("Meretrice")]="morto"
        if chat_roles[deadman] not in ["Criceto Mannaro", "Meretrice", "Becchino"]:
            deadlist += [deadman]; status_chat[deadman]="morto"
    if "Piromane" in chat_roles and (pyro_flag==True or chat_roles.index("Piromane") in deadlist):
        for ii in pyro_list:
            deadlist += [ii]; status_chat[ii]="morto"
    if "Cupido" in chat_roles_iniz:
        if lovers[0] in deadlist or lovers[1] in deadlist:
                if lovers[0] not in deadlist:
                    deadlist += [lovers[0]]; status_chat[lovers[0]]="morto"
                if lovers[1] not in deadlist:
                    deadlist += [lovers[1]]; status_chat[lovers[1]]="morto"
    if "Marco" in chat_roles:
        if day==1 and chat_roles.index("Marco") not in deadlist:
            chat_roles[chat_roles.index("Marco")]="Lupo"
    if "Cupido" in chat_roles and day==1:
        chat_roles[chat_roles.index("Cupido")] = "Contadino"
    book={}
    # fine feedback notte
    if len(deadlist)==0 and not becc_flag:
        update.message.reply_text("Oggi è un bellissimo giorno... per tutti!\n Non è morto nessuno stanotte")
    else:
        update.message.reply_text("Oggi è un bellissimo giorno... ma non per tutti! Infatti stanotte è morto:\n ")
        pp = ""
        for ii in deadlist:
            pp += "{}\n ".format(chat_names[ii])
        if becc_flag:
            pp += chat_names[chat_roles.index("Becchino")]
        context.bot.send_message(grup_id, pp)

    workinprogress="Situazione nel villaggio dopo {} notti:\n".format(day)
    for ii in range(giocatori):
        workinprogress += "{} è {}\n".format(chat_names[ii],status_chat[ii])

    context.bot.send_message(grup_id, workinprogress)

    #print(chat_names)
    #print(status_chat)
    vivi = [player for player in range(giocatori) if status_chat[player]=="vivo"]
    d_lupus = 2*len([player for player in vivi if chat_roles[player]=="Lupo"])
    if d_lupus >= len(vivi):
        update.message.reply_text("Vincono i Lupi!")
        win_flag = True
    elif d_lupus == 0:
        if "Criceto Mannaro" in chat_roles:
            crindex = chat_roles.index("Criceto Mannaro")
        else:
            crindex = -1
        if crindex in vivi:
            update.message.reply_text("Vince il Criceto Mannaro!")
            win_flag=True
        else:
            update.message.reply_text("Vincono i contadini!")
        win_flag = True

    arch="giorno1"
    if win_flag==False:
        update.message.reply_text("Ora è giunto il momento di incolpare chi credete sia un lupo.\nI due che riceveranno più voti finiranno al ballottaggio, dove i vivi decideranno chi uccidere. \nQuando tutti hanno finito di /votare scoprirete chi tra di voi rischia la vita.")
        for p_ind in [ind for ind in range(giocatori)]:
            keyboard = [[InlineKeyboardButton(chat_names[i], callback_data=chat_ids[i])] for i in range(giocatori) if status_chat[i]=="vivo"]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_ids[p_ind], 'Chi vuoi portare al ballottaggio? ', reply_markup=reply_markup)
            play_count += 1
        #endfor
    else:
        rruoli = "Ecco i ruoli sorteggiati all\'inizio\n"
        for ii in range(giocatori):
            rruoli += "{} - {}\n".format(chat_names[ii], chat_roles_iniz[ii])

        context.bot.send_message(grup_id, rruoli)


def vote_handler(update, context):
    global day, chat_ids, pool_ruoli, chat_names, chat_roles, status_chat, pray, m_ind, g_ind, pyro_list, pyro_flag, lovers, deadlist, arch, book, win_flag, grup_id, play_count
    play_count=0
    ballottaggio = []
    it = max(book.values())
    while len(ballottaggio) < 2:
        for ii in book.keys():
            if book[ii] == it:
                ballottaggio += [ii]
        it -= 1
    # endwhile
    if len(ballottaggio)==1:
        dead = ballottaggio[0]
        deadlist += [dead]; status_chat[dead] = "morto"
        context.bot.send_message(grup_id, "questa volta non servirà nessun ballottaggio, tutti (compreso se stesso) voglio {} morto, bene così sia.\nTrascorsa quindi una tranquilla giornata giunge infine la /notte".format(chat_roles[dead]))
    else:
        rballottaggio = [ballottaggio[0]]
        rballottaggio += [random.choice(ballottaggio[1:])]
        book = {}; arch="giorno2"
        update.message.reply_text("Siamo infine giunti al ballottaggio! Ora solo i vivi avranno il potere di /votare per la morte di {} o {}, che sono risultati i meno benvoluti dalla comunità. ".format(chat_names[rballottaggio[0]], chat_names[rballottaggio[1]]))
        for p_ind in [ind for ind in range(giocatori) if status_chat[ind] == "vivo"]:
            keyboard = [[InlineKeyboardButton(chat_names[i], callback_data=chat_ids[i])] for i in rballottaggio]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_ids[p_ind],'Chi vuoi votare?\n Quello con più voti verrà ucciso dalla comunità. ',reply_markup=reply_markup)
            play_count+=1
        # endfor

def ballo_handler(update, context):
    global day, chat_ids, pool_ruoli, chat_names, chat_roles, status_chat, pray, m_ind, g_ind, pyro_list, pyro_flag, lovers, deadlist, arch, book, win_flag, grup_id, play_count
    play_count=0
    dead = random.choice([pind for pind in book.keys() if book[pind] == max(book.values())])
    deadlist += [dead]; status_chat[dead] = "morto"
    update.message.reply_text("Per vostra decisione {} è morto,".format(chat_names[dead]))

    if "Cupido" in chat_roles_iniz:
        if lovers[0] in deadlist or lovers[1] in deadlist:
                if lovers[0] not in deadlist:
                    deadlist += [lovers[0]]; status_chat[lovers[0]]="morto"
                    context.bot.send_message(grup_id, "Per un folle legame d\'ammmmore anche {} da oggi non sarà più con noi".format(chat_names[lovers[0]]))
                if lovers[1] not in deadlist:
                    deadlist += [lovers[1]]; status_chat[lovers[1]]="morto"
                    context.bot.send_message(grup_id, "Per un folle legame d\'ammmmore anche {} da oggi non sarà più con noi".format(chat_names[lovers[1]]))
    day += 1
    vivi = [player for player in range(giocatori) if status_chat[player] == "vivo"]
    d_lupus = 2 * len([player for player in vivi if chat_roles[player] == "Lupo"])
    if d_lupus > len(vivi):
        update.message.reply_text("Vincono i Lupi!")
        win_flag = True
    elif d_lupus == 0:
        if "Criceto Mannaro" in chat_roles:
            crindex = chat_roles.index("Criceto Mannaro")
        else:
            crindex = -1
        if crindex in vivi:
            update.message.reply_text("Vince il Criceto Mannaro!")
            win_flag = True
        else:
            update.message.reply_text("Vincono i contadini!")
        win_flag = True
    if not win_flag:
        update.message.reply_text("è ora di trascorrere una tranquilla giornata in tranquillità.\nFinchè la /notte non giungerà nuovamente: ")
    else:
        rruoli = "Ecco i ruoli sorteggiati all\'inizio\n"
        for ii in range(giocatori):
            rruoli += "{} - {}\n".format(chat_names[ii], chat_roles_iniz[ii])

        context.bot.send_message(grup_id, rruoli)


if __name__ == '__main__':
    logger.info("Starting bot")

    updater = Updater(TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler("descrizione", descrizione_handler))
    updater.dispatcher.add_handler(CommandHandler("ballottaggio", ballo_handler))
    updater.dispatcher.add_handler(CommandHandler("votare", vote_handler))
    updater.dispatcher.add_handler(CommandHandler("crea", start_handler))
    updater.dispatcher.add_handler(CommandHandler("aggiungimi", aggiungimi_handler))
    updater.dispatcher.add_handler(CommandHandler("inizio", inizio_handler))
    updater.dispatcher.add_handler(CommandHandler("notte", notte_handler))
    updater.dispatcher.add_handler(CommandHandler("giorno", giorno_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    run(updater)
