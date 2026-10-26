import json
import time
import requests

# 1. SIMULATED REST API DATA
pages = {
    None: {
        "items": [
            {
                "deviceId": 101,
                "hostname": "SW1",
                "managementIp": "10.10.10.11",
                "deviceType": "switch",
                "reachabilityStatus": "Reachable",
                "environment": "production",
                "healthScore": 95
            },
            {
                "deviceId": 102,
                "hostname": "SW2",
                "managementIp": "10.10.10.12",
                "deviceType": "switch",
                "reachabilityStatus": "Unreachable",
                "environment": "production",
                "healthScore": 40
            },
            {
                "deviceId": 103,
                "hostname": "R1",
                "managementIp": "10.10.10.1",
                "deviceType": "router",
                "reachabilityStatus": "Reachable",
                "environment": "production",
                "healthScore": 80
            }
        ],
        "next_cursor": "page2"
    },

    "page2": {
        "items": [
            {
                "deviceId": 104,
                "hostname": "SW3",
                "managementIp": "10.10.10.13",
                "deviceType": "switch",
                "reachabilityStatus": "Unreachable",
                "environment": "development",
                "healthScore": 25
            },
            {
                "deviceId": 102,
                "hostname": "SW2",
                "managementIp": "10.10.10.12",
                "deviceType": "switch",
                "reachabilityStatus": "Unreachable",
                "environment": "production",
                "healthScore": 40
            },
            {
                "deviceId": 105,
                "hostname": "R2",
                "managementIp": "10.10.10.2",
                "deviceType": "router",
                "reachabilityStatus": "Unreachable",
                "environment": "production",
                "healthScore": 20
            }
        ],
        "next_cursor": "page3"
    },

    "page3": {
        "items": [
            {
                "deviceId": 106,
                "hostname": "",
                "managementIp": "10.10.10.14",
                "deviceType": "switch",
                "reachabilityStatus": "Reachable",
                "environment": "production",
                "healthScore": 70
            },
            {
                "deviceId": 107,
                "hostname": "SW4",
                "managementIp": "10.10.10.15",
                "deviceType": "firewall",
                "reachabilityStatus": "Reachable",
                "environment": "production",
                "healthScore": 60
            },
            {
                "deviceId": 108,
                "hostname": "SW1",
                "managementIp": "10.10.20.11",
                "deviceType": "switch",
                "reachabilityStatus": "Reachable",
                "environment": "production",
                "healthScore": 90
            }
        ],
        "next_cursor": None
    }
}

# 2. SIMULATED API BEHAVIOR
api_attempts = {}

def simulate_api(cursor=None):

    if cursor not in api_attempts:
        api_attempts[cursor] = 0

    api_attempts[cursor] += 1
    attempt = api_attempts[cursor]

    # Simulate temporary API failure on first attempt
    if attempt == 1:
        return {
            "status_code": 503,
            "data": {
                "message": "Service temporarily unavailable"
            },
            "headers": {}
        }

    # Simulate rate limiting on second attempt
    if attempt == 2:

        return {
            "status_code": 429,
            "data": {
                "message": "Rate limit exceeded"
            },
            "headers": {
                "Retry-After": "1"
            }
        }

    # Successful API response
    return {
        "status_code": 200,
        "data": pages.get(cursor),
        "headers": {}
    }

# 3. SESSION
session = requests.Session()

session.headers.update({
    "Accept": "application/json",
    "X-Automation-Tool": "NetworkAutomation"
})

# 4. RETRY DECISION
def should_retry(status_code):

    retryable_status_codes = [429, 500, 502, 503, 504]

    if status_code in retryable_status_codes:
        return True

    return False

# 5. EXPONENTIAL BACKOFF
def calculate_backoff(attempt, base_delay=2):

    return base_delay * (2 ** (attempt - 1))

max_retries = 3

# 6. RETRY DELAY
def get_retry_delay(response, attempt):

    retry_after = response.get("headers", {}).get("Retry-After")

    if retry_after:

        try:
            return int(retry_after)

        except ValueError:
            pass

    return calculate_backoff(attempt)

# 7. API REQUEST WITH RETRY
def api_request(cursor=None, max_retries=3):

    for attempt in range(1, max_retries + 2):

        print(f"\nAPI attempt {attempt} | Cursor: {cursor}")

        try:

            response = simulate_api(cursor)

        except Exception as error:

            print(f"API request failed: {error}")
            return None

        status_code = response["status_code"]

        print(f"HTTP status: {status_code}")

        # Successful response
        if 200 <= status_code < 300:
            print("Request successful")
            return response

        # Retryable response
        if should_retry(status_code):

            if attempt > max_retries:
                print("Maximum retry limit reached")
                return response

            delay = get_retry_delay(response, attempt)

            print(
                f"Retryable error detected. "
                f"Waiting {delay} seconds before retry..."
            )

            time.sleep(delay)
            continue

        # Non-retryable response
        print("Non-retryable Http error", status_code)
        return response

    return None

# 8. API RESPONSE VALIDATION
def validate_device_response(data):

    if not isinstance(data, dict):
        print("Validation failed: Response is not a dictionary")
        return False

    if "items" not in data:
        print("Validation failed: 'items' field is missing")
        return False


    if not isinstance(data["items"], list):
        print("Validation failed: 'items' is not a list")
        return False

    print ("Validation Successful")
    return True

# 9. GET ALL DEVICES USING CURSOR PAGINATION
def get_all_devices(max_pages=100):
    all_devices = []
    cursor = None
    page_count = 0

    while page_count < max_pages:
        page_count += 1
        print(f"\nFetching page {page_count}...")

        response = api_request(
            cursor=cursor,
            max_retries=3
        )

        if response is None:
            print("No API response received.")
            break

        status_code = response["status_code"]

        if not (200 <= status_code < 300):

            print(
                "Stopping pagination because "
                "API request failed."
            )

            break

        data = response["data"]

        if not validate_device_response(data):
            print("Stopping pagination because API response is invalid.")
            break

        print(f"Devices received: {len(data['items'])}" )

        all_devices.extend(data["items"])
        cursor = data.get("next_cursor")
        print("Next cursor:", cursor)

        if not cursor:
            print("\nPagination complete.")
            break

    else:
        print("\nMaximum page limit reached.")

    return(all_devices)

# 10. VALIDATE INDIVIDUAL DEVICE
def validate_device(device):

    required_fields = [
        "hostname",
        "managementIp",
        "deviceType",
        "reachabilityStatus",
        "environment",
        "healthScore"
]

    for field in required_fields:

        if field not in device:
            print(f"Validation failed: '{field}' is missing")
            return False

        if not device[field]:
            print(f"Validation failed: '{field}' is empty")
            return False

    valid_types = ["switch", "router"]
    valid_statuses = ["Reachable", "Unreachable"]

    if device["deviceType"] not in valid_types:
        print(
            f"Validation failed: Invalid device type "
            f"'{device['deviceType']}'"
        )
        return False

    if device["reachabilityStatus"] not in valid_statuses:
        print(
            f"Validation failed: Invalid status "
            f"'{device['reachabilityStatus']}'"
        )
        return False

    return True

# 11. VALIDATE ALL DEVICES
def validate_devices(devices):

    valid_devices = []
    invalid_devices = []

    for device in devices:

        if validate_device(device):
            valid_devices.append(device)
        else:
            invalid_devices.append(device)

    return valid_devices, invalid_devices

# 12. TRANSFORM API DATA
def transform_devices(valid_devices):

    transformed_devices = []

    for device in valid_devices:

        transformed_device = {
            "id": device["deviceId"],
            "hostname": device["hostname"],
            "ip": device["managementIp"],
            "type": device["deviceType"].lower(),
            "status": device["reachabilityStatus"].lower(),
            "environment": device["environment"],
            "health": device["healthScore"]
        }

        transformed_devices.append(transformed_device)

    return transformed_devices

# 13. REMOVE DUPLICATES AND DETECT CONFLICTS
def remove_duplicates(devices):

    unique_devices = {}
    duplicates = []
    conflicts = []

    for device in devices:

        hostname = device["hostname"]
        ip = device["ip"]

        if hostname not in unique_devices:
            # First time seeing this hostname
            # Add device to unique_devices
            unique_devices[hostname] = device
            pass


        else:
            # Hostname already exists
            existing_device = unique_devices[hostname]

            if existing_device["ip"] == ip:

                # Same hostname + same IP
                # Add to duplicates
                duplicates.append(device)

            else:

                # Same hostname + different IP
                # Add to conflicts
                conflicts.append(device)

    return (list(unique_devices.values()), conflicts, duplicates)

# 14. FILTER DEVICES
def filter_devices(devices, status=None, environment=None):

    filtered_devices = []

    for device in devices:

        if status is not None:
            if device["status"] != status:
                continue

        if environment is not None:
            if device["environment"] != environment:
                continue

        filtered_devices.append(device)

    return filtered_devices

# 15. SORT BY HEALTH
def sort_by_health(devices):

    sorted_devices = sorted(
        devices,
        key=lambda device: device["health"]
    )

    return sorted_devices

# 16. GENERATE FINAL REPORT
def generate_report(
    all_devices,
    valid_devices,
    invalid_devices,
    unique_devices,
    duplicates,
    conflicts,
    sorted_devices
):

    report = {
        "summary": {
        "total_records": len(all_devices),
        "valid_records": len(valid_devices),
        "invalid_records": len(invalid_devices),
        "unique_devices": len(unique_devices),
        "duplicate_count": len(duplicates),
        "conflict_count": len(conflicts),
        "reachable": 0,
        "unreachable": 0,
        "switches": 0,
        "routers": 0,
        "production": 0,
        "development": 0
        },
        "remediation_required": sorted_devices,
        "invalid_devices": invalid_devices,
        "duplicate_devices": duplicates,
        "conflict_devices": conflicts
    }

    for device in unique_devices:

        if device["status"] == "reachable":
            report["summary"]["reachable"] += 1

        elif device["status"] == "unreachable":
            report["summary"]["unreachable"] += 1

        if device["type"] == "switch":
            report["summary"]["switches"] += 1

        elif device["type"] == "router":
            report["summary"]["routers"] += 1

        if device["environment"] == "production":
            report["summary"]["production"] += 1

        elif device["environment"] == "development":
            report["summary"]["development"] += 1

    return report

# ============================================================
# 17. MAIN AUTOMATION WORKFLOW
# ============================================================
print("\n")
print("==============================================")
print(" ENTERPRISE DEVICE HEALTH & INVENTORY TOOL")
print("==============================================")

print("\n[1] Collecting devices from API...")
devices = get_all_devices(max_pages=100)
print(f"\nTotal raw records collected: {len(devices)}")

print("\n[2] Validating device records...")
valid_devices, invalid_devices = validate_devices(devices)
print(f"Valid records: {len(valid_devices)}")
print(f"Invalid records: {len(invalid_devices)}")

print("\n[3] Transforming API data...")
transformed_devices =  transform_devices(valid_devices)
print(f"Transformed records: {len(transformed_devices)}")

print("\n[4] Detecting duplicates and conflicts...")
unique_devices, conflicts, duplicates = remove_duplicates(transformed_devices)
print(f"Unique devices: {len(unique_devices)}")
print("Duplicates:", len(duplicates))
print(f"Conflicts: {len(conflicts)}")

print("\n[5] Filtering production unreachable devices...")
filtered_devices = filter_devices(unique_devices, status="unreachable", environment="production")
print(f"Devices requiring attention: {len(filtered_devices)}")

print("\n[6] Sorting devices by health...")
sorted_devices = sort_by_health(filtered_devices)
for device in sorted_devices:
    print(f"{device['hostname']} -> Health: {device['health']}")

print("\n[7] Generating final report...")
report = generate_report(
    devices,
    valid_devices,
    invalid_devices,
    unique_devices,
    duplicates,
    conflicts,
    sorted_devices
)

print("\n===============================")
print("Final Network Device Report")
print("=================================")
print("Total Records :", report["summary"]["total_records"])
print("Valid Records:", report["summary"]["valid_records"])
print("Invalid Records:", report["summary"]["invalid_records"])
print("Unique Devices:", report["summary"]["unique_devices"])
print("Duplicates:", report["summary"]["duplicate_count"])
print("Conflicts:", report["summary"]["conflict_count"])
print("Reachable     :", report["summary"]["reachable"])
print("Unreachable   :", report["summary"]["unreachable"])
print("Switches      :", report["summary"]["switches"])
print("Routers       :", report["summary"]["routers"])
print("Production    :", report["summary"]["production"])
print("Development   :", report["summary"]["development"])

print("\n[8] Saving JSON report...")

with open("device_health_report.json", "w") as file:
    json.dump(report, file, indent=4)

print(
    "Report saved as "
    "device_health_report.json"
)

print("\nAutomation completed successfully.")
