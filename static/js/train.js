console.log("train.js loaded");
const btnTrainAll = document.getElementById("btnTrainAll");
const progressBar = document.getElementById("trainingProgress");
const statusText = document.getElementById("trainingStatus");

let timer = null;

// ================================
// Start Training
// ================================

btnTrainAll.addEventListener("click", async () => {

    btnTrainAll.disabled = true;

    const response = await fetch("/api/train/start", {

        method: "POST"

    });

    const result = await response.json();

    if (result.success) {

        timer = setInterval(updateProgress, 1000);

    }
    else {

        alert("Training sedang berjalan.");

        btnTrainAll.disabled = false;

    }

});

// ================================
// Update Progress
// ================================

async function updateProgress() {

    console.log("Update Progress");

    const response = await fetch("/api/train/status");
    const data = await response.json();

    console.log(data);

    progressBar.style.width = data.progress + "%";
    progressBar.innerText = data.progress + "%";
    statusText.innerText = data.status;

    if (!data.running) {

        console.log("STOP TIMER");

        clearInterval(timer);

        timer = null;

        progressBar.classList.remove("progress-bar-animated");

        btnTrainAll.disabled = false;

    }
}