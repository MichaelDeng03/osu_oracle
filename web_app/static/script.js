document.addEventListener('DOMContentLoaded', () => {
    const userID = document.getElementById('userID');
    const submitUserID = document.getElementById('submitUserID');
    const beatmapURL = document.getElementById('beatmapURL');
    const submitBeatmap = document.getElementById('submitBeatmap');
    const getRecommendedBeatmaps = document.getElementById('recommendBeatmaps');
    const prevPageButton = document.getElementById('prevPage');
    const nextPageButton = document.getElementById('nextPage');
    const pageInfo = document.getElementById('pageInfo');

    let currentPage = 1;
    const rowsPerPage = 25;
    let recommendedBeatmapsData = [];

    submitUserID.addEventListener('click', () => {
        const regex = /\/users\/(\d+)/;
        const match = userID.value.match(regex);
        if (match && match[1]) {
            fetchUserTopScores(match[1]);
        } else {
            console.error("Invalid URL format");
        }
    });

    submitBeatmap.addEventListener('click', () => {
        const regex = /#osu\/(\d+)$/;
        const match = beatmapURL.value.match(regex);
        if (match && match[1]) {
            fetchBeatmap(match[1]);
        } else {
            console.error("Invalid URL format");
        }
    });

    getRecommendedBeatmaps.addEventListener('click', () => {
        fetchRecommendedBeatmaps();
    });

    document.getElementById('clearTable').addEventListener('click', function() {
        const tableBody = document.getElementById('scoresTableBody');
        tableBody.innerHTML = '';  // Clears all rows from the table body
    });

    prevPageButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            displayRecommendedBeatmaps();
        }
    });

    nextPageButton.addEventListener('click', () => {
        if (currentPage * rowsPerPage < recommendedBeatmapsData.length) {
            currentPage++;
            displayRecommendedBeatmaps();
        }
    });

    const tableHeaders = document.querySelectorAll("#recommendedBeatmaps th");
    tableHeaders.forEach((header, index) => {
        if (index >= 1 && index <= 6) {
            header.addEventListener("click", () => sortTable(index));
        }
    });

    function fetchUserTopScores(userID) {
        fetch('/get_user_top_scores/' + userID)
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Network response was not ok.');
            })
            .then(data => {
                if (Array.isArray(data)) {
                    addUserTopScores(data);
                } else {
                    console.log("Expected an array of scores, received something else:", data);
                }
            })
            .catch(error => console.log("Error:", error));
    }

    function addUserTopScores(scores) {
        const tableBody = document.getElementById('scoresTableBody');
        tableBody.innerHTML = '';

        scores.forEach(score => {
            const newRow = tableBody.insertRow(-1);

            const beatmapThumbnailCell = newRow.insertCell(0);
            const beatmapNameCell = newRow.insertCell(1);
            const modsCell = newRow.insertCell(2);
            const modEnumCell = newRow.insertCell(3); // Hidden cell for mod_enum
            const removeCell = newRow.insertCell(4);

            beatmapThumbnailCell.innerHTML = `<img src="${score['list_2x_url']} width="40" height="40">`;

            const beatmapLink = document.createElement('a');
            beatmapLink.href = score['link'];
            beatmapLink.textContent = `${score['title']} [${score['version']}]`;; 
            beatmapLink.target = "_blank";
            beatmapNameCell.appendChild(beatmapLink)

            if (score["mods_images"]) {
                score["mods_images"].forEach(imgUrl => {
                    const modImage = document.createElement('img');
                    modImage.src = imgUrl;
                    modImage.style.width = "25px"; // Set the width of mod images
                    modImage.style.height = "18px"; // Set the height of mod images
                    modImage.style.marginRight = "3px"; // Add some spacing between images
                    modImage.style.verticalAlign = "middle"; // Align images vertically
                    modsCell.appendChild(modImage);
                });
            }
            modEnumCell.style.display = "none"; // Hide the cell
            modEnumCell.textContent = score['mods']; // Store mod_enum in the cell

            modsCell.style.whiteSpace = "nowrap"; // Prevent wrapping to a new line

            const deleteButton = document.createElement('i');
            deleteButton.className = "fa fa-trash map-delete";
            deleteButton.setAttribute("aria-hidden", "true");
            deleteButton.addEventListener('click', () => removeRow(deleteButton));
            removeCell.appendChild(deleteButton);
        });
    }

    function fetchBeatmap(beatmapID) {
        const modifiers = document.querySelectorAll('.modifiers input[type="checkbox"]:checked');
        let modsEnum = 0;
        modifiers.forEach(mod => {
            modsEnum += parseInt(mod.value);
        });

        const url = `/get_beatmap/${beatmapID}?modsEnum=${modsEnum}`;

        fetch(url)
            .then(response => response.json())
            .then(data => addBeatmap(data))
            .catch(error => console.log("Error: " + error));
    }

    function addBeatmap(score) {
        const tableBody = document.getElementById('scoresTableBody');
        const newRow = tableBody.insertRow(-1);

        const beatmapThumbnailCell = newRow.insertCell(0);
        const beatmapNameCell = newRow.insertCell(1);
        const modsCell = newRow.insertCell(2);
        const modEnumCell = newRow.insertCell(3); // Hidden cell for mod_enums
        const removeCell = newRow.insertCell(4);

        beatmapThumbnailCell.innerHTML = `<img src="${score['list_2x_url']} width="40" height="40">`;

        const beatmapLink = document.createElement('a');
        beatmapLink.href = score['link'];
        beatmapLink.textContent = `${score['title']} [${score['version']}]`;; 
        beatmapLink.target = "_blank";
        beatmapNameCell.appendChild(beatmapLink)

        if (score["mods_images"]) {
            score["mods_images"].forEach(imgUrl => {
                const modImage = document.createElement('img');
                modImage.src = imgUrl;
                modImage.style.width = "25px"; // Set the width of mod images
                modImage.style.height = "18px"; // Set the height of mod images
                modImage.style.marginRight = "3px"; // Add some spacing between images
                modImage.style.verticalAlign = "middle"; // Align images vertically
                modsCell.appendChild(modImage);
            });
        }

        modEnumCell.style.display = "none"; // Hide the cell
        modEnumCell.textContent = score['mods']; // Store mod_enum in the cell

        modsCell.style.whiteSpace = "nowrap"; // Prevent wrapping to a new line

        removeCell.innerHTML = `<i class="fa fa-trash map-delete" aria-hidden="true" onclick="removeRow(this)"></i>`
    }

    let sortDirection = {}; // Object to keep track of sort direction for each column

    function sortTable(column) {
        console.log('Sorting by column:', column);
        const dir = sortDirection[column] === "asc" ? "desc" : "asc";
        sortDirection[column] = dir;
    
        const columnNames = ['list_2x_url', 'title', 'difficulty_rating', 'ar', 'bpm', 'total_length', 'mods_images'];
        const columnName = columnNames[column];
    
        recommendedBeatmapsData.sort((a, b) => {
            let x = a[columnName];
            let y = b[columnName];
            if (column >= 2 && column <= 5) { // Sort numerical columns
                x = parseFloat(x);
                y = parseFloat(y);
            } else if (column == 1) { // Sort by title
                x = x.toString().toLowerCase();
                y = y.toString().toLowerCase();
            }
            return dir === "asc" ? (x > y ? 1 : -1) : (x < y ? 1 : -1);
        });
    
        currentPage = 1; // Reset to the first page after sorting
        displayRecommendedBeatmaps(); 
        updateSortIcons(column, dir);
    }

    function parseTime(timeStr) {
        console.log('Parsing time:', timeStr);
        const parts = timeStr.split(':');
        console.log(parts);
        return parseInt(parts[0]) * 60 + parseInt(parts[1]);
    }

    function updateSortIcons(column, dir) {
        const headers = document.querySelectorAll("#recommendedBeatmaps th");
        headers.forEach((header, index) => {
            if (index === 0) return; // Skip the 0th column
            const icon = header.querySelector("i");
            if (index === column) {
                icon.className = dir === "asc" ? "fa fa-sort-up" : "fa fa-sort-down";
            } else {
                icon.className = "fa fa-sort";
            }
        });
    }

    function fetchRecommendedBeatmaps() {
        const tableBody = document.getElementById('recommendedBeatmapsBody');
        tableBody.innerHTML = '';
        const userScores = document.getElementById('scoresTableBody').rows;
        const userScoresArray = [];

        for (let i = 0; i < userScores.length; i++) {
            const bm_id = /#osu\/(\d+)/.exec(userScores[i].cells[1].innerHTML)[0].replace('#osu/', '');

            const mods_enum = userScores[i].cells[3].textContent;

            userScoresArray.push(bm_id + '-' + mods_enum);
        }

        const postData = {
            user_scores: userScoresArray,
        };

        fetch('/predict_beatmaps/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(postData),
        })
        .then(response => response.json())
        .then(data => {
            recommendedBeatmapsData = data;
            currentPage = 1;
            displayRecommendedBeatmaps();
        })
        .catch(error => console.log("Error: " + error));
    }

    function displayRecommendedBeatmaps() {
        const tableBody = document.getElementById('recommendedBeatmapsBody');
        tableBody.innerHTML = '';
        const start = (currentPage - 1) * rowsPerPage;
        const end = Math.min(start + rowsPerPage, recommendedBeatmapsData.length);
    
        for (let i = start; i < end; i++) {
            const beatmap = recommendedBeatmapsData[i];
            const newRow = tableBody.insertRow(-1);
    
            const beatmapThumbnailCell = newRow.insertCell(0);
            const beatmapNameCell = newRow.insertCell(1);
            const starsCell = newRow.insertCell(2);
            const arCell = newRow.insertCell(3);
            const bpmCell = newRow.insertCell(4);
            const lengthCell = newRow.insertCell(5);
            const modsCell = newRow.insertCell(6);
    
            beatmapThumbnailCell.innerHTML = `<img src="${beatmap['list_2x_url']}" width="40" height="40">`;
    
            const beatmapLink = document.createElement('a');
            beatmapLink.href = beatmap['link'];
            beatmapLink.textContent = `${beatmap['title']} [${beatmap['version']}]`;
            beatmapLink.target = "_blank";
            beatmapNameCell.appendChild(beatmapLink);
    
            starsCell.textContent = beatmap['difficulty_rating'];
            arCell.textContent = beatmap['ar'];
            bpmCell.textContent = beatmap['bpm'];
            lengthCell.textContent = formatTime(beatmap['total_length']);
    
            if (beatmap["mods_images"]) {
                beatmap["mods_images"].forEach(imgUrl => {
                    const modImage = document.createElement('img');
                    modImage.src = imgUrl;
                    modImage.style.width = "25px"; // Set the width of mod images
                    modImage.style.height = "18px"; // Set the height of mod images
                    modImage.style.marginRight = "3px"; // Add some spacing between images
                    modImage.style.verticalAlign = "middle"; // Align images vertically
                    modsCell.appendChild(modImage);
                });
            }
        }
    
        pageInfo.textContent = `Page ${currentPage} of ${Math.ceil(recommendedBeatmapsData.length / rowsPerPage)}`;
    }

    function formatTime(seconds) {
        const min = Math.floor(seconds / 60);
        const sec = seconds % 60;
        return `${min}:${sec.toString().padStart(2, '0')}`;
    }

});


function removeRow(button) {
    const row = button.parentNode.parentNode;
    row.parentNode.removeChild(row);
}