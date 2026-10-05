# MVP Feature List

`requirement_priority` เป็น enum ที่เอกสารนี้เป็นเจ้าของ: `P0` = must have, `P1` = should have, `P2` = nice to have.

| Feature | requirement_priority | Value Delivered |
|---|---|---|
| Upload campaign CSV | P0 | CP-01; ลดงานนำเข้าด้วยมือ |
| Validate required columns and row values | P0 | CP-01; ป้องกัน dataset ที่คำนวณไม่ได้ |
| Persist valid dataset to SQLite3 | P0 | CP-02; ใช้งานต่อได้หลัง import |
| Calculate Spend, Leads, Qualified Leads, CPL, CPQL, Qualification Rate | P0 | CP-03; ใช้ metric contract เดียว |
| Aggregate and compare by Channel | P0 | CP-04; เปรียบเทียบช่องทาง |
| Chart + comparison table | P0 | CP-04; อ่านผลได้เร็วและตรวจเลขได้ |
| Channel filter with Campaign detail | P0 | CP-05; trace จาก summary ไป detail |
| Identify lowest-CPQL eligible Channel | P0 | CP-04; ตอบคำถามหลักของโจทย์ |
| Automated tests/validation for import and calculations | P0 | รองรับการส่งงานและลด calculation defect |
| Docker + Coolify deployment | P0 | เปิดใช้งานจริงตามโจทย์ |
| Generate/save/display Campaign Review Brief via company AI endpoint | P1 | CP-06; โบนัส AI workflow |

# Out-of-Scope Items

- Multi-user account management, SSO และ permission administration
- Cross-period trend analysis เพราะโจทย์ให้ dataset ช่วงเวลาเดียวกัน
- Media attribution modeling, ROAS/revenue attribution และ conversion หลัง Qualified Lead
- Editing raw Campaign rows ใน UI
- AI chatbot หรือ natural-language query เหนือ dataset
- Automatic budget reallocation
- Scheduled CSV ingestion หรือ external ad-platform connectors

# Phase Roadmap

- MVP delivery: requirement ที่มี `requirement_priority = P0`
- Bonus extension: AI Campaign Review Brief (`requirement_priority = P1`) หลัง core flow ผ่าน test
- Post-MVP: authentication, historical datasets, scheduled ingestion และ broader analytics เมื่อมี requirement ใหม่

# External Dependencies

- Uploaded CSV ตาม schema ที่กำหนด
- SQLite3 runtime/storage
- Docker runtime และ Coolify
- Company Git repository
- Company AI endpoint และ quota สำหรับ feature P1
