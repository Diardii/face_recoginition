console.log("Person Add Loaded");

// =====================================
// Global
// =====================================

const MAX_PHOTO = 20;
let photos = [];

// =====================================
// DOM
// =====================================

// Camera
const cameraPreview = document.getElementById("cameraPreview");
const btnStartCamera = document.getElementById("btnStartCamera");
const btnStopCamera = document.getElementById("btnStopCamera");
const btnCapture = document.getElementById("btnCapture");

// Upload
const btnUpload = document.getElementById("btnUpload");
const fileUpload = document.getElementById("fileUpload");

// Dataset
const datasetGrid = document.getElementById("datasetGrid");
const photoCount = document.getElementById("photoCount");
const btnDeleteLast = document.getElementById("btnDeleteLast");

// Form
const personID = document.getElementById("personID");
const personName = document.getElementById("personName");
const personGender = document.getElementById("personGender");
const personDivision = document.getElementById("personDivision");
const btnSavePerson = document.getElementById("btnSavePerson");

// =====================================
// Init
// =====================================

window.addEventListener("DOMContentLoaded", () => {

    initialize();

});

async function initialize(){

    btnStopCamera.disabled = true;
    btnCapture.disabled = true;
    btnDeleteLast.disabled = true;

    await loadPersonID();

    renderDataset();

}

// =====================================
// Generate Person ID
// =====================================

async function loadPersonID(){

    try{

        const response = await fetch("/generate_person_id");

        const result = await response.json();

        personID.value = result.person_id;

    }

    catch(error){

        console.error(error);

    }

}

// =====================================
// Camera
// =====================================

btnStartCamera.addEventListener("click", startCamera);
btnStopCamera.addEventListener("click", stopCamera);
btnCapture.addEventListener("click", capturePhoto);
async function startCamera(){

    try{

        const response = await fetch("/camera/start",{

            method:"POST"

        });

        const result = await response.json();

        if(result.status !== "success"){

            alert(result.message);

            return;

        }

        cameraPreview.src = 
            "/dataset_video_feed?" + Date.now();

        btnStartCamera.disabled = true;
        btnStopCamera.disabled = false;
        btnCapture.disabled = false;

    }

    catch(error){

        console.error(error);

        alert("Gagal membuka kamera.");

    }

}

async function stopCamera(){

    try{

        await fetch("/camera/stop",{

            method:"POST"

        });

    }

    catch(error){

        console.error(error);

    }

    cameraPreview.src = "";

    btnStartCamera.disabled = false;
    btnStopCamera.disabled = true;
    btnCapture.disabled = true;

}

// =====================================
// Capture
// =====================================

async function capturePhoto() {

    if (photos.length >= MAX_PHOTO) {

        alert("Dataset sudah penuh.");

        return;

    }

    try {

        const response = await fetch("/camera/capture");

        const result = await response.json();

        if (result.status !== "success") {

            alert(result.message);

            return;

        }

        photos.push(result.photo);

        renderDataset();

    }

    catch (error) {

        console.error(error);

        alert("Gagal mengambil gambar.");

    }

}

// =====================================
// Upload Dataset
// =====================================

btnUpload.addEventListener("click",()=>{

    fileUpload.click();

});

fileUpload.addEventListener("change",function(){

    Array.from(this.files).forEach(file=>{

        if(photos.length >= MAX_PHOTO){

            return;

        }

        if(!file.type.startsWith("image/")){

            return;

        }

        const reader = new FileReader();

        reader.onload = e=>{

            photos.push(e.target.result);

            renderDataset();

        }

        reader.readAsDataURL(file);

    });

    this.value="";

});

// =====================================
// Delete Last
// =====================================

btnDeleteLast.addEventListener("click",()=>{

    if(photos.length===0){

        return;

    }

    photos.pop();

    renderDataset();

});

// =====================================
// Render Dataset
// =====================================

function renderDataset(){

    datasetGrid.innerHTML="";

    photoCount.innerHTML=`${photos.length} / ${MAX_PHOTO} Foto`;

    btnDeleteLast.disabled = photos.length===0;

    if(photos.length===0){

        datasetGrid.innerHTML=`
            <div class="text-muted">
                Belum ada dataset.
            </div>
        `;

        return;

    }

    photos.forEach(photo=>{

        const img=document.createElement("img");

        img.src=photo;

        img.className="img-thumbnail";

        datasetGrid.appendChild(img);

    });

}

// =====================================
// Save Person
// =====================================

btnSavePerson.addEventListener("click",savePerson);

async function savePerson(){

    if(personName.value.trim()===""){

        alert("Nama belum diisi.");

        return;

    }

    if(photos.length===0){

        alert("Dataset belum ada.");

        return;

    }

    try{

        const response = await fetch("/save_person",{

            method:"POST",

            headers:{

                "Content-Type":"application/json"

            },

            body:JSON.stringify({

                person_id:personID.value,
                name:personName.value,
                gender:personGender.value,
                division:personDivision.value,
                photos:photos

            })

        });

        const result = await response.json();

        if(result.status==="success"){

            alert("Person berhasil disimpan.");

            resetForm();

            await loadPersonID();

        }

        else{

            alert(result.message);

        }

    }

    catch(error){

        console.error(error);

        alert("Gagal menyimpan data.");

    }

}

// =====================================
// Reset
// =====================================

function resetForm(){

    personName.value="";
    personDivision.value="";
    personGender.selectedIndex=0;

    photos=[];

    renderDataset();

}
