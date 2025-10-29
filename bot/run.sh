#!/usr/bin/bash
cd /home/masher/development/receipt_bot/
python3 -c "from bot.db.db import init_db; init_db(); print('db initialized')"
python3 -m bot.__main__