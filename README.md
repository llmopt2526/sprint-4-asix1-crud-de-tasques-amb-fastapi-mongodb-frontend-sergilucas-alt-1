# Gestor de Llibres — Sprint 4
**Autor:** Sergi Lucas  
**Curs:** 2025-26 | Institut Montsià (ASIX)

Aplicació web per gestionar una col·lecció de llibres. Permet crear, llistar, editar, eliminar i filtrar llibres per categoria, estat, persona i valoració. El backend funciona amb FastAPI i es connecta a MongoDB Atlas. El frontend consumeix l'API amb JavaScript (fetch) i utilitza Skeleton CSS.

---

# Funcionalitats
- Crear, editar i eliminar llibres
- Canviar l'estat d'un llibre (pendent / llegit)
- Assignar valoració (1-5), categoria i persona
- Filtrar per categoria i estat
- Inserció massiva de llibres

---

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

---

# Instal·lació

## 1. Clonar el repositori
```bash
git clone https://github.com/llmopt2526/sprint-4-asix1-crud-de-tasques-amb-fastapi-mongodb-frontend-sergilucas-alt-1.git
cd sprint-4-asix1-crud-de-tasques-amb-fastapi-mongodb-frontend-sergilucas-alt-1
```

## 2. Entorn virtual i dependències
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pymongo pydantic python-dotenv
```

## 3. Configurar MongoDB Atlas
Crear un fitxer `.env` dins de `backend/` amb la URL de connexió:
```
MONGODB_URL=mongodb+srv://USUARI:CONTRASENYA@cluster.mongodb.net/?appName=NomCluster
```
Recorda autoritzar la teva IP a Atlas (Network Access).

## 4. Arrencar el backend
```bash
uvicorn app:app --reload
```
L'API estarà a `http://localhost:8000`.

## 5. Arrencar el frontend
En un altre terminal:
```bash
cd frontend
python3 -m http.server 5500
```
La pàgina estarà a `http://localhost:5500`.

---

# Tests amb Postman
A `tests/Postman_API_tests.json` hi ha la col·lecció amb 8 peticions ordenades que demostren tot el CRUD:

1. **POST** — Crear un llibre
2. **GET** — Llistar tots els llibres
3. **GET** — Obtenir un llibre per ID
4. **PUT** — Actualitzar un llibre
5. **PATCH** — Canviar l'estat
6. **GET** — Filtrar per categoria
7. **DELETE** — Eliminar un llibre
8. **GET** — Comprovar que retorna 404

La variable `{{llibre_id}}` s'assigna automàticament al fer el POST, així les altres peticions funcionen sense haver de canviar l'ID manualment.
