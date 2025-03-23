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

    if (type === "volume") {
        const pricing = await fetchData(`/item/${itemId}/pricing/`);
        const costing = await fetchData(`/item/${itemId}/costing/`);

        const pricingMap = {};
        pricing.pricing.forEach(p => {
            pricingMap[p.year] = p;
        });

        const costingMap = {};
        costing.costing.forEach(c => {
            costingMap[c.year] = c;
        });

        data.volume.forEach(row => {
            const year = row.year;
            const priceObj = pricingMap[year] || {};
            const costObj = costingMap[year] || {};

            const final_price =
                (parseFloat(priceObj.base_price) || 0) +
                (parseFloat(priceObj.packaging_price) || 0) +
                (parseFloat(priceObj.transport_price) || 0) +
                (parseFloat(priceObj.warehouse_price) || 0);

            const final_cost =
                (parseFloat(costObj.base_cost) || 0) +
                (parseFloat(costObj.labor_cost) || 0) +
                (parseFloat(costObj.material_cost) || 0) +
                (parseFloat(costObj.overhead_cost) || 0);

            row.final_price = final_price;
            row.final_cost = final_cost;

            calculateKPIs(data.volume);
        });
    }

    gridOptions = {
        columnDefs: columnDefs,
        rowData: data[type] || [],
        defaultColDef: { flex: 1, editable: true },
        rowHeight: 68.5,
        onGridReady: function (params) {
            gridApis[type] = params.api;
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
            { field: "max_volume", headerName: "Max Volume", editable: true, suppressMovable: true },
            {
                headerName: "Sales (€)",
                valueGetter: (params) => {
                    const vol = (parseFloat(params.data.expected_volume) + parseFloat(params.data.min_volume) + parseFloat(params.data.max_volume))/3 || 0;
                    const price = parseFloat(params.data.final_price) || 0;
                    return (vol * price).toFixed(2);
                },
                editable: false,
                cellStyle: { color: '#00bcd4', fontWeight: 'bold' }
            },
            {
                headerName: "EBIT (€)",
                valueGetter: (params) => {
                    const vol = parseFloat(params.data.expected_volume) || 0;
                    const price = parseFloat(params.data.final_price) || 0;
                    const cost = parseFloat(params.data.final_cost) || 0;
                    return (vol * (price - cost)).toFixed(2);
                },
                editable: false,
                cellStyle: { color: '#28a745', fontWeight: 'bold' }
            }
        ];
    } else if (type === "pricing") {
        return [
            { field: "year", headerName: "Year", editable: false, suppressMovable: true },
            { field: "base_price", headerName: "Base Price", editable: true, suppressMovable: true },
            { field: "packaging_price", headerName: "Packaging Price", editable: true, suppressMovable: true },
            { field: "transport_price", headerName: "Transport Price", editable: true, suppressMovable: true },
            { field: "warehouse_price", headerName: "Warehouse Price", editable: true, suppressMovable: true },
            {
                headerName: "Final Price",
                valueGetter: (params) => {
                    const base = parseFloat(params.data.base_price) || 0;
                    const pack = parseFloat(params.data.packaging_price) || 0;
                    const trans = parseFloat(params.data.transport_price) || 0;
                    const ware = parseFloat(params.data.warehouse_price) || 0;
                    return base + pack + trans + ware;
                },
                editable: false,
                cellStyle: { fontWeight: 'bold', color: '#00bcd4' }
            }
        ];
    } else if (type === "costing") {
        return [
            { field: "year", headerName: "Year", editable: false, suppressMovable: true },
            { field: "base_cost", headerName: "Base Cost", editable: true, suppressMovable: true },
            { field: "labor_cost", headerName: "Labor Cost", editable: true, suppressMovable: true },
            { field: "material_cost", headerName: "Material Cost", editable: true, suppressMovable: true },
            { field: "overhead_cost", headerName: "Overhead Cost", editable: true, suppressMovable: true },
            {
                headerName: "Total Cost",
                valueGetter: (params) => {
                    const base = parseFloat(params.data.base_cost) || 0;
                    const labor = parseFloat(params.data.labor_cost) || 0;
                    const mat = parseFloat(params.data.material_cost) || 0;
                    const over = parseFloat(params.data.overhead_cost) || 0;
                    return base + labor + mat + over;
                },
                editable: false,
                suppressMovable: true,
                cellStyle: { fontWeight: 'bold', color: '#00bcd4' }
            }
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

function calculateKPIs(rowData) {
    let totalSales = 0;
    let totalCost = 0;
    let totalEbit = 0;

    let priceSum = 0, costSum = 0, count = 0;

    rowData.forEach(row => {
        const vol = parseFloat(row.expected_volume) || 0;
        const price = parseFloat(row.final_price) || 0;
        const cost = parseFloat(row.final_cost) || 0;

        const sales = vol * price;
        const costTotal = vol * cost;
        const ebit = vol * (price - cost);

        totalSales += sales;
        totalCost += costTotal;
        totalEbit += ebit;

        if (price > 0) priceSum += price, count++;
        if (cost > 0) costSum += cost;
    });

    document.getElementById("totalSales").textContent = totalSales.toFixed(2);
    document.getElementById("totalCost").textContent = totalCost.toFixed(2);
    document.getElementById("totalEbit").textContent = totalEbit.toFixed(2);
    document.getElementById("avgPrice").textContent = count > 0 ? (priceSum / count).toFixed(2) : '-';
    document.getElementById("avgCost").textContent = count > 0 ? (costSum / count).toFixed(2) : '-';
}
