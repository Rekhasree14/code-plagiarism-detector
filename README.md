# 🔍 Code Plagiarism Detector

A robust, web-based code plagiarism detection system built with **Python** and **Flask**. It detects code similarity, refactoring, and obfuscation techniques such as variable renaming, comment removal/modification, and structural code reshaping using lexical tokenization and **Abstract Syntax Tree (AST)** analysis.

---

## ✨ Features

- **Lexical Tokenization**: Tokenizes source code, strips comments, and compares token sequences.
- **Variable Renaming Normalization**: Normalizes user-defined variables (`VAR1`, `VAR2`, ...) to catch plagiarism where only variable names were changed.
- **AST Structural Analysis**: Analyzes program flow and control structures (loops, conditions, function definitions, returns, and assignments) to catch structural copies even if variable and function names differ.
- **Function-Level Matching**: Parses and normalizes individual functions to detect code reuse and reordering.
- **Transformation & Obfuscation Detection**: Automatically flags:
  - Variable renaming
  - Comment additions or deletions
  - Whitespace and formatting alterations
  - Structural/functional reorganization
- **Multi-Language Support**: Supports `.py`, `.java`, `.c`, `.cpp`, `.js`, `.html`, and `.css` files.
- **Interactive Web Interface**: Clean web UI for uploading two files or pasting code directly, featuring a detailed similarity report with visual indicators.

---

## 📁 Project Structure

```text
code-plagiarism-detector/
│
├── app.py              # Main Flask application and plagiarism detection algorithms
├── static/
│   └── style.css       # UI styling and responsive design
├── templates/
│   ├── index.html      # Home page (code input & file upload forms)
│   ├── result.html     # Detailed similarity breakdown & comparison report
│   └── error.html      # Error handling page
├── uploads/            # Temporary storage for uploaded source files
├── .gitignore          # Git ignore rules for Python, cache, and uploads
└── README.md           # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** installed on your system.
- **pip** (Python package manager).

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Rekhasree14/code-plagiarism-detector.git
   cd code-plagiarism-detector
   ```

2. **(Optional) Create and activate a virtual environment:**
   - **Windows:**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install flask
   ```

---

## 💻 Running the Application

1. Start the Flask development server:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```text
   http://127.0.0.1:5000/
   ```

3. Upload or paste two source code files to generate an instant plagiarism and similarity report!

---

## 📊 How the Similarity is Calculated

The detector evaluates code across multiple dimensions:

| Analysis Layer | Method | What it Detects |
| :--- | :--- | :--- |
| **Token Similarity** | `difflib.SequenceMatcher` | Direct copy-paste and literal matches |
| **Variable Similarity** | Identifier normalization | Variable renaming and renaming obfuscation |
| **Structure Similarity** | Python AST Node Analysis | Logic copying despite name and formatting changes |
| **Function Similarity** | Normalized AST Function Trees | Reordered or borrowed function implementations |

---

## 👩‍💻 Author

- **Rekhasree** - [@Rekhasree14](https://github.com/Rekhasree14)
