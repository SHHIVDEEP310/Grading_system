async function registerUser() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    let formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    try {
        let response = await fetch("http://127.0.0.1:8000/register", {
            method: "POST",
            body: formData
        });

        let result = await response.json();
        console.log("Register Response:", result);

        document.getElementById("authStatus").innerText = response.ok ? `✅ Registered successfully` : `❌ ${result.detail}`;
    } catch (error) {
        console.error("Error registering user:", error);
        document.getElementById("authStatus").innerText = "❌ Registration failed.";
    }
}

async function loginUser() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    let formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    try {
        let response = await fetch("http://127.0.0.1:8000/login", {
            method: "POST",
            body: formData
        });

        let result = await response.json();
        console.log("Login Response:", result);

        if (response.ok) {
            window.location.href = "dashboard.html"; // Redirect to dashboard
        } else {
            document.getElementById("authStatus").innerText = `❌ ${result.detail}`;
        }
    } catch (error) {
        console.error("Error logging in:", error);
        document.getElementById("authStatus").innerText = "❌ Login failed.";
    }
}

async function uploadAnswerKey() {
    let fileInput = document.getElementById("answerKeyInput").files[0];

    if (!fileInput) {
        alert("Please select an answer key file.");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput);

    try {
        let response = await fetch("http://127.0.0.1:8000/upload_answer_key", {
            method: "POST",
            body: formData
        });

        let result = await response.json();
        console.log("Upload Answer Key Response:", result);

        document.getElementById("answerKeyStatus").innerText = response.ok ? `✅ Uploaded! (Total Questions: ${result.total_questions})` : `❌ Error: ${result.detail}`;
    } catch (error) {
        console.error("Error uploading answer key:", error);
        document.getElementById("answerKeyStatus").innerText = "❌ Upload failed.";
    }
}

async function processFile() {
    let studentName = document.getElementById("studentName").value;
    let fileInput = document.getElementById("fileInput").files[0];

    if (!studentName || !fileInput) {
        alert("Please enter student name and select a file.");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput);
    formData.append("studentName", studentName);

    try {
        let response = await fetch("http://127.0.0.1:8000/process_student_answer", {
            method: "POST",
            body: formData
        });

        let result = await response.json();
        console.log("Process File Response:", result);

        if (!response.ok) {
            console.error("Error from API:", result);
            alert("Error: " + (result.detail || "Unknown error"));
            return;
        }

        // ✅ Display results in the same page (No redirection)
        let resultContainer = document.getElementById("resultContainer");
        let resultDisplay = document.getElementById("resultDisplay");

        resultContainer.style.display = "block"; // Show the result section
        resultDisplay.innerHTML = `
            <p><strong>Student:</strong> ${result.student_name}</p>
            <p><strong>Score:</strong> ${result.score}%</p>
            <p><strong>Correct:</strong> ${result.correct}</p>
            <p><strong>Incorrect:</strong> ${result.incorrect}</p>
            <p><strong>Uncertain:</strong> ${result.uncertain}</p>
        `;

    } catch (error) {
        console.error("Error processing file:", error);
        alert("Error processing file: " + error.message);
    }
}

// ✅ Clear results and reset form
function clearResults() {
    document.getElementById("resultContainer").style.display = "none";
    document.getElementById("studentName").value = "";
    document.getElementById("fileInput").value = "";
}

function toggleMenu() {
    let sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}
