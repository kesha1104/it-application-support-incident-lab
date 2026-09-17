import sqlite3
from pathlib import Path

from flask import abort, Flask, redirect, render_template, request, url_for


app = Flask(__name__)


# ---------------------------------------------------------
# Database configuration
# ---------------------------------------------------------

project_directory = Path(__file__).resolve().parent
database_path = project_directory / "tickets.db"


# ---------------------------------------------------------
# Allowed ticket values
# ---------------------------------------------------------

allowed_statuses = [
    "Open",
    "In Progress",
    "Pending User",
    "Escalated",
    "Resolved",
    "Closed",
]

allowed_priorities = [
    "Low",
    "Medium",
    "High",
    "Critical",
]


# ---------------------------------------------------------
# Database helpers
# ---------------------------------------------------------

def get_database_connection():
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def get_ticket(ticket_id):
    connection = get_database_connection()

    ticket = connection.execute(
        """
        SELECT *
        FROM tickets
        WHERE id = ?
        """,
        (ticket_id,),
    ).fetchone()

    connection.close()

    if ticket is None:
        abort(404)

    return ticket


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

@app.route("/")
def home():

    selected_status = request.args.get("status", "").strip()
    selected_priority = request.args.get("priority", "").strip()
    search = request.args.get("search", "").strip()

    if selected_status not in allowed_statuses:
        selected_status = ""

    if selected_priority not in allowed_priorities:
        selected_priority = ""

    query = "SELECT * FROM tickets"

    conditions = []
    parameters = []

    if selected_status:
        conditions.append("status = ?")
        parameters.append(selected_status)

    if selected_priority:
        conditions.append("priority = ?")
        parameters.append(selected_priority)

    if search:
        conditions.append(
            """
            (
                title LIKE ?
                OR requester_name LIKE ?
                OR category LIKE ?
                OR assigned_analyst LIKE ?
            )
            """
        )

        search_value = f"%{search}%"

        parameters.extend(
            [
                search_value,
                search_value,
                search_value,
                search_value,
            ]
        )

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY created_at DESC"

    connection = get_database_connection()

    tickets = connection.execute(
        query,
        parameters,
    ).fetchall()

    statistics = connection.execute(
        """
        SELECT

            COUNT(*) AS total,

            COALESCE(
                SUM(status = 'Open'),
                0
            ) AS open,

            COALESCE(
                SUM(status = 'In Progress'),
                0
            ) AS in_progress,

            COALESCE(
                SUM(status = 'Pending User'),
                0
            ) AS pending_user,

            COALESCE(
                SUM(status = 'Escalated'),
                0
            ) AS escalated,

            COALESCE(
                SUM(status = 'Resolved'),
                0
            ) AS resolved,

            COALESCE(
                SUM(status = 'Closed'),
                0
            ) AS closed

        FROM tickets
        """
    ).fetchone()

    connection.close()

    return render_template(
        "index.html",
        tickets=tickets,
        statistics=statistics,
        statuses=allowed_statuses,
        priorities=allowed_priorities,
        selected_status=selected_status,
        selected_priority=selected_priority,
        search=search,
    )


# ---------------------------------------------------------
# Create incident
# ---------------------------------------------------------

@app.route("/tickets/new", methods=["GET", "POST"])
def create_ticket():

    if request.method == "POST":

        requester_name = request.form.get(
            "requester_name",
            "",
        ).strip()

        email = request.form.get(
            "email",
            "",
        ).strip()

        title = request.form.get(
            "title",
            "",
        ).strip()

        category = request.form.get(
            "category",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        priority = request.form.get(
            "priority",
            "",
        ).strip()

        fields = [
            requester_name,
            email,
            title,
            category,
            description,
            priority,
        ]

        if not all(fields):

            return render_template(
                "create_ticket.html",
                error="Please complete all fields.",
            )

        if priority not in allowed_priorities:
            abort(400)

        connection = get_database_connection()

        connection.execute(
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
                requester_name,
                email,
                title,
                category,
                description,
                priority,
            ),
        )

        connection.commit()
        connection.close()

        return redirect(
            url_for("home")
        )

    return render_template(
        "create_ticket.html"
    )


# ---------------------------------------------------------
# Incident details / investigation
# ---------------------------------------------------------

@app.route(
    "/tickets/<int:ticket_id>",
    methods=["GET", "POST"],
)
def ticket_detail(ticket_id):

    ticket = get_ticket(ticket_id)

    if request.method == "POST":

        new_status = request.form.get(
            "status",
            "",
        ).strip()

        assigned_analyst = request.form.get(
            "assigned_analyst",
            "",
        ).strip()

        investigation_notes = request.form.get(
            "investigation_notes",
            "",
        ).strip()

        root_cause = request.form.get(
            "root_cause",
            "",
        ).strip()

        resolution = request.form.get(
            "resolution",
            "",
        ).strip()

        if new_status not in allowed_statuses:
            abort(400)

        connection = get_database_connection()

        # Set resolved timestamp when incident is resolved or closed.
        if new_status in ["Resolved", "Closed"]:

            connection.execute(
                """
                UPDATE tickets

                SET
                    status = ?,
                    assigned_analyst = ?,
                    investigation_notes = ?,
                    root_cause = ?,
                    resolution = ?,
                    resolved_at = COALESCE(
                        resolved_at,
                        CURRENT_TIMESTAMP
                    )

                WHERE id = ?
                """,
                (
                    new_status,
                    assigned_analyst,
                    investigation_notes,
                    root_cause,
                    resolution,
                    ticket_id,
                ),
            )

        else:

            connection.execute(
                """
                UPDATE tickets

                SET
                    status = ?,
                    assigned_analyst = ?,
                    investigation_notes = ?,
                    root_cause = ?,
                    resolution = ?,
                    resolved_at = NULL

                WHERE id = ?
                """,
                (
                    new_status,
                    assigned_analyst,
                    investigation_notes,
                    root_cause,
                    resolution,
                    ticket_id,
                ),
            )

        connection.commit()
        connection.close()

        return redirect(
            url_for(
                "ticket_detail",
                ticket_id=ticket_id,
            )
        )

    return render_template(
        "ticket_detail.html",
        ticket=ticket,
        statuses=allowed_statuses,
    )


# ---------------------------------------------------------
# REST API
# ---------------------------------------------------------

@app.route("/api/incidents")
def incident_api():

    connection = get_database_connection()

    incidents = connection.execute(
        """
        SELECT
            id,
            title,
            category,
            priority,
            status,
            assigned_analyst,
            created_at,
            resolved_at

        FROM tickets

        ORDER BY created_at DESC
        """
    ).fetchall()

    connection.close()

    return {
        "incidents": [
            dict(incident)
            for incident in incidents
        ]
    }


# ---------------------------------------------------------
# Application entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)