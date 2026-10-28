"""
BloodBridge - Blood Donor Matching System
Educational console demo only; not for real medical use.
"""

import json
from pathlib import Path

DATA_FILE = Path(__file__).with_name("bloodbridge_data.json")

GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}

# Simplified red-blood-cell compatibility demonstration.
# Recipient group -> compatible donor groups.
COMPATIBILITY = {
    "O-": {"O-"},
    "O+": {"O-", "O+"},
    "A-": {"O-", "A-"},
    "A+": {"O-", "O+", "A-", "A+"},
    "B-": {"O-", "B-"},
    "B+": {"O-", "O+", "B-", "B+"},
    "AB-": {"O-", "A-", "B-", "AB-"},
    "AB+": {"O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"},
}

donors = []
blood_requests = []


# ------------------------- DATA STORAGE -------------------------

def load_data():
    global donors, blood_requests

    if not DATA_FILE.exists():
        donors, blood_requests = [], []
        return

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object.")

        loaded_donors = data.get("donors", [])
        loaded_requests = data.get("blood_requests", [])

        if not isinstance(loaded_donors, list) or not isinstance(loaded_requests, list):
            raise ValueError("Donors and requests must be lists.")

        for number, donor in enumerate(loaded_donors, start=1):
            donor.setdefault("id", number)
            donor.setdefault("name", "")
            donor.setdefault("age", 18)
            donor.setdefault("blood_group", "O+")
            donor.setdefault("location", "")
            donor.setdefault("available", "yes")
            donor.setdefault("units_available", 1)

        for number, request in enumerate(loaded_requests, start=1):
            request.setdefault("id", number)
            request.setdefault("recipient_name", "")
            request.setdefault("blood_group", "O+")
            request.setdefault("location", "")
            request.setdefault("units", 1)

        donors = loaded_donors
        blood_requests = loaded_requests

    except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
        print(f"WARNING: Could not load saved data: {error}")
        print("Starting with empty records. The saved file has not been overwritten.")
        donors, blood_requests = [], []


def save_data():
    data = {
        "donors": donors,
        "blood_requests": blood_requests,
    }

    temp_file = DATA_FILE.with_suffix(".tmp")

    try:
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        temp_file.replace(DATA_FILE)
        return True

    except OSError as error:
        print(f"ERROR: Could not save data: {error}")
        return False


def next_id(records):
    return max((int(record.get("id", 0)) for record in records), default=0) + 1


# ------------------------- INPUT HELPERS -------------------------

def get_text(prompt):
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("This field cannot be empty.")


def get_integer(prompt, minimum=None, maximum=None):
    while True:
        try:
            value = int(input(prompt).strip())

            if minimum is not None and value < minimum:
                print(f"Enter a number of at least {minimum}.")
            elif maximum is not None and value > maximum:
                print(f"Enter a number no greater than {maximum}.")
            else:
                return value

        except ValueError:
            print("Invalid input. Enter a whole number.")


def get_blood_group(prompt):
    while True:
        group = input(prompt).strip().upper()

        if group in GROUPS:
            return group

        print("Invalid blood group. Use A+, A-, B+, B-, AB+, AB-, O+, or O-.")


def get_yes_no(prompt):
    while True:
        answer = input(prompt).strip().lower()

        if answer in {"yes", "y"}:
            return "yes"

        if answer in {"no", "n"}:
            return "no"

        print("Please enter yes or no.")


def confirm(prompt):
    return get_yes_no(prompt) == "yes"


def pause():
    input("\nPress Enter to return to the menu...")


# ------------------------- DONOR FEATURES -------------------------

def register_donor():
    print("\n--- Register Donor ---")

    donor = {
        "id": next_id(donors),
        "name": get_text("Name: "),
        "age": get_integer("Age (18-100): ", 18, 100),
        "blood_group": get_blood_group("Blood group: "),
        "location": get_text("Location/city: "),
        "available": get_yes_no("Available in this demo? (yes/no): "),
        "units_available": get_integer("Demo units available (minimum 1): ", 1),
    }

    donors.append(donor)

    if save_data():
        print(f"Donor registered successfully. ID: {donor['id']}")
    else:
        donors.remove(donor)


def view_donors(records=None):
    records = donors if records is None else records

    print("\n--- Registered Donors ---")

    if not records:
        print("No donors found.")
        return

    for donor in records:
        print(
            f"\nID: {donor['id']} | Name: {donor['name']}\n"
            f"Age: {donor['age']} | Blood group: {donor['blood_group']}\n"
            f"Location: {donor['location']} | Available: {donor['available']}\n"
            f"Demo units: {donor['units_available']}"
        )


def search_donors():
    print("\n--- Search Donors ---")

    term = get_text("Search by name, blood group, or location: ").casefold()

    results = [
        donor for donor in donors
        if term in str(donor.get("name", "")).casefold()
        or term in str(donor.get("blood_group", "")).casefold()
        or term in str(donor.get("location", "")).casefold()
    ]

    view_donors(results)


def choose_donor():
    if not donors:
        print("No donors registered.")
        return None

    view_donors()
    donor_id = get_integer("Enter donor ID: ", 1)

    donor = next(
        (item for item in donors if item["id"] == donor_id),
        None
    )

    if donor is None:
        print("Donor ID not found.")

    return donor


def update_donor():
    print("\n--- Update Donor ---")

    donor = choose_donor()

    if donor is None:
        return

    print("Press Enter to keep the current value.")

    value = input(f"Name [{donor['name']}]: ").strip()
    if value:
        donor["name"] = value

    value = input(f"Age [{donor['age']}]: ").strip()
    if value:
        while True:
            try:
                age = int(value)

                if 18 <= age <= 100:
                    donor["age"] = age
                    break

                print("Age must be between 18 and 100.")

            except ValueError:
                print("Enter a whole number.")

            value = input("Age again: ").strip()

    value = input(f"Blood group [{donor['blood_group']}]: ").strip().upper()
    if value:
        while value not in GROUPS:
            value = input("Invalid group. Enter a valid group: ").strip().upper()

        donor["blood_group"] = value

    value = input(f"Location [{donor['location']}]: ").strip()
    if value:
        donor["location"] = value

    value = input(f"Available yes/no [{donor['available']}]: ").strip().lower()
    if value:
        while value not in {"yes", "no", "y", "n"}:
            value = input("Enter yes or no: ").strip().lower()

        donor["available"] = "yes" if value in {"yes", "y"} else "no"

    value = input(f"Demo units [{donor['units_available']}]: ").strip()
    if value:
        while True:
            try:
                units = int(value)

                if units >= 1:
                    donor["units_available"] = units
                    break

                print("Units must be at least 1.")

            except ValueError:
                print("Enter a whole number.")

            value = input("Units again: ").strip()

    if save_data():
        print("Donor updated successfully.")


def delete_donor():
    print("\n--- Delete Donor ---")

    donor = choose_donor()

    if donor is None:
        return

    if confirm(f"Delete {donor['name']} (ID {donor['id']})? (yes/no): "):
        donors.remove(donor)

        if save_data():
            print("Donor deleted successfully.")
        else:
            donors.append(donor)

    else:
        print("Deletion cancelled.")


# ------------------------- BLOOD REQUEST FEATURES -------------------------

def create_request():
    print("\n--- Create Blood Request ---")

    request = {
        "id": next_id(blood_requests),
        "recipient_name": get_text("Recipient name: "),
        "blood_group": get_blood_group("Required blood group: "),
        "location": get_text("Location/city: "),
        "units": get_integer("Required demo units (minimum 1): ", 1),
    }

    blood_requests.append(request)

    if save_data():
        print(f"Request created successfully. ID: {request['id']}")
    else:
        blood_requests.remove(request)


def view_requests(records=None):
    records = blood_requests if records is None else records

    print("\n--- Blood Requests ---")

    if not records:
        print("No requests found.")
        return

    for request in records:
        print(
            f"\nID: {request['id']} | Recipient: {request['recipient_name']}\n"
            f"Required group: {request['blood_group']} | Location: {request['location']}\n"
            f"Demo units requested: {request['units']}"
        )


def delete_request():
    print("\n--- Delete Blood Request ---")

    if not blood_requests:
        print("No requests available.")
        return

    view_requests()
    request_id = get_integer("Request ID to delete: ", 1)

    request = next(
        (item for item in blood_requests if item["id"] == request_id),
        None
    )

    if request is None:
        print("Request ID not found.")
        return

    if confirm(f"Delete request #{request_id}? (yes/no): "):
        blood_requests.remove(request)

        if save_data():
            print("Request deleted successfully.")
        else:
            blood_requests.append(request)

    else:
        print("Deletion cancelled.")


# ------------------------- MATCHING AND STATISTICS -------------------------

def is_compatible(donor_group, recipient_group):
    return donor_group in COMPATIBILITY.get(recipient_group, set())


def find_matches():
    print("\n--- Find Matching Donors ---")

    if not blood_requests:
        print("Create a blood request first.")
        return

    view_requests()
    request_id = get_integer("Request ID to match: ", 1)

    request = next(
        (item for item in blood_requests if item["id"] == request_id),
        None
    )

    if request is None:
        print("Request ID not found.")
        return

    matches = []

    for donor in donors:
        if str(donor.get("available", "")).strip().lower() != "yes":
            continue

        if int(donor.get("units_available", 0)) < int(request["units"]):
            continue

        donor_group = str(donor.get("blood_group", "")).strip().upper()
        recipient_group = str(request.get("blood_group", "")).strip().upper()

        if is_compatible(donor_group, recipient_group):
            matches.append(donor)

    matches.sort(
        key=lambda donor: (
            str(donor.get("location", "")).strip().casefold()
            != str(request.get("location", "")).strip().casefold(),
            str(donor.get("name", "")).casefold()
        )
    )

    print(f"\nMatching donors for request #{request_id}:")

    if not matches:
        print("No donors matched all demo criteria.")
        return

    for number, donor in enumerate(matches, start=1):
        same_location = (
            donor["location"].strip().casefold()
            == request["location"].strip().casefold()
        )

        priority = "Same location" if same_location else "Other location"

        print(
            f"\n{number}. {donor['name']} (Donor ID: {donor['id']})\n"
            f"Blood group: {donor['blood_group']} | Location: {donor['location']}\n"
            f"Demo units: {donor['units_available']} | Priority: {priority}"
        )


def show_statistics():
    print("\n--- BloodBridge Statistics ---")

    available = sum(
        1 for donor in donors
        if str(donor.get("available", "")).lower() == "yes"
    )

    print(f"Total donors: {len(donors)}")
    print(f"Available donors: {available}")
    print(f"Unavailable donors: {len(donors) - available}")
    print(f"Total blood requests: {len(blood_requests)}")

    print("\nDonors by blood group:")

    for group in sorted(GROUPS):
        count = sum(
            1 for donor in donors
            if donor.get("blood_group") == group
        )
        print(f"  {group}: {count}")


# ------------------------- MAIN MENU -------------------------

def main():
    load_data()

    print("\nWelcome to BloodBridge!")
    print("Educational demonstration only — not for real medical use.")

    actions = {
        "1": ("Register donor", register_donor),
        "2": ("View donors", view_donors),
        "3": ("Search donors", search_donors),
        "4": ("Update donor", update_donor),
        "5": ("Delete donor", delete_donor),
        "6": ("Create blood request", create_request),
        "7": ("View blood requests", view_requests),
        "8": ("Delete blood request", delete_request),
        "9": ("Find matching donors", find_matches),
        "10": ("View statistics", show_statistics),
    }

    while True:
        print("\n========== BLOODBRIDGE ==========")

        for key, (label, _) in actions.items():
            print(f"{key}. {label}")

        print("11. Exit")

        choice = input("Choose an option (1-11): ").strip()

        if choice == "11":
            print("Thank you for using BloodBridge!")
            break

        if choice not in actions:
            print("Invalid choice. Enter a number from 1 to 11.")
            continue

        try:
            actions[choice][1]()
        except (KeyError, TypeError, ValueError) as error:
            print(f"Action could not be completed: {error}")

        pause()


if __name__ == "__main__":
    main()