import azure.functions as func
import logging
import json
from typing import List

def main(events: List[func.EventHubEvent]):
    for event in events:
        try:
            raw_data = json.loads(event.get_body().decode('utf-8'))
            trip_data = raw_data.get("ContentData")
            if not isinstance(trip_data, dict):
                logging.warning("❌ ContentData must be a JSON object")
                continue

            vendor = trip_data.get("vendorID")
            distance = float(trip_data.get("tripDistance", 0))
            passenger_count = int(trip_data.get("passengerCount", 0))
            payment = str(trip_data.get("paymentType", ""))

            insights = []
            if distance > 10:
                insights.append("LongTrip")
            if passenger_count > 4:
                insights.append("GroupRide")
            if payment == "2":
                insights.append("CashPayment")
            if payment == "2" and distance < 1:
                insights.append("SuspiciousVendorActivity")

            logging.info(f"✅ Trip analyzed for vendor {vendor}: {insights or 'Trip normal'}")

        except Exception as e:
            logging.error(f"❌ Failed to process event: {e}")