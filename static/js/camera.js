console.log("camera.js loaded");
// ==========================================
// Camera Manager
// Browser Version (getUserMedia)
// ==========================================

const cameraSelect = document.getElementById("cameraSelect");
const resolutionSelect = document.getElementById("resolutionSelect");
const fpsSelect = document.getElementById("fpsSelect");
const mirrorCamera = document.getElementById("mirrorCamera");

const btnSaveCameraSetting = document.getElementById("btnSaveCameraSetting");
const btnStartCamera = document.getElementById("btnStartCamera");
const btnStopCamera = document.getElementById("btnStopCamera");

const video = document.getElementById("cameraPreview");
const placeholder = document.getElementById("cameraPlaceholder");
const cameraBadge = document.getElementById("cameraBadge");

let stream = null;

// ==========================================
// Event
// ==========================================

btnSaveCameraSetting.addEventListener("click", saveCameraSetting);
btnStartCamera.addEventListener("click", startCamera);
btnStopCamera.addEventListener("click", stopCamera);

// ==========================================
// Load Camera
// ==========================================
async function loadCameraList() {

    try {

        const response = await fetch("/camera/list");
        const cameras = await response.json();

        cameraSelect.innerHTML = "";

        cameras.forEach(camera => {

            const option = document.createElement("option");

            option.value = camera.index;   // <-- index OpenCV
            option.text = camera.name;

            cameraSelect.appendChild(option);

        });

    } catch (err) {

        console.error(err);
        alert("Gagal mengambil daftar kamera.");

    }
}

// ==========================================
// Load Setting
// ==========================================

function loadCameraSetting() {

    const setting =
        JSON.parse(localStorage.getItem("cameraSetting"));

    if (!setting)
        return;

    cameraSelect.value = setting.device || "";

    resolutionSelect.value =
        setting.resolution || "640x480";

    fpsSelect.value =
        setting.fps || 30;

    mirrorCamera.checked =
        setting.mirror || false;

}

// ==========================================
// Save Setting
// ==========================================

function saveCameraSetting() {

    const setting = {

        device: cameraSelect.value,

        resolution: resolutionSelect.value,

        fps: parseInt(fpsSelect.value),

        mirror: mirrorCamera.checked

    };

    localStorage.setItem(
        "cameraSetting",
        JSON.stringify(setting)
    );

    bootstrap.Modal
        .getInstance(
            document.getElementById("modalCameraSetting")
        )
        .hide();

}

// ==========================================
// Resolution
// ==========================================

function getResolution(resolution) {

    switch (resolution) {

        case "1280x720":
            return {
                width: 1280,
                height: 720
            };

        case "1920x1080":
            return {
                width: 1920,
                height: 1080
            };

        default:
            return {
                width: 640,
                height: 480
            };

    }

}
// ==========================================
// Start Camera
// ==========================================

async function startCamera() {

    try {

        if (stream) {

            stream.getTracks().forEach(track => track.stop());

        }

        const setting =
            JSON.parse(localStorage.getItem("cameraSetting"));

        const resolution =
            getResolution(setting?.resolution || "640x480");

        stream = await navigator.mediaDevices.getUserMedia({

            video: {

                deviceId: setting?.device
                    ? { exact: setting.device }
                    : undefined,

                width: {
                    ideal: resolution.width
                },

                height: {
                    ideal: resolution.height
                },

                frameRate: {
                    ideal: setting?.fps || 30
                }

            },

            audio: false

        });

        video.srcObject = stream;

        await video.play();

        if (setting?.mirror) {

            video.style.transform = "scaleX(-1)";

        } else {

            video.style.transform = "scaleX(1)";

        }

        video.style.display = "block";

        placeholder.style.display = "none";

        cameraBadge.classList.remove("bg-danger");
        cameraBadge.classList.add("bg-success");
        cameraBadge.innerText = "Online";

        btnStartCamera.disabled = true;
        btnStopCamera.disabled = false;

    }
    catch (err) {

        console.error(err);

        alert("Gagal membuka kamera.");

    }

}

// ==========================================
// Stop Camera
// ==========================================

function stopCamera() {

    if (stream) {

        stream.getTracks().forEach(track => track.stop());

        stream = null;

    }

    video.pause();

    video.srcObject = null;

    video.style.display = "none";

    placeholder.style.display = "flex";

    cameraBadge.classList.remove("bg-success");
    cameraBadge.classList.add("bg-danger");

    cameraBadge.innerText = "Offline";

    btnStartCamera.disabled = false;
    btnStopCamera.disabled = true;

}

// ==========================================
// Initialize
// ==========================================

document.addEventListener("DOMContentLoaded", async () => {

    await loadCameraList();

    loadCameraSetting();

    btnStopCamera.disabled = true;

});