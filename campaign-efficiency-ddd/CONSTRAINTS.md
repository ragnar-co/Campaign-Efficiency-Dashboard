# Legal and Compliance Constraints

- Dataset ที่ได้รับไม่มี field ที่ระบุตัวบุคคลโดยตรงจาก schema ปัจจุบัน; การจัดชั้นข้อมูลจริงให้ยืนยันอีกครั้งใน DATA_MODEL.md
- ห้ามส่ง raw CSV หรือ campaign-level row ทั้งชุดไปยัง AI endpoint โดยไม่จำเป็น; AI workflow รับเฉพาะผลวิเคราะห์ที่ backend เตรียมไว้และข้อมูลที่จำเป็นต่อ brief
- หากภายหลังมีการเพิ่มข้อมูลส่วนบุคคล ต้องอัปเดต DATA_MODEL.md, SECURITY.md และ TRACKING_PLAN.md ก่อน implement

# Technical Constraints

- แอปต้องรับ CSV schema: `campaign_id`, `campaign_name`, `channel`, `spend_thb`, `lead_count`, `qualified_lead_count`
- ต้อง persist ข้อมูลลง SQLite3
- ต้อง deploy ด้วย Docker ผ่าน Coolify
- ต้องสร้างและ push source code ไปยัง repository ของบริษัท
- เวลารวมสำหรับทำ MVP ตามโจทย์คือ 120 นาที
- ระบบต้องคำนวณ metrics ด้วย application code แบบ deterministic; AI ห้ามเป็นแหล่งคำนวณ metric หลัก

# Security Constraints

- MVP ไม่มี end-user login ตามสมมติฐานของงานนี้; การจำกัดการเข้าถึงภายนอก application เป็นหน้าที่ของ deployment/network control หากบริษัทกำหนด
- AI credential ต้องเป็น secret ฝั่ง server และห้ามส่งไป browser หรือ commit ลง repository
- Uploaded filename ต้องไม่ถูกนำไปใช้เป็น filesystem path โดยตรง
- SQL ต้องใช้ parameterized query/ORM และห้ามประกอบ query จากค่า filter ของผู้ใช้โดยตรง
- Maximum upload size: `null` — calibration owner: Developer/Platform Owner

# Business Constraints

- Core requirement ต้องทำงานได้แม้ AI endpoint ใช้งานไม่ได้หรือ quota หมด
- Dashboard ต้องรองรับการทบทวน Spend, Lead, Qualified Lead, CPL, CPQL และ Qualification Rate จาก dataset เดียวกัน
- ผู้ใช้ต้องเลือก Channel แล้วดูรายละเอียด Campaign ได้
- ต้องระบุ Channel ที่มี CPQL ต่ำที่สุดจาก Channel ที่มี Qualified Lead มากกว่า 0
- ต้องมี Test หรือ Validation ที่ผ่านก่อนส่งงาน
- RTO: `null` — calibration owner: Platform Owner
- RPO: `null` — calibration owner: Platform Owner

# Integration Constraints

- Coolify เป็น deployment target ที่โจทย์กำหนด
- Company Git repository เป็นปลายทาง source code ที่โจทย์กำหนด
- Company AI endpoint เป็น integration สำหรับโบนัส; endpoint URL, model identifier, quota และ request contract: `null` — calibration owner: Company AI Platform Owner
