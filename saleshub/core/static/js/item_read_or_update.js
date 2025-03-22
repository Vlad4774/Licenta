let activeGrid = "volume";
let gridOptions;
let gridApis = {
    volume: null,
    pricing: null,
    costing: null
};

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
        console.log("daddas");
        saveChanges(itemId);
    });
});

function showGrid(gridId) {
    document.getElementById("volumeGrid").style.display = "none";
    document.getElementById("pricingGrid").style.display = "none";
    document.getElementById("costingGrid").style.display = "none";
    document.getElementById(gridId).style.display = "block";

    if (gridId === "volumeGrid") activeGrid = "volume";
    if (gridId === "pricingGrid") activeGrid = "pricing";
    if (gridId === "costingGrid") activeGrid = "costing";
}

async function fetchData(url) {
    let response = await fetch(url);
    let data = await response.json();
    return data;
}

async function loadGridData(itemId, type) {
    let url = `/item/${itemId}/${type}/`;
    let data = await fetchData(url);

    let columnDefs = getColumnDefs(type);

    gridOptions = {
        columnDefs: columnDefs,
        rowData: data[type] || [],
        defaultColDef: { flex: 1, editable: true },
        rowHeight: 68.5,
        onGridReady: function (params) {
            gridApis[type] = params.api;  // Salvăm API-ul pentru gridul curent
            console.log(`Grid API set for ${type}`);
        }
    };

    new agGrid.createGrid(document.getElementById(`${type}Grid`), gridOptions);
}

function getColumnDefs(type) {
    if (type === "volume") {
        return [
            { field: "year", headerName: "Year", editable: false, suppressMovable: true },
            { field: "min_volume", headerName: "Min Volume", editable: true, suppressMovable: true },
            { field: "expected_volume", headerName: "Expected Volume", editable: true, suppressMovable: true },
            { field: "max_volume", headerName: "Max Volume", editable: true, suppressMovable: true }
        ];
    } else if (type === "pricing") {
        return [
            { field: "year", headerName: "Year", editable: false, suppressMovable: true },
            { field: "base_price", headerName: "Base Price", editable: true, suppressMovable: true },
            { field: "packaging_price", headerName: "Packaging Price", editable: true, suppressMovable: true },
            { field: "transport_price", headerName: "Transport Price", editable: true, suppressMovable: true },
            { field: "warehouse_price", headerName: "Warehouse Price", editable: true, suppressMovable: true }
        ];
    } else if (type === "costing") {
        return [
            { field: "year", headerName: "Year", editable: false, suppressMovable: true },
            { field: "base_cost", headerName: "Base Cost", editable: true, suppressMovable: true },
            { field: "labor_cost", headerName: "Labor Cost", editable: true, suppressMovable: true },
            { field: "material_cost", headerName: "Material Cost", editable: true, suppressMovable: true },
            { field: "overhead_cost", headerName: "Overhead Cost", editable: true, suppressMovable: true }
        ];
    }
}

async function saveChanges(itemId) {
    const api = gridApis[activeGrid];

    if (!api) {
        console.error("Grid API not initialized for:", activeGrid);
        return;
    }

    api.stopEditing(); // Asigură-te că valorile editate sunt salvate
    api.refreshCells(); // Opțional, dacă vrei să reîmprospătezi vizual

    let rowData = [];
    api.forEachNode(function (node) { // Utilizăm API-ul corect pentru a itera prin noduri
        rowData.push(node.data);
    });

    let url, dataKey;
    if (activeGrid === "volume") {
        url = `/item/${itemId}/save-volume/`;
        dataKey = "volume";
    } else if (activeGrid === "pricing") {
        url = `/item/${itemId}/save-pricing/`;
        dataKey = "pricing";
    } else {
        url = `/item/${itemId}/save-costing/`;
        dataKey = "costing";
    }

    console.log("Sending data:", JSON.stringify({ [dataKey]: rowData }));

    try {
        let response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ [dataKey]: rowData })
        });

        let result = await response.json();

        if (!response.ok) {
            throw new Error(`Server Error: ${result.message || response.status}`);
        }

        alert(`${activeGrid} changes saved!`);
    } catch (error) {
        console.error("Error saving data:", error);
        alert("Failed to save data. Check console.");
    }
}