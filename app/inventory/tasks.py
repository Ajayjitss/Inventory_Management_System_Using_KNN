# # app/inventory/tasks.py

# import threading
# import schedule
# import time
# from datetime import datetime
# from app.inventory.utils import update_inventory_predictions

# def run_daily_task():
#     """
#     Function to run daily background tasks at a specific time.
#     """
#     print("Starting background task...")

#     # Schedule the task to run at 12:00 AM every day (you can adjust it for testing)
#     schedule.every().minute.do(update_inventory_predictions)  # Run task every minute for testing purposes

#     while True:
#         try:
#             # Run all the scheduled tasks
#             schedule.run_pending()
#             print("Scheduled task running...")

#             # Sleep for 60 seconds between each check (not 24 hours for testing)
#             time.sleep(60)  # Sleep for 1 minute
#         except Exception as e:
#             print(f"Error in background task: {e}")
#             time.sleep(60)  # In case of error, wait 1 minute before retrying


# def start_background_task(app):
#     """
#     Start the background task in a separate thread so it doesn't block the main Flask process.
#     """
#     with app.app_context():
#         thread = threading.Thread(target=run_daily_task)
#         thread.daemon = True  # Ensures thread ends when app ends
#         thread.start()
