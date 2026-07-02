import shutil
from pathlib import Path

script_dir = Path(__file__).resolve().parent
candidates = [
    script_dir / 'backend' / 'media' / 'logos' / 'trillium_logo.jpeg',
    script_dir / 'backend' / 'static' / 'logos' / 'trillium_logo.jpeg',
    script_dir / 'static' / 'logos' / 'trillium_logo.jpeg',
]
src = next((path for path in candidates if path.exists()), None)

if src is None:
    raise FileNotFoundError('Could not find trillium_logo.jpeg in the expected logo locations')

for dst_dir in [script_dir / 'backend' / 'static' / 'logos', script_dir / 'static' / 'logos']:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / 'trillium_logo.jpeg'
    shutil.copy2(src, dst)
    print('copied', src, 'to', dst)
