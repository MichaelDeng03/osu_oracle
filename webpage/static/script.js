document.addEventListener('DOMContentLoaded', () => {
    const userID = document.getElementById('userID');
    const submitUserID = document.getElementById('submitUserID');
    const scoreID = document.getElementById('scoreID');
    const submitScoreID = document.getElementById('submitScoreID');
    const getRecommendedBeatmaps = document.getElementById('recommendBeatmaps');

    /*
    TODO:
        Error checking and handling of invalid URL's.
    */
    submitUserID.addEventListener('click', () => {
        const regex = /\/users\/(\d+)/;
        const match = userID.value.match(regex);

        fetchUserTopScores(match[1]);
    });

    submitScoreID.addEventListener('click', () => {
        const regex = /\/(\d+)$/;
        const match = scoreID.value.match(regex);

        fetchUserScore(match[1]);
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

function addUserTopScores(scoreRows) {
    const tableBody = document.getElementById('scoresTableBody');
    tableBody.innerHTML = '';

    scoreRows.forEach(row => {
        const newRow = tableBody.insertRow(-1);

        const scoreIDCell = newRow.insertCell(0);
        // const beatmapIDCell = newRow.insertCell(1);
        const beatmapNameCell = newRow.insertCell(1);
        const modsCell = newRow.insertCell(2);
        const rankCell = newRow.insertCell(3);
        const removeCell = newRow.insertCell(4);

        const scoreLink = document.createElement('a');
        scoreLink.href = 'https://osu.ppy.sh/scores/osu/' + row["score_id"];
        scoreLink.innerHTML = `<i class="fa-solid fa-link"></i>`
        scoreLink.target = "_blank"; // open in new tab
        scoreIDCell.appendChild(scoreLink);

        const beatmapLink = document.createElement('a');
        beatmapLink.href = row['beatmap_link'];
        beatmapLink.innerHTML = row["title"];
        beatmapLink.target = "_blank";
        // beatmapIDCell.appendChild(beatmapLink);

        // beatmapNameCell.textContent = row["beatmap_name"];
        beatmapNameCell.appendChild(beatmapLink);
        modsCell.innerHTML = modsToImages(row["mods"]);
        modsCell.setAttribute('mods', row["mods"]);

        let r = row["rank"]
        r = r.replace('H', '-Silver')
        r = r.replace('X', 'SS')

        rankCell.innerHTML = `
            <img src="https://raw.githubusercontent.com/ppy/osu-web/459ef4ad903647aef0daf6d4a24f4eb5fe436e4c/public/images/badges/score-ranks-v2019/GradeSmall-${r}.svg">`
        removeCell.innerHTML = `<i class="fa fa-trash map-delete" aria-hidden="true" onclick="removeRow(this)"></i>`
    });
}

function modsToImages(mods) {
    // This is hacky, considering rewriting script.js from ground up.
    const cdn = 'https://raw.githubusercontent.com/ppy/osu-web/459ef4ad903647aef0daf6d4a24f4eb5fe436e4c/public/images/badges/mods/mod_'
    const template = `<img src="${cdn}MOD.png" original="ORIGINAL" width=25px>`

    // I'm being lazy.
    mods = mods.replace('Hidden', template.replace('MOD', 'hidden'))
    mods = mods.replace('Double Time', template.replace('MOD', 'double-time'))
    mods = mods.replace('Nightcore', template.replace('MOD', 'nightcore.png'))
    mods = mods.replace('Hard Rock', template.replace('MOD', 'hard-rock'))
    mods = mods.replace('Flashlight', template.replace('MOD', 'flashlight'))
    mods = mods.replace('Easy', template.replace('MOD', 'easy'))
    // mods = mods.replace('Half Time', template.replace('MOD', 'half-time')) bruh i cna't be bothered.
    mods = mods.replaceAll(',', '')

    return mods
}

function fetchUserScore(scoreID) {
    fetch('/get_user_score/' + scoreID)
        .then(response => response.json())
        .then(data => addUserScore(data))
        .catch(error => console.log("Error: " + error));
}

function addUserScore(row) {
    const tableBody = document.getElementById('scoresTableBody');
    const newRow = tableBody.insertRow(-1);

    const scoreIDCell = newRow.insertCell(0);
    // const beatmapIDCell = newRow.insertCell(1);
    const beatmapNameCell = newRow.insertCell(1);
    const modsCell = newRow.insertCell(2);
    const rankCell = newRow.insertCell(3);
    const removeCell = newRow.insertCell(4);

    const scoreLink = document.createElement('a');
    scoreLink.href = 'https://osu.ppy.sh/scores/osu/' + row["score_id"];
    scoreLink.innerHTML = `<i class="fa-solid fa-link"></i>`
    scoreLink.target = "_blank"; // open in new tab
    scoreIDCell.appendChild(scoreLink);

    const beatmapLink = document.createElement('a');
    beatmapLink.href = row['beatmap_link'];
    beatmapLink.innerHTML = row["title"];
    beatmapLink.target = "_blank";
    // beatmapIDCell.appendChild(beatmapLink);

    // beatmapNameCell.textContent = row["beatmap_name"];
    beatmapNameCell.appendChild(beatmapLink);
    modsCell.innerHTML = modsToImages(row["mods"]);
    modsCell.setAttribute('mods', row["mods"]);

    let r = row["rank"]
    let original = row["rank"]
    r = r.replace('H', '-Silver')
    r = r.replace('X', 'SS')

    rankCell.innerHTML = `
        <img
            src="https://raw.githubusercontent.com/ppy/osu-web/459ef4ad903647aef0daf6d4a24f4eb5fe436e4c/public/images/badges/score-ranks-v2019/GradeSmall-${r}.svg">`
    removeCell.innerHTML = `<i class="fa fa-trash map-delete" aria-hidden="true" onclick="removeRow(this)"></i>`
}

function removeRow(button) {
    const row = button.parentNode.parentNode;
    row.parentNode.removeChild(row);
}

function fetchRecommendedBeatmaps() {
    const userScores = document.getElementById('scoresTableBody').rows;
    const noHD = document.getElementById('noHD').checked;
    const detectSkillsets = document.getElementById('detectSkillsets').checked;
    const numSkillsets = document.getElementById('numSkillsets').value;
    const userScoresArray = [];

    for (let i = 0; i < userScores.length; i++) {
        // Jesus fucking christ.
        bm_id = /#osu\/(\d+)/.exec(userScores[i].cells[1].innerHTML)[0].replace('#osu/', '');
        mods = userScores[i].cells[2].getAttribute("mods");
        userScoresArray.push(bm_id + '-' + mods);
    }
    const postData = {
        user_scores: userScoresArray,
        noHD: noHD,
        detectSkillsets: detectSkillsets,
        numSkillsets: numSkillsets
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

function addRecommendedBeatmaps(recommendedBeatmaps) {
    const tableBody = document.getElementById('recommendedBeatmapsBody');
    tableBody.innerHTML = '';

    // For each recommended
    recommendedBeatmaps.forEach(beatmapSegment => {
        beatmapSegment.forEach(beatmap => {
            const newRow = tableBody.insertRow(-1);
            const beatmapLink = document.createElement('a');
            const beatmapName = newRow.insertCell(0);
            const stars = newRow.insertCell(1);
            const ar = newRow.insertCell(2);
            const bpm = newRow.insertCell(3);
            const length = newRow.insertCell(4);
            const modsCell = newRow.insertCell(5);

            beatmapLink.href = beatmap['beatmap_link'];
            beatmapLink.innerHTML = beatmap['title'];
            beatmapLink.target = "_blank"; // open in new tab
            beatmapName.appendChild(beatmapLink);

            stars.textContent = beatmap['difficulty_rating'];

            ar.textContent = beatmap['ar'];

            bpm.textContent = beatmap['bpm'];

            length.textContent = beatmap['length_seconds'];

            modsCell.innerHTML = modsToImages(beatmap["mods"]);

            modsCell.setAttribute('mods', beatmap["mods"]);
        });

        // LINE GOES HERE
        const divider = tableBody.insertRow(-1);
        const dividerCell = divider.insertCell(0);
        dividerCell.colSpan = 6;
        hr = document.createElement('hr');
        dividerCell.appendChild(hr);
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
