import datetime
import math
import json

class ParkedCar:
    def __init__(self, license_plate, check_in=None):
        # Initializes a ParkedCar instance with a license plate and an optional check-in time.
        self.license_plate = license_plate
        self.check_in = check_in if check_in else datetime.datetime.now()  # Sets current time if no check-in time is provided.


class CarParkingMachine:
    parked_cars_registry = {}  # Class variable to keep track of all parked cars across all instances.

    def __init__(self, id="", capacity=10, hourly_rate=2.50):
        # Initializes a CarParkingMachine instance with an id, capacity, and hourly rate.
        self.id = id
        self.capacity = capacity
        self.hourly_rate = hourly_rate
        self.parked_cars = {}  # Stores parked cars in this specific machine.
        self.logger = CarParkingLogger(machine_id=self.id)  # Logger instance for this machine.
        self.load_state()  # Load the previous state of parked cars if available.

    def load_state(self):
        # Loads the parking machine state from a file to restore previous session's data.
        try:
            with open(f'{self.id}_state.json', 'r') as f:
                loadedjson = json.load(f)
                for car_data in loadedjson:
                    license_plate = car_data['license_plate']
                    check_in_time = datetime.datetime.strptime(car_data['check_in'], '%m-%d-%Y %H:%M:%S')
                    self.parked_cars[license_plate] = ParkedCar(license_plate, check_in_time)
        except FileNotFoundError:
            pass  # If file not found, do nothing (no previous state to load).

    def save_state(self):
        # Saves the current state of parked cars to a file for persistence.
        savedloginfo = [{'license_plate': license_plate, 'check_in': car.check_in.strftime('%m-%d-%Y %H:%M:%S')}
                        for license_plate, car in self.parked_cars.items()]
        with open(f'{self.id}_state.json', 'w') as f:
            json.dump(savedloginfo, f)

    def print_parked_cars_from_file(self):
        # Prints parked cars information from a file. (Not used in main function)
        try:
            with open(f'{self.id}.json', 'r') as f:
                writtenjson = json.load(f)
                print("Parked Cars:")
                for car_data in writtenjson:
                    print(f"License Plate: {car_data['license_plate']}, Check-in: {car_data['check_in']}")
        except FileNotFoundError:
            print("No parked cars recorded.")

    def check_in(self, license_plate, check_in=None):
        # Registers a car for parking if there's space and the car isn't already parked.
        if len(self.parked_cars) >= self.capacity:
            return False

        if license_plate in CarParkingMachine.parked_cars_registry:
            return False  # Car is already parked in another machine.

        self.parked_cars[license_plate] = ParkedCar(license_plate, check_in)  # Add car to this machine.
        CarParkingMachine.parked_cars_registry[license_plate] = self.id  # Register car in the global registry.
        self.logger.log_check_in(license_plate)  # Log the check-in event.
        self.save_state()  # Save the updated state.
        return True

    def check_out(self, license_plate):
        # Checks out a car from the parking, calculates the fee, and updates the state.
        if license_plate in self.parked_cars:
            parking_fee = self.get_parking_fee(license_plate)
            del self.parked_cars[license_plate]  # Remove car from this machine.
            
            if license_plate in CarParkingMachine.parked_cars_registry:
                del CarParkingMachine.parked_cars_registry[license_plate]  # Remove car from global registry.

            self.logger.log_check_out(license_plate, parking_fee)  # Log the check-out event.
            self.save_state()  # Save the updated state.
            return parking_fee
        return None

    def get_parking_fee(self, license_plate):
        # Calculates the parking fee for a car based on its parked duration.
        if license_plate in self.parked_cars:
            parked_car = self.parked_cars[license_plate]
            parking_duration = datetime.datetime.now() - parked_car.check_in
            parking_hours = math.ceil(parking_duration.total_seconds() / 3600)
            parking_hours = min(parking_hours, 24)  # Limit to a maximum of 24 hours.
            return parking_hours * self.hourly_rate
        return None


class CarParkingLogger:
    def __init__(self, machine_id):
        # Initializes a logger for a specific CarParkingMachine.
        self.id = machine_id
        self.log_entries = []  # Stores log entries.

    def log_check_in(self, license_plate):
        # Logs a check-in event for a car.
        log_message = (
            f"{datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')};"
            f"cpm_name={self.id};license_plate={license_plate};action=check-in"
        )
        self._write_to_log(log_message)

    def log_check_out(self, license_plate, parking_fee):
        # Logs a check-out event for a car and the parking fee.
        log_message = (
            f"{datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')};"
            f"cpm_name={self.id};license_plate={license_plate};"
            f"action=check-out;parking_fee={int(parking_fee)}"
        )
        self._write_to_log(log_message)

    def _write_to_log(self, log_message):
        # Writes a log message to the log file and stores it in the log_entries list.
        with open('carparklog.txt', 'a') as log_file:
            log_file.write(log_message + '\n')
            self.log_entries.append(log_message)

    def get_machine_fee_by_day(self, car_parking_machine_id, search_date):
        # Calculates the total fee collected by a specific machine on a specific day.
        car_parking_machine_id = car_parking_machine_id.lower()
        search_date = datetime.datetime.strptime(search_date, '%d-%m-%Y').date()
        total_fee = 0
        for entry in self.log_entries:
            entry_components = entry.split(';')
            if len(entry_components) >= 6:
                entry_machine_id = entry_components[1].split('=')[1].lower()
                entry_date = datetime.datetime.strptime(entry_components[0], '%m-%d-%Y %H:%M:%S').date()
                if entry_date == search_date and entry_machine_id == car_parking_machine_id:
                    total_fee += int(entry_components[5].split('=')[1])
        return round(total_fee, 2)

    def get_total_car_fee(self, license_plate):
        # Calculates the total fee paid by a specific car across all its parking events.
        total_fee = 0
        for entry in self.log_entries:
            entry_components = entry.split(';')
            if len(entry_components) >= 6:
                if license_plate.lower() == entry_components[2].split('=')[1].lower():
                    total_fee += int(entry_components[5].split('=')[1])
        return round(total_fee, 2)


def print_menu():
    # Prints the main menu options to the console.
    print("[I] Check-in car by license plate")
    print("[O] Check-out car by license plate")
    print("[Q] Quit program")


def main():
    # Main function to run the car parking program.
    cartolog = CarParkingMachine(id="North")  # Initialize a CarParkingMachine instance.
    while True:
        print_menu()
        choice = input("Enter your choice: ")
        if choice.upper() == "I":
            license_plate = input("Enter the license plate: ")
            if cartolog.check_in(license_plate):
                print("License registered")
            else:
                print("Capacity reached or car already parked")
        elif choice.upper() == "O":
            license_plate = input("Enter the license plate: ")
            fee = cartolog.check_out(license_plate)
            if fee is not None:
                print(f"Parking fee: {fee:.2f} EUR")
            else:
                print("Car with this license plate is not found.")
        elif choice.upper() == "Q":
            break  # Exit the loop and end the program.
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()  # Run the main function when the script is executed.
