# Term Definitions

| Term | Definition | Owning Role |
|---|---|---|
| Campaign | แถวข้อมูลการทำการตลาดหนึ่งรายการที่มี campaign_id, campaign_name, Channel, Spend, Lead และ Qualified Lead | Product Owner |
| Dataset | ชุด Campaign rows จาก CSV import หนึ่งครั้งที่ผ่าน validation และ persist สำเร็จ | Product Owner |
| Channel | ช่องทางการตลาดที่ใช้ group Campaign เพื่อเปรียบเทียบประสิทธิภาพ | Growth Marketing |
| Spend | ค่าใช้จ่ายของ Campaign ในหน่วย THB ตาม input dataset | Growth Marketing |
| Lead | จำนวน Lead ทั้งหมดของ Campaign | Growth Marketing |
| Qualified Lead | Lead ที่ผ่านเกณฑ์ qualification ของธุรกิจ; เกณฑ์ qualification อยู่นอก scope ของแอปนี้ | Growth Marketing |
| CPL | Cost per Lead = aggregated Spend / aggregated Lead; denominator 0 ให้ null | Product Owner |
| CPQL | Cost per Qualified Lead = aggregated Spend / aggregated Qualified Lead; denominator 0 ให้ null | Product Owner |
| Qualification Rate | aggregated Qualified Lead / aggregated Lead; denominator 0 ให้ null | Product Owner |
| Campaign Review Brief | AI-generated draft ที่ประกอบด้วย Facts, Items to Verify และ Next Experiment Proposals จาก analytics facts ของ Dataset | Product Owner |

# Term-to-Entity Mapping

| Term | Intended Entity/Resource |
|---|---|
| Dataset | `datasets` / `/datasets` |
| Campaign | `campaigns` / campaign collection under dataset |
| Channel | derived grouping key from `campaigns.channel` |
| Campaign Review Brief | `campaign_review_briefs` / brief resource under dataset |
| CPL, CPQL, Qualification Rate | derived metrics; ไม่ persist เป็น canonical raw fields |

# Disputed Terms

- `Lead` และ `Qualified Lead` เป็น business terms ที่รับมาจาก source dataset; แอปไม่เป็นเจ้าของเกณฑ์ qualification
- ใช้คำว่า `Channel` ใน UI และเอกสารทั้งหมด ไม่สลับกับ source/platform/media เพื่อหลีกเลี่ยง naming drift
- ใช้ `Campaign Review Brief` สำหรับ AI artifact; ไม่เรียกเป็น recommendation engine เพราะระบบสร้าง draft เพื่อ review ไม่ใช่คำสั่งจัดสรรงบอัตโนมัติ

# Glossary Change Log

- Initial project glossary created from challenge statement and uploaded CSV schema
- Term-to-Entity Mapping ต้อง reconcile หลัง DATA_MODEL.md และ API_SPEC.md เสร็จ โดยไม่เปลี่ยนนิยามศัพท์หากไม่มี product decision ใหม่

# Enumeration Registry

| Enum | Owner Document |
|---|---|
| `requirement_priority` | SCOPE.md |
| `adr_status` | ADR.md |
| `work_item_status` | TASKS.md |
| `pdpa_classification` | DATA_MODEL.md |
| `confidentiality_class` | DATA_MODEL.md |
| `environment` | ARCHITECTURE.md |
| `application_error_code` | API_SPEC.md |
| `role` | SECURITY.md |
| `event_name` | TRACKING_PLAN.md |
| `deployment_strategy` | DEPLOYMENT.md |
| `incident_severity` | RUNBOOK.md |
