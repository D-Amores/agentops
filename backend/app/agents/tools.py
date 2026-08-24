from langchain_core.tools import tool


@tool
def get_current_datetime() -> str:
    """Returns the current date and time in ISO format.

    Use this when the user asks about the current date, time, or 'today'.
    """
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()
