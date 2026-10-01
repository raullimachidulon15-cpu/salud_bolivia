class NodoColaP:
    def __init__(self,dato,prioridad):
        self.dato=dato
        self.prioridad=prioridad
        self.sig=None
        self.ant=None
class ColaPrioridad:
    def __init__(self):
        self.frente=None
        self.fin=None

    def encolar(self, dato, prioridad):
        nuevo =NodoColaP(dato,prioridad)
        if self.esta_vacio():
            self.frente= nuevo
            self.fin = nuevo
        else:
                self.fin.sig = nuevo
                nuevo.ant= self.fin
                self.fin=nuevo
        self.subirCola(self.fin)

    def subirCola(self, nodo):
        while nodo.ant is not None and nodo.prioridad < nodo.ant.prioridad:
            prev = nodo.ant
            A = prev.ant    # nodo antes del par
            B = nodo.sig    # nodo después del par (normalmente None si es el último)
            # reconectar el intercambio:  A <-> prev <-> nodo <-> B
            #queda como:                 A <-> nodo <-> prev <-> B
            prev.sig = B
            prev.ant = nodo
            nodo.ant = A
            nodo.sig = prev
            if A is not None:
                A.sig = nodo
            else:
                self.frente = nodo      # el nodo llegó al frente
            if B is not None:
                B.ant = prev
            else:
                self.fin = prev         # prev quedó como último

    def desencolar(self):
        res = None
        if not self.esta_vacio():
            res = self.frente.dato
            self.frente = self.frente.sig
            if self.frente is not None:
                self.frente.ant= None
        if self.frente is None:
            self.fin = None
        return res 
    def esta_vacio(self):
        return self.frente is None and self.fin is None
    
    def __len__(self):
        contador = 0
        aux = self.frente
        while aux is not None:
            contador += 1
            aux = aux.sig
        return contador
         
    def ordenar(self):
        datos=[]
        aux =self.frente
        while aux is not None:
            datos.append(aux.dato)
            aux =aux.sig 
        return datos
    
    def mostrar(self):
        self.aux=self.frente
        while self.aux is not None:
            print("DATO = ",self.aux.dato, "PRIORIDAD = ",self.aux.prioridad) 
            self.aux= self.aux.sig
        return