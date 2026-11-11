# HALB MCP TouchDesigner by Devza

ควบคุม TouchDesigner จาก Codex ผ่าน MCP: ตรวจโครงสร้าง สร้างและเชื่อมโหนด แก้พารามิเตอร์/Expression เขียน DAT รัน Python ดูภาพจาก TOP และบันทึกโปรเจกต์

มีตัวอย่าง **Interactive Flower Person**: เปลี่ยนคนจากกล้องเป็นดอกไม้บนฉากวิว พร้อมขอบฟุ้ง กลีบลอย ผีเสื้อ และปฏิสัมพันธ์จากมือกับแขน

[คู่มือใช้งานภาษาไทยแบบละเอียด](docs/USER_GUIDE_TH.md)

## สิ่งที่ต้องมี

| ส่วน | สิ่งที่ใช้ |
|---|---|
| MCP | Windows, TouchDesigner ที่รองรับ Python 3, Python 3.10+, Codex ที่เพิ่ม MCP ได้ |
| ตัวอย่างคนดอกไม้ | ทดสอบบน TouchDesigner 2025.33230, RTX 5070 Laptop, กล้อง USB |
| แยกคนออกจากฉาก | NVIDIA Video Effects SDK รุ่นตรงกับ GPU; รุ่นที่ทดสอบคือ 0.7.6 สำหรับ RTX 50 |
| ติดตามมือและแขน | MediaPipe Pose แยกโปรเซส ด้วย Python 3.11 ที่มากับ TouchDesigner |

MCP พื้นฐานใช้ได้โดยไม่ต้องติดตั้งระบบกล้องและ MediaPipe ส่วนตัวอย่างคนดอกไม้ต้องใช้ส่วนเสริมตามตาราง

## ติดตั้ง

ตัวอย่างใช้โฟลเดอร์ `D:\MCP\TD` หากใช้ที่อื่น ให้เปลี่ยนพาธในคำสั่งตามจริง

```powershell
git clone https://github.com/H-lab-official/halb-mcp-TouchDesigner-by-devza.git D:\MCP\TD
cd D:\MCP\TD
.\setup.ps1 -RegisterMcp
```

ถ้าจะใช้ตัวอย่างคนดอกไม้ด้วย:

```powershell
.\setup.ps1 -RegisterMcp -WithPose
```

`-WithPose` สร้าง `.pose-venv` ติดตั้ง MediaPipe/OpenCV และดาวน์โหลดโมเดล Pose Lite จาก Google พร้อมตรวจ SHA256 ส่วน NVIDIA SDK ให้ติดตั้งจาก[หน้า NVIDIA ทางการ](https://www.nvidia.com/en-us/geforce/broadcasting/broadcast-sdk/resources/) แล้วเปิด TouchDesigner ใหม่

หาก Python ของ TouchDesigner อยู่ที่อื่น:

```powershell
.\setup.ps1 -WithPose -TouchDesignerPython 'C:\path\to\TouchDesigner\bin\python.exe'
```

`setup.ps1` ไม่เปลี่ยน Execution Policy ของ Windows หากเครื่องไม่อนุญาตให้รันสคริปต์ ให้ใช้คำสั่งติดตั้งแยกในคู่มือ

## เชื่อมโปรเจกต์กับ MCP

1. เปิดโปรเจกต์ใน TouchDesigner
2. กด **Alt+T** เปิด Textport และเลือก Python
3. วางคำสั่งนี้แล้วกด Enter:

```python
p = 'D:/MCP/TD/install_td.py'; exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), dict(globals(), __file__=p))
```

จะได้ `/codex_mcp` และข้อความ `TouchDesigner MCP connected` ตัวติดตั้งสำรองไฟล์ที่บันทึกไว้เดิมลง `backups` ก่อน ไม่บันทึกทับโปรเจกต์ให้อัตโนมัติ

4. บันทึกโปรเจกต์เพื่อเก็บตัวเชื่อมต่อไว้
5. ให้ TouchDesigner อยู่ในสถานะ **Play** ระหว่างทำงาน
6. เปิด Codex ใหม่หลังเพิ่ม MCP ครั้งแรก แล้วสั่งให้ตรวจ `connection_status` และ `get_project`

ตัวอย่างคำสั่งในแชต:

- “อธิบายโครงสร้างโปรเจกต์นี้”
- “สร้าง Noise → Blur → Level แล้วเพิ่มตัวปรับความสว่าง”
- “ตรวจว่าโหนดไหนมีข้อผิดพลาด”
- “ปรับความหนาแน่นของดอกไม้และบันทึกเป็นไฟล์ใหม่”

## สร้างตัวอย่าง Interactive Flower Person

เปิดโปรเจกต์ใหม่ แล้วบันทึก `.toe` ไว้ในโฟลเดอร์ repo จากนั้นใช้ Python Textport:

```python
import sys
sys.path.insert(0, 'D:/MCP/TD/examples')
from build_garden import build
garden = build('D:/MCP/TD')
```

ตัวสร้างจะเพิ่ม `/project1/Flower_Person` เลือกกล้อง USB ที่พบ เปิดกล้อง และเปิดหน้าต่าง Output หากมีกล้องหลายตัว ให้เลือกที่ `Flower_Person/camera1` → Device

โมเดลทำงานในเครื่อง ภาพกล้องจะถูกย่อเหลือ 512×288 เพื่อส่งให้ worker ในโฟลเดอร์ `runtime_pose`; ไม่มีการส่งภาพไปบริการคลาวด์ โฟลเดอร์นี้ไม่อยู่ใน Git

### เล่นกับเอฟเฟกต์

| การกระทำ | ผลลัพธ์ |
|---|---|
| โบกมือ | กลีบพุ่งออกใกล้ข้อมือและขอบตัว ยิ่งขยับเร็วแรงกระจายยิ่งมาก |
| อยู่นิ่งประมาณ 3 วินาที | ดอกไม้ค่อย ๆ บาน |
| ยกหรือลดระดับมือ | โทนสีดอกไม้ค่อย ๆ เปลี่ยน |
| ให้กล้องเห็นไหล่ ศอก และข้อมือ | เถาวัลย์ค่อย ๆ งอกตามแขน |
| อยู่หน้ากล้อง | ผีเสื้อเคลื่อนไหวรอบตำแหน่งตัวที่ตรวจพบ |

ถอยให้เห็นตั้งแต่ศีรษะถึงเอวและแขนทั้งสองข้าง ใช้แสงให้เพียงพอ ตรวจสถานะที่ `interaction_status`: `tracked=1` หมายถึงพบคน และ `left_valid/right_valid` หมายถึงพบข้อมือ

ตัวอย่างนี้ติดตามคนหลักหนึ่งคน ความแม่นยำขึ้นกับแสง การบังแขน และระยะกล้อง

## เครื่องมือ MCP ทั้ง 12 ตัว

| เครื่องมือ | หน้าที่ |
|---|---|
| `connection_status` | ตรวจ heartbeat ของตัวเชื่อมต่อ |
| `get_project` | อ่านชื่อและโครงสร้างระดับบนของโปรเจกต์ |
| `list_nodes` | สำรวจโหนดในคอมโพเนนต์ |
| `get_node` | อ่านค่า การเชื่อมต่อ ข้อผิดพลาด และข้อความ DAT |
| `create_node` | สร้างโหนด โดยไม่ใช้ชื่อซ้ำ |
| `set_parameters` | ตั้งค่า/Expression และคืนค่าเดิม |
| `pulse_parameter` | กดพารามิเตอร์แบบ Pulse |
| `connect_nodes` | ต่อ output เข้ากับ input ที่ระบุ |
| `set_dat_text` | แก้ข้อความ DAT พร้อมคืนข้อความเดิม |
| `execute_python` | รัน Python บนเธรดหลักของ TouchDesigner |
| `save_project` | บันทึก `.toe`; ไฟล์เดิมต้องระบุ `overwrite=true` |
| `snapshot_top` | ส่งภาพจาก TOP กลับให้ Codex ตรวจ |

Python ที่รันผ่าน MCP มีสิทธิ์เท่ากับ TouchDesigner และเข้าถึงไฟล์ในเครื่องได้ จึงควรใช้กับโค้ดและงานที่คุณอนุญาต

## โครงสร้างและการทำงาน

```text
Codex → stdio MCP → local file queue → Execute DAT → TouchDesigner API

กล้อง → AI person mask → flower shader → glow / particle feedback → vines / butterflies → OUT
      └→ pose_input → MediaPipe worker → gesture controller ────────────────┘
```

- คำสั่ง TouchDesigner ทำบน main thread ไม่เรียก OP API จาก worker thread
- ไม่เปิดพอร์ต TCP ของ MCP
- คิวตรวจได้สูงสุด 20 ครั้ง/วินาที รับหนึ่งคำสั่งต่อรอบ และส่ง heartbeat ทุกวินาที
- คำสั่งผูกกับ session ปัจจุบันและหมดอายุใน 25 วินาที
- หากรอคำตอบเกิน 30 วินาที ระบบแจ้งว่าผลลัพธ์ยังไม่แน่นอน ต้องอ่านสถานะก่อนสั่งแก้ซ้ำ
- เปิดโปรเจกต์ที่ติด bridge เพียงหนึ่ง instance ต่อ repo ในเวลาเดียวกัน

## ทดสอบ

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s . -p 'test_*.py' -v
.\.pose-venv\Scripts\python.exe -m pip check
```

ทดสอบ transport, คำสั่งเก่า/หมดอายุ, การตอบหลาย client, การกู้หลังข้อผิดพลาด และ gesture logic ส่วนกล้อง/GPU ควรทดสอบบนเครื่องจริงอีกครั้ง

## ไฟล์สำคัญ

- `server.py` — stdio MCP server
- `td_runtime.py`, `install_td.py` — bridge ฝั่ง TouchDesigner
- `interaction_logic.py`, `pose_worker.py` — gesture state และ pose inference
- `examples/flower_person.json` — โครงสร้างตัวอย่างแบบข้อความ ไม่มีภาพกล้องหรือ device ID
- `examples/build_garden.py` — สร้างตัวอย่างจาก manifest
- `*.frag` — GLSL shaders ที่อ่านและแก้ได้
- `assets/landscape_lake.png` — ภาพวิวที่สร้างด้วย ImageGen; prompt อยู่ในโฟลเดอร์เดียวกัน

ตัวติดตั้ง SDK, environments, โมเดล, คิว, ภาพกล้องชั่วคราว และ `.toe` งานส่วนตัวไม่ถูกนำขึ้น Git
