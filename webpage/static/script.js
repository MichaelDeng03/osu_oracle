document.addEventListener('DOMContentLoaded', () => {
    const userID = document.getElementById('userID');
    const submitUserID = document.getElementById('submitUserID');
    const beatmapURL = document.getElementById('beatmapURL');
    const submitBeatmap = document.getElementById('submitBeatmap');
    const getRecommendedBeatmaps = document.getElementById('recommendBeatmaps');

    /*
    TODO:
        Error checking and handling of invalid URL's.
    */
    submitUserID.addEventListener('click', () => {
        const regex = /\/users\/(\d+)/;
        const match = userID.value.match(regex);
        if (match && match[1]) {
            console.log(match[1]);
            fetchUserTopScores(match[1]);
        } else {
            console.error("Invalid URL format");
        }
    });


    submitBeatmap.addEventListener('click', () => {
        const regex = /#osu\/(\d+)$/;
        const match = beatmapURL.value.match(regex);
        if (match && match[1]) {
            console.log(match[1]);
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
        
        removeCell.innerHTML = `<i class="fa fa-trash map-delete" aria-hidden="true" onclick="removeRow(this)"></i>`
    });
}


function fetchBeatmap(beatmapID) {
    // Calculate mods enumeration from checked checkboxes
    const modifiers = document.querySelectorAll('.modifiers input[type="checkbox"]:checked');
    let modsEnum = 0;
    modifiers.forEach(mod => {
        modsEnum += parseInt(mod.value);
    });

    // Construct the URL with both beatmapID and modsEnum as query parameters
    const url = `/get_beatmap/${beatmapID}?modsEnum=${modsEnum}`;

    fetch(url)
        .then(response => response.json())
        .then(data => addBeatmap(data))
        .catch(error => console.log("Error: " + error));
}

function addBeatmap(score) {
    //mods are already in url suffix format
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

function sortTable(column) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("recommendedBeatmaps");
    switching = true;
    // Set the sorting direction to ascending:
    dir = "asc";

    // Reset all icons to fa-sort:
    var headers = table.getElementsByTagName("TH");
    for (i = 0; i < headers.length; i++) {
        headers[i].getElementsByTagName("i")[0].className = "fa fa-sort";
    }

    // Make a loop that will continue until no switching has been done:
    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;
        // Loop through all table rows (except the first, which contains table headers):
        for (i = 1; i < (rows.length - 1); i++) {
            // Start by saying there should be no switching:
            shouldSwitch = false;
            // Get the two elements you want to compare, one from current row and one from the next:
            x = rows[i].getElementsByTagName("TD")[column];
            y = rows[i + 1].getElementsByTagName("TD")[column];
            // Check if the two rows should switch place, based on the direction, asc or desc:
            if (dir == "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            // If a switch has been marked, make the switch and mark that a switch has been done:
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            // Each time a switch is done, increase this count by 1:
            switchcount++;
        } else {
            // If no switching has been done AND the direction is "asc",
            // set the direction to "desc" and run the while loop again.
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
    // Update the icon for the sorted column:
    var icon = headers[column].getElementsByTagName("i")[0];
    if (dir == "asc") {
        icon.className = "fa fa-sort-up";
    } else {
        icon.className = "fa fa-sort-down";
    }
}


function removeRow(button) {
    const row = button.parentNode.parentNode;
    row.parentNode.removeChild(row);
}

function fetchRecommendedBeatmaps() {
    //clear recommended beatmaps table
    const tableBody = document.getElementById('recommendedBeatmapsBody');
    tableBody.innerHTML = '';
    const userScores = document.getElementById('scoresTableBody').rows;
    const userScoresArray = [];

    for (let i = 0; i < userScores.length; i++) {
        const bm_id = /#osu\/(\d+)/.exec(userScores[i].cells[1].innerHTML)[0].replace('#osu/', '');
        
        const mods_enum = userScores[i].cells[3].textContent; 

        console.log(bm_id, mods_enum);
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
    .then(data => addRecommendedBeatmaps(data))
    .catch(error => console.log("Error: " + error));
}


function formatTime(seconds) {
    const min = Math.floor(seconds / 60);  // Get the number of minutes
    const sec = seconds % 60;              // Get the remaining seconds
    return `${min}:${sec.toString().padStart(2, '0')}`; // Format as min:seconds
}

function addRecommendedBeatmaps(recommendedBeatmaps) {
    const tableBody = document.getElementById('recommendedBeatmapsBody');
    tableBody.innerHTML = '';

    // For each recommended
    
    recommendedBeatmaps.forEach(beatmap => {
        const newRow = tableBody.insertRow(-1);
        
        const beatmapThumbnailCell = newRow.insertCell(0);
        const beatmapNameCell = newRow.insertCell(1);
        const starsCell = newRow.insertCell(2);
        const arCell = newRow.insertCell(3);
        const bpmCell = newRow.insertCell(4);
        const lengthCell = newRow.insertCell(5);
        const modsCell = newRow.insertCell(6);
        
        beatmapThumbnailCell.innerHTML = `<img src="${beatmap['list_2x_url']} width="40" height="40">`;

        const beatmapLink = document.createElement('a');
        beatmapLink.href = beatmap['link'];
        beatmapLink.textContent = `${beatmap['title']} [${beatmap['version']}]`;; 
        beatmapLink.target = "_blank";
        beatmapNameCell.appendChild(beatmapLink)

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
    });
}

/*
    Function to determine the "difficulty color" based
    on its star rating.

    Input: star rating int
    Output: Hex color (ex. #4FC0FF)
*/
function getColor(value) {
    var domain = [0.1, 1.5, 2, 2.5, 3.3, 4.2, 4.9, 5.8, 6.7, 7.7, 9];
    var range = ['#F5FAFF', '#4FC0FF', '#4FFFD5', '#7CFF4F', '#F6F05C', '#FF8068', '#FF4E6F', '#C645B8', '#6563DE', '#18158E', '#000000'];

    var clampedValue = Math.max(Math.min(value, domain[domain.length - 1]), domain[0]);

    var index = 0;
    while (clampedValue > domain[index]) {
        index++;
    }

    var interpolationFactor = (clampedValue - domain[index - 1]) / (domain[index] - domain[index - 1]);

    var startColor = range[index - 1];
    var endColor = range[index];

    var startRGB = parseInt(startColor.slice(1), 16);
    var endRGB = parseInt(endColor.slice(1), 16);

    var interpolatedR = Math.round((1 - interpolationFactor) * (startRGB >> 16) + interpolationFactor * (endRGB >> 16));
    var interpolatedG = Math.round((1 - interpolationFactor) * ((startRGB >> 8) & 0xFF) + interpolationFactor * ((endRGB >> 8) & 0xFF));
    var interpolatedB = Math.round((1 - interpolationFactor) * (startRGB & 0xFF) + interpolationFactor * (endRGB & 0xFF));

    var interpolatedColor = '#' + ((1 << 24) + (interpolatedR << 16) + (interpolatedG << 8) + interpolatedB).toString(16).slice(1);

    return interpolatedColor;
}
