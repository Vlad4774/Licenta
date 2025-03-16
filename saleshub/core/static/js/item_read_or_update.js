let activeGrid = "volume"
let gridOptions;
let gridApi;

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

    if (gridId === "volumeGrid") activeGrid = "volume";
    if (gridId === "pricingGrid") activeGrid = "pricing";
    if (gridId === "costingGrid") activeGrid = "costing";
}

// Funcție pentru a încărca datele din API
async function fetchData(url) {
    let response = await fetch(url);
    let data = await response.json();
    return data;
}

// Funcție pentru a initializa AG Grid
async function loadGridData(itemId, type) {

    let url = `/item/${itemId}/${type}/`;
    let data = await fetchData(url);
     
    let columnDefs = getColumnDefs(type);
    gridOptions = {
        columnDefs: columnDefs,
        rowData: data[type] || [],
        defaultColDef: { flex: 1, editable: true },
        rowHeight: 68.5,
        onGridReady: (params) => {
            gridApi = params.api; // stocam api in variabila globala
        }   
    };

    new agGrid.createGrid(document.getElementById(`${type}Grid`), gridOptions);
}

// Funcție pentru a returna coloanele corecte în funcție de tipul grid-ului
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
    let url, dataKey;

    let rowData = [];

    gridApi.forEachNode(node => rowData.push(node.data));


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

    if (!gridOptions) {
        console.error(`Error: No grid options found for ${activeGrid}!`);
        return;
    }

    await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ [dataKey]: rowData })
    });

    alert(`${activeGrid} changes saved!`);
}

