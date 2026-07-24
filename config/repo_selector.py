# =========== #
# 📦 IMPORTS #
# ========== #
import os


# ====================== #
# ⚙️ CONFIGURACIÓN BASE #
# ===================== #
# Ruta donde se buscan los repositorios Git
BASE_DIR = r"C:\Users\danie\Desktop\Proyectos\JAVA"


# =============================== #
# 🔍 VALIDACIÓN: REPOSITORIO GIT #
# ============================== #
def es_repo_git(path):
    """
    Verifica si una carpeta contiene un repositorio Git
    (presencia de la carpeta .git)
    """
    return os.path.isdir(os.path.join(path, ".git"))


# ======================================= #
# 📁 DISCOVERY: REPOSITORIOS DISPONIBLES #
# ====================================== #
def obtener_repositorios() -> dict | None:
    """
    Busca repositorios dentro de BASE_DIR

    RETORNA:
        dict {
            "1": "ruta_repo_1",
            "2": "ruta_repo_2",
            ...
        }
        o None si no hay repos
    """

    # ------------------------- #
    # 🔄 ESCANEO DE DIRECTORIO #
    # ------------------------ #
    repos = {
        str(idx): os.path.join(BASE_DIR, folder)

        for idx, folder in enumerate(
            os.listdir(BASE_DIR),
            start=1
        )

        # 📌 FILTRO:
        # - debe ser carpeta
        # - debe contener .git
        if os.path.isdir(os.path.join(BASE_DIR, folder))
        and es_repo_git(os.path.join(BASE_DIR, folder))
    }

    # ------------- #
    # 📤 RESULTADO #
    # ------------ #
    return repos or None