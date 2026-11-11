# คู่มือใช้งาน HALB MCP TouchDesigner

## 1. ใช้ MCP กับงานที่มีอยู่

เปิดไฟล์ `.toe` ที่ต้องการแก้ ให้เป็นงานที่คุณไว้ใจ แล้วติดตั้ง bridge ใน Python Textport:

```python
p = 'D:/MCP/TD/install_td.py'; exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), dict(globals(), __file__=p))
```

หาก clone repo ไว้ที่อื่น เปลี่ยนค่าของ `p` ให้ตรงกับไฟล์จริง ตัว bridge ที่ถูกสร้างจะจำโฟลเดอร์ repo นั้น

เมื่อขึ้น `TouchDesigner MCP connected` ให้บันทึกงานและกด Play ตัว bridge อยู่ที่ `/codex_mcp` อย่าลบระหว่างใช้งาน หากเปิดไฟล์อื่นซึ่งยังไม่มี component นี้ ให้ติดตั้งอีกครั้งในไฟล์นั้น

เปิด Codex ใหม่หลังลงทะเบียน MCP ครั้งแรก จากนั้นสั่งงานเป็นภาษาปกติ เช่น:

> ตรวจการเชื่อมต่อ TouchDesigner แล้วอธิบายโครงสร้าง /project1

> สร้างคอมโพเนนต์ใหม่ที่มี Noise TOP ต่อ Blur TOP ต่อ Level TOP และเพิ่มตัวปรับความสว่าง

> อ่านข้อผิดพลาดของ /project1/Flower_Person แล้วแก้ให้แสดงภาพ

> บันทึกฉบับแก้ไขเป็น D:/MCP/TD/my_project_v2.toe

ก่อนเปลี่ยนงานสำคัญ ให้บันทึกฉบับใหม่หรือทำสำเนา `.toe` ตัว bridge สำรองไฟล์บนดิสก์เมื่อถูกติดตั้ง แต่สำเนานั้นไม่รวมการแก้ที่ยังไม่เคยบันทึก

## 2. ติดตั้งด้วยคำสั่งแยก

ถ้าเครื่องไม่อนุญาตให้เปิด `setup.ps1` ใช้ PowerShell รันคำสั่งเหล่านี้แทน โดยไม่ต้องเปลี่ยนนโยบายความปลอดภัยของระบบ:

```powershell
cd D:\MCP\TD
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
codex mcp add touchdesigner -- D:\MCP\TD\.venv\Scripts\python.exe D:\MCP\TD\server.py
```

สำหรับตัวอย่างที่ใช้กล้องและท่าทาง:

```powershell
& 'C:\Program Files\Derivative\TouchDesigner\bin\python.exe' -m venv .pose-venv
.\.pose-venv\Scripts\python.exe -m pip install -r requirements-pose.txt
New-Item -ItemType Directory -Path models -Force
Invoke-WebRequest 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task' -OutFile models\pose_landmarker_lite.task
Get-FileHash models\pose_landmarker_lite.task -Algorithm SHA256
```

เทียบ SHA256 กับ `models.sha256` ก่อนใช้โมเดล

เพิ่ม NVIDIA Video Effects SDK จาก[หน้า Download Center ของ NVIDIA](https://www.nvidia.com/en-us/geforce/broadcasting/broadcast-sdk/resources/) เลือก **Video Effects** ให้ตรงกับรุ่น GPU ทดสอบด้วย TouchDesigner 2025.33230 และ Video Effects 0.7.6 บน RTX 50 Series เมื่อติดตั้งแล้ว ปิดและเปิด TouchDesigner ใหม่

รายละเอียดการเพิ่ม MCP ฝั่ง Codex อยู่ใน[เอกสาร MCP ทางการ](https://learn.chatgpt.com/docs/extend/mcp)

## 3. สร้างตัวอย่างคนดอกไม้

สร้างโปรเจกต์ใหม่แล้ว Save As ไว้ในโฟลเดอร์ repo เช่น `D:/MCP/TD/My_Garden.toe` จากนั้นใน Textport:

```python
import sys
sys.path.insert(0, 'D:/MCP/TD/examples')
from build_garden import build
garden = build('D:/MCP/TD')
```

คำสั่งนี้เปิดกล้องและเริ่ม worker ติดตามท่าทางในเครื่อง เมื่อทำสำเร็จให้ Save อีกครั้งเพื่อเก็บ component ไว้ในโปรเจกต์

หากมี `Flower_Person` อยู่แล้ว ให้เลือกชื่อใหม่:

```python
garden = build('D:/MCP/TD', name='Flower_Person_2')
```

หากต้องการสร้างโครงสร้างโดยยังไม่เปิดกล้อง:

```python
garden = build('D:/MCP/TD', name='Flower_Person_Test', activate=False)
```

ถ้ากล้องผิดตัว ให้เข้า component → `camera1` → Device แล้วเลือกกล้องที่ต้องการ ภาพออกที่ `OUT` คลิกขวาที่ `OUT` แล้วเลือก View เพื่อเปิดภาพขนาดใหญ่

## 4. ท่าทางควบคุม

- **โบกมือ:** ความเร็วข้อมือเพิ่มค่า burst ทำให้กลีบแตกกระจายใกล้มือและขอบตัว ก่อนจางหาย
- **อยู่นิ่ง:** เมื่อพบคนและการเคลื่อนไหวต่ำ ดอกไม้ค่อย ๆ บานตามเวลาที่กำหนด
- **ยกหรือลดมือ:** ระดับข้อมือเฉลี่ยเปลี่ยนโทนสีอย่างนุ่มนวล
- **ยื่นแขนให้เห็น:** เถาวัลย์เริ่มงอกจากไหล่ผ่านศอกไปข้อมือ ใช้ประมาณ 4 วินาทีเมื่อพบร่างกาย
- **ผีเสื้อ:** บินและกระพือปีกรอบจุดศูนย์กลางตัว เมื่อไม่พบคนยังมีผีเสื้อบินบนฉากได้

กล้องควรเห็นศีรษะถึงเอวและแขนได้ครบ มีแสงด้านหน้า และไม่บังข้อมือ ตัวอย่างรองรับคนหลักหนึ่งคน การติดตามอาจขาดเมื่อแขนพ้นเฟรมหรือถูกบัง

## 5. ตัวปรับทั้งหมด

เลือก component แล้วดูแท็บ custom parameters:

| แท็บ | ตัวปรับ | วิธีใช้ |
|---|---|---|
| Flower Controls | Flower Density | เพิ่มค่า = ดอกเล็กและแน่นขึ้น |
| Flower Controls | Animation Speed | ความเร็วของดอกไม้ ค่า 0 หยุดเวลาการเคลื่อนไหวของดอก |
| Flower Controls | Flower Amount | 0 เป็นภาพคนเดิม, 1 เป็นคนดอกไม้เต็มที่ |
| Flower Controls | Brightness | ความสว่างรวม |
| Flower Controls | Landscape Brightness | ความสว่างฉากวิว |
| Flower Controls | Landscape Image | เลือกไฟล์ภาพฉากหลังใหม่ |
| Flower Controls | Mirror Camera | กลับภาพคนแบบกระจก |
| Flower Animation | Flower Motion | ความแรงการเคลื่อนไหวของดอกไม้ |
| Flower Animation | Flower Rotation | การหมุน |
| Flower Animation | Flower Sway | การโยก |
| Flower Animation | Flower Bloom | การบาน–หุบแบบเป็นจังหวะ |
| Edge and Particles | Edge Glow | ความแรงแสงขอบ |
| Edge and Particles | Edge Softness | ความกว้างขอบนุ่ม |
| Edge and Particles | Petal Amount | ปริมาณกลีบพื้นฐาน |
| Edge and Particles | Petal Size | ขนาดกลีบ |
| Edge and Particles | Trail Lifetime | เวลาที่รอยตามค่อย ๆ หาย |
| Edge and Particles | Petal Drift | ความเร็วกลีบลอย |
| Interactive Garden | Gesture Sensitivity | เพิ่มเพื่อให้ขยับน้อยก็ส่งผล; ลดถ้าตอบสนองมากเกิน |
| Interactive Garden | Stillness Bloom Time | จำนวนวินาทีโดยประมาณก่อนบานเต็ม |
| Interactive Garden | Hand Burst Strength | แรงกระจายจากการโบกมือ |
| Interactive Garden | Butterfly Count | จำนวนผีเสื้อ; 0 เพื่อปิด |
| Interactive Garden | Arm Vines | ความชัดของเถาวัลย์; 0 เพื่อปิด |
| Interactive Garden | Gesture Reactions | เปิด–ปิดผลท่าทางต่อดอกไม้และกลีบ |
| Interactive Garden | Wave Petal Bursts | เปิด–ปิดกลีบกระจายจากมือ |
| Interactive Garden | Bloom When Still | เปิด–ปิดการบานเมื่ออยู่นิ่ง |
| Interactive Garden | Hand Height Colors | เปิด–ปิดสีตามระดับมือ |

## 6. ตรวจสถานะและแก้ปัญหา

### Codex บอกว่า bridge offline

- เปิด `.toe` ที่มี `/codex_mcp`
- กด Play และปิดกล่องข้อความที่ทำให้โปรเจกต์หยุดประมวลผล
- เปิด bridge เพียงหนึ่งโปรเจกต์ต่อ repo
- ถ้าเพิ่งเพิ่ม MCP ให้เปิด Codex ใหม่

### TensorRT not found / NVIDIA Background เป็นกากบาท

ติดตั้ง NVIDIA Video Effects SDK ที่ตรงกับ GPU แล้วเปิด TouchDesigner ใหม่ ตัวอย่างไม่ใช้ NVIDIA Body Track; มือและแขนติดตามด้วย MediaPipe worker แยกต่างหาก

### ภาพคนไม่ออก แต่ฉากหลังออก

ตรวจ `camera1` ว่าเลือก Device ถูก และ Active เป็น On จากนั้นดู `person_mask` ว่ามีภาพ alpha ของคน รอสักครู่หลังเปิดกล้องให้กล้องส่งเฟรมจริงก่อน

### ดอกไม้ขึ้น แต่ท่าทางไม่ตอบสนอง

ดู `interaction_status`:

| ค่า | ความหมาย |
|---|---|
| tracked | 1 = พบคนจากตำแหน่งไหล่ |
| left_valid / right_valid | พบข้อมือข้างนั้น |
| motion | ระดับการขยับหลังกรองสัญญาณ |
| burst | แรงกระจายจากความเร็วข้อมือ |
| stillness | 0–1 ระดับการบานเมื่ออยู่นิ่ง |
| hue | ค่าสีจากระดับมือ |
| growth | 0–1 การเติบโตของเถาวัลย์ |

ถ้าไม่พบคน ให้ถอยให้เห็นช่วงตัวและแขนมากขึ้น ตรวจว่า `.pose-venv`, `models/pose_landmarker_lite.task`, `pose_worker.py` อยู่ครบ แล้วดู `runtime_pose/worker.log` การหยุดพบคนจะซ่อนเถาวัลย์ที่ระบุแขนไม่ได้และลดค่าปฏิกิริยาลง

### ฉากหลังหายหรือพาธภาพผิด

เลือก Landscape Image ใหม่ ตัว builder ตั้ง `asset_root` ให้ตรง repo ที่นำไปใช้ ถ้าย้าย repo ให้สร้างตัวอย่างใหม่จากตำแหน่งใหม่ หรือเปลี่ยน `asset_root` และพาธภาพให้ตรง

### MCP timeout หลังสั่งแก้ไข

อย่ารีบสั่งแก้ซ้ำ ให้ตรวจโหนดก่อน เพราะคำสั่งที่เริ่มทำไปแล้วอาจสำเร็จแม้คำตอบมาช้า การรัน Python ยาวหรือวนลูปใน main thread อาจทำให้ TouchDesigner ไม่ตอบสนอง

## 7. บันทึกและนำไปใช้ครั้งถัดไป

Save As เป็น `.toe` ฉบับใหม่ในโฟลเดอร์ repo แล้วเปิดไฟล์นั้นในครั้งถัดไป ควรเก็บโฟลเดอร์ `assets`, โมเดล และ worker ไว้ครบ ตัว bridge และ shaders อยู่ในโปรเจกต์ที่บันทึก ส่วน MediaPipe worker จะเริ่มเองเมื่อโปรเจกต์ Play

เมื่อปิดหรือหยุดโปรเจกต์ worker จะออกหลังไม่ได้รับเฟรมประมาณ 35 วินาที เปิดและ Play ใหม่แล้ว controller จะเริ่ม worker ใหม่ให้

## 8. สำหรับผู้พัฒนา

- `execute_python` รันโค้ดที่ได้รับอนุญาตบน main thread และเข้าถึงไฟล์ในเครื่องได้
- inference อยู่ใน `pose_worker.py` ใช้ภาพย่อที่เขียนแบบ atomic และคืน JSON
- เปลี่ยน gesture logic ได้ใน `interaction_logic.py` แล้วโหลดข้อความใหม่เข้า DAT ชื่อเดียวกัน
- `examples/flower_person.json` เป็น manifest แบบข้อความ ใช้สร้าง demo โดยไม่ต้องแจกไฟล์ `.toe` ส่วนตัว
- `export_demo.py` ใช้ส่งออก manifest จาก `/project1/Flower_Person`; ไม่ส่งออก device ID และปิดกล้อง/callback ไว้ใน manifest จนกว่าจะเรียก builder แบบ activate
- ใช้ `python -m unittest discover -s . -p 'test_*.py' -v` เพื่อตรวจ transport และ gesture logic
- ทดสอบบนกล้องจริงอีกครั้งเมื่อเปลี่ยน TouchDesigner, GPU driver หรือโมเดล
