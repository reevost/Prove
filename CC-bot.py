import logging
import os
import random
import sys
import time

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler

# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

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

SEX, NAME, DOMANDA1, DOMANDA2, DOMANDA3, DOMANDA4, DOMANDA5, DOMANDA6, DOMANDA7, DOMANDA8 = range(10)
AB1, AB2, AB3, AB4, AB5, AB6, RECAP = range(10, 17)
STAT1, STAT2, STAT3, STAT4, STAT5, STAT6, STAT7, STAT8, STAT9, STAT0 = range(17, 27)
scores = {"warrior": 0, "mage": 0, "bard": 0}; score = []; base_choice = []; tabby = "";
statum = {"Agility": 2, "Endurance": 2, "Intellect": 2, "Perception": 2, "Strength": 2,
         "Focus": 2, "Spirit": 2, "Sense": 2, "Beyond": 2, "Charisma": 2}
classe = {"guerriero": 0, "arcere": 0, "monaco": 0, "mago": 0, "druido": 0, "chierico": 0, "bardo": 0}

warrior_ab = ["Usare armi taglienti", "Usare armi pesanti", "Usare armature leggere", "Usare armature pesanti",
              "Usare scudi", "Usare arco", "Usare balestre", "Usare attrezzi da fabbro", "Usare attrezzi da conciatore",
              "Usare attrezzi da falegname", "Usare attrezzi da macellaio", "Usare pugni come armi",
              "Usare I calci come armi", "Corpo temprato", "Corpo atletico"]

mage_ab = ["Leggere e scrivere rune magiche", "Percepire magia dagli esseri viventi", "Percepire magia da artefatti",
           "Conoscenze di animali", "Conoscenze di piante", "Conoscenze di terreni", "Conoscenza di simboli religiosi",
           "Conoscenza di pratiche religiose", "Conoscenze mediche", "Basi di alchimia", "Conoscenze culinarie",
           "Costruire marchingegni", "Basi di lingue arcane"]

bard_ab = ["Conoscenze di galateo", "Conoscenze di poesia", "Conoscenze in persuasione",
           "Usare strumenti musicali", "Conoscenze di comunicazione non verbale"]

basic = {"sesso": 1, "nome": "", }


def start_handler(update, context):
    global scores, score, base_choice, tabby, statum, classe
    # Creating a handler-function for /start command
    logger.info("User {} started bot".format(update.effective_user["id"]))
    update.message.reply_text("Benvenuto avventuriero, benvenuto nel percorso di creazione del personaggio, clicca"
                              " /descrizione per saperne di più")
    print(update.effective_user)

    scores = {"warrior": 0, "mage": 0, "bard": 0};
    score = [];
    base_choice = [];
    tabby = "";
    statum = {"Agility": 2, "Endurance": 2, "Intellect": 2, "Perception": 2, "Strength": 2,
              "Focus": 2, "Spirit": 2, "Sense": 2, "Beyond": 2, "Charisma": 2}
    classe = {"guerriero": 0, "arcere": 0, "monaco": 0, "mago": 0, "druido": 0, "chierico": 0, "bardo": 0}


def descrizione_handler(update, context):
    dd = "/pg inizializza la creazione di un nuovo personaggio\nin qualunque momento cliccando il comando /ricomincia" \
         " annullerai quanto stai facendo, inoltre ricordiamo che il bot" \
         " non ha memoria quindi se non si interagisce con esso per più di trenta minuti esso dimenticherà " \
         "tutto  :)\n/risposta risponde alla domanda fondamentale sulla vita l\'universo e tutto il resto"
    update.message.reply_text(dd)


def new_pg_handler(update, context):
    chat_id = update.effective_user["id"]
    # print(update.effective_user)  Thoomy_id 477049523  fergie_id 457408841
    context.bot.send_message(chat_id, "Ciao ora immedesimati nel tuo personaggio, ti trovi nel fantastico mondo di "
                                      "Chronos, luogo di magia e fantasia. "
                                      "\n\nora parliamo un po\' di te... ")
    keyboard = [["Bimbo"], ["Bimba"], ["Non è importante"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "sei un bimbo o una bimba? ", reply_markup=reply_markup)

    return SEX


def sex(update, context):
    global basic
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("sesso di %s: %s", user.first_name, update.message.text)
    if update.message.text == "Bimba":
        basic["sesso"] = 0

    context.bot.send_message(chat_id, '\nDimmi Come ti chiami...\n')

    return NAME


def name(update, context):
    global basic
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("nome di %s: %s", user.first_name, update.message.text)
    context.bot.send_message(chat_id, 'Bene... Allora ti chiami {}.'.format(update.message.text))
    basic["nome"] = update.message.text

    context.bot.send_message(chat_id, '\nOra {}, rispondi alle seguenti '
                                      'domande:'.format(update.message.text))
    keyboard = [["A) niente"], ["B) energia scorrere attraverso di me"], ["C) passi di persone intorno a me"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "Se chiudi gli occhi cosa senti?", reply_markup=reply_markup)

    return DOMANDA1


def domanda1(update, context):
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("%s risponde a domanda1: %s", user.first_name, update.message.text[0])
    if update.message.text[0] != "A":
        context.bot.send_message(chat_id, 'Quindi se chiudi gli occhi senti {}.'
                                          '\nBene...'.format(update.message.text[3:]))
    else:
        context.bot.send_message(chat_id, 'Quindi se chiudi gli occhi non senti niente.\nBene...')
    if update.message.text[0] == "A":
        scores["warrior"] += 1
    elif update.message.text[0] == "B":
        scores["mage"] += 1
    else:
        scores["bard"] += 1

    keyboard = [["A) callose con qualche taglio"], ["B) vellutate e pulite"], ["C) sporche di inchiostro"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "Come sono le tue mani?", reply_markup=reply_markup)

    return DOMANDA2


def domanda2(update, context):
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("%s risponde a domanda2: %s", user.first_name, update.message.text[0])
    context.bot.send_message(chat_id, 'Quindi le tue mani sono {}.\nBene...'.format(update.message.text[3:]))
    if update.message.text[0] == "A":
        scores["warrior"] += 1
    elif update.message.text[0] == "B":
        scores["bard"] += 1
    else:
        scores["mage"] += 1

    keyboard = [["A) un\'armatura a piastre chiaramente"], ["B) una comoda veste in lino"],
                ["C) la lunga e buia notte"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "Qual\'è il miglior outfit per viaggiare?", reply_markup=reply_markup)

    return DOMANDA3


def domanda3(update, context):
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("%s risponde a domanda3: %s", user.first_name, update.message.text[0])
    context.bot.send_message(chat_id, 'Quindi il miglior vestito per viaggiare secodo te  è {}.'
                                      '\nBene...'.format(update.message.text[3:]))
    if update.message.text[0] == "A":
        scores["warrior"] += 1
    elif update.message.text[0] == "B":
        scores["mage"] += 1
    else:
        scores["bard"] += 1

    keyboard = [["A) Bussare"], ["B) THIS IS SPARTA!"], ["C) entrare dalla finestra"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "Sei davanti a una porta, cosa ti senti di fare?", reply_markup=reply_markup)

    return DOMANDA4


def domanda4(update, context):
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("%s risponde a domanda4: %s", user.first_name, update.message.text[0])
    context.bot.send_message(chat_id, 'Quindi davanti a una porta tu ti senti di  {}.\nBene...'.format(
        update.message.text[3:]))
    if update.message.text[0] == "A":
        r = random.choice(["warrior", "mage"])
        scores[r] += 1
    elif update.message.text[0] == "B":
        scores["warrior"] += 1
    else:
        scores["mage"] += 1

    keyboard = [["A) chiaccherare al bancone"], ["B) flirtare a gamba tesa"], ["C) una sana rissa e le scommesse"
                                                                               " rinforzano le ossa"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "Qual\'è il tuo mood in taverna?", reply_markup=reply_markup)

    return DOMANDA5


def domanda5(update, context):
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("%s risponde a domanda5: %s", user.first_name, update.message.text[0])
    context.bot.send_message(chat_id, 'Quindi il tuo mood in taverna è: {}.\nEccellente...'.format(
        update.message.text[3:]))
    if update.message.text[0] == "A":
        scores["mage"] += 1
    elif update.message.text[0] == "B":
        scores["bard"] += 1
    else:
        scores["warrior"] += 1

    keyboard = [["A) la prestanza fisica è tutto"], ["B) la versatilità e l\'adattamento sono carte vincenti"],
                ["C) perchè combattere quando puoi parlamentare?"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "In combattimento...", reply_markup=reply_markup)

    return DOMANDA6


def domanda6(update, context):
    global score
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("%s risponde a domanda6: %s", user.first_name, update.message.text[0])
    context.bot.send_message(chat_id, 'Quindi in combattimento pensi che: {}.\nBene...'.format(
        update.message.text[3:]))
    if update.message.text[0] == "A":
        scores["warrior"] += 1
    elif update.message.text[0] == "B":
        scores["mage"] += 1
    else:
        scores["bard"] += 1

    keyboard = [["Umano"], ["Elfo"], ["Nano"], ["Mezz\'orco"], ["Elfo oscuro"], ["Dragonborn"], ["Hobbit"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "Quel\'è la razza del tuo personaggio? ", reply_markup=reply_markup)

    score = [j for j in ["warrior", "mage", "bard"] for i in range(scores[j])]
    print(scores)
    return DOMANDA7


def domanda7(update, context):
    global basic
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("Razza di %s: %s", user.first_name, update.message.text)
    basic["razza"] = update.message.text
    context.bot.send_message(chat_id, 'Ah quindi sei un {}.\nMolto bene, siamo quasi alla fine...'.format(
        update.message.text))
    time.sleep(4)
    context.bot.send_message(chat_id, "Molto bene ora passiamo alle cose serie, è arrivato il momento di scegliere "
                                      "delle abilità di base che caratterizzeranno il tuo personaggio: \nCominciamo!")
    if score[0] == "warrior":
        keyboard = [[i] for i in warrior_ab]
    elif score[0] == "mage":
        keyboard = [[i] for i in mage_ab]
    else:
        keyboard = [[i] for i in bard_ab]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "Scegli una delle seguenti opzioni: ", reply_markup=reply_markup)

    return AB1


def ab1(update, context):
    global base_choice
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("Prima abilità scelta da %s: %s", user.first_name, update.message.text)
    base_choice += [update.message.text]
    context.bot.send_message(chat_id, 'Hai scelto: {}.\nOra passiamo alla scelta successiva: '.format(update.message.text))

    if score[1] == "warrior":
        keyboard = [[i] for i in warrior_ab if i not in base_choice]
    elif score[1] == "mage":
        keyboard = [[i] for i in mage_ab if i not in base_choice]
    else:
        keyboard = [[i] for i in bard_ab if i not in base_choice]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "Scegli una delle seguenti opzioni: ", reply_markup=reply_markup)

    return AB2


def ab2(update, context):
    global base_choice
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("Seconda abilità scelta da %s: %s", user.first_name, update.message.text)
    base_choice += [update.message.text]
    context.bot.send_message(chat_id, 'Hai scelto: {}.\nOra passiamo alla prossima scelta: '.format(update.message.text))

    if score[2] == "warrior":
        keyboard = [[i] for i in warrior_ab if i not in base_choice]
    elif score[2] == "mage":
        keyboard = [[i] for i in mage_ab if i not in base_choice]
    else:
        keyboard = [[i] for i in bard_ab if i not in base_choice]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "Scegli una delle seguenti opzioni: ", reply_markup=reply_markup)

    return AB3


def ab3(update, context):
    global base_choice
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("Terza abilità scelta da %s: %s", user.first_name, update.message.text)
    base_choice += [update.message.text]
    context.bot.send_message(chat_id, 'Hai scelto: {}.\nOra passiamo alla scelta successiva: '.format(update.message.text))

    if score[3] == "warrior":
        keyboard = [[i] for i in warrior_ab if i not in base_choice]
    elif score[3] == "mage":
        keyboard = [[i] for i in mage_ab if i not in base_choice]
    else:
        keyboard = [[i] for i in bard_ab if i not in base_choice]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "Scegli una delle seguenti opzioni: ", reply_markup=reply_markup)

    return AB4


def ab4(update, context):
    global base_choice
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("Quarta abilità scelta da %s: %s", user.first_name, update.message.text)
    base_choice += [update.message.text]
    context.bot.send_message(chat_id, 'Hai scelto: {}.\nOra passiamo alla prossima scelta: '.format(update.message.text))

    if score[4] == "warrior":
        keyboard = [[i] for i in warrior_ab if i not in base_choice]
    elif score[4] == "mage":
        keyboard = [[i] for i in mage_ab if i not in base_choice]
    else:
        keyboard = [[i] for i in bard_ab if i not in base_choice]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "Scegli una delle seguenti opzioni: ", reply_markup=reply_markup)

    return AB5


def ab5(update, context):
    global base_choice
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("Quinta abilità scelta da %s: %s", user.first_name, update.message.text)
    base_choice += [update.message.text]
    context.bot.send_message(chat_id, 'Hai scelto: {}.\nOra passiamo alla scelta successiva, nonchè ultima: '.format(update.message.text))

    if score[5] == "warrior":
        keyboard = [[i] for i in warrior_ab if i not in base_choice]
    elif score[5] == "mage":
        keyboard = [[i] for i in mage_ab if i not in base_choice]
    else:
        keyboard = [[i] for i in bard_ab if i not in base_choice]

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "Scegli una delle seguenti opzioni: ", reply_markup=reply_markup)

    return AB6


def ab6(update, context):
    global base_choice, basic, classe
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("Sesta abilità scelta da %s: %s", user.first_name, update.message.text)
    base_choice += [update.message.text]
    context.bot.send_message(chat_id, 'Hai scelto: {}.\nOra passiamo alla prossima scelta: '.format(update.message.text))
    time.sleep(3)
    context.bot.send_message(chat_id, 'Scherzone, le abilità di base le hai scelte tutte e sono le seguenti: ')
    time.sleep(2)
    for ab in base_choice:
        context.bot.send_message(chat_id, ab)
    time.sleep(1)
    if basic["sesso"] == 1:
        context.bot.send_message(chat_id, "In base alle risposte che hai dato caro il mio {} la classe più adatta"
                                          " a te è: ".format(basic["nome"]))
    for i in range(7):
        context.bot.send_message(chat_id, "...")
        time.sleep(1)

    if warrior_ab[0] in base_choice:
        classe["guerriero"] += 1
    if warrior_ab[1] in base_choice:
        classe["guerriero"] += 1
    if warrior_ab[3] in base_choice:
        classe["guerriero"] += 1
    if warrior_ab[4] in base_choice:
        classe["guerriero"] += 1
    if warrior_ab[2] in base_choice:
        classe["arcere"] += 1
        classe["guerriero"] += 1
    if warrior_ab[5] in base_choice:
        classe["arcere"] += 1
    if warrior_ab[6] in base_choice:
        classe["arcere"] += 1
    if warrior_ab[11] in base_choice:
        classe["monaco"] += 1
    if warrior_ab[12] in base_choice:
        classe["monaco"] += 1
    if warrior_ab[13] in base_choice:
        classe["monaco"] += 1
    if warrior_ab[13] in base_choice:
        classe["monaco"] += 1
        classe["guerriero"] += 1
        classe["arcere"] += 1
    if warrior_ab[7] in base_choice or warrior_ab[8] in base_choice or warrior_ab[9] in base_choice or warrior_ab[10] in base_choice:
        classe["monaco"] += 1
        classe["guerriero"] += 1
        classe["arcere"] += 1
    if mage_ab[0] in base_choice:
        classe["mago"] += 1
    if mage_ab[1] in base_choice:
        classe["mago"] += 1
        classe["druido"] += 1
    if mage_ab[2] in base_choice:
        classe["mago"] += 1
        classe["chierico"] += 1
    if mage_ab[9] in base_choice:
        classe["mago"] += 1
    if mage_ab[12] in base_choice:
        classe["mago"] += 1
    if mage_ab[3] in base_choice:
        classe["druido"] += 1
    if mage_ab[4] in base_choice:
        classe["druido"] += 1
    if mage_ab[5] in base_choice:
        classe["druido"] += 1
    if mage_ab[6] in base_choice:
        classe["chierico"] += 1
    if mage_ab[7] in base_choice:
        classe["chierico"] += 1
    if mage_ab[8] in base_choice:
        classe["chierico"] += 1
    if bard_ab[3] in base_choice:
        classe["bardo"] += 2
    if bard_ab[0] in base_choice or bard_ab[1] in base_choice:
        classe["bardo"] += 1
    if bard_ab[2] in base_choice:
        classe["bardo"] += 1
    if bard_ab[4] in base_choice:
        classe["bardo"] += 1
    print(classe)
    valor = max(list(classe.values()))
    best = [i for i in classe.keys() if classe[i] == valor]
    if len(best) == 1:
        context.bot.send_message(chat_id, best[0])
    elif len(best) == 2:
        context.bot.send_message(chat_id, "C'è grande indecisione tra {} e {}. Scegli tu quella che ti ispira maggiormente".format(best[0], best[1]))
    else:
        context.bot.send_message(chat_id, "C'è grande indecisione tra {}, {} e {}. Scegli tu quella che ti ispira maggiormente ".format(best[0], best[1], best[2]))
    time.sleep(4)
    keyboard = [[i] for i in best]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "Ricordami che classe ti è stata assegnata: ", reply_markup=reply_markup)

    return RECAP


def recap(update, context):
    global basic, base_choice, tabby
    user = update.message.from_user
    chat_id = update.effective_user["id"]
    logger.info("classe assegnata a %s: %s", basic["nome"], update.message.text)
    basic["classe"] = update.message.text
    if basic["classe"] != "arcere":
        context.bot.send_message(chat_id, "Ah giusto il {}".format(basic["classe"]))
    else:
        context.bot.send_message(chat_id, "Ah giusto l\'arcere")
    for a in base_choice:
        tabby += a
        tabby += "\n"
    context.bot.send_message(chat_id, "Molto bene ora non rimane che scegliere le /statistiche del tuo personaggio :)")
    context.bot.send_message(477049523, "{} ha fatto metà creazione del suo personaggio, "
                                        "{}:\nLa classe è: {}\nLe abilità di base sono: {}.\nLe statistiche sono:"
                                        " da fare".format(update.effective_user["first_name"], basic["nome"], basic["classe"], tabby))

    return ConversationHandler.END

    #keyboard = [["A) callose con qualche taglio"], ["B) vellutate e pulite"], ["C) sporche di inchiostro"]]
    #reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    #context.bot.send_message(chat_id, "Come sono le tue mani?", reply_markup=reply_markup)

    #return COSE


def stats_handler(update, context):
    global basic, statum
    chat_id = update.effective_user["id"]
    context.bot.send_message(chat_id, "nella vita si sa cambiano tante cose, ed una di queste saranno le statistiche "
                                      "che useremo.. Di seguito una breve introduzione alle nuove statistiche, "
                                      "successivamente ti verrà chiesto di spendere 45 punti nelle varie statistiche, "
                                      "così da ottenerele statistiche iniziali del tuo personaggio. Ti anticipiamo che "
                                      "ogni statistica potrà avere un punteggio minimo di 2 e un punteggio massimo di "
                                      "7. Inoltre gli attributi sono 10, 5 tangibili e 5 intangibili. "
                                      "Buon divertimento :)")
    time.sleep(10)
    context.bot.send_message(chat_id, "Cominciamo dagli attributi tangibili:  ")
    context.bot.send_message(chat_id, "Gli attributi tangibili sono aspetti di un personaggio che possono essere "
                                      "misurati in modo empirico o quantificati. Questi sono aspetti che sono più "
                                      "facili da notare e riconoscere per gli altri.")
    time.sleep(2)
    context.bot.send_message(chat_id, "AGILITY:\nCompetenza nel controllo fisico. L\'agilità comprende flessibilità, "
                                      "destrezza, velocità, precisione e controllo del moto. ")
    time.sleep(5)
    context.bot.send_message(chat_id, "ENDURANCE:\nDurata e qualità fisica. Ciò comprende costruzione, "
                                      "affidabilità, fisico ed efficienza. ")
    time.sleep(5)
    context.bot.send_message(chat_id, "INTELLECT:\nCapacità di elaborazione delle informazioni empiriche. Può essere"
                                      " paragonato ad averemolte nonscenze riguardo libri, abilità computazionali e "
                                      "ragionamento logico.")
    time.sleep(5)
    context.bot.send_message(chat_id, "PERCEPTION:\nCapacità di raccogliere informazioni utili dai sensi empirici. "
                                      "I personaggi possono avere sensi che offrono una maggiore portata da cui "
                                      "rilevare, ma si affidano comunque alla percezione per rendere utili le "
                                      "informazioni sensoriali. Non importa quanto lontano puoi vedere, se riesci a "
                                      "elaborare solo quanto basta per individuare un bersaglio nelle vicinanze.")
    time.sleep(5)
    context.bot.send_message(chat_id, "STRENGTH:\nForza fisica e potenza. La forza può determinare la forza fisica di "
                                      "un personaggio in un colpo, la capacità di carico e l\'abilità di usare la "
                                      "forza bruta a dovere nelle situazioni. La forza determina la forza con cui "
                                      "puoi colpire, ma non la frequenza.")
    time.sleep(10)
    context.bot.send_message(chat_id, "Infine vediamo quelli intangibili:  ")
    context.bot.send_message(chat_id, "Gli attributi intangibili sono aspetti di un personaggio di natura qualitativa "
                                      "ed eterea. Sai che esistono, ma non puoi definirli correttamente. Molti di "
                                      "questi attributi sono difficili da discernere per gli altri, a meno che non "
                                      "si trovino in un estremo o nell'altro.")
    time.sleep(2)
    context.bot.send_message(chat_id, "FOCUS:\nCoordinamento, concentrazione e applicazione del sé. Una misura del "
                                      "controllo di un personaggio sull'equilibrio del corpo e della mente.")
    time.sleep(5)
    context.bot.send_message(chat_id, "SPIRIT:\nCoraggio, volontà, spirito combattivo e / o fede. "
                                      "Complementare intangibile di Endurance, che misura la capacità di un "
                                      "personaggio di perseverare.")
    time.sleep(5)
    context.bot.send_message(chat_id, "SENSE:\nL\'Anti-Intelletto: buon senso, saggezza e altri elementi di "
                                      "intelligenza. Una rappresentazione della mente di un personaggio plasmata "
                                      "dall\'esperienza, dalle dure lezioni e dall\'intuizione grezza.")
    time.sleep(5)
    context.bot.send_message(chat_id, "BEYOND:\nSentimenti viscerali, sesti sensi e percezioni al di là dell'empiria. "
                                      "La capacità di un personaggio di raccogliere informazioni utili da fonti "
                                      "non empiriche.")
    time.sleep(5)
    context.bot.send_message(chat_id, "CHARISMA:\nForza caratteriale. La capacità di un personaggio di influenzare gli "
                                      "altri, attirare l'attenzione o ispirare quelli a seguire l'esempio. Il carisma "
                                      "non è legato all'aspetto fisico, ma alla presenza.")
    time.sleep(5)
    if basic["sesso"] != 0:
        context.bot.send_message(chat_id, "bene, ora dovresti essere scombussolato a sufficienza, per questo avrai un "
                                          "attimo per riflettere a come spalmare i 45 punti abilità nei 10 attributi, "
                                          "ricordando che minimo 2 massimo 7 per ogni attributo. tra un po\' comparirà "
                                          "un messaggio che ti chiederà quanti punti vuoi mettere in ogni abilità. una "
                                          "volta assegnati i punti a tutte le abilità verranno effettuati i controlli "
                                          "sul tutale. se va tutto bene ti manderemo un messaggio "
                                          "di conferma con tutti i dati del tuo personaggio. Enjoy :)")
        time.sleep(60)
    else:
        context.bot.send_message(chat_id, "bene, ora dovresti essere scombussolata a sufficienza, per questo avrai un "
                                          "attimo per riflettere a come spalmare i 45 punti abilità nei 10 attributi, "
                                          "ricordando che minimo 2 massimo 7 per ogni attributo. tra un po\' comparirà "
                                          "un messaggio che ti chiederà quanti punti vuoi mettere in ogni abilità. una "
                                          "volta assegnati i punti a tutte le abilità verranno effettuati i controlli "
                                          "sul tutale. se va tutto bene ti manderemo un messaggio "
                                          "di conferma con tutti i dati del tuo personaggio. Enjoy :)")
        time.sleep(60)
    context.bot.send_message(chat_id, "Molto bene cominciamo:  ")
    time.sleep(2)

    keyboard = [[str(i)] for i in range(2, 8)]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "AGILITY", reply_markup=reply_markup)

    return STAT1


def stat1(update, context):
    global basic, statum
    chat_id = update.effective_user["id"]
    logger.info("Agility di {}: {}".format(basic["nome"], update.message.text))
    context.bot.send_message(chat_id, "Bene il tuo punteggio di agility è: {}".format(update.message.text))
    statum["Agility"] = int(update.message.text)
    time.sleep(3)
    keyboard = [[str(i)] for i in range(2, 8)]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "ENDURANCE", reply_markup=reply_markup)

    return STAT2


def stat2(update, context):
    global basic, statum
    chat_id = update.effective_user["id"]
    logger.info("Endurance di {}: {}".format(basic["nome"], update.message.text))
    context.bot.send_message(chat_id, "Bene il tuo punteggio di endurance è: {}".format(update.message.text))
    statum["Endurance"] = int(update.message.text)
    time.sleep(3)
    keyboard = [[str(i)] for i in range(2, 8)]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "INTELLECT", reply_markup=reply_markup)

    return STAT3


def stat3(update, context):
    global basic, statum
    chat_id = update.effective_user["id"]
    logger.info("Intellect di {}: {}".format(basic["nome"], update.message.text))
    context.bot.send_message(chat_id, "Bene il tuo punteggio di intellect è: {}".format(update.message.text))
    statum["Intellect"] = int(update.message.text)
    time.sleep(3)
    keyboard = [[str(i)] for i in range(2, 8)]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "PERCEPTION", reply_markup=reply_markup)

    return STAT4


def stat4(update, context):
    global basic, statum
    chat_id = update.effective_user["id"]
    logger.info("Perception di {}: {}".format(basic["nome"], update.message.text))
    context.bot.send_message(chat_id, "Bene il tuo punteggio di perception è: {}".format(update.message.text))
    statum["Perception"] = int(update.message.text)
    time.sleep(3)
    keyboard = [[str(i)] for i in range(2, 8)]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "STRENGTH", reply_markup=reply_markup)

    return STAT5


def stat5(update, context):
    global basic, statum
    chat_id = update.effective_user["id"]
    logger.info("Strength di {}: {}".format(basic["nome"], update.message.text))
    context.bot.send_message(chat_id, "Bene il tuo punteggio di strength è: {}".format(update.message.text))
    statum["Strength"] = int(update.message.text)
    time.sleep(3)
    keyboard = [[str(i)] for i in range(2, 8)]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "FOCUS", reply_markup=reply_markup)

    return STAT6


def stat6(update, context):
    global basic, statum
    chat_id = update.effective_user["id"]
    logger.info("Focus di {}: {}".format(basic["nome"], update.message.text))
    context.bot.send_message(chat_id, "Bene il tuo punteggio di focus è: {}".format(update.message.text))
    statum["Focus"] = int(update.message.text)
    time.sleep(3)
    keyboard = [[str(i)] for i in range(2, 8)]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "SPIRIT", reply_markup=reply_markup)

    return STAT7


def stat7(update, context):
    global basic, statum
    chat_id = update.effective_user["id"]
    logger.info("Spirit di {}: {}".format(basic["nome"], update.message.text))
    context.bot.send_message(chat_id, "Bene il tuo punteggio di spirit è: {}".format(update.message.text))
    statum["Spirit"] = int(update.message.text)
    time.sleep(3)
    keyboard = [[str(i)] for i in range(2, 8)]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "SENSE", reply_markup=reply_markup)

    return STAT8


def stat8(update, context):
    global basic, statum
    chat_id = update.effective_user["id"]
    logger.info("Sense di {}: {}".format(basic["nome"], update.message.text))
    context.bot.send_message(chat_id, "Bene il tuo punteggio di sense è: {}".format(update.message.text))
    statum["Sense"] = int(update.message.text)
    time.sleep(3)
    keyboard = [[str(i)] for i in range(2, 8)]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "BEYOND", reply_markup=reply_markup)

    return STAT9


def stat9(update, context):
    global basic, statum
    chat_id = update.effective_user["id"]
    logger.info("Beyond di {}: {}".format(basic["nome"], update.message.text))
    context.bot.send_message(chat_id, "Bene il tuo punteggio di beyond è: {}".format(update.message.text))
    statum["Beyond"] = int(update.message.text)
    time.sleep(3)
    keyboard = [[str(i)] for i in range(2, 8)]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id, "CHARISMA", reply_markup=reply_markup)

    return STAT0


def stat0(update, context):
    global basic, statum, tabby
    chat_id = update.effective_user["id"]
    logger.info("Charisma di {}: {}".format(basic["nome"], update.message.text))
    context.bot.send_message(chat_id, "Bene il tuo punteggio di charisma è: {}".format(update.message.text))
    statum["Charisma"] = int(update.message.text)
    time.sleep(3)
    if sum(list(statum.values())) == 45:  # controllo
        if basic["razza"] == "Elfo":
            statum["Agility"] += 1
            statum["Endurance"] -= 1
        if basic["razza"] == "Mezz\'orco":
            statum["Strength"] += 1
            statum["Intellect"] -= 1
        if basic["razza"] == "Nano":
            statum["Spirit"] += 1
            statum["Beyond"] -= 1
        if basic["razza"] == "Elfo oscuro":
            statum["Intellect"] += 1
            statum["Strength"] -= 1
        if basic["razza"] == "Dragonborn":
            statum["Endurance"] += 1
            statum["Charisma"] -= 1
        if basic["razza"] == "Hobbit":
            statum["Sense"] += 1
            statum["Agility"] -= 1
        context.bot.send_message(chat_id, "Bene {} è ora tra noi, o lo sarà a breve, intanto ti mandiamo il "
                                          "riepilogo di tutto. A venerdì :)".format(basic["nome"]))
        time.sleep(5)
        stst = ""
        for i in statum.keys():
            stst += "\n"+i+":  "+str(statum[i])

        for cc in [477049523, 457408841, chat_id]:
            context.bot.send_message(cc, "{} ha appena finito la creazione del suo personaggio, {}:\nLa classe è: {}"
                                         "\nLe abilità di base sono: \n{}\nLe statistiche sono:"
                                         " {}".format(update.effective_user["first_name"], basic["nome"],
                                                      basic["classe"], tabby, stst))
    else:
        context.bot.send_message(chat_id, "MI spiace ma la somma non è 45 bensì "
                                          ""+str(sum(list(statum.values())))+"\nErgo devi ricominciare. "
                                                                             "clicca /statistiche")
        return ConversationHandler.END


def answer_handler(update, context):
    # Creating a handler-function for /stupid command
    number = random.randint(0, 10)
    logger.info("User {} randomed number {}".format(update.effective_user["id"], number))
    if number % 2 == 0:
        update.message.reply_text("scemo chi legge")
    else:
        update.message.reply_text("42")


def ricomincia(update, context):
    global scores, score, base_choice, tabby, statum, classe
    user = update.message.from_user
    logger.info("User %s clear the work.", user.first_name)
    update.message.reply_text('pulito e annullato tutto', reply_markup=ReplyKeyboardRemove())
    scores = {"warrior": 0, "mage": 0, "bard": 0};
    score = [];
    base_choice = [];
    tabby = "";
    statum = {"Agility": 2, "Endurance": 2, "Intellect": 2, "Perception": 2, "Strength": 2,
              "Focus": 2, "Spirit": 2, "Sense": 2, "Beyond": 2, "Charisma": 2}
    classe = {"guerriero": 0, "arcere": 0, "monaco": 0, "mago": 0, "druido": 0, "chierico": 0, "bardo": 0}

    return ConversationHandler.END


def clearing(update, context):
    global scores, score, base_choice, tabby, statum, classe
    user = update.message.from_user
    logger.info("User %s clear the work.", user.first_name)
    update.message.reply_text('pulito e annullato tutto', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(CommandHandler("descrizione", descrizione_handler))
    updater.dispatcher.add_handler(CommandHandler("risposta", answer_handler))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('pg', new_pg_handler)],

        states={
            SEX: [MessageHandler(Filters.regex('^(Bimbo|Bimba|Non)'), sex)],

            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],

            DOMANDA1: [MessageHandler(Filters.regex('^(A|B|C)'), domanda1)],

            DOMANDA2: [MessageHandler(Filters.regex('^(A|B|C)'), domanda2)],

            DOMANDA3: [MessageHandler(Filters.regex('^(A|B|C)'), domanda3)],

            DOMANDA4: [MessageHandler(Filters.regex('^(A|B|C)'), domanda4)],

            DOMANDA5: [MessageHandler(Filters.regex('^(A|B|C)'), domanda5)],

            DOMANDA6: [MessageHandler(Filters.regex('^(A|B|C)'), domanda6)],

            DOMANDA7: [MessageHandler(Filters.regex('^(Umano|Elfo|Nano|Mezz\'orco|Elfo oscuro|Dragonborn|Hobbit)'),
                                      domanda7)],
            AB1: [MessageHandler(Filters.regex('^(U|C|L|P|B)'), ab1)],

            AB2: [MessageHandler(Filters.regex('^(U|C|L|P|B)'), ab2)],

            AB3: [MessageHandler(Filters.regex('^(U|C|L|P|B)'), ab3)],

            AB4: [MessageHandler(Filters.regex('^(U|C|L|P|B)'), ab4)],

            AB5: [MessageHandler(Filters.regex('^(U|C|L|P|B)'), ab5)],

            AB6: [MessageHandler(Filters.regex('^(U|C|L|P|B)'), ab6)],

            RECAP: [MessageHandler(Filters.regex('^(guerriero|arcere|monaco|mago|druido|chierico|bardo)'), recap)]
        },

        fallbacks=[CommandHandler('ricomincia', ricomincia)]
    )

    conv_handler2 = ConversationHandler(
        entry_points=[CommandHandler('statistiche', stats_handler)],

        states={
            STAT1: [MessageHandler(Filters.regex('^(2|3|4|5|6|7)'), stat1)],

            STAT2: [MessageHandler(Filters.regex('^(2|3|4|5|6|7)'), stat2)],

            STAT3: [MessageHandler(Filters.regex('^(2|3|4|5|6|7)'), stat3)],

            STAT4: [MessageHandler(Filters.regex('^(2|3|4|5|6|7)'), stat4)],

            STAT5: [MessageHandler(Filters.regex('^(2|3|4|5|6|7)'), stat5)],

            STAT6: [MessageHandler(Filters.regex('^(2|3|4|5|6|7)'), stat6)],

            STAT7: [MessageHandler(Filters.regex('^(2|3|4|5|6|7)'), stat7)],

            STAT8: [MessageHandler(Filters.regex('^(2|3|4|5|6|7)'), stat8)],

            STAT9: [MessageHandler(Filters.regex('^(2|3|4|5|6|7)'), stat9)],

            STAT0: [MessageHandler(Filters.regex('^(2|3|4|5|6|7)'), stat0)]
        },
        fallbacks=[CommandHandler('clear', clearing)]
    )

    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(conv_handler2)

    run(updater)
