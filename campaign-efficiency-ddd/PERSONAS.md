# Persona Profiles

## Persona: Growth Marketing Analyst

- **name:** Growth Marketing Analyst
- **role:** ผู้ปฏิบัติงานที่นำเข้าข้อมูลแคมเปญ ตรวจสอบคุณภาพข้อมูล วิเคราะห์ประสิทธิภาพรายช่องทาง และเตรียมข้อมูลสำหรับการทบทวนงบ
- **technical_skill:** ปานกลาง — ใช้งาน CSV, spreadsheet และ dashboard ได้ แต่ไม่ควรต้องเขียน SQL หรือโค้ดเพื่อทำงานประจำ
- **pain_points:**
  - จำนวน Lead เพียงอย่างเดียวไม่บอกว่าช่องทางใดสร้าง Qualified Lead ได้คุ้มค่า
  - ต้องเปรียบเทียบ Spend, Lead และ Qualified Lead ข้ามหลายแคมเปญและหลายช่องทางจากข้อมูลชุดเดียวกัน
  - การคำนวณ Cost per Lead, Cost per Qualified Lead และ Qualification Rate ด้วยตนเองเสี่ยงต่อสูตรไม่สอดคล้องกัน
  - ต้องไล่ดูรายละเอียดระดับ Campaign เมื่อต้องอธิบายว่าผลรวมระดับ Channel เกิดจากรายการใด
  - ต้องตรวจให้ได้ว่าไฟล์ที่นำเข้ามีข้อมูลที่ระบบใช้คำนวณได้ก่อนนำผลไปตัดสินใจ
- **use_cases:**
  - นำเข้า CSV ของ Campaign Performance เข้าระบบ
  - เห็นผล validation ของข้อมูลก่อนใช้วิเคราะห์
  - ดู KPI รวมของชุดข้อมูล
  - เปรียบเทียบประสิทธิภาพระหว่าง Channel ด้วยกราฟและตาราง
  - เลือก Channel เพื่อดูรายละเอียด Campaign ภายใน Channel นั้น
  - ระบุ Channel ที่มี Cost per Qualified Lead ต่ำที่สุดในชุดข้อมูล
  - สร้างและเปิดดู Campaign Review Brief จากผลวิเคราะห์เมื่อใช้ AI workflow
- **critical_path:** `CP-01`, `CP-02`, `CP-03`, `CP-04`, `CP-05`, `CP-06`

## Persona: Growth Marketing Manager

- **name:** Growth Marketing Manager
- **role:** ผู้ใช้ผลวิเคราะห์เพื่อทบทวนการใช้งบ เปรียบเทียบคุณภาพ Lead ระหว่าง Channel และกำหนดประเด็นที่ต้องตรวจสอบหรือทดลองต่อ
- **technical_skill:** พื้นฐานถึงปานกลาง — อ่าน dashboard และตารางวิเคราะห์ได้ แต่ไม่ควรต้องตรวจสูตรหรือจัดการฐานข้อมูลเอง
- **pain_points:**
  - มองเห็นจำนวน Lead แต่ยังไม่เห็นความคุ้มค่าของ Qualified Lead ในแต่ละ Channel อย่างชัดเจน
  - ต้องใช้เวลารวมข้อมูลจากหลาย Campaign ก่อนจะเปรียบเทียบ Channel ได้
  - ต้องการตรวจกลับจากผลสรุประดับ Channel ไปยัง Campaign ที่เป็นต้นเหตุของผลลัพธ์
  - การเขียน Campaign Review Brief จากตัวเลขทุกครั้งใช้เวลาและอาจปะปนข้อเท็จจริงกับข้อเสนอแนะ
- **use_cases:**
  - เปิด dashboard เพื่อดู Spend, Lead, Qualified Lead และ efficiency metrics ของชุดข้อมูล
  - เปรียบเทียบ Channel เพื่อหา Channel ที่มี Cost per Qualified Lead ต่ำที่สุด
  - เลือก Channel เพื่อดู Campaign ที่อยู่เบื้องหลังผลรวม
  - อ่าน Campaign Review Brief ที่แยกข้อเท็จจริง ประเด็นที่ควรตรวจสอบ และข้อเสนอสำหรับการทดลองครั้งต่อไป
- **critical_path:** `CP-03`, `CP-04`, `CP-05`, `CP-06`

# Pain Points

| Persona | Pain Point | Frequency | Current Workaround |
|---|---|---|---|
| Growth Marketing Analyst | เปรียบเทียบประสิทธิภาพหลาย Channel จากข้อมูลหลาย Campaign ได้ยากเมื่อดู Lead อย่างเดียว | ทุกครั้งที่ทบทวนผล Campaign จาก dataset | รวมและคำนวณใน spreadsheet หรือเครื่องมือวิเคราะห์แบบ ad hoc |
| Growth Marketing Analyst | สูตร efficiency metric อาจถูกคำนวณไม่เหมือนกันระหว่างผู้วิเคราะห์ | ทุกครั้งที่ต้องสร้างตัวเลขเพื่อเปรียบเทียบ | สร้างสูตรเองใน spreadsheet |
| Growth Marketing Analyst | ข้อมูล CSV ที่ผิดรูปแบบอาจทำให้ผลวิเคราะห์คลาดเคลื่อน | ทุกครั้งที่รับไฟล์ใหม่ | ตรวจข้อมูลด้วยตนเองก่อนคำนวณ |
| Growth Marketing Manager | มองไม่เห็นทันทีว่า Channel ใดสร้าง Qualified Lead ได้คุ้มค่าที่สุด | ทุกครั้งที่ทบทวนการใช้งบ | ขอให้ผู้วิเคราะห์สรุปหรือเรียงผลให้ |
| Growth Marketing Manager | ต้องตรวจย้อนจากผลรวมระดับ Channel ไปยัง Campaign รายตัว | เมื่อพบ Channel ที่ต้องอธิบายหรือสอบทาน | เปิดไฟล์ข้อมูลแล้ว filter ด้วยตนเอง |
| Growth Marketing Manager | การเขียน Review Brief ใช้เวลาและเสี่ยงปะปน fact กับข้อเสนอ | เมื่อเตรียม Campaign Review | เขียนสรุปจาก dashboard หรือ spreadsheet ด้วยตนเอง |

# Primary Use Cases

| Use Case | Persona | Trigger | Expected Outcome |
|---|---|---|---|
| Import campaign CSV | Growth Marketing Analyst | ได้รับไฟล์ Campaign Performance ชุดใหม่ | ระบบรับไฟล์ ตรวจสอบ และจัดเก็บข้อมูลที่ผ่าน validation เพื่อใช้วิเคราะห์ |
| Review dataset KPIs | Growth Marketing Analyst, Growth Marketing Manager | เปิด dataset ที่นำเข้าแล้ว | เห็น Spend, Lead, Qualified Lead และ efficiency metrics จากข้อมูลชุดเดียวกัน |
| Compare channels | Growth Marketing Analyst, Growth Marketing Manager | ต้องทบทวนประสิทธิภาพการใช้งบ | เห็นผลราย Channel ในรูปกราฟและตารางที่เปรียบเทียบได้ |
| Inspect campaigns by channel | Growth Marketing Analyst, Growth Marketing Manager | ต้องอธิบายผลของ Channel ใด Channel หนึ่ง | เลือก Channel แล้วเห็น Campaign ภายใน Channel นั้นพร้อม metrics ที่เกี่ยวข้อง |
| Identify lowest-CPQL channel | Growth Marketing Analyst, Growth Marketing Manager | ต้องหาช่องทางที่สร้าง Qualified Lead ด้วยต้นทุนต่ำที่สุดใน dataset | ระบบแสดง Channel ที่เข้าเกณฑ์และมี Cost per Qualified Lead ต่ำที่สุดอย่างชัดเจน |
| Generate Campaign Review Brief | Growth Marketing Analyst | Core analysis พร้อมและต้องการร่างสรุป | ระบบสร้างร่างที่แยก Facts, Items to Verify และ Next Experiment Proposals แล้วบันทึกไว้ |
| Review saved Campaign Review Brief | Growth Marketing Manager | ต้องใช้ผลวิเคราะห์ประกอบการ review | เปิดอ่าน brief ที่ผูกกับผลวิเคราะห์ของ dataset ได้จากแอป |

# Critical Paths

| CP-ID | Persona | Critical Action | Delivery |
|---|---|---|---|
| `CP-01` | Growth Marketing Analyst | นำเข้า CSV และได้รับผล validation ที่บอกชัดว่าข้อมูลพร้อมหรือไม่พร้อมสำหรับการวิเคราะห์ | UI |
| `CP-02` | Growth Marketing Analyst | หลัง import สำเร็จ ระบบจัดเก็บ dataset เพื่อให้เปิดใช้งานต่อได้โดยไม่ต้อง upload ไฟล์เดิมใหม่ใน session เดียวกัน | system |
| `CP-03` | Growth Marketing Analyst, Growth Marketing Manager | เปิด dashboard แล้วเห็น KPI ที่จำเป็นสำหรับการประเมิน Spend, Lead, Qualified Lead และ efficiency ของ dataset | UI |
| `CP-04` | Growth Marketing Analyst, Growth Marketing Manager | เปรียบเทียบผลราย Channel และเห็นว่า Channel ใดมี Cost per Qualified Lead ต่ำที่สุดในชุดข้อมูล | UI |
| `CP-05` | Growth Marketing Analyst, Growth Marketing Manager | เลือก Channel แล้วตรวจรายละเอียด Campaign ที่ประกอบเป็นผลของ Channel นั้นได้ | UI |
| `CP-06` | Growth Marketing Analyst, Growth Marketing Manager | สร้าง บันทึก และเปิดอ่าน Campaign Review Brief ที่แยก Facts, Items to Verify และ Next Experiment Proposals ได้ | UI |
