# BloodBridge
# Blood Donor Matching System


# Stores all registered donors
donors = []

# Stores all blood requests
blood_requests = []


# ----------------------------------------
# Register a new donor
# ----------------------------------------

def register_donor():
    print("\n--- Donor Registration ---")

    name = input("Enter donor name: ")
    age = int(input("Enter age: "))
    blood_group = input("Enter blood group: ").upper()
    location = input("Enter location: ")
    available = input("Is the donor available? (yes/no): ").lower()

    donor = {
        "name": name,
        "age": age,
        "blood_group": blood_group,
        "location": location,
        "available": available
    }

    donors.append(donor)

    print("\nDonor registered successfully!")


# ----------------------------------------
# View all registered donors
# ----------------------------------------

def view_donors():
    print("\n--- Registered Donors ---")

    if len(donors) == 0:
        print("No donors registered yet.")
        return

    for i, donor in enumerate(donors, start=1):

        print(f"\nDonor {i}")
        print(f"Name        : {donor['name']}")
        print(f"Age         : {donor['age']}")
        print(f"Blood Group : {donor['blood_group']}")
        print(f"Location    : {donor['location']}")
        print(f"Available   : {donor['available']}")


# ----------------------------------------
# Create a blood request
# ----------------------------------------

def create_request():
    print("\n--- Blood Request ---")

    recipient_name = input("Enter recipient name: ")
    blood_group = input("Enter required blood group: ").upper()
    location = input("Enter location: ")
    units = int(input("Enter required units: "))

    request = {
        "recipient_name": recipient_name,
        "blood_group": blood_group,
        "location": location,
        "units": units
    }

    blood_requests.append(request)

    print("\nBlood request created successfully!")


# ----------------------------------------
# View blood requests
# ----------------------------------------

def view_requests():
    print("\n--- Blood Requests ---")

    if len(blood_requests) == 0:
        print("No blood requests yet.")
        return

    for i, request in enumerate(blood_requests, start=1):

        print(f"\nRequest {i}")
        print(f"Recipient   : {request['recipient_name']}")
        print(f"Blood Group : {request['blood_group']}")
        print(f"Location    : {request['location']}")
        print(f"Units       : {request['units']}")


# ----------------------------------------
# Check blood compatibility
# ----------------------------------------

def is_compatible(donor_group, recipient_group):

    compatibility = {
        "O-": ["O-"],
        "O+": ["O-", "O+"],
        "A-": ["O-", "A-"],
        "A+": ["O-", "O+", "A-", "A+"],
        "B-": ["O-", "B-"],
        "B+": ["O-", "O+", "B-", "B+"],
        "AB-": ["O-", "A-", "B-", "AB-"],
        "AB+": [
            "O-", "O+", "A-", "A+",
            "B-", "B+", "AB-", "AB+"
        ]
    }

    return donor_group in compatibility[recipient_group]


# ----------------------------------------
# Find matching donors
# ----------------------------------------

def find_matches():

    print("\n--- Find Matching Donors ---")

    if len(blood_requests) == 0:
        print("No blood requests available.")
        return

    print("\nSelect a blood request:")

    for i, request in enumerate(blood_requests, start=1):
        print(
            f"{i}. {request['recipient_name']} - "
            f"{request['blood_group']} - "
            f"{request['location']}"
        )

    choice = int(input("\nEnter request number: "))

    if choice < 1 or choice > len(blood_requests):
        print("Invalid request number.")
        return

    request = blood_requests[choice - 1]

    print("\nSearching for compatible donors...")

    matches = []

    for donor in donors:

        if donor["available"] != "yes":
            continue

        if is_compatible(
            donor["blood_group"],
            request["blood_group"]
        ):
            matches.append(donor)

    if len(matches) == 0:
        print("\nNo compatible donors found.")
        return

    print("\n--- Matching Donors ---")

    for i, donor in enumerate(matches, start=1):

        print(f"\nMatch {i}")
        print(f"Name        : {donor['name']}")
        print(f"Blood Group : {donor['blood_group']}")
        print(f"Location    : {donor['location']}")
        print(f"Available   : {donor['available']}")


# ----------------------------------------
# Main menu
# ----------------------------------------

def main():

    while True:

        print("\n==============================")
        print("        BLOODBRIDGE")
        print(" Blood Donor Matching System")
        print("==============================")

        print("\n1. Register Donor")
        print("2. View Donors")
        print("3. Create Blood Request")
        print("4. View Blood Requests")
        print("5. Find Matching Donors")
        print("6. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            register_donor()

        elif choice == "2":
            view_donors()

        elif choice == "3":
            create_request()

        elif choice == "4":
            view_requests()

        elif choice == "5":
            find_matches()

        elif choice == "6":
            print("\nThank you for using BloodBridge!")
            break

        else:
            print("\nInvalid choice. Please try again.")


# Start the program
main()