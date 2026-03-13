from plyer import notification


def send_notification(job):
    """
    Show desktop notification for a job
    job = {
        "title": "...",
        "division": "...",
        "location": "...",
        "link": "..."
    }
    """

    title = f"New Job: {job['title']}"

    message = f"""
Division: {job['division']}
Location: {job['location']}
"""

    notification.notify(
        title=title,
        message=message,
        timeout=10  # seconds
    )