console.log("Dashboard JS Loaded");

// =====================================================
// ELEMENT
// =====================================================

const video = document.getElementById("attendanceVideo");
const placeholder = document.getElementById("cameraPlaceholder");

const btnStartCamera = document.getElementById("btnStartCamera");
const btnStopCamera = document.getElementById("btnStopCamera");

const btnMasuk = document.getElementById("btnMasuk");
const btnPulang = document.getElementById("btnPulang");

const cameraStatus = document.getElementById("cameraStatus");
const cameraResolution = document.getElementById("cameraResolution");
const cameraFPS = document.getElementById("cameraFPS");

const modeAbsen = document.getElementById("modeAbsen");

let stream = null;
let attendanceType = null;


// =====================================================
// LOAD CAMERA SETTING
// =====================================================

function getCameraSetting() {

    const setting = localStorage.getItem("cameraSetting");

    if (!setting) {

        return {

            device: 0,
            resolution: "1280x720",
            fps: 30,
            mirror: false

        };

    }

    return JSON.parse(setting);

}

// =====================================================
// START CAMERA
// =====================================================
async function startAttendance() {
    if (!attendanceType) {

        alert(
            "Pilih Absen Masuk atau Absen Pulang "
            + "sebelum menjalankan kamera."
        );

        return;
    }
    const setting = getCameraSetting();

    const response = await fetch("/camera/start", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({

            camera: setting.device,
            resolution: setting.resolution,
            fps: setting.fps,
            mirror: setting.mirror

        })
    });

    const result = await response.json();

    if (!result.success) {
        alert("Gagal membuka kamera");
        return;
    }

    // Tampilkan video
    const img = document.getElementById("attendanceVideo");
    const placeholder = document.getElementById("cameraPlaceholder");

    img.style.display = "block";
    placeholder.style.display = "none";
    img.src = "/video_feed?" + Date.now();

    // Tombol
    btnStartCamera.disabled = true;
    btnStopCamera.disabled = false;

    // Mulai polling dashboard
    startDashboardPolling();

}
// =====================================================
// STOP CAMERA
// =====================================================
async function stopAttendance() {

    await fetch("/camera/stop", {
        method: "POST"
    });

    const img = document.getElementById("attendanceVideo");
	const placeholder = document.getElementById("cameraPlaceholder");

	img.src = "";
	img.style.display = "none";
	placeholder.style.display = "flex";

	// Ubah status tombol
	btnStartCamera.disabled = false;
	btnStopCamera.disabled = true;

	// Hentikan polling
	stopDashboardPolling();
}
// =====================================================
// MODE ABSENSI
// =====================================================

async function setAttendanceMode(type) {

    try {

        const response = await fetch(
            "/attendance/mode",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    attendance_type: type
                })
            }
        );

        const result = await response.json();

        if (!response.ok || !result.success) {

            alert(
                result.message
                || "Gagal mengubah mode absensi."
            );

            return;
        }

        attendanceType = type;

        modeAbsen.textContent = type;

        if (type === "Masuk") {

            btnMasuk.classList.add("active");
            btnPulang.classList.remove("active");

        } else {

            btnPulang.classList.add("active");
            btnMasuk.classList.remove("active");

        }

    } catch (err) {

        console.error(err);

        alert("Gagal mengirim mode absensi.");
    }
}

// =====================================================
// SIMPAN ABSENSI
// =====================================================

async function saveAttendance() {

    if (!attendanceType) {

        alert("Pilih jenis absensi terlebih dahulu.");

        return;

    }

    const data = {

        person_id: "FR0001",

        person_name: "Andi",

        attendance_type: attendanceType,

        confidence: 99.85,

        image: null

    };

    try {

        const response = await fetch("/attendance/save", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify(data)

        });

        const result = await response.json();

        if (result.success) {

            alert(result.message);

        }
        else {

            alert(result.message);

        }

    }

    catch (err) {

        console.error(err);

        alert("Gagal mengirim data.");

    }

}


// =====================================================
// EVENT
// =====================================================
btnStartCamera.addEventListener(
    "click",
    startAttendance
);

btnStopCamera.addEventListener(
    "click",
    stopAttendance
);

btnMasuk?.addEventListener("click", () => {

    setAttendanceMode("Masuk");

});

btnPulang?.addEventListener("click", () => {

    setAttendanceMode("Pulang");

});

let dashboardTimer = null;

function startDashboardPolling() {

    if (dashboardTimer)
        clearInterval(dashboardTimer);

    dashboardTimer = setInterval(
        updateDashboard,
        300
    );

}

function stopDashboardPolling() {

    if (dashboardTimer) {

        clearInterval(dashboardTimer);

        dashboardTimer = null;

    }

}
async function updateDashboard() {

    try {

        const response =
            await fetch("/recognition/status");

        const data = await response.json();

        document.getElementById("detectName").textContent =
            data.name;

        document.getElementById("detectID").textContent =
            data.person_id;

        document.getElementById("detectConfidence").textContent =
            data.confidence + "%";

        document.getElementById("detectStatus").textContent =
            data.status;

        document.getElementById("faceCount").textContent =
            data.face_count;

        document.getElementById("cameraFPS").textContent =
            data.fps;
	
	const livenessInstruction =
    	    document.getElementById("livenessInstruction");

	const livenessDirection =
    	    document.getElementById("livenessDirection");

	const livenessProgress =
            document.getElementById("livenessProgress");

	const livenessRemaining =
            document.getElementById("livenessRemaining");

	const livenessState =
            document.getElementById("livenessState");

	const livenessMessage =
            document.getElementById("livenessMessage");


	livenessInstruction.textContent =
            data.liveness_instruction || "Menunggu wajah dikenali";

	livenessDirection.textContent =
    	    data.liveness_direction || "UNKNOWN";

	livenessProgress.textContent =
            (data.liveness_progress || 0)
            + "/"
            + (data.liveness_required || 4);

	livenessRemaining.textContent =
            (data.liveness_remaining || 0)
            + " detik";

	livenessState.textContent =
            data.liveness_state || "IDLE";

	livenessMessage.textContent =
            data.liveness_message || "-";
        

	switch (data.liveness_state) {

    	    case "WAITING":
        	livenessState.className =
              	    "badge bg-warning text-dark";
        	break;

    	    case "PASSED":
        	livenessState.className =
                    "badge bg-success";
        	break;

    	    case "FAILED":
        	livenessState.className =
                    "badge bg-danger";
        	break;

    	    default:
        	livenessState.className =
                    "badge bg-secondary";
}
	const badge =
            document.getElementById("cameraStatus");

        if (data.camera) {

            badge.className =
                "badge bg-success";

            badge.textContent =
                "Online";

        } else {

            badge.className =
                "badge bg-danger";

            badge.textContent =
                "Offline";

        }

    }

    catch (err) {

        console.error(err);

    }

}
