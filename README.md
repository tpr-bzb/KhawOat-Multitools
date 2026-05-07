# 🛠️ KhawOat Multi-Tools (v16.4)

**KhawOat Multi-Tools** คือเครื่องมืออเนกประสงค์ (Utility Tools) ที่ออกแบบมาเพื่อช่วยอำนวยความสะดวกในการทำงานด้านไอที การจัดการข้อมูล และงานสนับสนุน (Application Support) โดยเน้นความเรียบง่าย รวดเร็ว และดีไซน์ที่ทันสมัยในสไตล์ Modern Minimal

![Flet](https://img.shields.io/badge/UI_Framework-Flet-blue?style=for-the-badge&logo=python)
![Python](https://img.shields.io/badge/Language-Python_3.13-yellow?style=for-the-badge&logo=python)
![Version](https://img.shields.io/badge/Version-16.4-orange?style=for-the-badge&logo=github)

---

## ✨ ฟีเจอร์หลัก (Key Features)

### 🗂️ Data Management
*   **Merge & Split**: จัดการไฟล์ CSV, Excel, และ Text ขนาดใหญ่ สามารถแบ่งไฟล์ตามจำนวนแถว หรือรวมไฟล์เข้าด้วยกันได้อย่างรวดเร็ว
*   **JSON Tool Pro**: เครื่องมือจัดการ JSON แบบครบวงจร (Format, Minify, Tree View, Search, Diff, และแปลงเป็น CSV)
*   **Hidden Char Check**: ตรวจสอบและล้างอักขระที่มองไม่เห็น (Zero-width characters) ที่มักทำให้ข้อมูลผิดพลาด

### 🔐 Security & Encoding
*   **Base64 Tool**: เข้ารหัสและถอดรหัสข้อความ/JSON ในรูปแบบ Base64
*   **Password Generator**: สร้างรหัสผ่านที่ปลอดภัยโดยกำหนดความยาวและรูปแบบได้ตามต้องการ
*   **QR Generator**: สร้าง QR Code จากข้อความหรือลิงก์ พร้อมบันทึกเป็นไฟล์ภาพ

### 🧮 Calculation & Conversion
*   **Binary Tool**: แปลงเลขฐาน 10 เป็นฐาน 2 พร้อมแสดง Breakdown ของแต่ละ Bit
*   **Bit Finder**: ค้นหาตำแหน่งของเลข '1' ในชุดตัวเลข พร้อมสร้าง SQL Query สำหรับตรวจสอบ Database
*   **Time Converter**: แปลงค่า Unix Epoch และ .NET Ticks ให้เป็นเวลาท้องถิ่น (Local Time)

### 📝 Support Utilities
*   **Smart Formatter**: เทมเพลตสำหรับเขียนอีเมลตอบกลับลูกค้า (Support Email Templates) เพื่อความรวดเร็วและเป็นมาตรฐาน
*   **Compare Text**: เปรียบเทียบข้อความสองชุดแบบ Side-by-side เพื่อหาจุดที่แตกต่างกัน

---

## 🎨 UI/UX Design
ตัวโปรแกรมออกแบบด้วยธีม **Midnight Earth Tone** ซึ่งช่วยถนอมสายตาและให้ความรู้สึกเป็นมืออาชีพ:
*   **Primary Color**: `#DDA15E` (โทนน้ำตาลทอง)
*   **Background**: `#0D0F0D` (โทนดำสนิท)
*   **Accent**: `#BC6C25` และ `#81B29A`

---

## 🚀 ระบบอัปเดตอัตโนมัติ (Auto-Update)
โปรแกรมมาพร้อมกับระบบตรวจสอบเวอร์ชันผ่าน GitHub โดยอัตโนมัติ:
*   ทุกครั้งที่เปิดโปรแกรม ระบบจะเช็คเวอร์ชันล่าสุดจาก GitHub
*   หากมีการอัปเดต ระบบจะดาวน์โหลด Patch เฉพาะไฟล์ที่แก้ไขมาติดตั้งให้ทันที (ไม่ต้องติดตั้งใหม่ทั้งหมด)

---

## 💻 วิธีการติดตั้ง (For Users)
1.  ดาวน์โหลดไฟล์ตัวติดตั้ง `KhawOat_MultiTools_v16.4_Setup.exe`
2.  รันตัวติดตั้งและทำตามขั้นตอนบนหน้าจอ
3.  เปิดโปรแกรมจาก Shortcut บน Desktop ได้ทันที

---

## 🛠️ สำหรับนักพัฒนา (For Developers)
โปรแกรมนี้พัฒนาด้วย **Python** และเฟรมเวิร์ก **Flet**

### การเตรียม Environment:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### การรันโปรแกรม:
```powershell
flet run main.py
```

---
*พัฒนาโดย: KhawOat & Jamie (AI Assistant)*
