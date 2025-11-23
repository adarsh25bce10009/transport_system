USERS = "users.txt"
TRANSPORTS = "transports_data.txt"
PASSENGERS = "passengers.txt"

transports = {}
ticket_counter = 1

#see if the files are created if not give some default values.
def check_files():
    try:
        open(USERS, "r").close()
    except FileNotFoundError:
        with open(USERS, "w") as f:
            f.write("admin,password123,admin\nuser1,1111,user\n")

    try:
        open(TRANSPORTS, "r").close()
    except FileNotFoundError:
        with open(TRANSPORTS, "w") as f:
            f.write("BUS,BUS-101,15,250\nBUS,BUS-202,20,300\nTRAIN,TRAIN-11,40,450\n")


def read_users():
    users = []
    try:
        with open(USERS) as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                p = ln.split(",")
                if len(p) >= 3:
                    users.append((p[0], p[1], p[2]))
    except:
        pass
    return users


def add_transports():
    global transports
    transports = {}
    index = 1
    try:
        with open(TRANSPORTS) as f:
            for i in f:
                i = i.strip()
                if not i:
                    continue
                lists_veh = i.split(",")
                if len(lists_veh) < 4:
                    continue
                try:
                    seats = int(lists_veh[2])
                    fare = int(lists_veh[3])
                except:
                    continue

                transports[index] = {
                    "type": lists_veh[0].upper(),
                    "number": lists_veh[1],
                    "total": seats,
                    "available": list(range(1, seats + 1)),
                    "fare": fare,
                    "passengers": {}
                }
                index += 1
    except:
        pass


def add_passengers():
    global ticket_counter
    highest = 0
    try:
        with open(PASSENGERS) as f:
            for j in f:
                j = j.strip()
                if not j:
                    continue
                p = j.split(",")
                if len(p) < 6:
                    continue
                tid, name, seat_s, tr_no, fare_s, who = p[:6]
                try:
                    seat = int(seat_s)
                    fare = int(fare_s)
                except:
                    continue

                target = None
                for t in transports.values():
                    if t["number"] == tr_no:
                        target = t
                        break
                if not target:
                    continue

                target["passengers"][tid] = {
                    "name": name,
                    "seat": seat,
                    "fare": fare,
                    "by": who
                }

                if seat in target["available"]:
                    try:
                        target["available"].remove(seat)
                    except:
                        pass

                if tid.startswith("TKT-"):
                    try:
                        num = int(tid.split("-")[1])
                        if num > highest:
                            highest = num
                    except:
                        pass
    except:
        pass

    ticket_counter = highest + 1


def save_passengers():
    with open(PASSENGERS, "w") as f:
        for tr in transports.values():
            for tid, d in tr["passengers"].items():
                f.write(f"{tid},{d['name']},{d['seat']},{tr['number']},{d['fare']},{d['by']}\n")


def new_ticket():
    global ticket_counter
    tid = f"TKT-{ticket_counter}"
    ticket_counter += 1
    return tid


def to_int(v):
    try:
        return int(v)
    except:
        return None


def show_transports():
    print()
    if not transports:
        print("No transport options available.\n")
        return
    print("Available Transports:")
    for i, t in transports.items():
        print(f"{i}. {t['number']} | {t['type']} | Seats Left: {len(t['available'])} | Fare ₹{t['fare']}")
    print()


def bus_seatmap(tr):
    print()
    taken = {p["seat"] for p in tr["passengers"].values()}
    total = tr["total"]
    seat_num = 1

    while seat_num <= total:
        left = []
        right = []
        for _ in range(2):
            if seat_num <= total:
                left.append(seat_num)
                seat_num += 1
        for _ in range(3):
            if seat_num <= total:
                right.append(seat_num)
                seat_num += 1

        for i in left:
            print(" X" if i in taken else f"{i:02}", end=" ")
        print("|", end=" ")
        for i in right:
            print(" X" if i in taken else f"{i:02}", end=" ")
        print()
    print()


def book(username):
    show_transports()
    ch = to_int(input("Enter transport number: "))
    print()

    if ch not in transports:
        print("Invalid choice.\n")
        return

    tr = transports[ch]

    if not tr["available"]:
        print("No seats left.\n")
        return

    name = input("Enter passenger name: ").strip()
    if not name:
        print("Name cannot be empty.\n")
        return

    if tr["type"] == "BUS":
        bus_seatmap(tr)

    print("Available seats:", tr["available"])
    s = to_int(input("Select seat: ").strip())
    print()

    if s not in tr["available"]:
        print("Seat not available.\n")
        return

    tid = new_ticket()
    tr["available"].remove(s)
    tr["passengers"][tid] = {"name": name, "seat": s, "fare": tr["fare"], "by": username}
    save_passengers()

    print("Booking Successful!\n")
    print(f"Ticket ID: {tid}\nName: {name}\nSeat: {s}\nTransport: {tr['number']}\nFare: ₹{tr['fare']}\n")


def cancel(username, role):
    print()
    tid = input("Enter Ticket ID: ").strip()
    if not tid:
        print("Ticket ID required.\n")
        return

    for tr in transports.values():
        if tid in tr["passengers"]:
            d = tr["passengers"][tid]
            if role != "admin" and d["by"] != username:
                print("You are not allowed to cancel this ticket.\n")
                return
            if d["seat"] not in tr["available"]:
                tr["available"].append(d["seat"])
                tr["available"].sort()
            del tr["passengers"][tid]
            save_passengers()
            print("Ticket cancelled.\n")
            return

    print("Ticket not found.\n")


def my_tickets(username):
    print()
    booking_check = False
    for tr in transports.values():
        for tid, d in tr["passengers"].items():
            if d["by"] == username:
                booking_check = True
                print(f"{tid} | {d['name']} | seat {d['seat']} | {tr['number']} | ₹{d['fare']}")
    if not booking_check:
        print("You have no bookings.\n")
    print()


def add_transport():
    print()
    typ = input("Type (BUS/TRAIN): ").strip().upper()
    num = input("Transport Number: ").strip()
    seats = to_int(input("Total Seats: ").strip())
    fare = to_int(input("Fare: ").strip())

    if not seats or not fare:
        print("Invalid.\n")
        return

    with open(TRANSPORTS, "a") as f:
        f.write(f"{typ},{num},{seats},{fare}\n")

    add_transports()
    save_passengers()
    print("Transport added.\n")


def login():
    print()
    u = input("Username: ").strip()
    p = input("Password: ").strip()

    for a, b, c in read_users():
        if u == a and p == b:
            print("\nLogin successful.\n")
            return u, c

    print("\nIncorrect username or password.\n")
    return None, None


def user_menu(username):
    while True:
        print("1. View Transports")
        print("2. Book Ticket")
        print("3. Cancel Ticket")
        print("4. My Bookings")
        print("5. Seat Map (Bus Only)")
        print("6. Logout\n")

        ch = input("Choose option: ").strip()
        print()

        if ch == "1":
            show_transports()
        elif ch == "2":
            book(username)
        elif ch == "3":
            cancel(username, "user")
        elif ch == "4":
            my_tickets(username)
        elif ch == "5":
            show_transports()
            k = to_int(input("Transport index: ").strip())
            print()
            if k in transports and transports[k]["type"] == "BUS":
                bus_seatmap(transports[k])
            else:
                print("Invalid.\n")
        elif ch == "6":
            print("Logged out.\n")
            return
        else:
            print("Invalid choice.\n")


def admin_menu(username):
    while True:
        print("1. View Transports")
        print("2. Add Transport")
        print("3. View All Bookings")
        print("4. Logout\n")

        ch = input("Choose option: ").strip()
        print()

        if ch == "1":
            show_transports()
        elif ch == "2":
            add_transport()
        elif ch == "3":
            found = False
            for tr in transports.values():
                for tid, d in tr["passengers"].items():
                    found = True
                    print(f"{tid} | {d['name']} | seat {d['seat']} | {tr['number']} | ₹{d['fare']} | by {d['by']}")
            if not found:
                print("No bookings.\n")
            print()
        elif ch == "4":
            print("Logged out.\n")
            return
        else:
            print("Invalid.\n")


def start():
    check_files()
    add_transports()
    add_passengers()

    while True:
        print("\nWelcome to the Ticket Booking System\n")
        print("1. Login")
        print("2. Create Account")
        print("3. Exit\n")

        ch = input("Choose option: ").strip()
        print()

        if ch == "1":
            u, r = login()
            if not u:
                continue
            if r == "admin":
                admin_menu(u)
            else:
                user_menu(u)

        elif ch == "2":
            u = input("New username: ").strip()
            pw = input("Password: ").strip()
            if "," in u or "," in pw:
                print("Invalid.\n")
                continue
            with open(USERS, "a") as f:
                f.write(f"{u},{pw},user\n")
            print("Account created.\n")

        elif ch == "3":
            print("Thank you for using the system.\nclosing...\n")
            return

        else:
            print("Invalid choice.\n")


start()
