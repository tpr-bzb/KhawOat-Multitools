# Implementation Plan

## Objective

เอกสารนี้สรุปงานถัดไปที่ควรทำเพื่อพัฒนาระบบ `KhawOat Multi-Tools Pro` ต่อจากสถานะปัจจุบัน โดยเน้น 3 เรื่องหลัก:

1. ทำให้โค้ดดูแลง่ายขึ้น
2. ลดความเสี่ยง regressions
3. ทำให้การ build/release เสถียรและทำซ้ำได้

---

## Current Status

สถานะที่มีอยู่แล้ว:

- แยก `app_release.py` และ `app_runtime.py` ออกจาก `main.py` แล้ว
- แยก handler ของหลายเครื่องมือออกจาก `main.py` แล้ว
- ซ่อม `.venv` ให้ใช้งานได้ใน workspace แล้ว
- เริ่ม `Phase 1` แล้ว:
  - ย้าย logic ของหลายเครื่องมือออกจาก `main.py` ครบตามแผนรอบแรก
  - เปลี่ยน navigation/tool orchestration เป็น registry-driven flow แล้ว
  - แยก `TOOL_SPECS` ไปที่ `tool_registry.py`
  - แยก `TOOL_BUILDERS` และ grouped setup functions ไปที่ `tool_builders.py`
  - เปลี่ยน dependency ที่ส่งเข้า builders จาก raw dict เป็น `ToolBuildContext`
  - รวม dependency ของ handler layer ผ่าน `HandlerContext` แล้ว
  - แยก Smart Formatter templates ไปที่ `formatter_templates.py`
  - แยก loading dialog และ file picker hub ไปที่ `ui_helpers.py`
  - ย้าย toast logic เข้า `UiRuntime`
- `scripts/check.ps1` กลับมาผ่าน:
  - `smoke_check_ok`
  - `handler_smoke_ok`
  - `services_unit` OK
  - `release_metadata_unit` OK
  - `updater_e2e` OK
  - `Project checks passed.`
- updater safety ดีขึ้น:
  - build แบบ executable จะ auto-patch ได้เฉพาะไฟล์ runtime-safe
  - ถ้ามี code patch หรือ dependency patch เช่น `requirements.txt` จะบังคับไป installer ใหม่
  - patch file มี hash verification และ rollback แล้ว
- มี `scripts/release.ps1` แล้วสำหรับ release workflow กลาง
- มี logging สำหรับ update/release/process flow แล้ว พร้อม rotation/retention เบื้องต้น

สถานะเชิงโครงสร้างตอนนี้ถือว่าเริ่มดีขึ้น แต่ยังควรลดภาระของ `main.py` และเพิ่มชั้นทดสอบให้มากขึ้นก่อนขยายฟีเจอร์เพิ่ม

---

## Recommended Priorities

ลำดับงานที่แนะนำ:

1. ทำ `handler/service boundary` ให้สม่ำเสมอครบทั้งระบบ
2. เพิ่ม automated tests สำหรับ logic สำคัญ
3. แยก config/release/update ออกจาก UI ให้ชัดขึ้น
4. เพิ่ม logging/telemetry สำหรับการใช้งานจริง
5. ทำ release workflow ให้เป็นมาตรฐาน

---

## Phase 1: Structural Cleanup

เป้าหมายของ phase นี้คือทำให้ codebase ขยายต่อได้ง่ายและลด logic ที่กระจุกในจุดเดียว

### 1. Reduce `main.py` further

สิ่งที่ควรทำ:

- เปลี่ยนจาก `if index == ...` ยาว ๆ ไปเป็น `tool registry`
- ให้แต่ละ tool มี metadata กลาง เช่น:
  - `id`
  - `title`
  - `icon`
  - `nav label`
  - `ui builder`
  - `handler registrar`

ผลลัพธ์ที่ต้องการ:

- เพิ่ม tool ใหม่ได้โดยแก้จุดเดียว
- ลด coupling ใน `main.py`
- ทำ responsive/layout wiring ง่ายขึ้น

สถานะ:

- ทำไปแล้วมากขึ้น
- orchestration/navigation เปลี่ยนมาใช้ registry แล้ว
- แยก `TOOL_BUILDERS` และ grouped setup functions ออกจาก `main.py` แล้ว
- builders ใช้ shared context object แล้ว
- งานถัดไปคือพิจารณาว่าจะลด argument ของ handlers ต่อด้วย context หรือ helper layer แบบไหนจึงเหมาะที่สุด

### 2. Move templates/constants out of handlers

จุดที่ควรแยก:

- Smart Formatter templates
- ข้อความ status/toast ที่ใช้ซ้ำ
- default sample data ของเครื่องมือบางตัว

แนวทาง:

- สร้าง `templates.py` หรือ `data/templates.json`
- สร้าง `constants.py` สำหรับข้อความและค่าคงที่ที่ใช้ร่วมกัน

ผลลัพธ์ที่ต้องการ:

- แก้ข้อความได้โดยไม่แตะ logic
- review diff ง่ายขึ้น

สถานะ:

- Smart Formatter templates แยกออกแล้ว
- ยังเหลือข้อความ status/toast ที่ใช้ซ้ำในหลาย handler ซึ่งควรค่อย ๆ รวมในรอบถัดไป

### 3. Extract shared UI helpers

สิ่งที่ควรแยก:

- file picker flow
- toast helpers
- modal helpers
- busy/loading state utilities

แนวทาง:

- พิจารณาสร้าง `app_context.py` หรือ `ui_context.py`
- รวม dependency ที่ handler ต้องใช้บ่อยให้อยู่ใน object เดียว

ผลลัพธ์ที่ต้องการ:

- ลดจำนวน argument ที่ส่งเข้า handler
- ทำ handler อ่านง่ายขึ้น

สถานะ:

- มี `ToolBuildContext` สำหรับ builder layer แล้ว
- มี shared UI helper สำหรับ loading dialog และ file picker แล้ว
- toast ถูกดันเข้า runtime layer แล้ว
- handler layer ใช้ `HandlerContext` ตัวเดียวร่วมกันแล้ว
- งานถัดไปคือพิจารณาว่าจะตัด helper/view logic ที่ยังหนาในบาง handler ออกเป็นโมดูลย่อยต่อหรือไม่

### 4. Move JSON tree rendering helper out of handler

สถานะปัจจุบัน:

- JSON Tool ถูกย้าย handler ออกจาก `main.py` แล้ว
- tree rendering ถูกแยกออกไปที่ `json_view_helpers.py` แล้ว
- line-number sync, reset state, และ diff result rendering ถูกแยกไปที่ `json_tool_helpers.py` แล้ว
- diff dialog open/close flow และ parse error focus ถูกแยกเป็น helper แล้ว
- handler ของ JSON Tool ยังเหลือ orchestration logic เป็นหลัก

สิ่งที่ควรทำ:

- ถ้าจะลดความหนาต่อ ให้พิจารณาว่าจะรวม parse/transform flow ของ JSON/CSV/B64 เป็น service helper เพิ่มหรือพอแค่นี้

ผลลัพธ์ที่ต้องการ:

- แยก business action กับ rendering responsibility ชัดขึ้น

### 5. Reduce Merge/Split handler thickness

สถานะปัจจุบัน:

- `merge/split` ยังอยู่ใน handler module เดิม แต่ logic ย่อยถูกแยกไปที่ `merge_split_helpers.py` แล้ว
- input normalization, request/config preparation, loading state wiring, status callback, และ summary rendering ถูกแยกออกจาก handler แล้ว

สิ่งที่ควรทำ:

- ถ้าจะลดความหนาต่อ ให้พิจารณาว่าจะย้าย cancel-flow state machine หรือ request validation ออกเพิ่มหรือพอแค่นี้

ผลลัพธ์ที่ต้องการ:

- ให้ handler เหลือ orchestration และ event binding เป็นหลัก

---

## Phase 2: Testing and Regression Safety

เป้าหมายของ phase นี้คือทำให้ refactor ต่อได้โดยไม่เสี่ยงพังเงียบ

### 1. Add unit tests for `services.py`

ลำดับแรกที่ควรครอบคลุม:

- `decode_jwt`
- `compare_json`
- `get_text_diff`
- `csv_to_json_data`
- `json_to_csv_text`
- `find_binary_indices`
- `clean_hidden_text`
- `epoch_to_local_datetime_text`
- `ticks_to_local_datetime_text`

ผลลัพธ์ที่ต้องการ:

- ตรวจพฤติกรรมของ logic หลักได้เร็ว
- ลดการไล่ทดสอบผ่าน UI ทุกครั้ง

สถานะ:

- เพิ่ม `scripts/services_unit.py` แล้ว
- เชื่อมเข้ากับ `scripts/check.ps1` แล้ว
- ครอบคลุมแล้วสำหรับ:
  - `analyze_hidden_chars`
  - `compare_json`
  - `csv_to_json_data`
  - `json_to_csv_text`
  - `find_binary_indices`
  - `clean_hidden_text`
  - `epoch_to_local_datetime_text`
  - `ticks_to_local_datetime_text`
  - `decode_jwt`
  - `list_files_to_process`
  - `process_file_split_streaming`
- ยังสามารถเพิ่มต่อได้ในรอบถัดไปสำหรับ:
  - `check_for_patches`
  - `apply_patch`

### 2. Add smoke/regression checks for release metadata

สิ่งที่ควรตรวจ:

- `version.json`
- `manifest.json`
- version ใน installer
- version ใน README

ผลลัพธ์ที่ต้องการ:

- กันเลขเวอร์ชันไม่ตรงกันก่อนปล่อย release

สถานะ:

- เพิ่ม `scripts/release_metadata_unit.py` แล้ว
- เช็ก version alignment ระหว่าง:
  - `version.json`
  - `manifest.json`
  - `README.md`
  - `setting.iss`
- มี regression test สำหรับ `generate_manifest.py` แล้ว
- สคริปต์ถูกผูกเข้ากับ `scripts/check.ps1` แล้ว
- `requirements.txt` ถูก track ใน manifest แล้ว เพื่อให้ dependency change ถูกตรวจจับใน update policy

### 2.5 Add updater end-to-end simulations

สถานะ:

- เพิ่ม `scripts/updater_e2e.py` แล้ว
- ครอบคลุม flow สำคัญของ `run_auto_update()` แล้วสำหรับ:
  - no-update path
  - asset-only patch path
  - installer-required path
  - patch failure fallback path
- สคริปต์ถูกผูกเข้ากับ `scripts/check.ps1` แล้ว

### 3. Add focused handler-level smoke tests

เครื่องมือที่ควรเริ่มก่อน:

- JSON Tool
- Merge & Split
- Hidden Char
- Smart Formatter

หัวข้อที่ควรตรวจ:

- format/minify/search
- cancel flow
- copy output
- sample/demo load

สถานะ:

- เพิ่ม `scripts/handler_smoke.py` แล้ว
- มี focused smoke tests สำหรับ JSON Tool และ Merge & Split แล้ว
- สคริปต์ถูกผูกเข้ากับ `scripts/check.ps1` แล้ว
- ยังเหลือ Hidden Char และ Smart Formatter หากต้องการขยาย coverage ต่อ

### 4. Add lint/format commands

สิ่งที่ควรพิจารณา:

- `ruff`
- `black`

ถ้ายังไม่อยากเพิ่มทันที:

- อย่างน้อยควรมี script ตรวจ style หรือ import consistency

---

## Phase 3: Runtime and UX Improvements

เป้าหมายของ phase นี้คือทำให้แอปพร้อมใช้งานจริงมากขึ้นในงาน support

### 1. Add logging/telemetry

ตัวอย่างที่ควรเก็บ:

- tool ที่ถูกใช้งาน
- เวลาเริ่ม/จบงาน
- error summary
- update check result

ข้อควรระวัง:

- อย่า log ข้อมูลลูกค้าที่ sensitive
- แยก debug log กับ user-facing error ให้ชัด

สถานะ:

- เพิ่ม `app_logging.py` แล้ว
- มี `logs/update.log` สำหรับ auto-update flow
- มี `logs/process.log` สำหรับ process flow สำคัญ
- มี `logs/release.log` สำหรับ release workflow
- มี rotation/retention เบื้องต้นแล้วทั้งฝั่ง Python และ PowerShell

### 2. Add recent input/history for selected tools

เครื่องมือที่เหมาะ:

- JSON Tool
- Compare Text
- Smart Formatter

ผลลัพธ์ที่ต้องการ:

- ใช้งานซ้ำได้เร็วขึ้น
- ลดการ paste ข้อมูลเดิมซ้ำ

### 3. Add export/save output features

เครื่องมือที่ควรมี:

- Compare Text
- Smart Formatter
- JSON Tool

รูปแบบที่เหมาะ:

- `.txt`
- `.json`
- `.csv`

### 4. Add keyboard shortcuts

ตัวอย่าง:

- `Ctrl+Enter` = run action หลัก
- `Ctrl+Shift+C` = copy result
- `Ctrl+L` = clear

### 5. Add system status panel

สิ่งที่อาจแสดง:

- app version
- manifest version
- update source
- last update check
- environment status

---

## Phase 4: Release Engineering

เป้าหมายของ phase นี้คือทำให้ build/release มีความนิ่งและทำซ้ำได้

### 1. Create a unified release script

แนะนำ:

- `scripts/release.ps1`

หน้าที่:

- ตรวจ version alignment
- regenerate manifest
- run checks
- build executable/installer
- สรุป artifact ที่ได้

สถานะ:

- เพิ่ม `scripts/release.ps1` แล้ว
- รองรับโหมด `-SkipExeBuild` และ `-SkipInstallerBuild`
- ทดสอบ flow verification mode ผ่านแล้ว
- ตรวจ artifact หลัง build แล้วทั้ง executable และ installer
- สร้าง `logs/release-summary.txt` เป็น release checklist หลังจบ workflow แล้ว

### 2. Add release checklist automation

สิ่งที่ควรตรวจอัตโนมัติ:

- `version.json` ตรงกับตัวแอป
- `manifest.json` ล่าสุด
- installer version ตรง
- README version ตรง

### 3. Improve updater safety

สิ่งที่ควรทำ:

- backup ก่อน patch
- rollback เมื่อ patch fail
- แจ้ง error ให้ชัดขึ้น

ผลลัพธ์ที่ต้องการ:

- ลดความเสี่ยงแอปเสียระหว่างอัปเดต

---

## Suggested First 3 Tasks

ถ้าจะเลือกงานที่คุ้มที่สุดก่อน ให้เริ่มจาก 3 งานนี้:

1. ทำ `tool registry` แทน `if index == ...`
2. ย้าย templates/constants ออกจาก handlers
3. เพิ่ม tests ให้ `services.py` และ `generate_manifest.py`

เหตุผล:

- ได้ผลต่อ maintainability สูง
- ลดความเสี่ยงเวลาทำ refactor รอบถัดไป
- ช่วยให้ release รอบต่อไปมั่นใจขึ้น

---

## Proposed Backlog

### Phase 1 Backlog

- สร้าง `tool registry` กลาง
- แยก Smart Formatter templates
- รวม shared UI helper/context

### Phase 2 Backlog

- เพิ่ม unit tests สำหรับ `services.py`
- เพิ่ม smoke tests สำหรับ metadata/update
- เพิ่ม lint/format scripts

### Phase 3 Backlog

- เพิ่ม logging
- เพิ่ม recent history
- เพิ่ม export output
- เพิ่ม keyboard shortcuts

### Phase 4 Backlog

- เพิ่ม `scripts/release.ps1`
- เพิ่ม automated release validation
- เพิ่ม rollback-safe updater flow

---

## Notes

- `ui_views.py.bak` ยังเป็นไฟล์ที่ควร cleanup แยกในรอบถัดไป หากไม่ต้องใช้งานแล้ว
- หลังจากมี test coverage พื้นฐานแล้ว ค่อยทำ refactor ใหญ่เช่น registry/context จะปลอดภัยกว่า
- ควรแยกงาน cleanup ออกจากงาน feature เพื่อให้ review ง่าย
