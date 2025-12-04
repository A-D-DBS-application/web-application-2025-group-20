const searchInput = document.getElementById("searchInput");
const clearBtn = document.getElementById("clearSearch");
const tbody = document.getElementById("debtorsTable");

let debounceTimer;

searchInput.addEventListener("input", () => {
    const query = searchInput.value.trim();
    clearBtn.classList.toggle("hidden", query === "");
    fetchDebtors(query);
});

clearBtn.addEventListener("click", () => {
    searchInput.value = "";
    clearBtn.classList.add("hidden");
    searchInput.focus();
    fetchDebtors('');
});

function debounce(func, delay) {
    return function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => func.apply(this, arguments), delay);
    };
}

async function fetchDebtors(query) {
    const response = await fetch(`/api/debtors?q=${encodeURIComponent(query)}`);
    const data = await response.json();

    tbody.innerHTML = '';

    if (!data.length) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center px-6 py-4">No debtors found.</td></tr>`;
        return;
    }

    data.forEach(d => {
        const row = document.createElement('tr');
        row.className = "hover:bg-gray-100 dark:hover:bg-gray-700 transition cursor-pointer";
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap" onclick="window.location.href='/debtor/${d.national_id}'">${d.national_id}</td>
            <td class="px-6 py-4 whitespace-nowrap" onclick="window.location.href='/debtor/${d.national_id}'">${d.name}</td>
            <td class="px-6 py-4 whitespace-nowrap" onclick="window.location.href='/debtor/${d.national_id}'">${d.address}</td>
            <td class="px-6 py-4 whitespace-nowrap" onclick="window.location.href='/debtor/${d.national_id}'">${d.financial_data_source}</td>
        `;
        tbody.appendChild(row);
    });
}
