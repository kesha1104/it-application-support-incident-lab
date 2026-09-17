import sqlite3
import tempfile
import unittest
from pathlib import Path

import app as app_module


class TicketSystemTests(unittest.TestCase):

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.test_database = (
            Path(self.temporary_directory.name) / "test_tickets.db"
        )

        schema_path = (
            Path(app_module.__file__).resolve().parent / "schema.sql"
        )

        connection = sqlite3.connect(self.test_database)

        with open(schema_path, encoding="utf-8") as schema_file:
            connection.executescript(schema_file.read())

        connection.close()

        app_module.database_path = self.test_database
        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_dashboard_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Incident Operations Dashboard", response.data)

    def test_ticket_can_be_created(self):
        response = self.client.post(
            "/tickets/new",
            data={
                "requester_name": "Test User",
                "email": "test@example.com",
                "title": "Printer issue",
                "category": "Hardware",
                "description": "The printer is not responding.",
                "priority": "High",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Printer issue", response.data)

        connection = sqlite3.connect(self.test_database)
        ticket_count = connection.execute(
            "SELECT COUNT(*) FROM tickets"
        ).fetchone()[0]
        connection.close()

        self.assertEqual(ticket_count, 1)

    def test_ticket_status_can_be_updated(self):
        connection = sqlite3.connect(self.test_database)
        cursor = connection.execute(
            """
            INSERT INTO tickets (
                requester_name,
                email,
                title,
                category,
                description,
                priority
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "Test User",
                "test@example.com",
                "Network problem",
                "Network",
                "The computer cannot connect to Wi-Fi.",
                "Medium",
            ),
        )
        ticket_id = cursor.lastrowid
        connection.commit()
        connection.close()

        response = self.client.post(
            f"/tickets/{ticket_id}",
            data={"status": "Resolved"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Resolved", response.data)

        connection = sqlite3.connect(self.test_database)
        saved_status = connection.execute(
            "SELECT status FROM tickets WHERE id = ?",
            (ticket_id,),
        ).fetchone()[0]
        connection.close()

        self.assertEqual(saved_status, "Resolved")


if __name__ == "__main__":
    unittest.main()