from flask import Flask, render_template, request
import joblib
import os
import pdfplumber
import docx
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Load trained model
model = joblib.load("placement_model.pkl")

# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Resume text extraction
def extract_resume_text(filepath):
    text = ""
    if filepath.endswith(".pdf"):
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif filepath.endswith(".docx"):
        document = docx.Document(filepath)
        for para in document.paragraphs:
            text += para.text + " "
    return text.lower()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        cgpa = float(request.form["cgpa"])
        internships = int(request.form["internships"])
        projects = int(request.form["projects"])
        skills = int(request.form["skills"])
        communication = int(request.form["communication"])
        backlogs = int(request.form["backlogs"])
        aptitude = int(request.form["aptitude"])
    except:
        return "Invalid input. Please enter numeric values only."

    # ML Prediction
    data = [[cgpa, internships, projects, skills, communication, backlogs, aptitude]]
    prediction = model.predict(data)[0]
    result = "Placed 🎉" if prediction == 1 else "Not Placed 😔"

    # Skill Improvement Tips
    tips = []
    if cgpa < 7:
        tips.append("📘 Improve CGPA (target ≥ 7.5).")
    if internships == 0:
        tips.append("🏢 Complete at least one internship.")
    if projects < 2:
        tips.append("💻 Build more practical projects.")
    if communication < 3:
        tips.append("🗣️ Improve communication skills.")
    if aptitude < 60:
        tips.append("🧠 Practice aptitude & reasoning.")
    if backlogs > 0:
        tips.append("⚠️ Clear backlogs as early as possible.")
    if not tips:
        tips.append("✅ You are well-prepared. Focus on mock interviews.")

    # Resume Upload & Analysis
    resume_tips = []
    file = request.files.get("resume")

    if file and file.filename != "":
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        resume_text = extract_resume_text(filepath)

        keywords = ["python", "machine learning", "project", "internship", "sql", "communication"]
        for word in keywords:
            if word not in resume_text:
                resume_tips.append(f"➕ Consider adding '{word}' to your resume.")

        if not resume_tips:
            resume_tips.append("✅ Resume looks strong and relevant.")
    else:
        resume_tips.append("ℹ️ Resume not uploaded for analysis.")

    return render_template(
        "result.html",
        result=result,
        tips=tips,
        resume_tips=resume_tips
    )

if __name__ == "__main__":
    app.run(debug=False)
