console.log("Persons JS Loaded");
// ==============================
// Person Page
// ==============================

let stream = null;
let photos = [];
function getCameraSetting(){

    const setting = localStorage.getItem("cameraSetting");

    if(!setting){

        return {
            device: null,
            resolution: "1280x720",
            fps: 30,
            mirror: false
        };

    }

    return JSON.parse(setting);

}
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");

const btnStartCamera = document.getElementById("btnStartCamera");
const btnStopCamera = document.getElementById("btnStopCamera");
const btnCapture = document.getElementById("btnCapture");
const btnDeleteLast = document.getElementById("btnDeleteLast");
const btnUploadDataset = document.getElementById("btnUploadDataset");
const fileUpload = document.getElementById("fileUpload");

const datasetGrid = document.getElementById("datasetGrid");
const photoCount = document.getElementById("photoCount");

const modalTambahPerson = document.getElementById("modalTambahPerson");
// ==============================
// Dataset Modal
// ==============================

const btnUploadNewDataset = document.getElementById("btnUploadNewDataset");
const datasetUpload = document.getElementById("datasetUpload");

const datasetVideo = document.getElementById("datasetVideo");
const datasetCanvas = document.getElementById("datasetCanvas");

const btnStartDatasetCamera = document.getElementById("btnStartDatasetCamera");
const btnCaptureDataset = document.getElementById("btnCaptureDataset");
const btnStopDatasetCamera = document.getElementById("btnStopDatasetCamera");

const modalDataset = document.getElementById("modalDataset");

let datasetStream = null;

// ==============================
// Stop Camera
// ==============================

function stopCamera() {

    if (stream) {

        stream.getTracks().forEach(track => track.stop());

        stream = null;

    }

    if (video) {

        video.pause();
		video.style.display = "none";

    }

    if (btnStartCamera) btnStartCamera.disabled = false;

    if (btnStopCamera) btnStopCamera.disabled = true;

    if (btnCapture) btnCapture.disabled = true;

}
if (btnStopCamera) {

    btnStopCamera.addEventListener("click", function () {

        stopCamera();

    });

}

// ==============================
// Start Camera
// ==============================

if (btnStartCamera) {

    btnStartCamera.addEventListener("click", async function () {

        try {

const camera = getCameraSetting();

const resolution = camera.resolution.split("x");

		stream = await navigator.mediaDevices.getUserMedia({

			video:{

				width:{
					ideal:parseInt(resolution[0])
				},

				height:{
					ideal:parseInt(resolution[1])
				},

				frameRate:{
					ideal:camera.fps
				},

				...(camera.device ? {
					deviceId:{
						exact:camera.device
					}
				} : {})

			},

			audio:false

		});

			video.srcObject = stream;

			video.onloadedmetadata = function () {

				video.play();

			};

            btnStartCamera.disabled = true;
            btnStopCamera.disabled = false;
            btnCapture.disabled = false;

        }

        catch (err) {

            console.error(err);

            alert("Kamera tidak dapat diakses.");

        }

    });

}

// ==============================
// Stop Camera Button
// ==============================

if(btnStopDatasetCamera){

    btnStopDatasetCamera.addEventListener("click",function(){

        stopDatasetCamera();

    });

}

// ==============================
// Capture
// ==============================

if (btnCapture) {

    btnCapture.addEventListener("click", function () {

        const ctx = canvas.getContext("2d");

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        ctx.drawImage(video, 0, 0);

		const image = canvas.toDataURL("image/jpeg", 0.95);
		if (photos.length >= 20) {

			alert("Maksimal 20 foto.");

			return;

		}

		photos.push(image);

		renderDataset();

    });

}

// ==============================
// Delete Last
// ==============================

if (btnDeleteLast) {

    btnDeleteLast.addEventListener("click", function () {

        if (photos.length > 0) {

            photos.pop();

            renderDataset();

        }

    });

}
// ==============================
// Upload Dataset
// ==============================

if (btnUploadDataset && fileUpload) {

    btnUploadDataset.addEventListener("click", function () {

        fileUpload.click();

    });

}
// ==============================
// Pilih File
// ==============================

if (fileUpload) {

    fileUpload.addEventListener("change", function () {

        const files = this.files;

        if (files.length === 0) {

            return;

        }

        Array.from(files).forEach(file => {

            if (!file.type.startsWith("image/")) {

                return;

            }

            const reader = new FileReader();

            reader.onload = function (e) {

               if (photos.length >= 20) {

    alert("Maksimal 20 foto.");

    return;

}

photos.push(e.target.result);

photos.sort();

renderDataset();

            };

            reader.readAsDataURL(file);

        });

        // Reset agar file yang sama bisa dipilih lagi
        this.value = "";

    });

}
// ==============================
// Render Dataset
// ==============================

function renderDataset() {

    if (!datasetGrid || !photoCount) return;

    datasetGrid.innerHTML = "";

    if (photos.length === 0) {

        datasetGrid.innerHTML = `
            <div class="text-muted">
                Belum ada dataset
            </div>
        `;

        btnDeleteLast.disabled = true;

    }

    else {

        photos.forEach(function (photo) {

            const img = document.createElement("img");

            img.src = photo;

            datasetGrid.appendChild(img);

        });

        btnDeleteLast.disabled = false;

    }

    photoCount.innerHTML = photos.length + " / 20 Foto";

}
// ==============================
// Reset Form
// ==============================

function resetForm() {

    const personID = document.getElementById("personID");
    const personName = document.getElementById("personName");
    const gender = document.querySelector("select");
    const divisi = document.getElementById("personDivision");

    if (personID) personID.value = "";
    if (personName) personName.value = "";
    if (gender) gender.selectedIndex = 0;
    if (divisi) divisi.value = "";

    photos = [];

    renderDataset();

    stopCamera();
	
	if (canvas) {

    const ctx = canvas.getContext("2d");

    ctx.clearRect(0, 0, canvas.width, canvas.height);

}

}
async function loadPersonID() {

    const response = await fetch("/generate_person_id");

    const result = await response.json();

    document.getElementById("personID").value = result.person_id;

}
// ==============================
// Modal Closed
// ==============================

if (modalTambahPerson) {

    modalTambahPerson.addEventListener("shown.bs.modal", function () {

        loadPersonID();

    });

    modalTambahPerson.addEventListener("hidden.bs.modal", function () {

        resetForm();

    });

}

const btnSavePerson = document.getElementById("btnSavePerson");

if(btnSavePerson){

    btnSavePerson.addEventListener("click", savePerson);

}

async function savePerson(){
	const personName = document.getElementById("personName").value;
	const gender = document.getElementById("personGender").value;
	const division = document.getElementById("personDivision").value;
    const personID = document.getElementById("personID").value;

    if(personID==""){

        alert("ID Person belum diisi.");

        return;

    }

    if(photos.length==0){

        alert("Belum ada dataset.");

        return;

    }
const response = await fetch("/save_person", {

    method: "POST",

    headers: {
        "Content-Type": "application/json"
    },

    body: JSON.stringify({

        person_id: personID,
        name: personName,
        gender: gender,
        division: division,
        photos: photos

    })

});

if (!response.ok) {

    alert("Gagal menyimpan data.");

    return;

}

const result = await response.json();
   if(result.status=="success"){

    alert("Person berhasil disimpan.");

    resetForm();

    const modal = bootstrap.Modal.getInstance(
        document.getElementById("modalTambahPerson")
    );

    modal.hide();

    location.reload();

}
}
// ==============================
// Detail Person
// ==============================

document.querySelectorAll(".btnDetail").forEach(button => {

    button.addEventListener("click", async function () {

        const personID = this.dataset.id;

        const response = await fetch(`/person/${personID}`);

        const result = await response.json();

        if(result.status !== "success"){

            alert("Data tidak ditemukan");

            return;

        }

        const person = result.person;

        document.getElementById("detailPersonID").innerText = person.person_id;
        document.getElementById("detailPersonName").innerText = person.name;
        document.getElementById("detailGender").innerText = person.gender;
        document.getElementById("detailDivision").innerText = person.division;
        document.getElementById("detailDataset").innerText = person.dataset_count + " Foto";
        document.getElementById("detailStatus").innerText = person.status;
        document.getElementById("detailCreated").innerText = person.created_at;

        new bootstrap.Modal(
            document.getElementById("modalDetailPerson")
        ).show();

    });

});
let deletePersonID = "";

document.querySelectorAll(".btnDelete").forEach(button=>{

    button.addEventListener("click",function(){

        deletePersonID = this.dataset.id;

        document.getElementById("deletePersonName").innerText =
            this.dataset.name;

        new bootstrap.Modal(
            document.getElementById("modalDeletePerson")
        ).show();

    });

});
document.getElementById("btnConfirmDelete")
.addEventListener("click",async()=>{

    const response = await fetch(
        `/person/${deletePersonID}`,
        {
            method:"DELETE"
        }
    );

    const result = await response.json();

    if(result.status==="success"){

        location.reload();

    }else{

        alert(result.message);

    }

});
let currentDatasetPerson = "";
let currentDatasetName = "";
let editPersonID = "";

const modalEditPerson =
    document.getElementById("modalEditPerson");

const btnUpdatePerson =
    document.getElementById("btnUpdatePerson");
async function loadDataset(personID){
	
    const response = await fetch(
        `/person/${personID}/dataset`
    );

    const result = await response.json();

    const grid = document.getElementById(
        "datasetPersonGrid"
    );

    grid.innerHTML = "";

    if(result.images.length===0){

        grid.innerHTML = `
            <div class="text-muted">
                Belum ada dataset.
            </div>
        `;

        return;

    }

    result.images.forEach(image=>{

        grid.innerHTML += `

        <div class="dataset-card">

            <img
                src="/dataset/${personID}/${image}"
                class="img-fluid">

            <div class="dataset-overlay">

                <button
                    class="btn btn-danger btn-sm btnDeleteImage"
                    data-person="${personID}"
                    data-image="${image}">

                    <i class="bi bi-trash-fill"></i>

                </button>

            </div>

        </div>

        `;

    });

    attachDeleteImageEvent();

}
function attachDeleteImageEvent(){

    document
    .querySelectorAll(".btnDeleteImage")
    .forEach(button=>{

        button.onclick = async function(){

            if(!confirm("Hapus foto ini?")){

                return;

            }

            const response = await fetch(

                `/person/${this.dataset.person}/dataset/${this.dataset.image}`,

                {

                    method:"DELETE"

                }

            );

            const result = await response.json();

            if(result.status==="success"){

                loadDataset(currentDatasetPerson);

            }

        };

    });

}
async function deletePerson(personID){

    if(!confirm("Hapus person ini?")){

        return;

    }

    const response = await fetch(

        "/persons/delete/" + personID,

        {

            method:"POST"

        }

    );

    const result = await response.json();

    if(result.status==="success"){

        alert("Person berhasil dihapus.");

        location.reload();

    }

    else{

        alert(result.message);

    }

}
document.querySelectorAll(".btnDataset")
.forEach(button=>{

    button.addEventListener("click",async function(){

        currentDatasetPerson = this.dataset.id;
        currentDatasetName = this.dataset.name;

        document.getElementById("datasetPersonName").innerText =
            currentDatasetName;

        await loadDataset(currentDatasetPerson);

        new bootstrap.Modal(
            document.getElementById("modalDataset")
        ).show();

    });

});
if(btnUploadNewDataset){

    btnUploadNewDataset.addEventListener("click",function(){

        datasetUpload.click();

    });

}
if(datasetUpload){

    datasetUpload.addEventListener("change",async function(){

        const files=this.files;

        if(files.length===0){
            return;
        }

        for(const file of files){

            if(!file.type.startsWith("image/")){
                continue;
            }

            const reader=new FileReader();

            reader.onload=async function(e){

                const response=await fetch(

                    `/person/${currentDatasetPerson}/dataset/add`,

                    {

                        method:"POST",

                        headers:{
                            "Content-Type":"application/json"
                        },

                        body:JSON.stringify({

                            photo:e.target.result

                        })

                    }

                );

                const result=await response.json();

                if(result.status==="success"){

                    await loadDataset(currentDatasetPerson);

                }

            };

            reader.readAsDataURL(file);

        }

        this.value="";

    });

}
if(btnStartDatasetCamera){

    btnStartDatasetCamera.addEventListener("click", async function(){

        try{

            const camera = getCameraSetting();

const resolution = camera.resolution.split("x");

datasetStream = await navigator.mediaDevices.getUserMedia({

    video:{

        width:{
            ideal:parseInt(resolution[0])
        },

        height:{
            ideal:parseInt(resolution[1])
        },

        frameRate:{
            ideal:camera.fps
        },

        ...(camera.device ? {
            deviceId:{
                exact:camera.device
            }
        } : {})

    },

    audio:false

});

            datasetVideo.srcObject = datasetStream;
			await datasetVideo.play();
            datasetVideo.style.display = "block";

            btnStartDatasetCamera.disabled = true;
            btnCaptureDataset.disabled = false;
            btnStopDatasetCamera.disabled = false;

        }

        catch(err){

            console.error(err);

            alert("Kamera tidak dapat diakses.");

        }

    });

}
// ==============================
// Edit Person
// ==============================

document.querySelectorAll(".btnEdit")
.forEach(button=>{

    button.addEventListener("click", async function(){

        editPersonID = this.dataset.id;

        const response = await fetch(

            `/person/${editPersonID}/edit`

        );

        const result = await response.json();

        if(result.status !== "success"){

            alert("Data tidak ditemukan.");

            return;

        }

        const person = result.person;

        document.getElementById("editPersonID").value =
            person.person_id;

        document.getElementById("editPersonName").value =
            person.name;

        document.getElementById("editPersonGender").value =
            person.gender;

        document.getElementById("editPersonDivision").value =
            person.division;

        new bootstrap.Modal(modalEditPerson).show();

    });

});
// ==============================
// Update Person
// ==============================

if(btnUpdatePerson){

    btnUpdatePerson.addEventListener("click", async function(){

        const response = await fetch(

            `/person/${editPersonID}/update`,

            {

                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify({

                    name:document.getElementById("editPersonName").value,

                    gender:document.getElementById("editPersonGender").value,

                    division:document.getElementById("editPersonDivision").value

                })

            }

        );

        const result = await response.json();

        if(result.status==="success"){

            alert("Data berhasil diperbarui.");

            bootstrap.Modal
                .getInstance(modalEditPerson)
                .hide();

            location.reload();

        }else{

            alert("Gagal memperbarui data.");

        }

    });

}
// ==============================
// Capture Dataset
// ==============================

if(btnCaptureDataset){

    btnCaptureDataset.addEventListener("click", async function(){

        if(!datasetStream){

            alert("Kamera belum aktif.");

            return;

        }

        datasetCanvas.width = datasetVideo.videoWidth;
        datasetCanvas.height = datasetVideo.videoHeight;

        const ctx = datasetCanvas.getContext("2d");

        ctx.drawImage(
            datasetVideo,
            0,
            0,
            datasetCanvas.width,
            datasetCanvas.height
        );

        const photo = datasetCanvas.toDataURL(
            "image/jpeg",
            0.95
        );

        const response = await fetch(

            `/person/${currentDatasetPerson}/dataset/add`,

            {

                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify({

                    photo:photo

                })

            }

        );

        const result = await response.json();

        if(result.status==="success"){

            await loadDataset(currentDatasetPerson);

        }else{

            alert("Gagal menyimpan foto.");

        }

    });

}
if(btnStopDatasetCamera){

    btnStopDatasetCamera.addEventListener("click",function(){

        stopDatasetCamera();

    });

}
if(modalDataset){

    modalDataset.addEventListener("hidden.bs.modal", function(){

        stopDatasetCamera();

    });

}
function stopDatasetCamera(){

    if(datasetStream){

        datasetStream.getTracks().forEach(track=>track.stop());

        datasetStream = null;

    }

    datasetVideo.pause();

    datasetVideo.srcObject = null;

    datasetVideo.style.display = "none";

    btnStartDatasetCamera.disabled = false;
    btnCaptureDataset.disabled = true;
    btnStopDatasetCamera.disabled = true;

}
const searchPerson = document.getElementById("searchPerson");

if (searchPerson) {

    searchPerson.addEventListener("keyup", function () {

        const keyword = this.value.toLowerCase().trim();

        const rows = document.querySelectorAll(".person-row");

        rows.forEach(row => {

            const id = row.querySelector(".person-id")
                          .innerText
                          .toLowerCase();

            const name = row.querySelector(".person-name")
                            .innerText
                            .toLowerCase();

            if (id.includes(keyword) || name.includes(keyword)) {

                row.style.display = "";

            } else {

                row.style.display = "none";

            }

        });

    });

}
