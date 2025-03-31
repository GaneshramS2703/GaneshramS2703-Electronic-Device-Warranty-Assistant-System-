from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
import json
import requests


def my_view(request):
    response = JsonResponse({"message": "Hello, world!"})
    response["Cross-Origin-Opener-Policy"] = "unsafe-none"  # Allow cross-origin access
    return response


TRADEIN_PRICES = {
    "iphone 13": {"new": 700, "good": 600, "fair": 450, "poor": 300},  # Lowercase keys
    "samsung galaxy s21": {"new": 650, "good": 550, "fair": 400, "poor": 250},
    "macbook pro 2021": {"new": 1500, "good": 1300, "fair": 1000, "poor": 600},
    "google pixel 6": {"new": 500, "good": 400, "fair": 300, "poor": 150},
}

# Homepage
def home(request):
    return render(request, "warranty_api/index.html")

# Warranty Calculator Page
def warranty(request):
    return render(request, "warranty_api/warranty.html")

# Repair Center Locator Page
def repair(request):
    return render(request, "warranty_api/repair.html")

# Trade-In Value Page
def tradein(request):
    return render(request, "warranty_api/tradein.html")

# API for Warranty Calculation

@csrf_exempt
def calculate_warranty(request):
    # ✅ Handle CORS Preflight (OPTIONS request)
    if request.method == "OPTIONS":
        response = JsonResponse({"message": "CORS preflight successful"}, status=200)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "*"
        return response

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            purchase_date_str = data.get('purchase_date')
            warranty_duration = data.get('warranty_duration')

            if not purchase_date_str or warranty_duration is None:
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            # Convert date formats
            try:
                purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d')
            except ValueError:
                try:
                    purchase_date = datetime.strptime(purchase_date_str, '%d-%m-%Y')
                except ValueError:
                    return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD or DD-MM-YYYY'}, status=400)

            expiration_date = purchase_date + timedelta(days=30 * int(warranty_duration))

            response_data = {
                'purchase_date': purchase_date.strftime('%d-%m-%Y'),
                'warranty_duration_months': warranty_duration,
                'expiration_date': expiration_date.strftime('%d-%m-%Y')
            }

            response = JsonResponse(response_data)
            response["Access-Control-Allow-Origin"] = "*"  # ✅ Explicitly allow all origins
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "*"
            return response

        except Exception as e:
            return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)

    return JsonResponse({'error': 'POST request required.'}, status=400)


# API for Trade-In Value Estimator
@csrf_exempt
def tradein_value(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            device_model = data.get("device_model", "").strip().lower()
            condition = data.get("condition", "").strip().lower()

            if not device_model or not condition:
                response = JsonResponse({"error": "Missing device_model or condition"}, status=400)
            else:
                matched_model = TRADEIN_PRICES.get(device_model)
                if not matched_model:
                    response = JsonResponse({"error": "Device model not found"}, status=404)
                elif condition not in matched_model:
                    response = JsonResponse({"error": "Invalid condition. Choose from: new, good, fair, poor"}, status=404)
                else:
                    estimated_value = matched_model[condition]
                    response = JsonResponse({
                        "device": device_model,
                        "condition": condition,
                        "estimated_value": estimated_value
                    })

            # ✅ Add CORS headers explicitly
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "*"
            return response

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        except Exception as e:
            return JsonResponse({"error": "Internal Server Error", "details": str(e)}, status=500)

    elif request.method == "OPTIONS":
        # ✅ Handle CORS preflight request
        response = JsonResponse({"message": "CORS preflight successful"}, status=200)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "*"
        return response

    return JsonResponse({"error": "POST request required"}, status=400)
    
    
@csrf_exempt
def repair_locator(request):
    if request.method == "GET":
        location = request.GET.get("location", "")

        # Classmate's API URL
        api_url = "https://wsl1cfbhud.execute-api.us-east-1.amazonaws.com/default/GetServiceCentersAPI"
        
        if location:
            api_url += f"?location={location}"

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()

                # ✅ Ensure valid data format & filter needed fields
                formatted_data = []
                for center in data:
                    formatted_data.append({
                        "name": center.get("name", "Unknown"),
                        "address": center.get("address", "No address available"),
                        "type": center.get("type", "General Service")
                    })

                # ✅ Return formatted response
                return JsonResponse({"centers": formatted_data}, safe=False)

            else:
                return JsonResponse({"error": "Failed to fetch repair centers", "status_code": response.status_code}, status=500)
        except requests.RequestException as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "GET request required"}, status=400)
