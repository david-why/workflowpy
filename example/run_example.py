from pathlib import Path
import plistlib

from workflowpy.compiler import Compiler
from workflowpy.utils import sign_shortcut

path = Path(__file__).parent

with open(path / 'example.py') as f:
    code = f.read()

shortcut = Compiler().compile(code)
# signed_shortcut = sign_shortcut(shortcut)

with open(path / 'unsigned.shortcut', 'wb') as f:
    plistlib.dump(shortcut.model_dump(mode='json'), f)
