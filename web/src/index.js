import * as d3 from "d3";

let page = 1;
let itemsPerPage = 100;
let loadedEntries = [];
let totalCount = 0;
let fields = [];
let metadata = {};
let sortBy = "id";
let sortOrder = "ASC";
let transitioning = true;

document.addEventListener("DOMContentLoaded", function () {
    Promise.all([
        fetch(new Request(`/api/?page=${page.toString(10)}&items_per_page=${itemsPerPage}`)),
        fetch(new Request("/api/entries")),
        fetch(new Request("/api/fields")),
        fetch(new Request("/api/metadata"))
    ]).then(rs => Promise.all(rs.map(r => r.json()))).then(data => {
        loadedEntries = data[0];
        totalCount = parseInt(data[1], 10);
        fields = data[2];
        metadata = data[3];
        populateEntryTable();
        updatePagination();
        updateTableColumnHeaders();

        const chromosomeLabels = d3.select("#chromosome-checkboxes").selectAll("label").data(metadata["chr"])
            .enter()
            .append("label")
            .attr("for", c => c);
        chromosomeLabels.append("input")
            .attr("type", "checkbox")
            .attr("id", c => c)
            .attr("name", c => c)
            .attr("checked", "checked");
        chromosomeLabels.append("span").text(c => `${c.replace("chr", "")}`);

        d3.select("#start").attr("min", metadata["min_pos"]);
        d3.select("#start").attr("max", metadata["max_pos"]);
        d3.select("#end").attr("min", metadata["min_pos"]);
        d3.select("#end").attr("max", metadata["max_pos"]);

        const searchContainer = d3.select("#advanced-search-container");
        d3.select("#show-advanced-search").on("click", () => searchContainer.classed("shown", true));
        d3.select("#hide-advanced-search").on("click", () => searchContainer.classed("shown", false));
        d3.select("#advanced-search-container").on("click", () => searchContainer.classed("shown", false));
        d3.select("#advanced-search-modal").on("click", () => d3.event.stopPropagation());

        d3.select("#prev-page").on("click", () => {
            if (transitioning) return;
            page = Math.max(page - 1, 1);
            reloadPage();
        });

        d3.select("#next-page").on("click", () => {
            if (transitioning) return;
            page = Math.min(page + 1, parseInt(getTotalPages(), 10));
            reloadPage();
        });

        d3.select("#items-per-page").on("change", () => {
            itemsPerPage = parseInt(d3.event.target.value, 10);
            page = 1;
            reloadPage();
        });

        d3.select("#table-display").classed("loading", false);
        transitioning = false;

        d3.selectAll("table#entry-table thead th").data(fields, f => f["name"]).on("click", f => {
            if (sortBy === f["name"]) {
                sortOrder = (sortOrder === "ASC" ? "DESC" : "ASC");
            } else {
                sortOrder = "ASC";
                sortBy = f["name"];
            }

            page = 1;
            reloadPage();
        });
    });
});

function populateEntryTable() {
    const tableColumns = d3.select("table#entry-table thead").selectAll("th").data(fields, f => f["name"]);
    // TODO: Use original column name for display
    tableColumns.enter().append("th").text(f => f["name"]).append("span").attr("class", "material-icons");
    tableColumns.exit().remove();

    const tableRows = d3.select("table#entry-table tbody").selectAll("tr").data(loadedEntries, e => e["id"]);
    const rowEntry = tableRows.enter().append("tr");

    fields.forEach(f => rowEntry.append("td")
        .classed("lighter", e => e[f["name"]] === null || e[f["name"]] === "NA" || e[f["name"]] === "-")
        .html(e => formatEntryCell(e, f)));

    tableRows.exit().remove();
}

function formatEntryCell(e, f) {
    if (f["name"] === "rs") {
        if (e["rs"] === null) return "-";
        return `<a href="https://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=${e["rs"]}"
                   target="_blank" rel="noopener">${e["rs"]}</a>`
    }
    if (f["name"] === "gene_info" && e["gene_info"] !== "-" && e["gene_info"] !== "NA") {
        return e["gene_info"]
            .split("|")
            .map(og => `<a href="https://www.ncbi.nlm.nih.gov/gene/${og.split(":")[1]}/"
                           target="_blank" rel="noopener">${og}</a>`)
            .join("|");
    }
    if (f["name"] === "allele_id" && e["allele_id"] !== "NA") {
        return `<a href="https://www.ncbi.nlm.nih.gov/clinvar/variation/${e["allele_id"]}/"
                   target="_blank" rel="noopener">${e["allele_id"]}</a>`
    }
    return e[f["name"]] === null ? "NA" : e[f["name"]]; // TODO: Maybe shouldn't always be NA
}

function updateTableColumnHeaders() {
    d3.selectAll("table#entry-table thead th").data(fields, f => f["name"])
        .select("span.material-icons")
        .text(f => (sortBy === f["name"] ? (sortOrder === "ASC" ? "expand_less" : "expand_more") : ""));
}

function updatePagination() {
    const totalPages = getTotalPages();
    d3.select("#current-page").text(page.toFixed(0));
    d3.select("#total-pages").text(totalPages);
    d3.select("#prev-page").attr("disabled", page === 1 ? "disabled" : null);
    d3.select("#next-page").attr("disabled", page.toString(10) === totalPages ? "disabled" : null);
}

function reloadPage() {
    transitioning = true;

    if (itemsPerPage >= 100) d3.select("#table-display").classed("loading", true)
        .on("transitionend", () => transitioning = false);

    let url = new URL("/api/", window.location.origin);
    let params = {
        page: page.toString(10),
        items_per_page: itemsPerPage,
        sort_by: sortBy,
        sort_order: sortOrder
    };
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

    return fetch(new Request(url.toString()))
        .then(r => r.json())
        .then(data => {
            loadedEntries = data;
            if (transitioning && itemsPerPage >= 100) {
                d3.select("#table-display").on("transitionend", () => {
                    populateEntryTable();
                    updatePagination();
                    updateTableColumnHeaders();
                    d3.select("#table-display").classed("loading", false);
                    transitioning = false;
                });
                // Fallback if the transitionend event is not triggered.
                setTimeout(() => d3.select("#table-display").dispatch("transitionend"), 300);
            } else {
                populateEntryTable();
                updatePagination();
                updateTableColumnHeaders();
                d3.select("#table-display").classed("loading", false);
                transitioning = false;
            }
        });
}

function getTotalPages() {
    return Math.ceil(totalCount / itemsPerPage).toFixed(0);
}
