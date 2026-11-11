# HALB MCP TouchDesigner by Devza

MCP bridge สำหรับให้ Codex หรือ MCP client ควบคุม **โปรเจกต์ TouchDesigner ของคุณเอง** ผ่าน Python API

อ่านโครงสร้าง สร้างและเชื่อมโหนด ตั้งค่าพารามิเตอร์/Expression แก้ DAT รัน Python ดูภาพจาก TOP และบันทึกงานได้ ตัว bridge เพิ่ม component `/codex_mcp` เข้าไปในโปรเจกต์ที่คุณเลือก

[คู่มือใช้งานภาษาไทย](docs/USER_GUIDE_TH.md)

## สิ่งที่ต้องมี

- Windows และ TouchDesigner ที่รองรับ Python 3 — ทดสอบกับ 2025.33230
- Python 3.10 ขึ้นไปสำหรับ MCP server
- Codex หรือโปรแกรมที่รองรับ MCP ผ่าน stdio

ตัว MCP ไม่ต้องใช้ API key และไม่กำหนดให้ใช้ GPU, กล้อง หรือโมเดล AI เฉพาะ ความต้องการของโหนดในโปรเจกต์ขึ้นกับงานของคุณ

## ติดตั้ง

เลือกโฟลเดอร์ที่ต้องการ แล้วรันใน PowerShell:

```powershell
git clone https://github.com/H-lab-official/halb-mcp-TouchDesigner-by-devza.git
cd halb-mcp-TouchDesigner-by-devza
.\setup.ps1 -RegisterMcp
```

สคริปต์สร้าง `.venv`, ติดตั้ง dependencies และเพิ่ม MCP ชื่อ `touchdesigner` ใน Codex หากใช้ MCP client อื่น ให้รัน `setup.ps1` โดยไม่ใส่ `-RegisterMcp` แล้วตั้งค่า stdio ตามคู่มือ

หากเครื่องไม่อนุญาตให้รันสคริปต์ ใช้คำสั่งติดตั้งแยกในคู่มือ สคริปต์นี้ไม่เปลี่ยน Execution Policy ของ Windows

## เชื่อมกับโปรเจกต์

1. เปิดไฟล์ `.toe` ที่ต้องการให้ควบคุม
2. กด **Alt+T** เปิด Python Textport
3. เปลี่ยนพาธ `p` ด้านล่างให้ตรงกับ repo บนเครื่อง แล้ววางทั้งบรรทัด:

```python
p = 'C:/tools/halb-mcp-TouchDesigner-by-devza/install_td.py'; exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), dict(globals(), __file__=p))
```

4. เมื่อขึ้น `TouchDesigner MCP connected` ให้บันทึกโปรเจกต์
5. ให้โปรเจกต์อยู่ในสถานะ **Play** ระหว่างใช้งาน
6. เปิด Codex ใหม่หลังเพิ่ม MCP ครั้งแรก แล้วให้ตรวจ `connection_status` และ `get_project`

ตัวติดตั้งสำรองไฟล์โปรเจกต์เดิมบนดิสก์ไว้ใน `backups` ก่อนเพิ่ม bridge และไม่บันทึกทับงานให้อัตโนมัติ หากเปิดโปรเจกต์อื่นที่ยังไม่มี bridge ให้ทำขั้นตอนนี้กับโปรเจกต์นั้นอีกครั้ง

## ตัวอย่างสั่งงาน

- “อธิบายโครงสร้าง /project1 และตรวจว่ามีโหนดไหนผิดพลาด”
- “สร้าง Noise TOP → Blur TOP → Level TOP พร้อมตัวปรับความสว่าง”
- “เพิ่ม Expression ให้พารามิเตอร์นี้เคลื่อนไหวตามเวลา”
- “แก้โค้ดใน DAT นี้ และตรวจผลจาก TOP output”
- “บันทึกฉบับแก้ไขเป็นไฟล์ใหม่”

## เครื่องมือ 12 ตัว

| เครื่องมือ | หน้าที่ |
|---|---|
| `connection_status` | ตรวจว่า bridge กำลังทำงาน |
| `get_project` | อ่านชื่อและโครงสร้างระดับบนของโปรเจกต์ |
| `list_nodes` | สำรวจโหนดใต้คอมโพเนนต์ |
| `get_node` | อ่านพารามิเตอร์ การเชื่อมต่อ ข้อผิดพลาด และข้อความ DAT |
| `create_node` | สร้างโหนด โดยไม่ใช้ชื่อซ้ำ |
| `set_parameters` | ตั้งค่า/Expression และคืนค่าเดิม |
| `pulse_parameter` | กดพารามิเตอร์แบบ Pulse |
| `connect_nodes` | เชื่อม output เข้ากับ input ที่ระบุ |
| `set_dat_text` | เปลี่ยนข้อความ DAT พร้อมคืนข้อความเดิม |
| `execute_python` | รัน Python บน main thread ของ TouchDesigner |
| `save_project` | บันทึก `.toe`; ไฟล์เดิมต้องระบุ `overwrite=true` |
| `snapshot_top` | ส่งภาพจาก TOP กลับให้ client ตรวจ |

## การทำงาน

```text
MCP client → stdio server → local file queue → Execute DAT → TouchDesigner API
```

- ไม่เปิดพอร์ต TCP
- OP API ทำงานบน main thread ของ TouchDesigner
- คำสั่งผูกกับ session และหมดอายุใน 25 วินาที
- หากรอคำตอบเกิน 30 วินาที จะไม่สั่งแก้ซ้ำให้อัตโนมัติ ให้ตรวจสถานะก่อนลองใหม่
- ใช้หนึ่งโปรเจกต์ที่เปิด bridge ต่อ repo ในเวลาเดียวกัน
- `execute_python` มีสิทธิ์เข้าถึงไฟล์และระบบเท่ากับโปรเซส TouchDesigner ใช้กับงานและโค้ดที่คุณอนุญาต

## ไฟล์ใน repo

| ไฟล์ | หน้าที่ |
|---|---|
| `server.py` | stdio MCP server |
| `td_runtime.py` | ตัวรับคำสั่งบน main thread |
| `install_td.py` | ติดตั้ง bridge เข้าโปรเจกต์ที่เปิดอยู่ |
| `setup.ps1` | ติดตั้ง environment และลงทะเบียน Codex |
| `requirements.txt` | เวอร์ชัน MCP SDK |
| `test_bridge.py` | ทดสอบการรับส่งและจัดการคำสั่ง |
| `docs/USER_GUIDE_TH.md` | คู่มือใช้งานและแก้ปัญหา |

## ทดสอบ

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s . -p test_bridge.py -v
```

ทดสอบคำสั่งหมดอายุ, session เก่า, การตอบหลาย client, การกู้หลังข้อผิดพลาด และการทำคำสั่งเพียงครั้งเดียว ส่วนโหนดและอุปกรณ์ในแต่ละโปรเจกต์ควรตรวจบน TouchDesigner จริง
