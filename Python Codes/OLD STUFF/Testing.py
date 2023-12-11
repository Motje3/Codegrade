from datetime import datetime
import math


class ParkedCar:
    def __init__(self, license_plate, check_in):
        self.license_plate = license_plate
        self.check_in = check_in


class CarParkingLogger:
    def __init__(self, id):
        self.identifier = id

    def restore_state(self):
        try:
            with open("carparklog.txt", 'r') as file:
                # Lees alle lijnen en stop ze in een lijst
                lines = file.readlines()
                matching_lines = list()
                for line in range(len(lines)):
                    if "check-in" in lines[line]:

                        # Loop door alle lines
                        valid_plates = list()
                        for line in matching_lines:
                            # Splits line tot individuele delen
                            all_items = line.split(";")
                            date = all_items[0]

                            print(date)

                            # Loop door alle individuele delen van de line uit carparklog.txt
                            for item in all_items:
                                if "license_plate" in item:
                                    license_plate = item.replace(
                                        'license_plate=', '')

                                    # als de line een check out is wordt de nummerplaat verwijderd,
                                    # zoniet toegevoegd tot de list die de valide nummerplaten houdt
                                    if "check-out" in line:
                                        if license_plate in valid_plates:
                                            valid_plates.remove(license_plate)
                                    elif "check-in" in line:
                                        valid_plates.append(
                                            [license_plate, date])

                        # Return alle correcte license plates
                        return valid_plates

        except FileNotFoundError:
            print("Error reading file")

    def log_check_in(self, license_plate, check_in_time):
        # Format de datum
        check_in_formatted = check_in_time.strftime('%d-%m-%Y %H:%M:%S')
        string_to_write = f"{check_in_formatted};cpm_name={self.identifier};license_plate={license_plate};action=check-in\n"
        # Lijn schrijven naar carparklog.txt
        try:
            with open("carparklog.txt", 'a') as file:
                file.write(string_to_write)
        except FileNotFoundError:
            print("Error reading file")

    def log_check_out(self, license_plate, parking_fee, check_out_time):
        check_out_formatted = check_out_time.strftime('%d-%m-%Y %H:%M:%S')
        string_to_write = f"{check_out_formatted};cpm_name={self.identifier};license_plate={license_plate};action=check-out;parking_fee={parking_fee}\n"
        # Lijn schrijven naar carparklog.txt
        try:
            with open("carparklog.txt", 'a') as file:
                file.write(string_to_write)
        except FileNotFoundError:
            print("Error reading file")

    def get_machine_fee_by_day(car_parking_machine_id, search_date):
        # Lees file en bereken fee op basis van dag
        try:
            with open("carparklog.txt", 'r') as file:
                lines = file.readlines()
                matching_lines = list()
                for line in range(len(lines)):
                    if search_date in lines[line] and car_parking_machine_id in lines[line]:
                        matching_lines.append(lines[line])
                        # Maak een lijst en voeg alle fees er aan toe als float value
                        all_fees = list()
                        for line in matching_lines:
                            all_items = line.split(";")
                            for item in all_items:
                                if "parking_fee=" in item:
                                    all_fees.append(
                                        float(item.replace('parking_fee=', '')))
                # Stuur de som van alle fees terug
                return sum(all_fees)

        except FileNotFoundError:
            print("Error reading file")

    def get_total_car_fee(license_plate):
        try:
            with open("carparklog.txt", 'r') as file:
                lines = file.readlines()
                matching_lines = list()
                for line in range(len(lines)):
                    if license_plate in lines[line] and "check-out" in lines[line]:
                        matching_lines.append(lines[line])

                all_fees = list()
                for line in matching_lines:
                    all_items = line.split(";")
                    for item in all_items:
                        if "parking_fee=" in item:
                            all_fees.append(
                                float(item.replace('parking_fee=', '')))

                return sum(all_fees)

        except FileNotFoundError:
            print("Error reading file")


class CarParkingMachine:
    def __init__(self, id="Default", capacity=10, hourly_rate=2.50):
        self.capacity = capacity
        self.hourly_rate = hourly_rate
        self.parked_cars = {}
        self.identifier = id
        self.cpl = CarParkingLogger(self.identifier)
        restore_data = self.cpl.restore_state()
        print(restore_data)
        if restore_data:
            print("Restore state found")
            for data in restore_data:
                print(f"data: {data}")
                check_in(data[0], data[1])

    def check_in(self, license_plate, check_in=datetime.now()):
        if len(self.parked_cars) >= self.capacity:
            return False

        car = ParkedCar(license_plate, check_in)
        self.parked_cars[license_plate] = car
        self.cpl.log_check_in(license_plate, check_in)
        return True

    def check_out(self, license_plate):
        if license_plate not in self.parked_cars:
            return None

        check_out_time = datetime.now()
        parking_fee = self.get_parking_fee(license_plate, check_out_time)
        self.cpl.log_check_out(license_plate, parking_fee, check_out_time)
        del self.parked_cars[license_plate]
        return parking_fee

    def get_parking_fee(self, license_plate, check_out_time=datetime.now()):
        if license_plate not in self.parked_cars:
            return False
        check_in_time = self.parked_cars[license_plate].check_in

        parking_duration = check_out_time - check_in_time
        parking_hours = math.ceil(parking_duration.total_seconds() / 3600)

        # Ensure the parking fee does not exceed the maximum for 24 hours
        parking_hours = min(parking_hours, 24)

        return self.hourly_rate * parking_hours

    class logger():
        def get_total_car_fee(license_plate):
            total_fee = CarParkingLogger.get_total_car_fee(license_plate)
            return "{:.2f}".format(total_fee)

        def get_machine_fee_by_day(cpm_name, time):
            fee_sum = CarParkingLogger.get_machine_fee_by_day(cpm_name, time)
            return "{:.2f}".format(fee_sum)


def main():
    parking_machine = CarParkingMachine()
    while True:
        print("\nDefault menu:")
        print("[I] Check-in car by license plate")
        print("[O] Check-out car by license plate")
        print("[Q] Quit program")

        choice = input("Enter your choice: ").upper()

        if choice == 'I':
            license_plate = input("License: ")
            check_license_plate = parking_machine.check_in(license_plate)
            if check_license_plate is True:
                print("License registered")
            else:
                print("Capacity reached!")

        elif choice == 'O':
            license_plate = input("License: ")
            parking_fee = parking_machine.check_out(license_plate)
            if parking_fee:
                print(f"Parking fee: {parking_fee:.2f} EUR")
            else:
                print(f"License {license_plate} not found!")
        elif choice == 'Q':
            break


if __name__ == "__main__":
    main()
