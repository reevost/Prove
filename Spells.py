import os, time
os.getcwd()


class Spell:
    def __init__(self, nome, costo, turni, raggio, danno, scuola, descrizione):
        self.nome = nome
        self.costo = costo
        self.turni = turni
        self.raggio = raggio
        self.danno = danno
        self.scuola = scuola
        self.descrizione = descrizione

    def wrisp(self):
        return self.nome+"\t"+self.costo+"\t"+self.turni+"\t"+self.raggio+"\t"+self.danno+"\t"+self.scuola+"\t"+self.descrizione+"\n"

    def rapp(self):
        dd = ""
        for i in range(1+len(self.descrizione)//140):
            dd += self.descrizione[140*i: 140*(i+1)]+"\n"
        stt = self.nome.upper()+"\n"+"Costo: "+self.costo+"\n"+"Turni: "+self.turni+"\n"+"Raggio: "+self.raggio+\
              "\n"+"Danno: "+self.danno+"\n"+"Scuola: "+self.scuola+"\n\n"+dd
        return stt


file1 = open("spell.txt", "r")
spells = file1.readlines()
file1.close()

spellbook = {}

for strspell in spells:
    listspell = strspell.split("\t")
    spellbook[listspell[0]] = Spell(listspell[0], listspell[1], listspell[2], listspell[3], listspell[4], listspell[5], listspell[6])


flag = int(input("vuoi aggiungere una spell? (1/0): "))
if flag == 1:
    while flag == 1:
        print("inseriamo una nuova spell")
        nome = input("inserisci il nome della spell: ")
        costo = input("inserisci il costo della spell: ")
        turni = input("inserisci il numero di turni necessari per castare la spell: ")
        raggio = input("inserisci il raggio della spell: ")
        danno = input("inserisci il danno della spell: ")
        scuola = input("inserisci la scuola della spell: ")
        descrizione = input("inserisci la descrizione della spell: ")

        ok = int(input("sei sicuro che vada tutto bene? (1/0): "))
        if ok == 1:
            s = Spell(nome, costo, turni, raggio, danno, scuola, descrizione)
            spellbook[nome] = s
            file2 = open("spell.txt", "a")
            file2.write(s.wrisp())
            file2.close()

            flag = input("vuoi aggiungere un'altra spell? (1/0): ")
        else:
            flag = 1

view = input("vuoi visualizzare una spell? (1/0): ")
while view == "1":
    spname = input("inserisci il nome della spell: ")
    if spname in spellbook.keys():
        print("\n")
        print(spellbook[spname].rapp())
    else:
        print("spell non presente")

    time.sleep(2)
    view = input("vuoi visualizzare un\'altra spell? (1/0): ")

