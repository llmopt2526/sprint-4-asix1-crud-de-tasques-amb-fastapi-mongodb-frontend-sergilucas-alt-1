# Gestor de Llibres — Sprint 4
**Autor:** Sergi Lucas  
**Curs:** 2025-26 | Institut Montsià (ASIX)

Aplicació web per gestionar una col·lecció de llibres. Permet crear, llistar, editar, eliminar i filtrar llibres per categoria, estat, persona i valoració. El backend funciona amb FastAPI i es connecta a MongoDB Atlas. El frontend consumeix l'API amb JavaScript (fetch) i utilitza Skeleton CSS.

# Funcionalitats
- Crear, editar i eliminar llibres
- Canviar l'estat d'un llibre (pendent / llegit)
- Assignar valoració (1-5), categoria i persona
- Filtrar per categoria i estat
- Inserció massiva de llibres

# Estructura del projecte
```text
.
├── README.md
├── backend/
│   ├── app.py                  # Servidor FastAPI amb tots els endpoints
│   ├── .env                    # URL de connexió a MongoDB Atlas
│   └── requirements.txt        # Dependències de Python
├── frontend/
│   ├── index.html              # Pàgina web
│   ├── style.css               # Estils personalitzats
│   └── app.js                  # JavaScript que connecta amb l'API
└── tests/
    └── Postman_API_tests.json  # Tests per validar l'API
```

# Instal·lació

## 1. Clonar el repositori
Descarreguem el projecte de GitHub al nostre ordinador.
```bash
git clone https://github.com/llmopt2526/sprint-4-asix1-crud-de-tasques-amb-fastapi-mongodb-frontend-sergilucas-alt-1.git
cd sprint-4-asix1-crud-de-tasques-amb-fastapi-mongodb-frontend-sergilucas-alt-1
```

## 2. Entorn virtual i dependències
Creem un entorn virtual de Python per tenir les llibreries del projecte separades de la resta del sistema. Després instal·lem tot el que necessita el backend per funcionar.
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pymongo pydantic python-dotenv
```

## 3. Configurar MongoDB Atlas
Creem un fitxer `.env` dins de `backend/` on posem la URL per connectar-nos a la nostra base de dades al núvol.
```
MONGODB_URL=mongodb+srv://USUARI:CONTRASENYA@cluster.mongodb.net/?appName=NomCluster
```
Recorda autoritzar la teva IP a Atlas (Network Access) perquè et deixi connectar.

## 4. Arrencar el backend
Arrenquem el servidor de l'API perquè escolti les peticions.
```bash
uvicorn app:app --reload
```
L'API estarà a `http://localhost:8000`.

## 5. Arrencar el frontend
En un altre terminal, arrenquem un petit servidor web per veure la pàgina al navegador.
```bash
cd frontend
python3 -m http.server 5500
```
La pàgina estarà a `http://localhost:5500`.

# Tests amb Postman
A `tests/Postman_API_tests.json` hi ha la col·lecció amb 8 peticions ordenades que demostren tot el CRUD:

1. **POST** — Crea un llibre nou
2. **GET** — Mostra tots els llibres
3. **GET** — Busca un llibre concret pel seu ID
4. **PUT** — Modifica les dades d'un llibre
5. **PATCH** — Canvia l'estat d'un llibre
6. **GET** — Filtra els llibres per categoria
7. **DELETE** — Elimina un llibre
8. **GET** — Comprova que el llibre eliminat ja no existeix

Les peticions 3, 4, 5, 7 i 8 utilitzen la variable `{{llibre_id}}`. Després de fer el POST (petició 1), cal copiar l'`_id` de la resposta i assignar-lo manualment a la variable `llibre_id` a la col·lecció (botó dret a la col·lecció → Variables).
