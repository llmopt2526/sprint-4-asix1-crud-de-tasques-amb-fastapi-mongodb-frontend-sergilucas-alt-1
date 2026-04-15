# ======================================================================== #
# IMPORTS                                                                  #
# · FastAPI: framework per crear l'API.                                    #
# · Pydantic: defineix l'estructura de les dades (camps i tipus).          #
# · pymongo + AsyncMongoClient: connecta amb MongoDB de forma asíncrona.   #
# · ObjectId: tipus que MongoDB fa servir per identificar cada document.   #
# · BeforeValidator: converteix ObjectId a string (JSON no entén ObjectId).#
# · dotenv: carrega les variables del fitxer .env.                         #
# ======================================================================== #

import os
from typing import Optional, List
from dotenv import load_dotenv

from fastapi import FastAPI, Body, HTTPException, status, Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ConfigDict, BaseModel, Field
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

from bson import ObjectId
from pymongo import AsyncMongoClient
from pymongo import ReturnDocument

# Carreguem les variables d'entorn del fitxer .env
load_dotenv()

# ------------------------------------------------------------------------ #
# Inicialització de l'aplicació     			                   #
# · Creem la instància de FastAPI amb un títol i descripció.               #
# · El bloc CORS és important: sense ell, el navegador bloquejaria les     #
#   peticions del frontend cap al backend perquè són en ports diferents.   #
# · Amb allow_origins=["*"] permetem connexions des de qualsevol lloc.     #
# ------------------------------------------------------------------------ #

app = FastAPI(
    title="Gestor de Llibres API",
    summary="API REST per gestionar una col·lecció de llibres",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------ #
# Connexió amb MongoDB Atlas               		                   #
# 1. AsyncMongoClient es connecta a Atlas amb la URL del fitxer .env.      #
# 2. Seleccionem la base de dades "biblioteca" i la col·lecció "llibres".  #
# No cal crear-les manualment, MongoDB les crea soles quan hi              #
# 3. Inserim el primer document.                                           #
# 4. PyObjectId converteix l'_id de MongoDB (ObjectId) a string, perquè    # 
# les respostes JSON no suporten ObjectId directament.        		   #
# ------------------------------------------------------------------------ #

client = AsyncMongoClient(os.environ["MONGODB_URL"])
db = client.biblioteca
coleccio_llibres = db.get_collection("llibres")

PyObjectId = Annotated[str, BeforeValidator(str)]

# ------------------------------------------------------------------------ #
#                            Models                                        #
# · LlibreModel: defineix l'estructura d'un llibre.                        #
#    - Field(...) = camp obligatori (títol, autor).                        #
#    - Field(default="pendent") = valor per defecte si no s'envia.         #   
# · ActualitzarLlibreModel: tots els camps opcionals (None), perquè quan   #
#   editem potser només volem canviar un camp, no tots.                    #
# · ColeccioLlibres: encapsula una llista de llibres per a les respostes.  #
# ------------------------------------------------------------------------ #

class LlibreModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    titol: str = Field(...)
    autor: str = Field(...)
    estat: str = Field(default="pendent")
    valoracio: Optional[int] = Field(default=None, ge=1, le=5)
    categoria: str = Field(default="general")
    persona: str = Field(default="")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "titol": "El Petit Príncep",
                "autor": "Antoine de Saint-Exupéry",
                "estat": "pendent",
                "valoracio": None,
                "categoria": "infantil",
                "persona": "Anna",
            }
        },
    )


class ActualitzarLlibreModel(BaseModel):
    titol: Optional[str] = None
    autor: Optional[str] = None
    estat: Optional[str] = None
    valoracio: Optional[int] = Field(default=None, ge=1, le=5)
    categoria: Optional[str] = None
    persona: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "titol": "1984",
                "autor": "George Orwell",
                "estat": "llegit",
                "valoracio": 5,
            }
        },
    )


class ColeccioLlibres(BaseModel):
    llibres: List[LlibreModel]


# ------------------------------------------------------------------------ #
#                            Endpoints CRUD                                #
# ------------------------------------------------------------------------ #

# CREATE - Crear un llibre nou
# Rep un llibre en JSON, l'insereix a MongoDB amb insert_one i el torna a llegir amb find_one per retornar-lo amb l'_id que MongoDB li ha assignat. 
# Retorna codi 201 (creat).
@app.post(
    "/llibres/",
    response_description="Crea un nou llibre",
    response_model=LlibreModel,
    status_code=status.HTTP_201_CREATED,
)
async def crear_llibre(llibre: LlibreModel = Body(...)):
    nou_llibre = await coleccio_llibres.insert_one(
        llibre.model_dump(by_alias=True, exclude=["id"])
    )
    creat = await coleccio_llibres.find_one({"_id": nou_llibre.inserted_id})
    return creat


# READ - Llistar tots els llibres (amb filtres opcionals)
# Podem filtrar per categoria, estat, persona o valoració.
# Si no s'envia cap filtre, retorna tots els llibres.
@app.get(
    "/llibres/",
    response_description="Llista tots els llibres",
    response_model=ColeccioLlibres,
)
async def llistar_llibres(
    categoria: Optional[str] = Query(default=None),
    estat: Optional[str] = Query(default=None),
    persona: Optional[str] = Query(default=None),
    valoracio: Optional[int] = Query(default=None),
):
    filtre = {}
    if categoria:
        filtre["categoria"] = categoria
    if estat:
        filtre["estat"] = estat
    if persona:
        filtre["persona"] = persona
    if valoracio is not None:
        filtre["valoracio"] = valoracio

    llibres = await coleccio_llibres.find(filtre).to_list(1000)
    return ColeccioLlibres(llibres=llibres)


# READ - Obtenir un llibre per ID
# Busca el document amb find_one. Si no el troba, llança error 404.
@app.get(
    "/llibres/{id}",
    response_description="Obtenir un llibre",
    response_model=LlibreModel,
)
async def obtenir_llibre(id: str):
    llibre = await coleccio_llibres.find_one({"_id": ObjectId(id)})
    if llibre is None:
        raise HTTPException(status_code=404, detail=f"Llibre {id} no trobat")
    return llibre


# UPDATE - Actualitzar un llibre
# Rep l'id i les dades noves. Filtra els camps buits (None) per actualitzar només els que l'usuari ha enviat. 
# Amb $set actualitza aquells camps i retorna el document actualitzat.
@app.put(
    "/llibres/{id}",
    response_description="Actualitza un llibre",
    response_model=LlibreModel,
)
async def actualitzar_llibre(id: str, llibre: ActualitzarLlibreModel = Body(...)):
    dades = {k: v for k, v in llibre.model_dump().items() if v is not None}

    if len(dades) < 1:
        raise HTTPException(status_code=400, detail="Cal almenys un camp")

    actualitzat = await coleccio_llibres.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": dades},
        return_document=ReturnDocument.AFTER,
    )
    if actualitzat is None:
        raise HTTPException(status_code=404, detail=f"Llibre {id} no trobat")
    return actualitzat


# DELETE - Eliminar un llibre
# Fa delete_one. Si deleted_count == 0, no existia i retorna 404.
# Si s'ha eliminat correctament, retorna 204 (sense contingut).
@app.delete(
    "/llibres/{id}",
    response_description="Elimina un llibre",
)
async def eliminar_llibre(id: str):
    resultat = await coleccio_llibres.delete_one({"_id": ObjectId(id)})
    if resultat.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Llibre {id} no trobat")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# PATCH - Canviar l'estat d'un llibre (pendent / llegit)
@app.patch(
    "/llibres/{id}/estat",
    response_description="Canvia l'estat d'un llibre",
    response_model=LlibreModel,
)
async def canviar_estat(id: str, estat: str = Body(..., embed=True)):
    if estat not in ("pendent", "llegit"):
        raise HTTPException(status_code=400, detail="L'estat ha de ser 'pendent' o 'llegit'")

    actualitzat = await coleccio_llibres.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": {"estat": estat}},
        return_document=ReturnDocument.AFTER,
    )
    if actualitzat is None:
        raise HTTPException(status_code=404, detail=f"Llibre {id} no trobat")
    return actualitzat


# CREATE - Crear múltiples llibres de cop
@app.post(
    "/llibres/bulk",
    response_description="Crea múltiples llibres",
    response_model=ColeccioLlibres,
    status_code=status.HTTP_201_CREATED,
)
async def crear_llibres(llibres: List[LlibreModel] = Body(...)):
    docs = [ll.model_dump(by_alias=True, exclude=["id"]) for ll in llibres]
    resultat = await coleccio_llibres.insert_many(docs)
    creats = await coleccio_llibres.find(
        {"_id": {"$in": resultat.inserted_ids}}
    ).to_list(1000)
    return ColeccioLlibres(llibres=creats)
