📜 Project Overview:
This is a web-based grading assistant that allows users to:
✔ Register and log in securely with a username and password.
✔ Upload an answer key (the correct answers for an exam).
✔ Upload a student's answer sheet (PDF or text file).
✔ Automatically evaluate the answers, determine correct, incorrect, and uncertain responses.
✔ Display the results in a structured format with scrolling and navigation.

This project helps teachers and educators quickly grade students' answer sheets without manual checking, making the evaluation process faster and more efficient. 🚀

🔧 Technologies Used:
📌 Frontend (User Interface)
HTML → Structure of the web pages.
CSS → Styling and animations.
JavaScript → Handling UI interactions (buttons, form submission, etc.).
LocalStorage → Storing result data for easy access.
Fetch API → Sending requests to the backend.
📌 Backend (Server & Logic)
Python (FastAPI) → Handles user authentication, file uploads, and grading logic.
pytesseract (OCR) → Extract text from PDF answers (if needed).
PyMuPDF / pdfplumber → Extract text from PDFs.
Regular Expressions (Regex) → Match and evaluate student answers.
SQLite → Stores registered users and their credentials.
📌 Additional Features
Secure login (without email, only username & password).
Animated UI with smooth scrolling.
Sidebar navigation for dashboard.
File handling for both answer keys & student sheets.
Results stored and displayed with scrolling support.
⚙️ How the System Works?
1️⃣ User Registration & Login
User enters a username & password.
The system stores credentials securely.
If login is successful, the user is redirected to the dashboard.
2️⃣ Uploading the Answer Key
The teacher uploads the answer key (PDF/Text file).
The system extracts the correct answers and stores them.
3️⃣ Uploading the Student’s Answer Sheet
The teacher uploads the student's answer sheet.
The system extracts the answers and compares them with the answer key.
The grading logic identifies:
✅ Correct Answers
❌ Incorrect Answers
⚠ Uncertain Answers (partially correct)
4️⃣ Viewing the Result
The system calculates the score.
Results are displayed in a scrollable box.
The results are stored locally for future reference.
