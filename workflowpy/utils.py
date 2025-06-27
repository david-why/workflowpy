import os
import plistlib
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from workflowpy.models.shortcuts import Action, Shortcut


def find_action_with_uuid(actions: 'list[Action]', uuid: str):
    for action in actions:
        if action.uuid == uuid:
            return action


class SignShortcutError(Exception):
    def __init__(self, stdout: bytes, stderr: bytes) -> None:
        super().__init__(('Failed to sign shortcut', stdout, stderr))


def sign_shortcut(shortcut: 'Shortcut') -> bytes:
    if sys.platform != 'darwin':
        raise OSError('Shortcuts can only be signed on macOS devices')

    data = shortcut.model_dump(mode='json')

    with tempfile.TemporaryDirectory() as tmpdir:
        raw_filename = os.path.join(tmpdir, 'raw.shortcut')
        signed_filename = os.path.join(tmpdir, 'signed.shortcut')

        with open(raw_filename, 'wb') as f:
            plistlib.dump(data, f)

        result = subprocess.run(
            [
                'shortcuts',
                'sign',
                '--mode',
                'anyone',
                '--input',
                raw_filename,
                '--output',
                signed_filename,
            ],
            capture_output=True,
        )

        if result.returncode != 0:
            raise SignShortcutError(result.stdout, result.stderr)

        with open(signed_filename, 'rb') as f:
            return f.read()


def convert_property_to_name(property: str) -> str:
    return property.lower().replace(' ', '_')
