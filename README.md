# 🛠️ KhawOat Multi-Tools Pro (v17.0.0)

**KhawOat Multi-Tools Pro** คือเครื่องมืออเนกประสงค์ระดับมืออาชีพ ที่ได้รับการปรับโฉมใหม่หมดจดภายใต้แนวคิด **Modern Midnight Pro** มอบประสบการณ์การใช้งานที่ลื่นไหล สวยงาม และทรงพลัง สำหรับงานด้านไอทีและการสนับสนุนระบบ

![Flet](https://img.shields.io/badge/UI_Framework-Flet-blue?style=for-the-badge&logo=python)
![Python](https://img.shields.io/badge/Language-Python_3.13-yellow?style=for-the-badge&logo=python)
![Version](https://img.shields.io/badge/Version-17.0.0_Pro-orange?style=for-the-badge&logo=github)

---

## ✨ มีอะไรใหม่ใน Big Update (v17.0.0)
*   **Structural Refactor**: ปรับโครงสร้าง handler, helper และ context ให้ขยายต่อได้ง่ายขึ้น
*   **Updater Hardening**: จำกัดขอบเขต auto-patch ให้ปลอดภัยขึ้น, เพิ่ม hash verification และ rollback
*   **Installer-first Policy for Major Changes**: ถ้ามีการเปลี่ยน code/runtime/dependency จะบังคับใช้ installer ใหม่แทน patch ตรง
*   **Release Workflow**: เพิ่ม `scripts/release.ps1` เพื่อรวมขั้นตอน validate, manifest refresh และ build ให้อยู่ใน flow เดียว
*   **Regression Safety**: เพิ่ม smoke tests และ unit tests สำหรับ logic สำคัญและ release metadata

### 📝 Maintenance Note (2026-05-08)
*   รอบนี้เน้นเก็บงาน **Version / Release Alignment** และรีเฟรช `manifest.json` ให้ตรงกับไฟล์จริงล่าสุด
*   มีการทดลองปรับ layout เพิ่มเติมระหว่าง QA แต่ได้ถอยกลับแล้ว เพื่อคงหน้าตา UI เดิมและลดความเสี่ยงกับ `flet==0.21.2`
*   งาน QA เชิง visual/live runtime ยังควรทำต่อในรอบถัดไปหลังจาก environment Python/venv เสถียรกว่านี้

## 💎 Pro Redesign (v16.6)
*   **Modern Midnight Aesthetic**: ธีมสีใหม่ที่ลุ่มลึกและสบายตา พร้อมการเล่นระดับมิติ (Depth & Elevation)
*   **Glassmorphism UI**: การใช้เอฟเฟกต์โปร่งแสงและเงาที่นุ่มนวล ทำให้ปุ่มและเครื่องมือดูมีมิติ
*   **Professional Sidebar**: เมนูด้านข้างแบบใหม่ที่เพรียวบาง พร้อม Hover Effects และการจัดวางที่ชัดเจน
*   **Dashboard Patch Notes**: (NEW!) เพิ่มส่วนแสดงบันทึกการเปลี่ยนแปลงล่าสุดในหน้า Home โดยดึงข้อมูลโดยตรงจากระบบ
*   **Compact Home Layout**: ปรับปรุงการจัดวาง Quick Access และ Middle Banner ให้กะทัดรัดและสมดุลยิ่งขึ้น
*   **Time Converter Fix**: แก้ไขบัคการคำนวณ .NET Ticks ให้ตรงกับเวลาท้องถิ่น (Local Time) อย่างแม่นยำ
*   **Flet Compatibility**: ปรับปรุงโค้ดให้รองรับ Flet v0.21.2+ เพื่อความเสถียรสูงสุดในการใช้งาน
*   **Enhanced Typography**: ปรับปรุงระบบตัวอักษรให้อ่านง่ายและเป็นระเบียบตามมาตรฐานสากล

---

## ✨ ฟีเจอร์หลัก (Key Features)

### 🗂️ Data Management
*   **Merge & Split**: จัดการไฟล์ CSV, Excel, และ Text ขนาดใหญ่
*   **JSON Tool Pro**: เครื่องมือจัดการ JSON แบบครบวงจร (Format, Diff, CSV conversion)
*   **Hidden Char Check**: ตรวจสอบและล้างอักขระที่มองไม่เห็น
*   **Image Optimizer**: บีบอัดขนาดไฟล์รูปภาพ (PNG, JPEG, WEBP) และเปลี่ยนนามสกุล

### 🔐 Security & Encoding
*   **JWT Decoder**: ถอดรหัส JWT Token พร้อมตรวจสอบสถานะการหมดอายุ
*   **Base64 Tool**: เข้ารหัสและถอดรหัสข้อความในรูปแบบ Base64
*   **Password Generator**: สร้างรหัสผ่านที่ปลอดภัยระดับสูง
*   **QR Generator**: สร้าง QR Code จากข้อความหรือลิงก์

### 🧮 Calculation & Conversion
*   **Binary Tool**: แปลงเลขฐาน 10 เป็นฐาน 2 พร้อมแสดง Breakdown ของแต่ละ Bit
*   **Bit Finder**: ค้นหาตำแหน่งของเลข '1' ในชุดตัวเลข พร้อมสร้าง SQL Query สำหรับตรวจสอบ Database
*   **Time Converter**: แปลงค่า Unix Epoch และ .NET Ticks ให้เป็นเวลาท้องถิ่น (Local Time)

### 📝 Support Utilities
*   **Smart Formatter**: เทมเพลตอีเมลตอบกลับมาตรฐานสำหรับทีม Support
*   **Compare Text**: เปรียบเทียบข้อความสองชุดแบบ Side-by-side เพื่อหาจุดที่แตกต่างกัน

---

## 🎨 UI/UX Design
ตัวโปรแกรมออกแบบด้วยธีม **Velvet Amethyst Pro** ซึ่งให้ความรู้สึกหรูหรา ทันสมัย และเป็นมืออาชีพ:
*   **Primary Color**: `#9D4EDD` (Amethyst Purple)
*   **Background**: `#10002B` (Deep Velvet Obsidian)
*   **Accent**: `#FFD700` (Champagne Gold)

แนวทาง UI ปัจจุบันของแอป:
*   **Panel-based Workspace**: ใช้ card/panel แบบมิติชัดเจนเพื่อแบ่ง input, action และ result ออกจากกัน
*   **Scroll-safe Layouts**: จัดหน้าที่มีผลลัพธ์ยาว เช่น JWT, Compare Text และ Smart Formatter ให้เลื่อนได้โดยไม่ทำให้ layout พัง
*   **Consistent Action Rows**: ปุ่มหลักถูกจัดให้อยู่ใน action row ที่รูปแบบสม่ำเสมอขึ้นในหลายเครื่องมือ
*   **Quick Access Dashboard**: หน้า Home ถูกปรับให้เป็นศูนย์รวมเครื่องมือและสถานะระบบที่อ่านง่ายขึ้น

---

## 🚀 ระบบอัปเดตอัตโนมัติ (Auto-Update)
โปรแกรมมาพร้อมกับระบบตรวจสอบเวอร์ชันผ่าน GitHub โดยอัตโนมัติ:
*   ทุกครั้งที่เปิดโปรแกรม ระบบจะเช็คเวอร์ชันล่าสุดจาก GitHub
*   หากเป็นการอัปเดตที่ปลอดภัยต่อ runtime ระบบจะดาวน์โหลด Patch เฉพาะไฟล์ที่อนุญาต เช่น asset ภายนอก
*   หากเป็นการอัปเดตที่กระทบโค้ดหลัก, executable packaging หรือ dependency เช่น `requirements.txt` ระบบจะบังคับให้ดาวน์โหลดตัวติดตั้งใหม่แทน
*   ทุกไฟล์ที่ patch จะถูกตรวจ hash ก่อนแทนที่ และมี rollback หากเขียนไฟล์ไม่สำเร็จหรือ hash ไม่ตรง

---

## 💻 วิธีการติดตั้ง (For Users)
1.  ดาวน์โหลดไฟล์ตัวติดตั้ง `KhawOat_MultiTools_v17.0.0_Setup.exe`
2.  รันตัวติดตั้งและทำตามขั้นตอนบนหน้าจอ
3.  เปิดโปรแกรมจาก Shortcut บน Desktop ได้ทันที

---

## 🛠️ สำหรับนักพัฒนา (For Developers)
โปรแกรมนี้พัฒนาด้วย **Python** และเฟรมเวิร์ก **Flet**

### หมายเหตุด้าน UI / Layout
โปรเจกต์นี้ยังใช้ `flet==0.21.2` และมีข้อควรระวังในการจัด layout:
*   หลีกเลี่ยงการใช้ `expand=True` ร่วมกับคอลัมน์ที่เปิด `scroll` โดยไม่จำเป็น
*   หลีกเลี่ยง `width=float("inf")` ในปุ่มหรือ container หลัก
*   ระวัง `Row(..., wrap=True)` ในหน้าที่มีหลาย control เพราะอาจทำให้บางหน้า render เพี้ยนในเวอร์ชันนี้
*   หากเพิ่มหน้าใหม่ ควรยึด pattern แบบ panel + action row + scroll-safe result section ตามที่ใช้ในหน้าล่าสุด

### การเตรียม Environment:
```powershell
.\scripts\setup.ps1
```

### การรันโปรแกรม:
```powershell
.\scripts\run.ps1
```

### การตรวจสุขภาพโปรเจกต์:
```powershell
.\scripts\check.ps1
```

### การเตรียม Release:
```powershell
.\scripts\release.ps1
```

ตัวเลือกที่ใช้ได้:
```powershell
.\scripts\release.ps1 -SkipExeBuild -SkipInstallerBuild
.\scripts\release.ps1 -SkipInstallerBuild
```

สิ่งที่สคริปต์ตรวจให้อัตโนมัติ:
*   version alignment
*   manifest refresh
*   project checks ก่อนและหลัง regenerate manifest
*   การมีอยู่จริงของ artifact หลัง build เช่น `.exe` และ installer
*   การสร้าง `logs/release-summary.txt` เป็น release checklist หลังจบ workflow

### Logging
โปรเจกต์จะเขียน log ลงโฟลเดอร์ `logs/` สำหรับ flow สำคัญ:
*   `logs/update.log` สำหรับระบบ auto-update
*   `logs/process.log` สำหรับ flow งานสำคัญ เช่น merge/split และ hidden char
*   `logs/release.log` สำหรับ release workflow

log ฝั่ง Python มี rotation อัตโนมัติ และ release log มี retention แบบง่ายเพื่อไม่ให้ไฟล์โตไม่จำกัด

---
*พัฒนาโดย: KhawOat & (AI Assistant)*
