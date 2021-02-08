import copy
import sys
import time
sys.setrecursionlimit(10**6) #DACA BUM NO BUM

class NodParcurgere:
    def __init__(self, info, parinte, cost_g=0, cost_h=0):
        self.info = info
        self.parinte = parinte
        self.cost_g = cost_g
        self.cost_h = cost_h
        self.cost_f = self.cost_g + self.cost_h

    def obtineDrum(self):
        drum = [self]
        nod = self
        while nod.parinte is not None:
            drum.insert(0, nod.parinte)
            nod = nod.parinte
        return drum

    def afiseazaDrum(self, startTime):
        drum = self.obtineDrum()
        sir = ""
        sir += "Cost: %d\n" % self.cost_g
        sir += "Lungime: %d\n" % len(drum)
        curentTime = time.time()
        sir += "Timp: %.3f ms\n" % ((curentTime - startTime) * 1000)
        for idx in range(len(drum)):
            sir += "%d)\n" % (idx + 1)
            sir += str(drum[idx])
        sir += "============================\n"
        return sir

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if infoNodNou == nodDrum.info:
                return True
            nodDrum = nodDrum.parinte
        return False

    def __str__(self):
        sir = ""
        for stiva in self.info:
            for bloc in stiva:
                sir += "[" + bloc[0] + "/" + bloc[1] + "/" + bloc[2] + "] "
            sir += "\n"
        return sir


class Graph:
    def __init__(self, fisierDeIntrare, fisierDeIesire):
        def obtineStive(sir):
            stiveSiruri = sir.strip().split("\n")
            listaStiveSiruri = [sirStiva.strip().split("|") if sirStiva != "_" else [] for sirStiva in stiveSiruri]
            listaStive = []
            for listaStivaSir in listaStiveSiruri:
                stiva = []
                for blocSir in listaStivaSir:
                    stiva.append(blocSir.strip().split(","))
                if self.esteStivaValida(stiva):
                    listaStive.append(stiva)
                else:
                    print("Configuratie invalida")
                    exit(0)
            return listaStive

        f = open(fisierDeIntrare, 'r')
        continutFisier = f.read()
        self.start = obtineStive(continutFisier)
        self.fisierDeIesire = open(fisierDeIesire, 'w')

    def testeaza_scop(self, stive):
        nr_blocuri_in_stare_finala = self.nrBlocuriInStareaFinala(stive)
        for stiva in stive:
            if len(stiva) != nr_blocuri_in_stare_finala and len(stiva) != nr_blocuri_in_stare_finala + 1:
                return False
        return True

    def nrBlocuriInStareaFinala(self, stive):
        nr_blocuri = sum(len(stiva) for stiva in stive)
        nr_blocuri_echilibrate = int(nr_blocuri / len(stive))
        return nr_blocuri_echilibrate

    def genereazaSuccesori(self, nodCurent, euristica="euristica_banala"):
        listaSuccessori = []
        stive_curente = nodCurent.info
        nr_stive = len(stive_curente)
        for idx in range(nr_stive):
            copie_intermediara = copy.deepcopy(stive_curente)
            if len(copie_intermediara[idx]) == 0:
                continue
            bloc = copie_intermediara[idx].pop()
            for j in range(nr_stive):
                # nu consideram acelasi index
                if idx == j:
                    continue
                stive_noi = copy.deepcopy(copie_intermediara)
                stive_noi[j].append(bloc)
                if self.esteStivaValida(stive_noi[j]) and not nodCurent.contineInDrum(stive_noi):
                    costMutareBloc = int(bloc[1])
                    nod_nou = NodParcurgere(stive_noi, nodCurent,
                                            cost_g=nodCurent.cost_g + costMutareBloc,
                                            cost_h=self.calculeaza_cost_h(stive_noi, euristica))
                    listaSuccessori.append(nod_nou)
        return listaSuccessori

    def esteStivaValida(self, stiva):
        greutate = 0
        for bloc in stiva[::-1]:
            if greutate > int(bloc[2]):
                return False
            greutate += int(bloc[1])
        return True

    def calculeaza_cost_h(self, stive, euristica="euristica_banala"):
        if euristica == "euristica_banala":
            if self.testeaza_scop(stive):
                return 0
            return 1
        nr_blocuri = sum(len(stiva) for stiva in stive)
        nr_blocuri_in_stare_finala = int(nr_blocuri / len(stive))
        if euristica == "euristica_avansata":
            if nr_blocuri % len(stive) != 0:
                nr_blocuri_in_stare_finala += 1
        return self.calculeaza_cost_h_avansat(stive, nr_blocuri_in_stare_finala)

    def calculeaza_cost_h_avansat(self, stive, nr_blocuri_in_stare_finala):
        cost_h = 0
        for stiva in stive:
            if len(stiva) <= nr_blocuri_in_stare_finala:
                continue
            nr_blocuri_de_mutat = len(stiva) - nr_blocuri_in_stare_finala
            for bloc in stiva[::-1]:
                if nr_blocuri_de_mutat == 0:
                    break
                nr_blocuri_de_mutat -= 1
                cost_h += int(bloc[1])
        return cost_h

####################
# ALGORITM BF
####################
def breadth_first(graph, nrSolutiiCautate, timeout):
    startTime = time.time()
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(graph.start, None, 0, graph.calculeaza_cost_h(graph.start))]

    while len(c) > 0:
        curentTime = time.time()
        if (curentTime - startTime) * 1000 > timeout:
            print("Am intrat in timeout.")
            return
        nodCurent = c.pop(0)

        if graph.testeaza_scop(nodCurent.info):
            graph.fisierDeIesire.write("Solutie Breadth First:\n")
            graph.fisierDeIesire.write(nodCurent.afiseazaDrum(startTime))
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        succesori = graph.genereazaSuccesori(nodCurent)
        c.extend(succesori)


####################
# ALGORITM DF
####################
def depth_first(graph, nrSolutiiCautate, timeout):
    startTime = time.time()
    # vom simula o stiva prin relatia de parinte a nodului curent
    df(NodParcurgere(graph.start, None, 0, graph.calculeaza_cost_h(graph.start)),
       nrSolutiiCautate, startTime, timeout)


def df(nodCurent, nrSolutiiCautate, startTime, timeout):
    curentTime = time.time()
    if (curentTime - startTime) * 1000 > timeout:
        print("Am intrat in timeout.")
        return 0
    if nrSolutiiCautate == 0:  # testul acesta s-ar valida doar daca in apelul initial avem df(start,if nrSolutiiCautate=0)
        return nrSolutiiCautate
    if graph.testeaza_scop(nodCurent.info):
        graph.fisierDeIesire.write("Solutie Depth First:\n")
        graph.fisierDeIesire.write(nodCurent.afiseazaDrum(startTime))
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return nrSolutiiCautate
    succesori = graph.genereazaSuccesori(nodCurent)
    for succesor in succesori:
        if nrSolutiiCautate != 0:
            nrSolutiiCautate = df(succesor, nrSolutiiCautate, startTime, timeout)
    return nrSolutiiCautate



####################
# ALGORITM DFI
####################
def depth_first_iterativ(graph, nrSolutiiCautate, timeout):
    startTime = time.time()
    for adancime in range(1, 20):
        if nrSolutiiCautate == 0:
            return
        nrSolutiiCautate = dfi(NodParcurgere(graph.start, None, 0, graph.calculeaza_cost_h(graph.start)),
                               adancime, nrSolutiiCautate, startTime, timeout)



def dfi(nodCurent, adancime, nrSolutiiCautate, startTime, timeout):
    curentTime = time.time()
    if (curentTime - startTime) * 1000 > timeout:
        print("Am intrat in timeout.")
        return 0
    if adancime == 1 and graph.testeaza_scop(nodCurent.info):
        graph.fisierDeIesire.write("Solutie Depth First Iterativ:\n")
        graph.fisierDeIesire.write(nodCurent.afiseazaDrum(startTime))
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return nrSolutiiCautate
    if adancime > 1:
        succesori = graph.genereazaSuccesori(nodCurent)
        for succcesor in succesori:
            if nrSolutiiCautate != 0:
                nrSolutiiCautate = dfi(succcesor, adancime - 1, nrSolutiiCautate, startTime, timeout)
    return nrSolutiiCautate


####################
# ALGORITM UCS
####################
def uniform_cost(graph, nrSolutiiCautate, timeout):
    startTime = time.time()
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(graph.start, None, 0, graph.calculeaza_cost_h(graph.start))]
    
    while len(c) > 0:
        curentTime = time.time()
        if (curentTime - startTime) * 1000 > timeout:
            print("Am intrat in timeout.")
            return
        nodCurent = c.pop(0)

        if graph.testeaza_scop(nodCurent.info):
            graph.fisierDeIesire.write("Solutie Uniform Cost:\n")
            graph.fisierDeIesire.write(nodCurent.afiseazaDrum(startTime))
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        succesori = graph.genereazaSuccesori(nodCurent)
        for successor in succesori:
            i = 0
            gasit_loc = False
            
            for i in range(len(c)):
                # diferenta e ca ordonez dupa cost
                if c[i].cost_g > successor.cost_g:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, successor)
            else:
                c.append(successor)


####################
# ALGORITM A*
####################
def a_star(graph, nrSolutiiCautate, timeout, euristica):
    startTime = time.time()
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(graph.start, None, 0, graph.calculeaza_cost_h(graph.start, euristica))]

    while len(c) > 0:
        curentTime = time.time()
        if (curentTime - startTime) * 1000 > timeout:
            print("Am intrat in timeout.")
            return
        nodCurent = c.pop(0)

        if graph.testeaza_scop(nodCurent.info):
            graph.fisierDeIesire.write("Solutie A* %s:\n" % euristica)
            graph.fisierDeIesire.write(nodCurent.afiseazaDrum(startTime))
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        succesori = graph.genereazaSuccesori(nodCurent, euristica)
        for successor in succesori:
            i = 0
            gasit_loc = False
            
            for i in range(len(c)):
                # diferenta fata de UCS e ca ordonez dupa o functie scor
                if c[i].cost_f > successor.cost_f:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, successor)
            else:
                c.append(successor)

def greedy(graph, nrSolutiiCautate, timeout, euristica):
    startTime = time.time()
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(graph.start, None, 0, graph.calculeaza_cost_h(graph.start, euristica))]

    while len(c) > 0:
        curentTime = time.time()
        if (curentTime - startTime) * 1000 > timeout:
            print("Am intrat in timeout.")
            return
        nodCurent = c.pop(0)

        if graph.testeaza_scop(nodCurent.info):
            graph.fisierDeIesire.write("Solutie Greedy %s:\n" % euristica)
            graph.fisierDeIesire.write(nodCurent.afiseazaDrum(startTime))
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        succesori = graph.genereazaSuccesori(nodCurent, euristica)
        for successor in succesori:
            i = 0
            gasit_loc = False
            
            for i in range(len(c)):
                # diferenta fata de UCS e ca ordonez dupa o functie scor
                if c[i].cost_h > successor.cost_h:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, successor)
            else:
                c.append(successor)


if (len(sys.argv) != 5):
    print("Ne asteptam sa avem 4 parametrii indicati.")
    exit(0)

fisierDeIntrare = sys.argv[1]
fisierDeIesire = sys.argv[2]
nrSolutiiCautate = int(sys.argv[3])
timeout = float(sys.argv[4])

graph = Graph(fisierDeIntrare, fisierDeIesire)

# Rezolvat cu breadth first
print("Breadth first")
breadth_first(graph, nrSolutiiCautate, timeout)

# Rezolvat cu depth first
print("Depth first")
depth_first(graph, nrSolutiiCautate, timeout)

# Rezolvat cu depth first iterativ
print("Depth first iterativ")
depth_first_iterativ(graph, nrSolutiiCautate, timeout)

# Rezolvat cu uniform cost
print("Uniform cost")
uniform_cost(graph, nrSolutiiCautate, timeout)

# Rezolvat cu a star
print("A* euristica banala")
a_star(graph, nrSolutiiCautate, timeout, "euristica_banala")
print("A* euristica avansata")
a_star(graph, nrSolutiiCautate, timeout, "euristica_avansata")

#Rezolvat cu greedy
print("Greedy euristica banala")
greedy(graph, nrSolutiiCautate, timeout, "euristica_banala")
print("Greedy euristica avansata")
greedy(graph, nrSolutiiCautate, timeout, "euristica_avansata")
