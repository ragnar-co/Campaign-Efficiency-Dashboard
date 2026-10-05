# Problem Statement

ทีม Growth Marketing มีค่าใช้จ่ายและ Lead จากหลาย Campaign/Channel แต่จำนวน Lead อย่างเดียวไม่ตอบว่าช่องทางใดสร้าง Qualified Lead ได้คุ้มค่า แอปต้องเปลี่ยน CSV ชุดเดียวให้เป็นข้อมูลที่ validated, persisted, คำนวณได้สม่ำเสมอ และเปรียบเทียบได้จาก summary ลงถึง Campaign detail

# Goals and Success Metrics

- Core success: ผู้ใช้สามารถ upload CSV ที่ถูกต้องและเห็น dashboard ได้โดยไม่ใช้ spreadsheet เพิ่มเติม
- Calculation correctness: metric ที่แสดงต้องตรงกับสูตรใน Functional Requirements และ automated test fixture
- Traceability: ผู้ใช้เลือก Channel แล้วเห็น Campaign ที่ประกอบเป็นผลรวมได้
- Deployment success: application container เปิดใช้งานได้ผ่าน Coolify และ health check ผ่าน
- AI bonus success: เมื่อ AI integration พร้อม ผู้ใช้สร้าง brief, บันทึก และเปิดอ่านได้; core dashboard ต้องไม่ fail หาก AI unavailable
- Performance target: `null` — calibration owner: Developer; วัดจาก dataset อ้างอิงที่อัปโหลดและบันทึกผลก่อน launch จริง

# User Stories

- ในฐานะ Growth Marketing Analyst ฉันต้องการ upload CSV และเห็น validation result เพื่อไม่ใช้ข้อมูลผิดไปวิเคราะห์
- ในฐานะ Growth Marketing Analyst ฉันต้องการเห็น Spend, Lead, Qualified Lead, CPL, CPQL และ Qualification Rate ที่คำนวณด้วยสูตรเดียวกัน
- ในฐานะ Growth Marketing Manager ฉันต้องการเปรียบเทียบ Channel เพื่อเห็น Channel ที่มี CPQL ต่ำที่สุด
- ในฐานะ Growth Marketing Manager ฉันต้องการเลือก Channel และเห็น Campaign detail เพื่ออธิบายผลรวมได้
- ในฐานะ Growth Marketing Analyst ฉันต้องการสร้าง Campaign Review Brief จาก facts ที่คำนวณแล้วและบันทึกไว้

# Functional Requirements

| ID | requirement_priority | Requirement |
|---|---|---|
| FR-01 | P0 | รับไฟล์ CSV ที่มี required columns ตาม CONSTRAINTS.md |
| FR-02 | P0 | Reject ทั้งไฟล์เมื่อ required column หาย, campaign_id ว่าง/ซ้ำภายในไฟล์, campaign_name/channel ว่าง, spend ติดลบ, count ไม่ใช่จำนวนเต็มไม่ติดลบ หรือ qualified_lead_count > lead_count พร้อม error ที่ระบุ row/field |
| FR-03 | P0 | Persist dataset และ Campaign rows ที่ valid ลง SQLite3 แบบ transaction เดียว |
| FR-04 | P0 | Dataset totals: Spend = SUM(spend), Leads = SUM(lead_count), Qualified Leads = SUM(qualified_lead_count) |
| FR-05 | P0 | CPL = SUM(spend)/SUM(leads); เมื่อ denominator = 0 ให้ค่า metric เป็น null และ UI แสดง N/A |
| FR-06 | P0 | CPQL = SUM(spend)/SUM(qualified_leads); เมื่อ denominator = 0 ให้ค่า metric เป็น null และ UI แสดง N/A |
| FR-07 | P0 | Qualification Rate = SUM(qualified_leads)/SUM(leads); เมื่อ denominator = 0 ให้ค่า metric เป็น null และ UI แสดง N/A |
| FR-08 | P0 | Channel metrics ต้อง aggregate numerator/denominator ก่อนหาร ห้าม average ratio ราย Campaign |
| FR-09 | P0 | แสดง Channel comparison เป็นกราฟและตาราง |
| FR-10 | P0 | ผู้ใช้เลือก Channel เพื่อกรอง Campaign detail ได้ และเลือก All เพื่อดูทุก Campaign |
| FR-11 | P0 | Lowest-CPQL Channel = Channel ที่ CPQL ต่ำสุดเฉพาะ Channel ที่ SUM(qualified_lead_count) > 0; ถ้าไม่มี Channel เข้าเกณฑ์ให้แสดง N/A |
| FR-12 | P1 | AI brief รับ structured analytics facts จาก backend และสร้างส่วน Facts, Items to Verify, Next Experiment Proposals |
| FR-13 | P1 | AI brief ที่ generate สำเร็จต้อง persist และเปิดอ่านจาก application ได้ |
| FR-14 | P1 | AI failure ต้องแสดง error โดยไม่กระทบข้อมูลหรือ core dashboard |

# Non-Functional Requirements

- แอปเป็น single deployable service สำหรับ MVP และใช้ SQLite3 persistent volume
- AI credential อยู่ server-side secret เท่านั้น
- การ import ต้อง atomic: validation ล้มเหลวแล้วห้ามมี partial Campaign rows ของ upload นั้น
- UI ต้องใช้งานได้บน desktop viewport และไม่ซ่อนข้อมูลสำคัญไว้หลัง interaction ที่ไม่จำเป็น
- Availability SLO: `null` — calibration owner: Platform Owner
- Response-time SLO: `null` — calibration owner: Developer
- Rate limit: อ้าง API_SPEC.md; ค่าปัจจุบันยังไม่ calibrate

# Acceptance Criteria

| AC-ID | Traces To | Acceptance Criterion |
|---|---|---|
| AC-01 | FR-01, FR-02 | Given valid CSV, import succeeds; given missing required column or invalid row, import is rejected with actionable error and no partial rows are stored |
| AC-02 | FR-04..FR-08 | Fixture ที่รู้ผลล่วงหน้าคำนวณ totals/CPL/CPQL/Qualification Rate ตรงตามสูตร รวม edge case denominator = 0 |
| AC-03 | FR-09 | Dashboard แสดงกราฟและตารางที่ใช้ Channel aggregation ชุดเดียวกัน |
| AC-04 | FR-10 | เลือก Channel แล้ว Campaign table มีเฉพาะ Channel นั้น; All แสดงทุก Channel |
| AC-05 | FR-11 | ระบบแสดง eligible Channel ที่มี CPQL ต่ำที่สุด และไม่เลือก Channel ที่ qualified leads รวมเป็น 0 |
| AC-06 | CP-02 | หลัง import สำเร็จและ reload แอป ข้อมูลยังอ่านจาก SQLite3 ได้ |
| AC-07 | Deployment | Container health check ผ่านและหน้า dashboard เปิดได้จาก Coolify URL |
| AC-08 | FR-12..FR-14 | เมื่อ AI integration พร้อม สามารถ generate/save/read brief ได้; เมื่อ AI error core dashboard ยังใช้งานได้ |
