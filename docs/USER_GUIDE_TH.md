# คู่มือใช้ MCP กับโปรเจกต์ TouchDesigner

## 1. ติดตั้ง MCP server

Clone repo ไปยังโฟลเดอร์ใดก็ได้ แล้วเปิด PowerShell ในโฟลเดอร์นั้น:

```powershell
.\setup.ps1 -RegisterMcp
```

ตัวเลือก `-RegisterMcp` ใช้กับ Codex หากใช้ client อื่นให้รัน `setup.ps1` แล้วนำพาธ Python กับ `server.py` ไปตั้งค่า stdio ของ client

หากเครื่องไม่อนุญาตให้เปิดสคริปต์ ให้ติดตั้งแยกดังนี้:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

ตัวอย่างเพิ่ม MCP ให้ Codex เมื่อ repo อยู่ที่ `C:\tools\halb-mcp-TouchDesigner-by-devza`:

```powershell
codex mcp add touchdesigner -- C:\tools\halb-mcp-TouchDesigner-by-devza\.venv\Scripts\python.exe C:\tools\halb-mcp-TouchDesigner-by-devza\server.py
```

รายละเอียดการตั้งค่าฝั่ง Codex: [เอกสาร MCP ทางการ](https://learn.chatgpt.com/docs/extend/mcp)

สำหรับ client ที่ใช้รูปแบบ `mcpServers` ตัวอย่างการตั้งค่าคือ:

```json
{
  "mcpServers": {
    "touchdesigner": {
      "command": "C:\\tools\\halb-mcp-TouchDesigner-by-devza\\.venv\\Scripts\\python.exe",
      "args": ["C:\\tools\\halb-mcp-TouchDesigner-by-devza\\server.py"]
    }
  }
}
```

เปลี่ยนพาธให้ตรงกับเครื่องของคุณ แล้วเปิด client ใหม่เพื่อโหลดเครื่องมือ

## 2. เชื่อมโปรเจกต์ของคุณ

เปิดไฟล์ `.toe` ที่ต้องการควบคุม กด **Alt+T** แล้วเลือก Python Textport วางคำสั่งนี้ โดยเปลี่ยนพาธ `p` ให้ตรงกับตำแหน่ง repo:

```python
p = 'C:/tools/halb-mcp-TouchDesigner-by-devza/install_td.py'; exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), dict(globals(), __file__=p))
```

เมื่อสำเร็จจะมี component `/codex_mcp` และข้อความ `TouchDesigner MCP connected`

- บันทึกโปรเจกต์เพื่อเก็บ bridge สำหรับการเปิดครั้งถัดไป
- ให้โปรเจกต์อยู่ในสถานะ **Play** ระหว่างสั่งงาน
- อย่าลบ `/codex_mcp` ขณะใช้งาน
- เปิดโปรเจกต์ที่ติด bridge เพียงหนึ่ง instance ต่อ repo
- เปิดโปรเจกต์อื่นที่ไม่มี bridge ให้ติดตั้งอีกครั้งในโปรเจกต์นั้น

สำเนาใน `backups` เป็นไฟล์ที่เคยบันทึกไว้บนดิสก์ ไม่รวมการแก้ที่ยังไม่ได้ Save ก่อนเริ่มงานสำคัญควรบันทึกฉบับใหม่ไว้ด้วย

## 3. เริ่มสั่งงาน

เริ่มจากให้ AI ตรวจ `connection_status` และ `get_project` เพื่อยืนยันว่าเชื่อมกับโปรเจกต์ที่ตั้งใจ จากนั้นบอกผลลัพธ์ที่ต้องการ เช่น:

> อ่านโครงสร้าง /project1 แล้วอธิบายเส้นทางข้อมูล

> สร้างคอมโพเนนต์ใหม่ชื่อ Animated_Noise มี Noise TOP ต่อ Blur TOP ต่อ Level TOP พร้อมตัวปรับความสว่าง

> อ่านข้อผิดพลาดของโหนดนี้แล้วแก้ไข

> ตั้ง Expression ให้ Translate Z เปลี่ยนตาม absTime.seconds

> แสดงภาพจาก /project1/output1 ให้ตรวจ

> บันทึกฉบับแก้ไขเป็น C:/projects/my_project_v2.toe

AI สามารถใช้ `execute_python` เพื่อทำงานที่ไม่มีเครื่องมือเฉพาะได้ ควรใช้สคริปต์ที่ทำงานสั้นและคืนผลเร็ว เพราะการรันโค้ดเกิดบน main thread

## 4. รูปแบบข้อมูลที่ใช้บ่อย

### พาธโหนด

ใช้พาธเต็ม เช่น `/project1/noise1` หรือ `/project1/effect/level1`

### ตั้งค่าหรือ Expression

```json
{"path":"/project1/level1","values":{"brightness1":1.2}}
```

```json
{"path":"/project1/noise1","values":{"tz":{"expression":"absTime.seconds * 0.2"}}}
```

### เชื่อมโหนด

```json
{"source":"/project1/noise1","target":"/project1/blur1","input_index":0,"output_index":0}
```

การเชื่อมเข้าช่อง input ที่มีสายอยู่จะเปลี่ยนการเชื่อมต่อของช่องนั้น

### รัน Python

```python
n = op('/project1/noise1')
result = {'path': n.path, 'type': n.OPType}
```

ตั้งค่า `result` เป็นข้อมูลที่แปลงเป็น JSON ได้ เครื่องมือจะคืน stdout และ `result` กลับมา Python นี้มีสิทธิ์เท่ากับ TouchDesigner และเข้าถึงไฟล์ในเครื่องได้

### บันทึก

ระบุพาธ `.toe` แบบเต็ม ไฟล์ที่มีอยู่แล้วต้องตั้ง `overwrite=true` หากต้องการเขียนทับ การเปลี่ยนโหนดมีผลทันที ส่วนการบันทึกลงดิสก์เป็นอีกขั้นตอนหนึ่ง

## 5. ตรวจและแก้ปัญหา

### Bridge offline

ตรวจว่าเปิด `.toe` ที่มี `/codex_mcp`, กด Play และไม่มี dialog ที่ทำให้แอปหยุดประมวลผล ถ้าปิด TouchDesigner แล้ว heartbeat จะเก่าและ server จะไม่ส่งคำสั่งแก้ไขเข้าไป

### ไม่พบเครื่องมือ MCP ใน client

เปิด client ใหม่หลังลงทะเบียน ตรวจว่า command ชี้ไปที่ `.venv/Scripts/python.exe` และ args ชี้ไปที่ `server.py` ของ repo เดียวกับที่ใช้ติดตั้ง bridge

### มีหลายโปรเจกต์เปิดพร้อมกัน

แต่ละโปรเจกต์จะใช้คิวเดียวกันเมื่ออ้าง repo เดียวกัน ให้เปิด bridge เพียงโปรเจกต์เดียว หรือแยกสำเนา repo และลงทะเบียน MCP คนละชื่อเมื่อจำเป็นต้องควบคุมหลาย instance

### ย้าย repo ไปที่ใหม่

ตั้งค่า MCP client ให้ใช้พาธใหม่ จากนั้นรันคำสั่งติดตั้ง bridge ในโปรเจกต์อีกครั้งโดยใช้ `install_td.py` จากตำแหน่งใหม่ แล้วบันทึกโปรเจกต์

### Unknown operator / parameter

ชื่อโหนดและพารามิเตอร์ขึ้นกับเวอร์ชัน TouchDesigner ให้ใช้ `get_node` อ่านชื่อจริงก่อนแก้ โหนดที่ต้องใช้อุปกรณ์ ปลั๊กอิน หรือไลเซนส์ยังต้องมีสิ่งนั้นพร้อมในเครื่อง

### Timeout หลังสั่งแก้ไข

อย่าสั่งแก้ซ้ำทันที ให้ตรวจสถานะก่อน เพราะคำสั่งที่เริ่มทำแล้วอาจสำเร็จแม้คำตอบมาช้า คำสั่งที่ยังไม่เริ่มจะหมดอายุเมื่อเกิน 25 วินาที

## 6. ทดสอบและถอดการติดตั้ง

ทดสอบ core transport:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s . -p test_bridge.py -v
```

ถอด MCP ออกจาก Codex:

```powershell
codex mcp remove touchdesigner
```

จากนั้นลบ `/codex_mcp` ในโปรเจกต์เมื่อไม่ต้องการใช้งานแล้ว และบันทึกโปรเจกต์ สำเนาไฟล์เดิมยังอยู่ในโฟลเดอร์ `backups`

## 7. ขอบเขตของ bridge

MCP นี้ควบคุมผ่าน TouchDesigner Python API ไม่ได้แทนการกดทุกเมนูของโปรแกรมโดยอัตโนมัติ การเปิด dialog, การตั้งค่าเฉพาะอุปกรณ์ และสิทธิ์การเข้าถึงระบบบางอย่างอาจต้องทำในหน้าจอด้วยตนเอง

ตัว server ใช้ stdio และ local file queue ไม่เปิดพอร์ต TCP และไม่ส่งข้อมูลไปบริการคลาวด์เอง การส่งผลลัพธ์กลับให้ AI เป็นไปตาม client ที่คุณเชื่อมต่อ
