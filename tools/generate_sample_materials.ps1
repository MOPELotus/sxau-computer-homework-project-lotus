param(
    [string]$OutputDir = "materials/source/全格式示例"
)

$ErrorActionPreference = "Stop"

$absoluteOutput = Join-Path (Get-Location) $OutputDir
New-Item -ItemType Directory -Path $absoluteOutput -Force | Out-Null

$pythonScript = @'
from pathlib import Path
import json
import pandas as pd
import fitz
from docx import Document
from pptx import Presentation
from PIL import Image, ImageDraw, ImageFont

out = Path(r"__OUTPUT_DIR__")
out.mkdir(parents=True, exist_ok=True)

rows = [
    {
        "事件编号": "FMT001",
        "报告日期": "2025-04-01",
        "来源平台": "WOAH",
        "国家": "越南",
        "边境区域": "老街省",
        "疫病": "非洲猪瘟",
        "宿主动物": "生猪",
        "发病数": 136,
        "死亡数": 20,
        "扑杀数": 300,
        "14日周边疫情数": 4,
        "养殖密度指数": 79,
        "贸易流指数": 82,
        "交通可达性指数": 76,
        "距边境距离公里": 88,
        "降雨异常": 1.1,
        "气温异常": 0.7,
        "疫情通报文本": "边境市场周边猪场出现异常死亡，运输链条在封控前持续运行，存在跨境传播风险。",
        "跨境预警标签": 1,
    },
    {
        "事件编号": "FMT002",
        "报告日期": "2025-04-03",
        "来源平台": "FAO",
        "国家": "尼泊尔",
        "边境区域": "蓝毗尼省",
        "疫病": "口蹄疫",
        "宿主动物": "牛",
        "发病数": 42,
        "死亡数": 3,
        "扑杀数": 0,
        "14日周边疫情数": 1,
        "养殖密度指数": 45,
        "贸易流指数": 35,
        "交通可达性指数": 40,
        "距边境距离公里": 260,
        "降雨异常": -0.2,
        "气温异常": 0.1,
        "疫情通报文本": "病例集中于内陆牧场，已在短时间内完成封锁和免疫，跨境扩散可能性较低。",
        "跨境预警标签": 0,
    },
]

df = pd.DataFrame(rows)
df.to_csv(out / "示例疫情台账.csv", index=False, encoding="utf-8-sig")
df.to_excel(out / "示例疫情台账.xlsx", index=False)

(out / "示例疫情通报.txt").write_text(
    "国家：老挝\n边境区域：博胶省\n报告日期：2025-04-05\n来源平台：地方监测材料\n疫病：非洲猪瘟\n宿主动物：生猪\n发病数：67\n死亡数：11\n扑杀数：150\n疫情描述：边境通道附近多个养殖点出现异常死亡，活畜交易车辆往来频繁。\n",
    encoding="utf-8",
)

(out / "示例疫情通报.md").write_text(
    "# 边境疫情补充说明\n\n国家：缅甸\n边境区域：掸邦\n报告日期：2025-04-07\n来源平台：监测简报\n疫病：禽流感\n宿主动物：家禽\n发病数：93\n死亡数：25\n扑杀数：210\n\n疫情描述：多个边境乡镇出现家禽死亡聚集，交易市场和运输节点存在扩散隐患。\n",
    encoding="utf-8",
)

json_rows = [
    {
        "事件编号": "FMT003",
        "报告日期": "2025-04-08",
        "来源平台": "National Portal",
        "国家": "孟加拉国",
        "边境区域": "锡尔赫特",
        "疫病": "PPR小反刍兽疫",
        "宿主动物": "山羊",
        "发病数": 88,
        "死亡数": 17,
        "扑杀数": 120,
        "14日周边疫情数": 3,
        "养殖密度指数": 66,
        "贸易流指数": 63,
        "交通可达性指数": 61,
        "距边境距离公里": 140,
        "降雨异常": 0.5,
        "气温异常": 1.0,
        "疫情通报文本": "多个乡镇羊群病例与市场交易和共牧活动相关，存在跨境传播风险。",
        "跨境预警标签": 1,
    }
]
(out / "示例疫情记录.json").write_text(json.dumps(json_rows, ensure_ascii=False, indent=2), encoding="utf-8")

document = Document()
document.add_heading("DOCX 疫情材料", level=1)
document.add_paragraph("国家：不丹")
document.add_paragraph("边境区域：萨姆策")
document.add_paragraph("报告日期：2025-04-09")
document.add_paragraph("来源平台：项目整理稿")
document.add_paragraph("疫病：新城疫")
document.add_paragraph("宿主动物：家禽")
document.add_paragraph("发病数：34")
document.add_paragraph("死亡数：9")
document.add_paragraph("扑杀数：70")
document.add_paragraph("疫情描述：边境村庄小规模家禽疫情已完成扑杀和消杀。")
document.save(out / "示例疫情材料.docx")

presentation = Presentation()
slide = presentation.slides.add_slide(presentation.slide_layouts[1])
slide.shapes.title.text = "PPTX 疫情汇报"
slide.placeholders[1].text = (
    "国家：印度\n"
    "边境区域：阿鲁纳恰尔邦\n"
    "报告日期：2025-04-10\n"
    "来源平台：阶段汇报\n"
    "疫病：H5N1高致病性禽流感\n"
    "宿主动物：鸭\n"
    "发病数：58\n"
    "死亡数：16\n"
    "扑杀数：90\n"
    "疫情描述：候鸟活动区域附近养殖点出现疫情，局部封控已启动。"
)
presentation.save(out / "示例疫情汇报.pptx")

pdf = fitz.open()
page = pdf.new_page()
page.insert_text(
    (72, 72),
    "country: Russia\nregion: Primorsky Krai\ndate: 2025-04-11\ndisease: HPAI\nhost: poultry\ncases: 120\ndeaths: 32\nculling: 260\nnarrative: farms near a border transport corridor reported clustered poultry mortality.",
    fontsize=12,
)
pdf.save(out / "示例疫情扫描.pdf")
pdf.close()

image_text = "Country: Laos  Disease: ASF  Note: border trade checkpoint risk"
font = None
for font_name in ["msyh.ttc", "simhei.ttf", "arial.ttf"]:
    try:
        font = ImageFont.truetype(font_name, 24)
        break
    except Exception:
        continue
if font is None:
    font = ImageFont.load_default()

base_image = Image.new("RGB", (1000, 360), color="white")
draw = ImageDraw.Draw(base_image)
draw.rectangle((20, 20, 980, 340), outline="black", width=2)
draw.text((40, 60), image_text, fill="black", font=font)
draw.text((40, 130), "Cases: 74  Deaths: 12  Culling: 140", fill="black", font=font)
draw.text((40, 200), "Narrative: outbreaks were reported near the border market.", fill="black", font=font)
draw.text((40, 270), "This image is used for multimodal input testing.", fill="black", font=font)

for name, fmt in [
    ("示例疫情图片.png", "PNG"),
    ("示例疫情图片.jpg", "JPEG"),
    ("示例疫情图片.jpeg", "JPEG"),
    ("示例疫情图片.webp", "WEBP"),
    ("示例疫情图片.bmp", "BMP"),
]:
    base_image.save(out / name, format=fmt)
'@

$pythonScript = $pythonScript.Replace("__OUTPUT_DIR__", $absoluteOutput)
$pythonScript | python -

$xlsxPath = Join-Path $absoluteOutput "示例疫情台账.xlsx"
$xlsPath = Join-Path $absoluteOutput "示例疫情台账.xls"
$docxPath = Join-Path $absoluteOutput "示例疫情材料.docx"
$docPath = Join-Path $absoluteOutput "示例疫情材料.doc"
$pptxPath = Join-Path $absoluteOutput "示例疫情汇报.pptx"
$pptPath = Join-Path $absoluteOutput "示例疫情汇报.ppt"

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$workbook = $excel.Workbooks.Open($xlsxPath)
$workbook.SaveAs($xlsPath, 56)
$workbook.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($workbook) | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$wordDoc = $word.Documents.Open($docxPath, $false, $false)
$wordDoc.SaveAs([string]$docPath, 0)
$wordDoc.Close()
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($wordDoc) | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null

$pptApp = New-Object -ComObject PowerPoint.Application
$pptPresentation = $pptApp.Presentations.Open($pptxPath, $true, $false, $false)
$pptPresentation.SaveAs($pptPath, 1)
$pptPresentation.Close()
$pptApp.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($pptPresentation) | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($pptApp) | Out-Null

Write-Output "示例资料已生成到: $absoluteOutput"
