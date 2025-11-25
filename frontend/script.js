const API = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    loadProducts();

    document.getElementById("productForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        addProduct();
    });
});

async function loadProducts() {
    const res = await fetch(`${API}/products`);
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
            </td>
        `;

        table.appendChild(row);
    });
}

async function addProduct() {
    const name = document.getElementById("name").value;
    const url = document.getElementById("url").value;
    const target_price = parseFloat(document.getElementById("target_price").value);

    const res = await fetch(`${API}/products`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, url, target_price })
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
