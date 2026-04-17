// Aquí posem l'adreça on corre el nostre servidor (backend)

const API_URL = "http://localhost:8000";

// Quan volem editar un llibre, guardem el seu id aquí.
// Si no estem editant cap llibre, posem null.

let editantId = null;

// Aquesta funció busca els llibres al servidor i els ensenya a la pàgina.
// Si hem posat filtres (per exemple "fantasia"), només ens ensenya aquells.

async function carregarLlibres() {

    // Mirem què ha escrit l'usuari als camps de filtre

    const categoria = document.getElementById("filter-categoria").value;
    const estat = document.getElementById("filter-estat").value;

    // Preparem els filtres per enviar-los al servidor

    const params = new URLSearchParams();
    if (categoria) params.append("categoria", categoria);
    if (estat) params.append("estat", estat);

    // Li demanem al servidor que ens doni els llibres

    const res = await fetch(`${API_URL}/llibres/?${params}`);
    const data = await res.json();

    // Un cop els tenim, els ensenyem a la pàgina

    mostrarLlibres(data.llibres);
}

// Aquesta funció agafa els llibres que hem rebut del servidor i crea una caixa per cadascun amb tota la seva informació.

function mostrarLlibres(llibres) {

    // Busquem el lloc de la pàgina on volem posar els llibres

    const contenidor = document.getElementById("llista-llibres");

    // Si no hi ha cap llibre, ensenyem un avís

    if (llibres.length === 0) {
        contenidor.innerHTML = "<p>No hi ha llibres.</p>";
        return;
    }

    // Per cada llibre, creem una caixa amb el seu títol, autor, etc.
    // També afegim els botons d'editar i eliminar

    contenidor.innerHTML = llibres.map(ll => `
        <div class="llibre">
            <h3>${ll.titol}</h3>
            <p><strong>Autor:</strong> ${ll.autor}</p>
            <p><strong>Estat:</strong> <span class="badge badge-${ll.estat}">${ll.estat}</span></p>
            <p><strong>Valoració:</strong> ${ll.valoracio || "—"}</p>
            <p><strong>Categoria:</strong> ${ll.categoria} | <strong>Persona:</strong> ${ll.persona || "—"}</p>
            <button onclick="editarLlibre('${ll._id}')">Editar</button>
            <button class="btn-eliminar" onclick="eliminarLlibre('${ll._id}')">Eliminar</button>
        </div>
    `).join("");
}

// Això passa quan l'usuari clica el botó "Afegir" o "Actualitzar".
// Si estem editant un llibre que ja existeix, l'actualitza amb les dades noves.
// Si no, crea un llibre completament nou.

document.getElementById("book-form").addEventListener("submit", async (e) => {
    
    // Evitem que la pàgina es recarregui sola al clicar el botó

    e.preventDefault();

    // Agafem tot el que l'usuari ha escrit al formulari

    const llibre = {
        titol: document.getElementById("titol").value,
        autor: document.getElementById("autor").value,
        estat: document.getElementById("estat").value,
        categoria: document.getElementById("categoria").value || "general",
        persona: document.getElementById("persona").value,
        valoracio: document.getElementById("valoracio").value
            ? parseInt(document.getElementById("valoracio").value)
            : null,
    };

    if (editantId) {
        
	// Estem editant un llibre: enviem les dades noves al servidor
        
	await fetch(`${API_URL}/llibres/${editantId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(llibre),
        });
        cancelarEdicio();
    } else {
       
	// No estem editant: demanem al servidor que creï un llibre nou

        await fetch(`${API_URL}/llibres/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(llibre),
        });
    }

    // Buidem el formulari i tornem a carregar la llista

    document.getElementById("book-form").reset();
    carregarLlibres();
});

// Quan l'usuari clica "Editar" en un llibre, busquem les seves dades al servidor i les posem al formulari perquè les pugui modificar.

async function editarLlibre(id) {
    
    // Demanem al servidor les dades d'aquest llibre

    const res = await fetch(`${API_URL}/llibres/${id}`);
    const llibre = await res.json();

    // Les posem als camps del formulari

    document.getElementById("titol").value = llibre.titol;
    document.getElementById("autor").value = llibre.autor;
    document.getElementById("estat").value = llibre.estat;
    document.getElementById("categoria").value = llibre.categoria;
    document.getElementById("persona").value = llibre.persona;
    document.getElementById("valoracio").value = llibre.valoracio || "";

    // Guardem l'id del llibre i canviem el botó perquè digui "Actualitzar"

    editantId = id;
    document.getElementById("form-title").textContent = "Editar llibre";
    document.getElementById("btn-submit").textContent = "Actualitzar";
    document.getElementById("btn-cancel").style.display = "inline-block";
}

// Si l'usuari decideix no editar, tornem el formulari com estava al principi

function cancelarEdicio() {
    editantId = null;
    document.getElementById("book-form").reset();
    document.getElementById("form-title").textContent = "Afegir nou llibre";
    document.getElementById("btn-submit").textContent = "Afegir llibre";
    document.getElementById("btn-cancel").style.display = "none";
}

// Quan l'usuari clica "Eliminar", demanem al servidor que l'esborri i tornem a carregar la llista perquè ja no hi aparegui

async function eliminarLlibre(id) {
    await fetch(`${API_URL}/llibres/${id}`, { method: "DELETE" });
    carregarLlibres();
}

// Buida els filtres i torna a ensenyar tots els llibres

function netejarFiltres() {
    document.getElementById("filter-categoria").value = "";
    document.getElementById("filter-estat").value = "";
    carregarLlibres();
}

// El primer que fem quan s'obre la pàgina és carregar tots els llibres

carregarLlibres();
