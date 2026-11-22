from pathlib import Path
import json, zipfile, hashlib, shutil

out=Path('dist/reels'); kit=Path('work/delivery-kit');kit.mkdir(parents=True,exist_ok=True)
manifest=json.loads((out/'production_manifest.json').read_text())
report=json.loads((out/'technical_verification.json').read_text())
for name in ['build.py','verify.py']:
 shutil.copy2(Path('scripts/premium-reels')/name,kit/name)
for path in out.iterdir():
 if path.is_file() and path.suffix!='.mp4':shutil.copy2(path,kit/path.name)
for scene in manifest['scenes']:
 path=Path('assets/photos-new')/scene['source'];dst=kit/'Villa-Indah'/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dst)
fonts=kit/'fonts';fonts.mkdir(exist_ok=True)
shutil.copy2('/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',fonts)
shutil.copy2('/usr/share/doc/fonts-noto-core/copyright',fonts/'NOTO_LICENSE.txt')
fonts=kit/'Villa-Indah/assets/fonts';fonts.mkdir(parents=True,exist_ok=True)
shutil.copy2('assets/fonts/AlumniSansPinstripe-Regular.ttf',fonts)
with zipfile.ZipFile('Alumni_Sans_Pinstripe.zip') as z:(fonts/'OFL.txt').write_bytes(z.read('Alumni_Sans_Pinstripe/OFL.txt'))
shutil.copy2('work/production/render/original_score.wav',kit/'Original_Score.wav')
(kit/'requirements.txt').write_text('numpy\nPillow\nopencv-python-headless\nscipy\n')
(kit/'README.txt').write_text('Villa Indah — RU + EN. 42 seconds, 1080x1920, 30 FPS.\n\nRebuild:\nInstall FFmpeg and Python.\npython -m pip install -r requirements.txt\npython build.py --repo Villa-Indah --out dist/reels\npython verify.py --repo Villa-Indah --out dist/reels\n\nPhotos: unchanged originals from Isadavrai/Villa-Indah/assets/photos-new.\nMusic: original algorithmically synthesized composition; no third-party recordings or samples. Generator is in build.py.\nFonts: Alumni Sans Pinstripe and Noto Sans. Licenses included.\n')
lines=['VILLA INDAH — ТЕХНИЧЕСКАЯ ПРОВЕРКА','']
for lang,r in report.items():
 lines.extend([lang, f"Продолжительность: {r['duration_seconds']} с; декодировано кадров: {r['decoded_frames']}",f"H.264/AAC, 1080x1920, 30 FPS CFR, yuv420p, Rec.709, faststart: {r['faststart']}",f"Проверено кадров с титрами: {r['caption_frames_checked']}; смещение: {r['caption_max_integer_displacement_px']} px",f"Ошибки декодирования: {r['decode_errors'] or 'нет'}",''])
lines.extend(['Оптический поток общей визуальной последовательности проверен на RU:',f"{report['RU']['motion_pairs_checked']} пар; максимальная медианная невязка {report['RU']['motion_max_median_residual_px']:.4f} px.",'EN использует те же исходники, траектории и монтаж.','Текст накладывается отдельными неподвижными RGBA-слоями после движения фотографий.'])
(out/'Technical_Report_RU.txt').write_text('\n'.join(lines))
shutil.copy2(out/'Technical_Report_RU.txt',kit)
(out/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name for p in sorted(out.glob('*.mp4')))+'\n')
with zipfile.ZipFile(out/'Villa_Indah_Production_Kit.zip','w',zipfile.ZIP_DEFLATED) as z:
 for path in sorted(kit.rglob('*')):
  if path.is_file():z.write(path,path.relative_to(kit))
