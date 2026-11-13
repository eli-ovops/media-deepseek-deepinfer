import hashlib, json, os, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent
NAMES = [
    'f32fb78288400a049735f4d7eda7282b_raw.mp4',
    'bb11ee2cc59e622e89b9dc2319d6c749_raw.mp4',
    'ce340b9ef79b7ba55d2f97c69c701c74_raw.mp4',
    '0c6d3d3e47190c06034b525e9b71cf34_raw.mp4',
    '9980ef5b04e6ffc502fdcc233c7a9253_raw.mp4',
]
COMPOSITOR = pathlib.Path('/Volumes/EXTERNAL/\u81ea\u5a92\u4f53/Fred\u590d\u523b\u6d4b\u8bd5-20261016/7694088597179239690/source-snapshot/FredTalk-1.5-3D/camera/node_modules/@remotion/compositor-darwin-arm64')
env = dict(os.environ, DYLD_LIBRARY_PATH=str(COMPOSITOR))
records = []
for number, name in enumerate(NAMES, 1):
    path = pathlib.Path('/Users/USER/Downloads') / name
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    result = subprocess.run([str(COMPOSITOR/'ffprobe'), '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)], env=env, capture_output=True, text=True, check=True)
    record = {'input_number': number, 'id': 'S'+str(number), 'path': str(path), 'bytes': path.stat().st_size, 'sha256': h.hexdigest(), 'probe': json.loads(result.stdout)}
    records.append(record)
    print(json.dumps({'id': record['id'], 'sha256': record['sha256'], 'probe': record['probe']}, ensure_ascii=True))
(ROOT/'source-metadata.json').write_text(json.dumps(records, ensure_ascii=True, indent=2)+'\n')
