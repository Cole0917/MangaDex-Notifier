from plyer import notification

# Defines a function to send a desktop notification with the manga title and chapter number.
def send(title, chapter):

    notification.notify(
        title="New Manga Chapter",
        message=f"{title} - Chapter {chapter}",
        timeout=10
    )