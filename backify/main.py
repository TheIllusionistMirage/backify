"""
Automation to backup Spotify playlists and liked songs
"""

import traceback
from typing import Any

from backify.backup import Backup


def handler(event: dict, context: dict) -> dict[str, Any]:
    try:
        backup = Backup()
        backup.backup_all()
        return {
            'status': 'Done'
        }
    except Exception as e:
        print(f'Exceptions occurred: {e}')
        print(f'Full stack trace: {traceback.format_exc()}')
        return {
            'status': 'Error'
        }


if __name__ == '__main__':
    handler(None, None)
