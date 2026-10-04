"""Verify normal native GUI startup, without opening an assistance session."""
import json
from pathlib import Path
import platform
import subprocess
import time

config = json.loads(Path('config/public-build.json').read_text())
if platform.system() == 'Windows':
    executable = Path('dist/bundle') / (config['BINARY_NAME'] + '.exe')
else:
    app = Path('client/flutter/build/macos/Build/Products/Release') / (config['APP_NAME'] + '.app')
    subprocess.run(['codesign', '--verify', '--deep', '--strict', str(app)], check=True)
    executable = app / 'Contents/MacOS' / config['APP_NAME']
assert executable.is_file()
with Path('work/gui-startup.log').open('wb') as output:
    process = subprocess.Popen([str(executable.resolve())], stdout=output, stderr=output)
    try:
        time.sleep(15)
        assert process.poll() is None, 'Normal GUI exited early: ' + str(process.returncode)
        print('Normal GUI remains running; assistance was not started. Remote E2E remains to be tested.')
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
