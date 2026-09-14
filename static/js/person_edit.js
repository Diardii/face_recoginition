const btnSave = document.getElementById("btnSave");

btnSave.addEventListener("click", savePerson);

async function savePerson() {

    const personID = document.getElementById("personID").value;

    const data = {

        name: document.getElementById("personName").value.trim(),

        gender: document.getElementById("personGender").value,

        division: document.getElementById("personDivision").value.trim(),

        email: document.getElementById("personEmail").value.trim()

    };

    if (data.name === "") {

        alert("Nama tidak boleh kosong.");

        return;

    }

    if (data.email !== "" && !data.email.includes("@")) {

        alert("Format email tidak valid.");

        return;

    }

    try {

        const response = await fetch(`/person/${personID}/update`, {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify(data)

        });

        const result = await response.json();

        if (result.status === "success") {

            alert("Data berhasil diperbarui.");

            window.location.href = "/persons";

        } else {

            alert(result.message || "Gagal memperbarui data.");

        }

    }
    catch (error) {

        console.error(error);

        alert("Tidak dapat terhubung ke server.");

    }

}