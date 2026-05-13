# 📘 คู่มือการพัฒนาและระบบอัปเดต (KhawOat Multi-Tools)

คู่มือนี้สรุปขั้นตอนการทำงานตั้งแต่การพัฒนาไปจนถึงการปล่อยอัปเดตผ่าน GitHub สำหรับเวอร์ชัน 16.4 เป็นต้นไป

---

### 🛠️ 1. ขั้นตอนการเตรียมเครื่อง (Setup ครั้งแรก)
หากคุณเริ่มโปรเจกต์ใหม่ในเครื่องอื่น หรือยังไม่ได้เชื่อมต่อ GitHub:
1.  **เชื่อมต่อ Repo**:
    ```powershell
    git init
    git remote add origin https://github.com/tpr-bzb/KhawOat-Multitools.git
    git branch -M main
    ```

---

### 🚀 2. ขั้นตอนการปล่อยอัปเดตใหม่ (Workflow ปัจจุบัน)
เมื่อคุณแก้ไขโค้ดเสร็จแล้วและต้องการส่งให้ผู้ใช้งานอัปเดต:

#### **ขั้นที่ A: เตรียมข้อมูลเวอร์ชัน**
1.  แก้ไข `version.json`: เปลี่ยนเลข `"version"` และเขียน `"change_log"`
2.  ถ้าเป็น big update หรือมี dependency ใหม่ ให้ตั้ง `force_setup` เป็น `true`

#### **ขั้นที่ B: รัน release workflow กลาง**
```powershell
.\scripts\release.ps1
```

สคริปต์นี้จะทำงานหลักให้เอง:
1.  รัน checks ทั้งหมด
2.  regenerate `manifest.json`
3.  ตรวจ version alignment
4.  build `.exe`
5.  build installer ถ้าเครื่องมี Inno Setup
6.  validate artifact หลัง build ว่ามีไฟล์ output จริงและไม่เป็นไฟล์ว่าง
7.  สร้าง `logs/release-summary.txt` เพื่อใช้เป็น checklist หลัง release

ตัวอย่างโหมดเบา:
```powershell
.\scripts\release.ps1 -SkipExeBuild -SkipInstallerBuild
.\scripts\release.ps1 -SkipInstallerBuild
```

#### **ขั้นที่ C: ส่งขึ้น GitHub (Push)**
```powershell
git add .
git commit -m "Release vX.Y: [ระบุสิ่งที่เปลี่ยน]"
git push origin main
```

---

### 📦 3. กรณีต้องออกตัวติดตั้งใหม่ (Major Update)
หากคุณมีการแก้ไขโครงสร้างโปรแกรมครั้งใหญ่ หรือเปลี่ยน Library ใหม่ๆ จนระบบ Patch เอาไม่อยู่:
1.  ตั้ง `force_setup` เป็น `true` ใน `version.json`
2.  รัน `.\scripts\release.ps1`
3.  แจกจ่ายตัว Setup ใหม่ให้ผู้ใช้

---

### 📥 4. สิ่งที่ผู้ใช้จะได้รับ
1.  เมื่อผู้ใช้เปิดโปรแกรม v16.4+ ขึ้นมา หน้า Splash Screen จะเช็คไฟล์จาก GitHub อัตโนมัติ
2.  **กรณี Patch ปกติ**: โปรแกรมจะโหลดไฟล์ที่แก้ไขมาทับเครื่องผู้ใช้ และ Restart ตัวเองทันที
3.  **กรณี Force Setup (อัปเดตใหญ่)**: หากคุณตั้งค่า `force_setup: true` ใน `version.json` ผู้ใช้จะเห็นปุ่มให้ดาวน์โหลดตัวติดตั้งใหม่แทนการ Patch อัตโนมัติ (เหมาะสำหรับเวลาเพิ่ม Library ใหม่)

---

### ⚠️ ข้อควรระวัง
*   **ให้ใช้ `scripts/release.ps1` เป็น flow หลัก**: อย่าปล่อย release ด้วยการ regenerate manifest หรือ build แบบแยกขั้นเองถ้าไม่จำเป็น
*   **โครงสร้าง Assets**: หากมีการเพิ่มรูปใหม่ในโฟลเดอร์ `assets` ต้องตรวจสอบให้แน่ใจว่าได้ Push โฟลเดอร์นั้นขึ้น GitHub ด้วย
*   **เลขเวอร์ชัน**: `version.json`, `manifest.json`, `README.md`, และ `setting.iss` ต้องตรงกันเสมอ
*   **Patch Policy**: build แบบ `.exe` จะ auto-patch ได้เฉพาะไฟล์ runtime-safe; ถ้ากระทบ code หรือ dependency เช่น `requirements.txt` ต้องใช้ installer ใหม่
*   **Logs**: หากต้องไล่ปัญหา update/release ให้ตรวจ `logs/update.log` และ `logs/release.log` ก่อน

---
*บันทึกโดย เจมี่ (Senior AI Developer) - พฤษภาคม 2026*
