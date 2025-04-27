import sqlite3
from src.application.ports.dialog_repo import IDialogRepository
from src.domain.entities import Dialog

class SQLiteDialogRepo(IDialogRepository):
    def __init__(self, db_path="storage/dialogs.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS dialogs (
            user_id TEXT PRIMARY KEY,
            state TEXT,
            context TEXT
        )
        """)
        self.conn.commit()

    def get(self, user_id: str) -> Dialog:
        cur = self.conn.cursor()
        cur.execute("SELECT state, context FROM dialogs WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        if row:
            state, context = row
            return Dialog(user_id=user_id, state=state, context={})  # context parsing stub
        return None

    def save(self, dialog: Dialog):
        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO dialogs(user_id, state, context) VALUES(?,?,?)",
            (dialog.user_id, dialog.state, str(dialog.context))
        )
        self.conn.commit()
