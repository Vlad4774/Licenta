document.addEventListener("DOMContentLoaded", function () {
    const itemId = document.getElementById("grid-container").dataset.itemId;

    loadGridData(itemId, "volume");
    loadGridData(itemId, "pricing");
    loadGridData(itemId, "costing");

    document.getElementById("btnVolume").addEventListener("click", function () {
        showGrid("volumeGrid");
    });

    document.getElementById("btnPricing").addEventListener("click", function () {
        showGrid("pricingGrid");
    });

    document.getElementById("btnCosting").addEventListener("click", function () {
        showGrid("costingGrid");
    });

    document.getElementById("saveChanges").addEventListener("click", function () {
        saveChanges(itemId);
    });
});

// Funcție pentru a schimba între grid-uri
function showGrid(gridId) {
    document.getElementById("volumeGrid").style.display = "none";
    document.getElementById("pricingGrid").style.display = "none";
    document.getElementById("costingGrid").style.display = "none";
    document.getElementById(gridId).style.display = "block";
}

// Funcție pentru a încărca datele din API
async function fetchData(url) {
    let response = await fetch(url);
    let data = await response.json();
    return data;
}

// Funcție pentru a inițializa AG Grid
async function loadGridData(itemId, type) {
    let url = `/item/${itemId}/${type}/`;
    let data = await fetchData(url);
    console.log(`${type} Data:`, data);

    let columnDefs = getColumnDefs(type);
    let gridOptions = {
        columnDefs: columnDefs,
        rowData: data[type] || [],
        defaultColDef: { flex: 1, editable: true }
    };

    new agGrid.createGrid(document.getElementById(`${type}Grid`), gridOptions);
}

// Funcție pentru a returna coloanele corecte în funcție de tipul grid-ului
function getColumnDefs(type) {
    if (type === "volumes") {
        return [
            { field: "year", headerName: "Year", editable: true },
            { field: "min_volume", headerName: "Min Volume", editable: true },
            { field: "expected_volume", headerName: "Expected Volume", editable: true },
            { field: "max_volume", headerName: "Max Volume", editable: true }
        ];
    } else if (type === "pricing") {
        return [
            { field: "year", headerName: "Year", editable: true },
            { field: "base_price", headerName: "Base Price", editable: true },
            { field: "packaging_price", headerName: "Packaging Price", editable: true },
            { field: "transport_price", headerName: "Transport Price", editable: true },
            { field: "warehouse_price", headerName: "Warehouse Price", editable: true }
        ];
    } else if (type === "costing") {
        return [
            { field: "year", headerName: "Year", editable: true },
            { field: "base_cost", headerName: "Base Cost", editable: true },
            { field: "labor_cost", headerName: "Labor Cost", editable: true },
            { field: "material_cost", headerName: "Material Cost", editable: true },
            { field: "overhead_cost", headerName: "Overhead Cost", editable: true }
        ];
    }
}

// Funcție pentru a salva datele
async function saveChanges(itemId) {
    let volumeGrid = agGrid.Grid.getGridOptions(document.getElementById("volumeGrid")).api.getRowData();
    let pricingGrid = agGrid.Grid.getGridOptions(document.getElementById("pricingGrid")).api.getRowData();
    let costGrid = agGrid.Grid.getGridOptions(document.getElementById("costingGrid")).api.getRowData();

    await fetch(`/item/${itemId}/save-volumes/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ volumes: volumeGrid })
    });

    await fetch(`/item/${itemId}/save-pricing/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pricing: pricingGrid })
    });

    await fetch(`/item/${itemId}/save-costs/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ costs: costGrid })
    });

    alert("Changes saved!");
}