# 🏢 Address Standardization & Entity Resolution System

## 📌 Overview

This project is a **desktop-based solution for address cleaning and entity resolution**, designed to process raw, unstructured affiliation/address data and convert it into a standardized, structured format.

It is particularly useful for **research datasets, institutional records, and business intelligence applications**, where inconsistent address formats create challenges in data analysis.

---

## 🚀 Key Features

* 🔹 Multi-phase address cleaning pipeline (9 phases)
* 🔹 Removal of noise, abbreviations, and redundant terms
* 🔹 Intelligent conflict resolution (e.g., acad vs inst rules)
* 🔹 Entity normalization and restructuring
* 🔹 Deduplication of similar address entries
* 🔹 Manual mapping support for edge cases
* 🔹 Desktop-based executable for easy usage

---

## 🧠 Core Logic

The system processes addresses through a **custom pipeline**:

1. Basic keyword and pattern removal
2. Abbreviation merging with organization names
3. Removal of unnecessary campus/location terms
4. Context-aware filtering (e.g., dept, cent rules)
5. Priority-based restructuring
6. Special handling for “center/ctr” terms
7. Conflict resolution between entities (acad, inst, lab, council)
8. Deduplication of processed addresses
9. Final normalization and cleanup

---

## 🛠️ Tech Stack

* **Python**
* Data Processing & String Manipulation
* Rule-based NLP Techniques
* Desktop Packaging (Executable using PyInstaller)

---

## 📂 Project Structure

```
address_standardizer_app/
├── cleaning.py
├── deduplication.py
├── manual_mapping.py
├── main_app.py
└── README.md
```

---

## ▶️ How to Run

### Option 1: Run Python Code

1. Clone the repository
2. Install dependencies (if any)
3. Run:

   ```bash
   python main_app.py
   ```

### Option 2: Run Executable

* Navigate to the `dist/` folder
* Run:

  ```
  main_app.exe
  ```

---

## 📊 Use Cases

* Research paper affiliation cleaning
* Institutional data standardization
* Business intelligence data preprocessing
* Dataset preparation for ML models

---

## 🔮 Future Improvements

* Integration with ML-based entity matching
* GUI enhancements
* Support for international address formats
* API-based deployment

---

## 👨‍💻 Author

**Anurag Sharma**

---

## ⭐ Notes

This project was developed as part of a **data cleaning and entity resolution system**, focusing on improving data quality for downstream analytics and machine learning tasks.
