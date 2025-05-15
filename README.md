# 📝 AMTA Scraper  

This script scrapes massage therapist data from the **American Massage Therapy Association (AMTA)** website, specifically for professionals in Connecticut.  

---

## 📁 **Generated Files**  
- **amta.csv:** Master database storing all professionals without duplicates.  
- **amta_newprof.csv:** Contains only the newly detected professionals in each run (empty if no new professionals are found).  

---

## ⚙️ **Requirements**  
- **Python 3.8+**  
- **Google Chrome**  
- **Selenium:**  
    ```bash
    pip install selenium webdriver-manager
    ```  

---

## 🚀 **How to Use**  
1. **Clone the repository or download the script.**  
2. **Install the dependencies:**  
    ```bash
    pip install selenium webdriver-manager
    ```  
3. **Run the script:**  
    ```bash
    python amta.py
    ```  

---

## 🌐 **Script Details**  
- Searches for "Massage" in "CT".  
- Filters professionals located in specific cities in Fairfield County.  
- Extracts names, cities, and websites (if available).  
- Avoids duplicates by comparing with the master file (`amta.csv`).  
- If no new professionals are found, the `amta_newprof.csv` file remains empty.  

---

## 🤖 **Customization**  
To add or remove target cities, edit the `TARGET_CITIES` list in the script.  
