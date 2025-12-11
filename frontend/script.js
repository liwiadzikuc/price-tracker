const API = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    updateUI();
    loadProducts();

    document.getElementById("productForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        addProduct();
    });

    const editForm = document.getElementById("editForm");
    if (editForm) {
        editForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            editProduct();
        });
    }
    document.getElementById("login-form")?.addEventListener("submit", (e) => {
        e.preventDefault();
        login();
    });

    document.getElementById("register-form")?.addEventListener("submit", (e) => {
        e.preventDefault();
        register();
    });

    document.getElementById("verify-form")?.addEventListener("submit", (e) => {
        e.preventDefault();
        verifyCode();
    });

});
function updateUI() {
    const user_id = localStorage.getItem("user_id");

    if (user_id) {
        document.getElementById("logged-in").style.display = "block";
        document.getElementById("not-logged-in").style.display = "none";
         document.getElementById("verify").style.display = "none";
    } else {
        document.getElementById("logged-in").style.display = "none";
         document.getElementById("verify").style.display = "none";
        document.getElementById("not-logged-in").style.display = "block";
    }
}

async function login() {
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    const res = await fetch(`${API}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (res.ok) {
        localStorage.setItem("user_id", data.user_id);
        alert("Zalogowano!");
        document.getElementById("login-email").value = "";
        document.getElementById("login-password").value = "";
        updateUI();
        loadProducts(); 
    } else {
        alert("Błędny login lub hasło");
    }
}

async function register() {
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;

    const res = await fetch(`${API}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (res.ok) {
        alert("Rejestracja udana! Sprawdź maila i wpisz kod.");
        document.getElementById("verify-email").value = email;
        document.getElementById("reg-email").value = "";
        document.getElementById("reg-password").value = "";
        document.getElementById("login").style.display = "none";
        document.getElementById("verify").style.display = "block";
    } else {
        alert("Błąd rejestracji: " + data.detail);
    }
}

async function verifyCode() {
    const email = document.getElementById("verify-email").value;
    const code = document.getElementById("verify-code").value;

    const res = await fetch(`${API}/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, code })
    });

    const data = await res.json();

    if (res.ok) {
        alert("Konto aktywowane! Możesz się zalogować.");
        document.getElementById("verify-email").value = "";
        document.getElementById("verify-code").value = "";
        //document.getElementById("verify").style.display = "none";
        document.getElementById("not-logged-in").style.display = "block";
        document.getElementById("verify").style.display = "none";
    } else {
        alert("Błąd: " + data.detail);
    }
}

async function loadProducts() {
    const user_id = localStorage.getItem("user_id");
    if (!user_id) {
        alert("Najpierw się zaloguj!");
        return;
    }
    const res = await fetch(`${API}/products/${user_id}`);
    const products = await res.json();

    const table = document.getElementById("productsTable");
    table.innerHTML = "";

    products.forEach(p => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${p.id}</td>
            <td>${p.name}</td>
            <td>${p.target_price}</td>
            <td><a href="${p.url}" target="_blank">link</a></td>
            <td>
                <button onclick="checkPrice(${p.id})">Sprawdź cenę</button>
                <button onclick="showHistory(${p.id})">Historia</button>
                <button onclick="showEditModal(${p.id}, '${p.name}', '${p.url}', ${p.target_price})">Edytuj</button> 
                <button onclick="deleteProduct(${p.id})">Usuń</button>
            </td>
        `;

        table.appendChild(row);
    });
}
function logout() {
    localStorage.removeItem("user_id");
    alert("Wylogowano!");
    document.getElementById("login-email").value = "";
    document.getElementById("login-password").value = "";
    document.getElementById("reg-email").value = "";
    document.getElementById("reg-password").value = "";
    document.getElementById("verify-email").value = "";
    document.getElementById("verify-code").value = "";

    updateUI();
}

async function addProduct() {
    const name = document.getElementById("name").value;
    const url = document.getElementById("url").value;
    const target_price = parseFloat(document.getElementById("target_price").value);
    const user_id = parseInt(localStorage.getItem("user_id"));
    if (!user_id) {
    alert("Najpierw się zaloguj!");
    return;
    }

    const res = await fetch(`${API}/products`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, url, target_price, user_id })
    });

    if (res.ok) {
        alert("Dodano produkt!");
        loadProducts();
    } else {
        alert("Błąd przy dodawaniu produktu.");
    }
}

async function checkPrice(id) {
    alert("Sprawdzanie ceny... to może potrwać kilka sekund.");

    const res = await fetch(`${API}/products/${id}/check-price`);

    if (res.ok) {
        const data = await res.json();
        alert(`Aktualna cena: ${data.current_price} zł`);
    } else {
        alert("Nie udało się pobrać ceny.");
    }
}

async function showHistory(id) {
    const section = document.getElementById("history-section");
    const list = document.getElementById("history");

    section.classList.remove("hidden");
    list.innerHTML = "Ładowanie...";

    const res = await fetch(`${API}/products/${id}/history`);
    const history = await res.json();

    list.innerHTML = "";

    history.forEach(h => {
        const li = document.createElement("li");
        li.textContent = `Cena: ${h.price} zł | ${h.checked_at}`;
        list.appendChild(li);
    });
}
async function deleteProduct(id) {
    if (!confirm("Czy na pewno chcesz usunąć ten produkt i całą jego historię cen?")) {
        return;
    }

    const res = await fetch(`${API}/products/${id}`, {
        method: "DELETE"
    });

    if (res.ok) {
        alert("Produkt usunięty pomyślnie!");
        loadProducts(); 
    } else {
        alert("Błąd przy usuwaniu produktu.");
    }
}


function showEditModal(id, name, url, target_price) {
    document.getElementById("edit-id").value = id;
    document.getElementById("edit-name").value = name;
    document.getElementById("edit-url").value = url;
    document.getElementById("edit-target_price").value = target_price;
    document.getElementById("edit-modal").classList.remove("hidden");
}

function closeEditModal() {
    document.getElementById("edit-modal").classList.add("hidden");
}

async function editProduct() {
    const id = document.getElementById("edit-id").value;
    const name = document.getElementById("edit-name").value;
    const url = document.getElementById("edit-url").value;
    const target_price = parseFloat(document.getElementById("edit-target_price").value);

    const res = await fetch(`${API}/products/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, url, target_price })
    });

    if (res.ok) {
        alert("Produkt zaktualizowany!");
        closeEditModal();
        loadProducts(); 
    } else {
        alert("Błąd przy aktualizacji produktu.");
    }
}

