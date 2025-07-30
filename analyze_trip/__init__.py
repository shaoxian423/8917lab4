import logging
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        input_data = req.get_json()
        # 支持单条或多条数据
        trips = input_data if isinstance(input_data, list) else [input_data]

        results = []

        for raw_data in trips:
            trip_data = raw_data.get("ContentData", {})
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

            results.append({
                "vendorID": vendor,
                "tripDistance": distance,
                "passengerCount": passenger_count,
                "paymentType": payment,
                "insights": insights,
                "isInteresting": bool(insights),
                "summary": f"{len(insights)} flags: {', '.join(insights)}" if insights else "Trip normal"
            })

        return func.HttpResponse(
            json.dumps(results),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"❌ Failed to process request: {e}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=400)