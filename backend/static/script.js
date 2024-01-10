document.addEventListener('DOMContentLoaded', () => {
    const userID = document.getElementById('userID');
    const submitUserID = document.getElementById('submitUserID');
    const scoreID = document.getElementById('scoreID');
    const submitScoreID = document.getElementById('submitScoreID');
    const getRecommendedBeatmaps = document.getElementById('recommendBeatmaps');

    submitUserID.addEventListener('click', () => {
        fetchUserTopScores(userID.value);
    });

    submitScoreID.addEventListener('click', () => {
        fetchUserScore(scoreID.value);
    });

    getRecommendedBeatmaps.addEventListener('click', () => {
        fetchRecommendedBeatmaps();
    });
});

function fetchUserTopScores(userID) {
    fetch('/get_user_scores/' + userID)
        .then(response => response.json())
        .then(data => addUserTopScores(data))
        .catch(error => console.log("Error: " + error));
}

function addUserTopScores(userScores) {
    const tableBody = document.getElementById('scoresTableBody');
    tableBody.innerHtml = '';

    userScores.forEach(score => {
        const newRow = tableBody.insertRow(-1);
        const scoreIDCell = newRow.insertCell(0);
        const beatmapNameCell = newRow.insertCell(1);
        const beatmapCell = newRow.insertCell(2);
        const modsCell = newRow.insertCell(3);
        const rankCell = newRow.insertCell(4);
        const removeCell = newRow.insertCell(5);

        const scoreLink = document.createElement('a');
        scoreLink.href = 'https://osu.ppy.sh/scores/osu/' + score.score_id;
        scoreLink.textContent = score.score_id;
        scoreIDCell.appendChild(scoreLink);
        beatmapNameCell.textContent = score.name;
        beatmapCell.textContent = score.beatmap_id;
        modsCell.textContent = score.mods;
        rankCell.textContent = score.rank;
        removeCell.innerHTML = '<button onclick="removeRow(this)">Remove</button>';
    });
}

function fetchUserScore(scoreID) {
    fetch('/get_user_score/' + scoreID)
        .then(response => response.json())
        .then(data => addUserScore(data))
        .catch(error => console.log("Error: " + error));
}

function addUserScore(userScore) {
    const tableBody = document.getElementById('scoresTableBody');
    const newRow = tableBody.insertRow(-1);
    const scoreIDCell = newRow.insertCell(0);
    const beatmapCell = newRow.insertCell(1);
    const modsCell = newRow.insertCell(2);
    const rankCell = newRow.insertCell(3);
    const removeCell = newRow.insertCell(4);

    scoreIDCell.textContent = userScore.id;
    beatmapCell.textContent = userScore.beatmap_id;
    modsCell.textContent = userScore.mods;
    rankCell.textContent = userScore.rank;
    removeCell.innerHTML = '<button onclick="removeRow(this)">Remove</button>';
}

function removeRow(button) {
    const row = button.parentNode.parentNode;
    row.parentNode.removeChild(row);
}

function fetchRecommendedBeatmaps() {
    const userScores = document.getElementById('scoresTableBody').rows;
    // const model = document.getElementById('model_select').value;
    const userScoresArray = [];

    for (let i = 0; i < userScores.length; i++) {
        bm_id = userScores[i].cells[2].innerHTML;
        mods = userScores[i].cells[3].innerHTML;
        userScoresArray.push(bm_id + '-' + mods);
    }

    fetch('/predict_beatmaps/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_scores: userScoresArray }),
    })
        .then(response => response.json())
        .then(data => addRecommendedBeatmaps(data))
        .catch(error => console.log("Error: " + error));
}

function addRecommendedBeatmaps(recommendedBeatmaps) {
    const tableBody = document.getElementById('recommendedBeatmapsBody');
    // Clear tableBody
    tableBody.innerHTML = '';

    // For each recommended
    recommendedBeatmaps.forEach(beatmap => {
        
        const newRow = tableBody.insertRow(-1);
        const beatmapIDCell = newRow.insertCell(0);
        const beatmapLink = document.createElement('a');
        const beatmapName = newRow.insertCell(1);
        const stars = newRow.insertCell(2);
        const mods = newRow.insertCell(3);
        
        // beatmapIDCell.textContent = beatmap['beatmap_id'];
        beatmapLink.href = beatmap['beatmap_link'];
        beatmapLink.textContent = beatmap['beatmap_id'];
        beatmapIDCell.appendChild(beatmapLink);
        beatmapName.textContent = beatmap['title'];
        stars.textContent = beatmap['stars'];
        mods.textContent = beatmap['mods'];
    });


}