console.log("Person Add Loaded");

// =====================================
// DOM
// =====================================

const personID =
    document.getElementById("personID");

const personName =
    document.getElementById("personName");

const personGender =
    document.getElementById("personGender");

const personDivision =
    document.getElementById("personDivision");

const personEmail =
    document.getElementById("personEmail");

const personUsername =
    document.getElementById("personUsername");

const personPassword =
    document.getElementById("personPassword");

const btnSavePerson =
    document.getElementById("btnSavePerson");


// =====================================
// Init
// =====================================

window.addEventListener(
    "DOMContentLoaded",
    async () => {
        await loadPersonID();
    }
);


// =====================================
// Generate Person ID
// =====================================

async function loadPersonID() {

    try {

        const response =
            await fetch("/generate_person_id");

        const result =
            await response.json();

        if (!response.ok) {
            alert(
                result.message ||
                "Gagal membuat ID Person."
            );
            return;
        }

        personID.value =
            result.person_id;

    } catch (error) {

        console.error(error);

        alert(
            "Gagal mengambil ID Person dari server."
        );
    }
}


// =====================================
// Save Person
// =====================================

btnSavePerson.addEventListener(
    "click",
    savePerson
);


async function savePerson() {

    if (
        personName.value.trim() === ""
    ) {
        alert("Nama belum diisi.");
        return;
    }

    if (
        personDivision.value.trim() === ""
    ) {
        alert("Divisi belum diisi.");
        return;
    }

    if (
        personEmail.value.trim() === ""
    ) {
        alert("Email belum diisi.");
        return;
    }

    if (
        !personEmail.value.includes("@")
    ) {
        alert("Format email tidak valid.");
        return;
    }

    if (
        personUsername.value.trim() === ""
    ) {
        alert("Username belum diisi.");
        return;
    }

    if (
        personPassword.value.trim() === ""
    ) {
        alert("Password belum diisi.");
        return;
    }

    btnSavePerson.disabled = true;
    btnSavePerson.innerText =
        "Menyimpan...";

    try {

        const response =
            await fetch(
                "/admin/person/create",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        person_id:
                            personID.value,

                        name:
                            personName.value.trim(),

                        gender:
                            personGender.value,

                        division:
                            personDivision.value.trim(),

                        email:
                            personEmail.value.trim(),

                        username:
                            personUsername.value.trim(),

                        password:
                            personPassword.value
                    })
                }
            );

        const result =
            await response.json();

        if (!response.ok) {

            alert(
                result.message ||
                "Gagal menyimpan person."
            );

            return;
        }

        if (
            result.status === "success"
        ) {

            alert(
                result.message ||
                "Person dan akun berhasil dibuat."
            );

            resetForm();

            await loadPersonID();

            return;
        }

        alert(
            result.message ||
            "Gagal menyimpan person."
        );

    } catch (error) {

        console.error(error);

        alert(
            "Gagal terhubung ke server."
        );

    } finally {

        btnSavePerson.disabled = false;

        btnSavePerson.innerText =
            "Simpan Person";
    }
}


// =====================================
// Reset
// =====================================

function resetForm() {

    personName.value = "";
    personDivision.value = "";
    personEmail.value = "";
    personUsername.value = "";
    personPassword.value = "";
    personGender.selectedIndex = 0;
}