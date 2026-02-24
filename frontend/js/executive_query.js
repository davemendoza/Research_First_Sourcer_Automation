/*
====================================================================
AI TALENT ENGINE – EXECUTIVE QUERY MODULE
© 2026 L. David Mendoza. All Rights Reserved.
====================================================================
*/

(function () {

    console.log("Executive Query Module Loaded");

    const API_BASE = "http://127.0.0.1:8000";

    const exampleQueries = [
        "Find strongest Triton engineers",
        "Top GPU inference engineers",
        "Engineers similar to Phil Tillet",
        "Top frontier AI engineers",
        "Best engineers outside OpenAI",
        "Top HuggingFace contributors",
        "Who builds inference engines",
        "Find emerging frontier engineers"
    ];

    let queryInput;
    let resultsContainer;
    let dropdown;

    function init() {

        queryInput = document.getElementById("executive-query-input");
        resultsContainer = document.getElementById("executive-results");

        if (!queryInput) {
            console.warn("Executive query input not found");
            return;
        }

        createDropdown();

        queryInput.addEventListener("focus", showDropdown);

        queryInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                executeQuery(queryInput.value);
            }
        });

        console.log("Executive Query Ready");

    }

    function createDropdown() {

        dropdown = document.createElement("div");

        dropdown.style.position = "absolute";
        dropdown.style.background = "#111";
        dropdown.style.border = "1px solid #333";
        dropdown.style.width = "400px";
        dropdown.style.display = "none";
        dropdown.style.zIndex = "9999";

        exampleQueries.forEach(q => {

            const item = document.createElement("div");

            item.innerText = q;
            item.style.padding = "8px";
            item.style.cursor = "pointer";

            item.addEventListener("click", function () {

                queryInput.value = q;
                dropdown.style.display = "none";

                executeQuery(q);

            });

            dropdown.appendChild(item);

        });

        queryInput.parentNode.appendChild(dropdown);

    }

    function showDropdown() {

        dropdown.style.display = "block";

    }

    async function executeQuery(query) {

        if (!query) return;

        renderLoading();

        try {

            const response =
                await fetch(`${API_BASE}/intel/query?q=${encodeURIComponent(query)}`);

            if (!response.ok) {
                throw new Error("Query failed");
            }

            const data = await response.json();

            renderResults(data);

        }
        catch (err) {

            console.error(err);

            renderError(err);

        }

    }

    function renderLoading() {

        resultsContainer.innerHTML =
            `<div style="padding:10px;color:#999;">Executing intelligence query...</div>`;

    }

    function renderError(err) {

        resultsContainer.innerHTML =
            `<div style="padding:10px;color:red;">Query failed</div>`;

    }

    function renderResults(data) {

        if (!data || data.length === 0) {

            resultsContainer.innerHTML =
                `<div style="padding:10px;color:#999;">No results found</div>`;

            return;
        }

        resultsContainer.innerHTML = "";

        data.forEach(identity => {

            const card = document.createElement("div");

            card.style.padding = "10px";
            card.style.borderBottom = "1px solid #222";
            card.style.cursor = "pointer";

            card.innerHTML =
                `<div style="color:#fff;font-weight:bold;">
                    ${identity.name || identity.id}
                </div>
                <div style="color:#888;">
                    ${identity.company || ""}
                </div>`;

            card.addEventListener("click", function () {

                openIdentity(identity.identity_key || identity.id);

            });

            resultsContainer.appendChild(card);

        });

    }

    async function openIdentity(identityKey) {

        try {

            const response =
                await fetch(`${API_BASE}/intel/identity/${identityKey}`);

            const identity = await response.json();

            if (window.renderIdentityDrawer) {
                window.renderIdentityDrawer(identity);
            }

        }
        catch (err) {

            console.error(err);

        }

    }

    document.addEventListener("DOMContentLoaded", init);

})();
