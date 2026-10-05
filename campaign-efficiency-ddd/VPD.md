# Customer Profile

- Growth Marketing Analyst: ต้องนำเข้า ตรวจ และวิเคราะห์ campaign dataset โดยไม่ต้องสร้างสูตรซ้ำเอง
- Growth Marketing Manager: ต้องใช้ผลรวมเพื่อทบทวนความคุ้มค่าของ Channel และตัดสินใจว่าจะตรวจหรือทดลองอะไรต่อ

# Customer Jobs

- ตรวจว่า dataset พร้อมวิเคราะห์หรือไม่
- เปรียบเทียบคุณภาพและต้นทุนของ Lead ระหว่าง Channel
- เจาะจากผลรวมระดับ Channel ไปยัง Campaign
- สรุปข้อเท็จจริงและประเด็นติดตามเพื่อใช้ใน Campaign Review

# Pains

- จำนวน Lead อย่างเดียวไม่สะท้อนคุณภาพหรือความคุ้มค่า
- การคำนวณ metric ด้วย spreadsheet มีโอกาสใช้สูตรไม่ตรงกัน
- การรวม campaign จำนวนมากด้วยมือทำให้หาเหตุผลเบื้องหลัง Channel ได้ช้า
- การเขียน review brief ด้วยมือเสี่ยงปะปน fact กับข้อเสนอ

# Gains

- เห็น metric ที่คำนวณด้วยกติกาเดียวกันทั้งระบบ
- เปรียบเทียบ Channel ได้ทันทีจาก dataset ที่ validated แล้ว
- ตรวจย้อน Campaign ภายใน Channel ได้
- ได้ draft brief ที่แยก fact, issue to verify และ next experiment proposal ชัดเจน

# Value Map

- CSV validation + persistence
- Deterministic metric engine
- Channel comparison dashboard
- Channel filter + campaign detail table
- Lowest-CPQL identification
- Optional AI Campaign Review Brief ที่ save และเปิดอ่านได้

# Pain Relievers

- Validation ป้องกัน row ที่ใช้คำนวณไม่ได้ก่อน persist
- Metric calculation อยู่ที่ backend เป็นแหล่งเดียว
- Aggregation ใช้ผลรวม numerator/denominator ก่อนหาร ไม่เฉลี่ย ratio ราย Campaign
- Filter ช่วย trace ผลรวม Channel กลับไปยัง Campaign
- AI รับ structured facts จาก backend แทนการให้ AI เดาตัวเลข

# Gain Creators

- Dashboard แสดง KPI รวมและ comparison ในหน้าเดียว
- Lowest-CPQL Channel ถูก highlight โดยไม่ต้อง sort เอง
- Saved brief ทำให้กลับมาอ่านผล review ได้
- Core dashboard ยังทำงานได้เมื่อ AI integration ไม่พร้อม

# Value Propositions

- สำหรับ Growth Marketing Analyst: เครื่องมือที่ลดงานตรวจสูตรและรวมข้อมูลซ้ำจาก CSV ไปสู่ dashboard ที่ตรวจสอบย้อนกลับได้
- สำหรับ Growth Marketing Manager: มุมมองที่ช่วยเทียบ Channel ด้วย Qualified Lead economics และเชื่อมจาก summary ไปยัง Campaign detail
- สำหรับ AI workflow: ผู้ช่วยร่าง review จาก facts ที่ระบบคำนวณแล้ว โดยไม่แทนที่ deterministic analytics
