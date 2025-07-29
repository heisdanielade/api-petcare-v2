from datetime import datetime, timezone


def standard_response(status: str, message: str, data: dict = None):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "message": message,
        "data": data,
    }
