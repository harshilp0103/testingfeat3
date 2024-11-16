import csv
import os
import streamlit as st
import pydeck as pdk
import pandas as pd

# Function to read existing flood data from CSV
def read_flood_data():
    try:
        with open("flood_data.csv", mode="r") as file:
            reader = csv.DictReader(file)
            return [row for row in reader]
    except FileNotFoundError:
        return []  # Return an empty list if the file doesn't exist

# Function to save updated flood data to CSV
def save_flood_data(data):
    with open("flood_data.csv", mode="w", newline='') as file:
        fieldnames = ["lat", "lon", "address", "type", "severity", "image_path"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()  # Write header row
        writer.writerows(data)  # Write the rows of data

# Function to save the uploaded image to the 'flood_images/' directory
def save_image(image, image_name):
    # Ensure the 'flood_images' directory exists
    if not os.path.exists('flood_images'):
        os.makedirs('flood_images')
    
    # Define the path where the image will be saved
    image_path = os.path.join('flood_images', image_name)
    
    # Save the image to the defined path
    with open(image_path, "wb") as img_file:
        img_file.write(image.getbuffer())
    
    return image_path

# Sidebar form for reporting a flood
st.sidebar.header("Report a Flood")
with st.sidebar.form("flood_form"):
    street_address = st.text_input("Street Address")
    flood_type = st.selectbox("Cause of Flood", ["Storm Drain Blockage", "Well/Reservoir Overflow", "Pipe Burst", "Debris", "Other"])
    
    # Conditional text input for custom flood type
    if flood_type == "Other":
        custom_flood_type = st.text_input("Please specify the cause of flooding")
    else:
        custom_flood_type = flood_type  # Use selected flood type if it's not "Other"
    
    severity = st.slider("Flood Severity (1 = Minor, 5 = Severe)", min_value=1, max_value=5)
    
    # Image uploader
    flood_image = st.file_uploader("Upload an image of the flood", type=["jpg", "png", "jpeg"])
    
    submitted = st.form_submit_button("Submit Report")

# If a user submits a new report, save it to the CSV file
if submitted and street_address:
    # If an image is uploaded, save it to the flood_images folder
    if flood_image:
        image_name = f"{street_address.replace(' ', '_')}_{flood_type}.jpg"  # Name the image based on address and flood type
        image_path = save_image(flood_image, image_name)  # Save the image and get the file path
    else:
        image_path = None  # No image uploaded
    
    new_report = {
        "lat": 37.7749,  # Placeholder for latitude (you can replace with real geolocation data)
        "lon": -122.4194,  # Placeholder for longitude (replace with real data)
        "address": street_address,
        "type": custom_flood_type,
        "severity": severity,
        "image_path": image_path  # Store the path to the image
    }
    
    # Append the new report to the existing data
    flood_data = read_flood_data()  # Get current data from the CSV
    flood_data.append(new_report)  # Add the new report
    
    # Save the updated data to the CSV file
    save_flood_data(flood_data)
    
    # Display a success message
    st.success(f"Flood report added at {street_address}. See it on the map below.")
    
    # Display the image if it was uploaded
    if flood_image:
        st.image(flood_image, caption="Uploaded Flood Image", use_column_width=True)

# Load and display all flood data (including images) from the CSV
flood_data = read_flood_data()

# If there is any flood data, show the map
if flood_data:
    # Create DataFrame for pydeck map rendering
    df = pd.DataFrame(flood_data)
    
    # Convert the 'lat' and 'lon' columns to numeric types
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')

    # Create the map with pydeck using a street map style from Mapbox
    view = pdk.ViewState(latitude=df['lat'].mean(), longitude=df['lon'].mean(), zoom=12)
    
    # Define a layer for the flood reports
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_radius=1000,  # Adjust the radius for visibility
        get_fill_color=[255, 0, 0],  # Red color for flood markers
        pickable=True,  # Allows interaction with the markers
        radius_min_pixels=5
    )
    
    # Mapbox style for street map
    map_style = "mapbox://styles/mapbox/streets-v11"  # Street map style from Mapbox

    # Create the pydeck deck with the specified map style
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        map_style=map_style  # Set the street map style
    )
    
    # Render the map in Streamlit
    st.pydeck_chart(deck)

# Display the flood reports in a user-friendly format
if flood_data:
    st.header("Flood Reports")
    
    # Create a table to display the reports
    for report in flood_data:
        with st.expander(f"Details for {report['address']}"):  # Make each report expandable
            st.subheader(f"Address: {report['address']}")
            st.write(f"Flood Type: {report['type']}")
            st.write(f"Severity: {report['severity']}/5")
            
            # Display image if available
            if report["image_path"]:
                st.image(report["image_path"], caption="Flood Image", use_column_width=True)
            
            st.write("----")

else:
    st.info("No flood reports available.")
