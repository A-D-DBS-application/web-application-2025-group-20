const searchInput = document.getElementById("searchInput");
const clearBtn = document.getElementById("clearSearch");
const tbody = document.getElementById("debtorsTable");
const healthSortHeader = document.getElementById('healthSortHeader');
const sortIndicator = document.getElementById('sortIndicator');

let debounceTimer;
// State variable: 0 = Neutral (Default), -1 = Descending, 1 = Ascending
let sortState = 0;
// Array to store the initial (neutral) order of the rows
let initialDebtorsOrder = [];

// --- Sorting Functionality ---

// Helper function to update the sort icon
function updateSortIcon() {
    if (!sortIndicator) return;

    // Reset classes
    sortIndicator.classList.remove('opacity-100', 'opacity-30');

    if (sortState === 1) { // Ascending (Click 2)
        sortIndicator.classList.add('opacity-100');
        // Up arrow SVG
        sortIndicator.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M14.707 10.707a1 1 0 01-1.414 0L10 7.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
            </svg>
        `;
    } else if (sortState === -1) { // Descending (Click 1)
        sortIndicator.classList.add('opacity-100');
        // Down arrow SVG
        sortIndicator.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5.293 9.293a1 1 0 011.414 0L10 12.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
        `;
    } else { // Neutral (State 0 / Initial Load / Click 3)
        sortIndicator.classList.add('opacity-30'); // Faint visibility
        // Up arrow (as a placeholder/default indicator)
        sortIndicator.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M14.707 10.707a1 1 0 01-1.414 0L10 7.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
            </svg>
        `;
    }
}

// Function to perform the actual sorting
function sortTable() {
    if (!tbody || tbody.querySelector('td[colspan="5"]')) {
        updateSortIcon();
        return;
    }

    let rows;

    if (sortState === 0) {
        // Neutral state: use the saved initial (Jinja/API) order
        rows = initialDebtorsOrder;
    } else {
        // Get currently displayed rows
        rows = Array.from(tbody.querySelectorAll('tr'));

        // Sort the rows based on the Health Indicator (4th column, index 3)
        rows.sort((rowA, rowB) => {
            // Note: Assuming health indicator values are numbers and sorting numerically for better accuracy
            const cellA = parseInt(rowA.cells[3].textContent.trim());
            const cellB = parseInt(rowB.cells[3].textContent.trim());

            let comparison = 0;
            if (cellA > cellB) {
                comparison = 1;
            } else if (cellA < cellB) {
                comparison = -1;
            }

            // Apply sort direction based on state (-1 for Descending, 1 for Ascending)
            return comparison * sortState;
        });
    }

    // Clear the current table body content
    tbody.innerHTML = '';

    // Append the sorted rows back to the table body
    rows.forEach(row => tbody.appendChild(row));
    
    // Update the icon to reflect the current state
    updateSortIcon();
}

// Event listener for the header click
if (healthSortHeader) {
    healthSortHeader.addEventListener('click', function() {
        // Cycle the state: 0 (Neutral) -> -1 (Desc) -> 1 (Asc) -> 0 (Neutral)
        if (sortState === 0) {
            sortState = -1; // Click 1: Neutral -> Descending
        } else if (sortState === -1) {
            sortState = 1; // Click 2: Descending -> Ascending
        } else {
            sortState = 0; // Click 3: Ascending -> Neutral
        }

        // Sort the table
        sortTable();
    });
}

// --- Search Functionality ---

// Helper function to debounce the API call
function debounce(func, delay) {
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => func.apply(context, args), delay);
    };
}

async function fetchDebtors(query) {
    try {
        const response = await fetch(`/api/debtors?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        tbody.innerHTML = ''; // Clear previous results
        initialDebtorsOrder = [];

        // ***************************************************************
        // CRITICAL FIX: Define the correct Tailwind classes used in the HTML template
        // These replace the undefined 'table-cell-base' and 'table-action-cell'
        // ***************************************************************
        const baseCellClasses = "px-3 md:px-6 py-3 md:py-4 whitespace-nowrap text-sm md:text-base";
        const actionCellClasses = "px-3 md:px-6 py-3 md:py-4 whitespace-nowrap";
        // ***************************************************************

        if (!data.length) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center ${baseCellClasses} text-gray-500 dark:text-gray-400">No debtors found.</td></tr>`;
            sortState = 0;
            updateSortIcon();
            return;
        }

        data.forEach(d => {
            const row = document.createElement('tr');
            row.className = "hover:bg-gray-100 dark:hover:bg-gray-700 transition cursor-pointer";

            // Add the row click handler
            row.addEventListener('click', () => {
                window.location.href = `/debtor/${d.national_id}`;
            });

            // Using the defined baseCellClasses and actionCellClasses for correct layout
            row.innerHTML = `
                <td class="${baseCellClasses}">${d.btw_nummer}</td>
                <td class="${baseCellClasses}">${d.name}</td>
                
                <td class="${baseCellClasses} hidden md:table-cell">${d.address}</td>
                
                <td class="${baseCellClasses} hidden md:table-cell">${d.health_indicator}</td>
                
                <td class="${actionCellClasses}" onclick="event.stopPropagation()">
                    <form action="/delete-debtor/${d.national_id}" method="POST" onsubmit="return confirm('Are you sure you want to delete this debtor?');" class="inline">
                        <button type="submit" class="bg-red-600 hover:bg-red-700 text-white px-2 md:px-3 py-1 rounded-xl transition text-xs md:text-sm">
                            Delete
                        </button>
                    </form>
                </td>
            `;
            tbody.appendChild(row);
            initialDebtorsOrder.push(row);
        });
        
        sortState = 0; 
        sortTable(); 

    } catch (error) {
        console.error("Error fetching debtors:", error);
        if (tbody.innerHTML === '' || tbody.innerHTML.includes("Searching...")) {
            // Using baseCellClasses for consistent styling even on error
            const baseCellClasses = "px-3 md:px-6 py-3 md:py-4 whitespace-nowrap text-sm md:text-base";
            tbody.innerHTML = `<tr><td colspan="5" class="text-center ${baseCellClasses} text-red-500">Failed to load data. Please try again.</td></tr>`;
        }
    }
}

// Attach the debounced function to the input event (300ms delay)
const debouncedFetchDebtors = debounce(fetchDebtors, 300);

searchInput.addEventListener("input", () => {
    const query = searchInput.value.trim();
    clearBtn.classList.toggle("hidden", query === "");
    debouncedFetchDebtors(query); // Use the debounced function
});

clearBtn.addEventListener("click", () => {
    searchInput.value = "";
    clearBtn.classList.add("hidden");
    searchInput.focus();
    fetchDebtors(''); // Call immediately on clear
});


// Initial setup on page load
document.addEventListener('DOMContentLoaded', function() {
    // 1. Capture the initial state of the table rows (Jinja-rendered data)
    initialDebtorsOrder = Array.from(tbody.querySelectorAll('tr'));

    // 2. Ensure the sort state is neutral (0)
    sortState = 0;
    
    // 3. Apply the neutral state (updates icon appearance)
    updateSortIcon();
});