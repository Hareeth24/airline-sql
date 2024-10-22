import streamlit as st
from fpdf import FPDF
from datetime import datetime
from pymongo import MongoClient

# Set up the database connection
def create_connection():
    client = MongoClient("mongodb+srv://arjun:hareeth24@clusterariline.tspcv.mongodb.net/?retryWrites=true&w=majority&appName=Clusterariline")
    db = client.airline_management  # Change to your database name
    return db

# Custom CSS for colors and design
st.markdown("""
    <style>
    .title {
        color: #2E8B57;
        font-size: 36px;
        font-weight: bold;
        text-align: center;
    }
    .subtitle {
        color: #1E90FF;
        font-size: 28px;
        margin-top: 20px;
    }
    .btn-primary {
        background-color: #1E90FF;
        color: white;
        border-radius: 5px;
        font-size: 16px;
        margin: 10px;
    }
    .btn-danger {
        background-color: #FF4500;
        color: white;
        border-radius: 5px;
        font-size: 16px;
        margin: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'register_or_login'

# Registration form
def registration():
    st.markdown('<p class="title">User Registration</p>', unsafe_allow_html=True)
    username = st.text_input("Username", key='register_username')
    password = st.text_input("Password", type="password", key='register_password')

    if st.button('Register', key='register_button', use_container_width=True):
        if username and password:
            db = create_connection()
            users_collection = db.users  # Change to your collection name
            if users_collection.find_one({"username": username}):
                st.error(f"User '{username}' already exists! Please sign in.")
            else:
                users_collection.insert_one({"username": username, "password": password, "role": 'user'})
                st.success(f"User '{username}' registered successfully!")
                st.session_state['page'] = 'login'  # Redirect to login page after registration
        else:
            st.error("Please fill out all fields.")

# User/Admin Login
def login():
    st.markdown('<p class="title">Sign In</p>', unsafe_allow_html=True)
    username = st.text_input("Username", key='login_username')
    password = st.text_input("Password", type="password", key='login_password')

    if st.button('Login', key='login_button', use_container_width=True):
        # Check if the user is an admin
        if username == "admin" and password == "admin1234":
            st.session_state['current_user'] = {'username': username, 'role': 'admin'}
            st.success(f"Logged in as Admin")
            st.session_state['page'] = 'admin_dashboard'  # Admin goes to dashboard
        else:
            db = create_connection()
            users_collection = db.users  # Change to your collection name
            user = users_collection.find_one({"username": username, "password": password})
            if user:
                st.session_state['current_user'] = {'username': user['username'], 'role': user['role']}
                st.success(f"Logged in as {username}")
                st.session_state['page'] = 'book_flight'  # User goes to booking page
            else:
                st.error("Invalid credentials!")

# Admin functionalities
def admin_dashboard():
    st.markdown('<p class="subtitle">Admin Dashboard</p>', unsafe_allow_html=True)

    flight_name = st.text_input("Flight Name")
    departure = st.text_input("Departure Location")
    arrival = st.text_input("Arrival Location")
    seats = st.number_input("Number of Seats", min_value=1, max_value=500, value=100)

    if st.button('Add Flight', key='add_flight', use_container_width=True):
        db = create_connection()
        flights_collection = db.flights  # Change to your collection name
        flights_collection.insert_one({"flight_name": flight_name, "departure": departure, "arrival": arrival, "seats": seats})
        st.success(f"Flight '{flight_name}' added successfully!")

    # Display available flights
    db = create_connection()
    flights_collection = db.flights  # Change to your collection name
    flights = flights_collection.find()
    if flights:
        st.markdown('<p class="subtitle">Available Flights</p>', unsafe_allow_html=True)
        for flight in flights:
            st.write(f"Flight: {flight['flight_name']}, Departure: {flight['departure']}, Arrival: {flight['arrival']}, Seats: {flight['seats']}")
    
# Booking function for users
def book_flight():
    st.markdown('<p class="subtitle">Book a Flight</p>', unsafe_allow_html=True)

    db = create_connection()
    flights_collection = db.flights  # Change to your collection name
    flights = flights_collection.find()

    if flights:
        flight_options = [flight['flight_name'] for flight in flights]  # Assuming flight name is a key
        selected_flight = st.selectbox("Select a Flight", flight_options)

        passenger_name = st.text_input("Passenger Name")
        age = st.number_input("Passenger Age", min_value=1, max_value=120, value=25)
        travel_date = st.date_input("Date of Travel", min_value=datetime.today())
        
        from_location = st.text_input("From Location")
        to_location = st.text_input("To Location")
        
        num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=10, value=1)

        if st.button('Book Ticket', key='book_ticket', use_container_width=True):
            if from_location and to_location:
                # Generate PDF ticket
                generate_ticket(passenger_name, age, travel_date, selected_flight, from_location, to_location, num_tickets)
                st.success(f"{num_tickets} ticket(s) booked for {selected_flight}!")
            else:
                st.error("Please enter both 'From Location' and 'To Location'.")
    else:
        st.error("No flights available to book. Please check back later or contact the admin.")

# Function to generate PDF tickets
def generate_ticket(passenger_name, age, travel_date, flight_name, from_location, to_location, num_tickets):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Flight Ticket", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Passenger: {passenger_name}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Age: {age}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Flight: {flight_name}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"From: {from_location} To: {to_location}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Date of Travel: {travel_date.strftime('%Y-%m-%d')}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Tickets: {num_tickets}", ln=True, align="L")

    pdf_file = f"{passenger_name}_ticket.pdf"
    pdf.output(pdf_file)

    st.success("Ticket generated!")
    st.download_button(label="Download Ticket", data=open(pdf_file, "rb"), file_name=pdf_file)

# Main app logic
def main():
    if st.session_state['current_user'] is None:
        # Registration and Login flow
        if st.session_state['page'] == 'register_or_login':
            st.markdown('<p class="title">Welcome to Airline Management System</p>', unsafe_allow_html=True)
            st.write("New user? Please register below:")
            registration()
            st.write("Already have an account? Sign in below:")
            login()
        elif st.session_state['page'] == 'login':
            login()
        else:
            st.session_state['page'] = 'register_or_login'
    else:
        user = st.session_state['current_user']
        if user['role'] == 'user':
            book_flight()
        elif user['role'] == 'admin':
            admin_dashboard()

        if st.button('Logout', key='logout', use_container_width=True):
            st.session_state['current_user'] = None
            st.session_state['page'] = 'register_or_login'

# Run the main app
if __name__ == "__main__":
    main()
