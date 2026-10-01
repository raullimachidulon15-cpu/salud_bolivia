"""Procesamiento de texto clínico básico."""
import unicodedata, re

DICCIONARIO_SINTOMAS = {
    "dolor de cabeza":"Neurología","migraña":"Neurología","mareo":"Neurología",
    "dolor de pecho":"Cardiología","corazon":"Cardiología","presion":"Cardiología",
    "tos":"Neumología","respirar":"Neumología","asma":"Neumología",
    "fiebre":"Medicina General","gripe":"Medicina General","resfriado":"Medicina General",
    "estomago":"Gastroenterología","diarrea":"Gastroenterología","vomito":"Gastroenterología",
    "hueso":"Traumatología","fractura":"Traumatología","esguince":"Traumatología",
    "vista":"Oftalmología","ojo":"Oftalmología","oido":"Otorrinolaringología",
    "garganta":"Otorrinolaringología","diente":"Odontología","muela":"Odontología",
    "embarazo":"Ginecología","menstruacion":"Ginecología","depresion":"Psicología",
    "ansiedad":"Psicología","estres":"Psicología","nino":"Pediatría","bebe":"Pediatría",
}
VACIAS = {"de","la","el","los","las","un","una","y","o","que","porque","necesito",
          "quiero","me","mi","con","para","es","tengo","saber","debo","medico","doctor"}

def normalizar(texto):
    texto = unicodedata.normalize("NFD", str(texto).lower().strip())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")

def contar_palabras(texto):
    return len(re.findall(r"\b\w+\b", str(texto)))

def extraer_palabras_clave(texto, maximo=8):
    palabras = re.findall(r"\b\w+\b", normalizar(texto))
    return list(dict.fromkeys(p for p in palabras if len(p)>2 and p not in VACIAS))[:maximo]

def extraer_palabras(texto, maximo=8):
    return extraer_palabras_clave(texto, maximo)

def clasificar_consulta(texto):
    t = " " + normalizar(texto) + " "
    return list(dict.fromkeys(
        especialidad for frase, especialidad in DICCIONARIO_SINTOMAS.items()
        if normalizar(frase) in t
    ))

def casificar_consulta(texto):
    return clasificar_consulta(texto)
