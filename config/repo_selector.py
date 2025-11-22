import os

BASE_DIR = r"C:\Users\danie\Desktop\Proyectos\Funcionan"   #Define carpeta donde se buscan los repos en modo raw string(r"") para evitar problemas con barras invertidas\


def es_repo_git(path):
    return os.path.isdir(os.path.join(path, ".git"))       #Verifica que carpetas contienen la carpeta .git dentro de BASE_DIR y construye las rutas para que obtener_repositorios las recorra


def obtener_repositorios() -> dict | None:                 #Define la función que devuelve un diccionario de repositorios o None
    
    repos = {                                                                                             #Crea un diccionario con todos los repositorios detectados
        str(idx): os.path.join(BASE_DIR, folder)                                                          #Clave = índice como string, Valor = ruta completa del folder
        for idx, folder in enumerate(os.listdir(BASE_DIR), start=1)                                       #Itera sobre todas las carpetas en BASE_DIR con índice
        if os.path.isdir(os.path.join(BASE_DIR, folder)) and es_repo_git(os.path.join(BASE_DIR, folder))  #Solo agrega carpetas que sean directorios y contengan .git
    }
    return repos or None                                                                                  #Devuelve el diccionario si tiene elementos, si no devuelve None

