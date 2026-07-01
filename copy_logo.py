import shutil
from pathlib import Path
src = Path('backend/media/logos/trillium_logo.jpeg')
dst_dir = Path('backend/static/logos')
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / 'trillium_logo.jpeg'
shutil.copy2(src, dst)
print('copied', src, 'to', dst)
