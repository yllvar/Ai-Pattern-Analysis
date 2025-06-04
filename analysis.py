import schedule
import time
from utils import fetch_historical_data, calculate_indicators, plot_chart

# Function to capture and save the chart
def capture_chart():
    df = fetch_historical_data()
    df = calculate_indicators(df)
    image_path = plot_chart(df)
    print(f"Chart analysis completed and saved as {image_path}")

# Schedule the function to run every 10 minutes
schedule.every(10).minutes.do(capture_chart)

# Run the scheduler
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
