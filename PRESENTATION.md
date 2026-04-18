# MedAnalyzer AI — Project Presentation Guide

This document is designed to help you present the **MedAnalyzer AI** project. It includes a breakdown of the technical stack, the application workflow, core features, and a list of common Questions & Answers that you can use to prepare for a demonstration or pitch.

---

## 1. The Core Concept

**What is MedAnalyzer?**
MedAnalyzer is an intelligent medical platform that uses AI to parse unstructured medical reports (PDFs, Images), extract crucial health data (diseases, lab results, medications), cross-reference medications for potential interactions, and present the data dynamically in a unified patient health timeline and dashboard.

**The Problem it Solves:**
Doctors and patients deal with fragmented medical records in various formats. MedAnalyzer eliminates manual data entry, warns about drug interactions instantly, and provides a clear historical view of a patient's health.

---

## 2. Tech Stack Overview

MedAnalyzer uses a microservices architecture separating the frontend/backend from the heavy AI processing.

### **Frontend & User Interface**
- **HTML/CSS/JS (Vanilla & EJS)**: Server-side rendered views using EJS (Embedded JavaScript) for dynamic data injection.
- **Dynamic Charts**: (If applicable) Used for rendering the patient health timelines and lab results.

### **Node.js Backend (Main Server)**
- **Express.js**: Handles routing, user authentication, and API endpoints.
- **Multer**: Manages file uploads (PDFs, Images) from the frontend.
- **Axios**: Communicates with the Python AI microservice.
- **Mongoose / MongoDB Atlas**: Stores user accounts, structured patient data, and historical report logs.

### **Python AI Microservice (Data Extraction Engine)**
- **Flask**: Serves as the lightweight REST API for the AI engine.
- **PyTesseract & OpenCV**: Performs Optical Character Recognition (OCR) to convert images to text.
- **PyMuPDF (fitz)**: Extracts text directly from PDF documents.
- **spaCy**: Natural Language Processing (NLP) to extract medical entities (Diseases, Medications, Lab Values).

---

## 3. Application Workflow & Data Flow

Here is the step-by-step flow of what happens when a user uploads a report:

1. **Upload (Frontend -> Node.js)**
   - The user (Doctor/Patient) uploads a medical report (PDF/Image) via the dashboard.
   - The Node.js backend receives the file using `multer` and temporarily stores it.

2. **Delegation (Node.js -> Python AI)**
   - Node.js forwards the uploaded file via an HTTP request to the Python Flask microservice for processing.

3. **Extraction & NLP (Python AI)**
   - **Text Extraction:** If it's a PDF, `PyMuPDF` extracts the text. If it's an image, `OpenCV` processes the image and `PyTesseract` extracts the text via OCR.
   - **Entity Recognition:** `spaCy` analyzes the raw text, looking for specific patterns (e.g., Blood Pressure, Heart Rate, prescribed medications, diagnosed diseases).

4. **Safety Check (Python AI)**
   - The extracted medications are checked against a drug-interaction database/logic.
   - The AI generates alerts for any potentially dangerous drug combinations (e.g., Aspirin + Warfarin).

5. **Response & Persistence (Python AI -> Node.js -> MongoDB)**
   - The Python service sends structured JSON back to Node.js containing: `{ labResults, medications, diseases, alerts }`.
   - Node.js links this data to the Patient's profile and saves it to MongoDB Atlas.

6. **Visualization (Node.js -> Frontend)**
   - The frontend dashboard fetches the updated MongoDB data.
   - The EJS views render a beautiful, chronological health timeline, a summary of lab results, and any critical drug interaction warnings.

---

## 4. Potential Q&A (For Presentation/Defense)

### Q1: Why did you split the backend into Node.js and Python instead of using just one?
**Answer:** Node.js is excellent for handling asynchronous web requests, routing, database interactions, and serving frontend views quickly. However, Python has the most mature ecosystem for AI, ML, OCR (Tesseract), and NLP (spaCy). Splitting them into microservices allows each language to do what it's best at, making the application more scalable. 

### Q2: How does the OCR and NLP process work?
**Answer:** First, OpenCV preprocesses the image to increase contrast, then PyTesseract reads the text. Once we have raw text, we use spaCy (NLP) along with custom regular expressions to find specific medical keywords like "Hemoglobin" or "Blood Pressure", extract the numerical values next to them, and structure them into JSON format.

### Q3: What happens if the AI fails to read a bad quality scan?
**Answer:** The system is designed to extract whatever is legible. We can implement a manual override feature on the frontend where a doctor can correct or manually enter data that the OCR missed due to poor scan quality.

### Q4: How is patient data secured?
**Answer:** User passwords are encrypted using `bcryptjs`. We use session-based authentication to ensure users can only access their own data. Furthermore, the database is hosted securely on MongoDB Atlas with IP whitelisting (Network Access control).

### Q5: How do you handle Drug Interactions?
**Answer:** Once medications are extracted via NLP, we run them through an interaction checker algorithm. If it detects conflicting drugs, it immediately attaches an 'Alert' to the response payload, which is then flagged in red on the patient's dashboard.

---

## 5. Key Highlights to Emphasize in Your Demo
1. **Show a "Before and After":** Show a messy, unstructured medical report PDF, and then show how beautifully it gets organized on the MedAnalyzer dashboard.
2. **Highlight the Alerts:** Upload a fake report containing conflicting drugs to trigger the Drug Interaction warning live. This emphasizes the *intelligence* of the system.
3. **Show the Timeline:** Explain how this saves doctors time. Instead of reading 10 separate PDFs from the past year, they just scroll through the chronological timeline.
