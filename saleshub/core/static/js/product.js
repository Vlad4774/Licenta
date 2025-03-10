document.addEventListener('DOMContentLoaded', function () {
    const gridDiv = document.querySelector('#pricingGrid');

    // Define grid options
    const gridOptions = {
        columnDefs: [
            { headerName: "Product", field: "product__name", sortable: true, filter: true },
            { headerName: "Year", field: "year", sortable: true, filter: true },
            { headerName: "List Price", field: "list_price", sortable: true, filter: true },
            { headerName: "Discount (%)", field: "discount_percentage", sortable: true, filter: true },
            { headerName: "Markup (%)", field: "markup_percentage", sortable: true, filter: true },
            {
                headerName: "Net Price",
                valueGetter: params => {
                    const listPrice = params.data.list_price;
                    const discount = (params.data.discount_percentage / 100) * listPrice;
                    const priceAfterDiscount = listPrice - discount;
                    const markup = (params.data.markup_percentage / 100) * priceAfterDiscount;
                    return priceAfterDiscount + markup;
                },
                sortable: true
            }
        ],
        defaultColDef: {
            resizable: true,
            flex: 1, // Auto-resize columns
        },
        rowData: null, // Data will be loaded dynamically
    };

    // Initialize the grid
    new agGrid.Grid(gridDiv, gridOptions);

    // Fetch data from the Django backend
    fetch('/get_pricing_data/')
        .then(response => response.json())
        .then(data => gridOptions.api.setRowData(data))
        .catch(error => console.error('Error fetching pricing data:', error));
});
