from flask import Flask, render_template, jsonify, request
import pandas as pd
import json # Import the json module to convert data to JSON format
import os
import fnmatch

app = Flask(__name__)

# Define the base file name to search for
base_file_name = "100 WD Report"

# Define a function to find the appropriate file in the directory
def find_file(base_name, directory=".", extensions=("*.xlsx", "*.csv")):
    """
    Search for a file in the given directory that matches the base name and has a valid extension.
    """
    for file_name in os.listdir(directory):
        if base_name in file_name and any(fnmatch.fnmatch(file_name, ext) for ext in extensions):
            return os.path.join(directory, file_name)
    return None

# Locate the file
file_path = find_file(base_file_name)

if file_path:
    try:
        # Load the dataset into a pandas DataFrame, skipping the first row
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path, skiprows=1)
        elif file_path.endswith(".csv"):
            df = pd.read_csv(file_path, skiprows=1)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        # print(f"Successfully loaded data from {file_path}")
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
else:
    print(f"No file matching '{base_file_name}' found in the directory.")

# Define the hierarchy levels based on the corporate titles
title_hierarchy = {
    "Managing Director": 1,
    "Director": 2,
    "Vice President": 3,
    "Assistant Vice President": 4,
    "Associate": 5,
    "Analyst": 6
}

# Strip column names and filter relevant columns
df.columns = df.columns.str.strip()
important_columns = ['Employee ID', 'Preferred Name', 'Email - Work', 'Worker Corporate Title', 'Location Address - City', 
                     'Cost Center Name', 'UBR Level 8', 'Organization Manager', 'Organization Manager Employee ID', 
                     'Organization Manager Email', 'Matrix Manager', 'Worker Type']
try:
    filtered_df = df[important_columns].copy()
except KeyError as e:
    print(f"Error: Missing columns in the dataset - {e}")
    filtered_df = pd.DataFrame(columns=important_columns)  # Create an empty DataFrame with required columns


# Clean up data
filtered_df.columns = filtered_df.columns.str.strip()
# Normalize the Worker Type column
if 'Worker Type' in filtered_df.columns:
    filtered_df['Worker Type'] = filtered_df['Worker Type'].str.strip().replace(
        {'Contingent Worker / Person of Interest': 'Contingent Worker'}
    ).str.title()  # Ensures consistent case (e.g., "Employee" or "Contingent Worker")

filtered_df['Worker Type'] = filtered_df['Worker Type'].str.lower()
filtered_df['Employee ID'] = filtered_df['Employee ID'].astype(str).str.replace(r'\D', '', regex=True)
filtered_df['Worker Corporate Title'] = filtered_df['Worker Corporate Title'].str.strip().str.title()

# filtered_df['Organization Manager Employee ID'] = filtered_df['Organization Manager Employee ID'].astype(str).str.replace(r'\D', '', regex=True)
filtered_df['Organization Manager Employee ID'] = (
    filtered_df['Organization Manager Employee ID']
    .astype(str)                  # Ensure the column is treated as strings
    .str.replace(r'\D', '', regex=True)  # Remove non-numeric characters
    .str[:7]                      # Extract the first seven characters
)
filtered_df.fillna({
    "Employee ID": "Unknown",
    "Preferred Name": "Not Available",
    "Email - Work": "No Email Provided",
    "Worker Corporate Title": "No Title",
    "Location Address - City": "Unknown City",
    "Cost Center Name": "Not Assigned",
    "Organization Manager": "No Manager",
    "Organization Manager Employee ID": "Unknown",
    "Organization Manager Email": "No Email",
    "Matrix Manager": "No Matrix Manager",
    "Worker Type": "Unknown"
}, inplace=True)

# Step 1: Fill NaN values with 'Unknown'
filtered_df['UBR Level 8'] = filtered_df['UBR Level 8'].fillna("Unknown")

# Step 2: Split the string and handle cases where there might not be a space
filtered_df['UBR Level 8'] = filtered_df['UBR Level 8'].apply(
    lambda x: x.split(' ', 1)[1] if ' ' in x and len(x.split(' ', 1)) > 1 else x
)


unique_ubr_levels = filtered_df['UBR Level 8'].unique()

# Assuming `unique_ubr_levels` is a Pandas Series or similar array-like object
unique_ubr_levels_list = unique_ubr_levels.tolist()  # Convert to list if it's not already
unique_ubr_levels_list.append('CCAR')  # Append 'CCAR' to the list


# Generate a dictionary to map each unique UBR Level to a unique key
ubr_level_keys = {level: 100 * (i + 1) for i, level in enumerate(unique_ubr_levels)}

# Step 2: Map these keys to the 'UBR Level 8' column
filtered_df['Key'] = filtered_df['UBR Level 8'].map(ubr_level_keys)


# ubr_level_datasets = {
#     ubr_level.strip(): filtered_df[filtered_df['UBR Level 8'].str.strip() == ubr_level.strip()].copy()
#     for ubr_level in unique_ubr_levels
# }

# # Create datasets for organizational charts, excluding "Contingent Worker"
# ubr_level_chart_datasets = {
#     ubr_level.strip(): filtered_df[(filtered_df['UBR Level 8'].str.strip() == ubr_level.strip()) & 
#                                    (filtered_df['Worker Type'] != "contingent worker")].copy()
#     for ubr_level in unique_ubr_levels
# }


# Create datasets based on unique keys, using the 'Key' column instead of 'UBR Level 8'
ubr_level_datasets = {
    key: filtered_df[filtered_df['Key'] == key].copy()
    for key in filtered_df['Key'].unique()
}

# Create datasets for organizational charts, excluding "Contingent Worker", using 'Key' instead of 'UBR Level 8'
ubr_level_chart_datasets = {
    key: filtered_df[(filtered_df['Key'] == key) & (filtered_df['Worker Type'] != "contingent worker")].copy()
    for key in filtered_df['Key'].unique()
}

# Filter for Cost Center 'CCAR'
ccar_filtered_df = filtered_df[filtered_df['Cost Center Name'].str.contains('CCAR Team', case=False, na=False)]

# If needed, you can also create a chart dataset for CCAR, similar to what you've done for UBR levels
ccar_chart_dataset = ccar_filtered_df[ccar_filtered_df['Worker Type'] != "contingent worker"].copy()

# Helper function to filter and process data for a given UBR level
def filter_ubr_level_data(ubr_level, filtered_df):
    # Step 1: Filter employees for the specific UBR level
    filtered_by_ubr_level = filtered_df[filtered_df['UBR Level 8'] == ubr_level]
    
    # Step 2: Normalize the Worker Corporate Title
    filtered_by_ubr_level['Worker Corporate Title'] = filtered_by_ubr_level['Worker Corporate Title'].str.strip().str.title()

    # Step 3: Filter for Managing Director and Director
    data_filtered = filtered_by_ubr_level[filtered_by_ubr_level['Worker Corporate Title'].isin(["Managing Director", "Director"])]
    
    # Step 4: If no Managing Director or Director, fallback to the highest-ranked employee
    if data_filtered.empty:
        fallback_rank = filtered_by_ubr_level['Worker Corporate Title'].map(title_hierarchy).min()
        data_filtered = filtered_by_ubr_level[filtered_by_ubr_level['Worker Corporate Title'].map(title_hierarchy) == fallback_rank]

    # Return the filtered data
    return data_filtered



# Define colors for UBR Level rectangles on the homepage
ubr_colors = ["#FFD700", "#FF8C00", "#48C9B0", "#F39C12", "#9B59B6", "#3498DB"]

# Define the route for the homepage
@app.route('/')
def index():
    ubr_level_data = {}
    
    # Normalize the corporate titles for consistency
    filtered_df['Worker Corporate Title'] = filtered_df['Worker Corporate Title'].str.strip().str.title()

    # Filter the data by UBR Level and exclude Contingent Workers once
    # This is done only once to avoid repeating the same operation multiple times
    ubr_level_filtered_df = filtered_df[filtered_df['Worker Type'] != "contingent worker"]

    # Group data by unique UBR Levels (based on Key, assuming the 'Key' column is correct)
    unique_ubr_levels = ubr_level_filtered_df['UBR Level 8'].unique()
    
    # Process each UBR level
    for ubr_level in unique_ubr_levels:
        # Filter by current UBR level
        level_df = ubr_level_filtered_df[ubr_level_filtered_df['UBR Level 8'] == ubr_level]
        
        # Now filter by titles ("Managing Director" or "Director")
        data_filtered = level_df[level_df['Worker Corporate Title'].isin(["Managing Director", "Director"])]
    
        # If no Managing Directors or Directors, fallback to the highest-ranked person
        if data_filtered.empty:
            fallback_rank = level_df['Worker Corporate Title'].map(title_hierarchy).min()
            data_filtered = level_df[level_df['Worker Corporate Title'].map(title_hierarchy) == fallback_rank]

        # Store the filtered employees and total count for each UBR level
        ubr_level_data[ubr_level] = {
            "employees": data_filtered.to_dict(orient="records"),
            "total_count": len(level_df),  # Total count of employees for this UBR level
            "employee_ids": data_filtered['Employee ID'].tolist()  # Include employee IDs for validation
        }

    # Pass the processed data to the template
    return render_template('index.html', ubr_levels=unique_ubr_levels.tolist(), ubr_level_data=ubr_level_data, ubr_colors=ubr_colors)




@app.route('/managers', methods=['GET'])
def get_managers():
    division = request.args.get('division')  # Get the selected division from the URL parameter
    division_type = 'CCAR' if division and 'CCAR' in division else 'UBR'  # Ensure 'division' is not None before checking

    # Step 1: Get the appropriate dataframe (filtered for UBR levels or CCAR)
    if division_type == 'UBR':
        # Get the UBR level data
        division_df = filtered_df[filtered_df['UBR Level 8'] == division]
    elif division_type == 'CCAR':
        # Get the CCAR division data
        division_df = ccar_filtered_df

    # Step 2: Filter out contingent workers
    division_df = division_df[division_df['Worker Type'] != "contingent worker"]

    # Step 3: Get the unique manager IDs for the division
    unique_manager_ids = division_df['Organization Manager Employee ID'].unique()

    # Step 4: For each unique manager ID, get the employees they manage
    manager_employee_dict = {}

    for manager_id in unique_manager_ids:
        # Get the employees managed by this manager in the current division
        employees = division_df[division_df['Organization Manager Employee ID'] == manager_id]['Preferred Name'].tolist()
        manager_employee_dict[manager_id] = employees

    # Step 5: Dynamically generate the mapping of manager IDs to names
    manager_id_to_name = {}

    # Iterate through unique manager IDs and get corresponding names from the dataframe
    for manager_id in unique_manager_ids:
        manager_name = division_df[division_df['Organization Manager Employee ID'] == manager_id]['Organization Manager'].iloc[0]
        manager_id_to_name[manager_id] = manager_name

    # Step 6: Convert manager IDs in `manager_employee_dict` to names
    manager_employee_dict_named = {
        manager_id_to_name[manager_id]: employees
        for manager_id, employees in manager_employee_dict.items()
    }

    # Get unique UBR levels for the filter dropdown
    unique_ubr_levels = filtered_df['UBR Level 8'].unique()

    # Step 7: Pass the manager-employee mapping and other data to the template
    return render_template('managers.html', division=unique_ubr_levels, manager_employee_dict=manager_employee_dict_named)



@app.route('/management')
def management_view():
    ubr_level_data = {}
    
    # Normalize the corporate titles for consistency
    filtered_df['Worker Corporate Title'] = filtered_df['Worker Corporate Title'].str.strip().str.title()

    # Filter the data by UBR Level and exclude Contingent Workers
    ubr_level_filtered_df = filtered_df[filtered_df['Worker Type'] != "contingent worker"]

    # Group data by unique UBR Levels
    unique_ubr_levels = ubr_level_filtered_df['UBR Level 8'].unique()
    
    # Process each UBR level
    for ubr_level in unique_ubr_levels:
        level_df = ubr_level_filtered_df[ubr_level_filtered_df['UBR Level 8'] == ubr_level]
        
        # Filter by titles ("Managing Director" or "Director")
        data_filtered = level_df[level_df['Worker Corporate Title'].isin(["Managing Director", "Director"])]
    
        # Fallback to the highest-ranked person if no Managing Directors or Directors are found
        if data_filtered.empty:
            fallback_rank = level_df['Worker Corporate Title'].map(title_hierarchy).min()
            data_filtered = level_df[level_df['Worker Corporate Title'].map(title_hierarchy) == fallback_rank]

        # Clean data to ensure it's serializable
        data_filtered_cleaned = data_filtered.copy()

        # Convert any problematic columns to strings or appropriate types
        for column in data_filtered_cleaned.columns:
            # For any column that contains NaN or None, replace with a string
            data_filtered_cleaned[column] = data_filtered_cleaned[column].fillna('').astype(str)

        # Store the filtered employees and their total count for this UBR level
        ubr_level_data[ubr_level] = {
            "employees": data_filtered_cleaned.to_dict(orient="records"),
            "total_count": len(level_df),
            "employee_ids": data_filtered_cleaned['Employee ID'].tolist()
        }

    # Pass the processed data to the management template
    return render_template('management.html', ubr_list=unique_ubr_levels.tolist(), ubr_list_data=ubr_level_data)


@app.route('/employees')
def show_employees():
    all_employees = []
    cities = set()

    for key, df in ubr_level_datasets.items():
        # Collect all employees
        all_employees.extend(df.to_dict(orient="records"))

        # Collect unique cities
        cities.update(df['Location Address - City'].dropna().unique())

    # Convert cities to a sorted list for consistent dropdowns
    cities = sorted(cities)

    return jsonify({
        "all_employees": all_employees,
        "cities": cities
    })


@app.route('/api/ccar_chart_data')
def show_ccar_employees():
    try:
        # Make sure the dataset exists
        if ccar_chart_dataset.empty:
            return jsonify({"error": "CCAR dataset is empty"}), 404

        # Process and filter CCAR data
        ccar_filtered_data = ccar_chart_dataset.copy()
        ccar_filtered_data['Hierarchy Rank'] = ccar_filtered_data['Worker Corporate Title'].map(title_hierarchy)
        ccar_filtered_data.sort_values(by='Hierarchy Rank', inplace=True)

        # Simplify the data to a dictionary format
        simplified_data = ccar_filtered_data.to_dict(orient="records")

        # Return the processed data as JSON with 200 status code
        return jsonify(simplified_data), 200

    except Exception as e:
        # If something goes wrong, return the error message with 500 status code
        return jsonify({"error": str(e)}), 500


@app.route('/api/chart_data/<ubr_level>')
def get_chart_data(ubr_level):
    try:
        # First, check if the requested level is "CCAR"
        if ubr_level == "CCAR":
            # Use the CCAR-specific dataset
            chart_data = ccar_chart_dataset.copy()  # Replace 'ccar_chart_dataset' with the actual CCAR data variable
            
            # Check if dataset is empty
            if chart_data.empty:
                return jsonify({"error": "CCAR dataset is empty"}), 404

            # Check for missing corporate titles, which could cause the filtering to fail
            missing_titles = chart_data['Worker Corporate Title'].isnull().sum()
            if missing_titles > 0:
                return jsonify({"error": f"{missing_titles} rows with missing corporate title found"}), 400

            # Proceed with processing
            chart_data['Hierarchy Rank'] = chart_data['Worker Corporate Title'].map(title_hierarchy)
            chart_data.sort_values(by='Hierarchy Rank', inplace=True)

            simplified_data = chart_data.to_dict(orient="records")
            return jsonify(simplified_data)

        # Convert ubr_level to its corresponding Key value
        if ubr_level in ubr_level_keys:
            ubr_key = ubr_level_keys[ubr_level]
            
            # Check if the Key exists in ubr_level_chart_datasets
            if ubr_key in ubr_level_chart_datasets:
                chart_data = ubr_level_chart_datasets[ubr_key].copy()

                # Check if dataset is empty
                if chart_data.empty:
                    return jsonify({"error": f"No data found for UBR Level {ubr_level}"}), 404

                # Check for missing corporate titles
                missing_titles = chart_data['Worker Corporate Title'].isnull().sum()
                if missing_titles > 0:
                    return jsonify({"error": f"{missing_titles} rows with missing corporate title found for UBR Level {ubr_level}"}), 400

                # Process the data
                chart_data['Hierarchy Rank'] = chart_data['Worker Corporate Title'].map(title_hierarchy)
                chart_data.sort_values(by='Hierarchy Rank', inplace=True)

                simplified_data = chart_data.to_dict(orient="records")
                return jsonify(simplified_data)
            else:
                return jsonify({"error": "UBR Level data not found for the specified Key"}), 404
        else:
            return jsonify({"error": "Invalid UBR level"}), 404

    except Exception as e:
        # Return the error message with 500 status code if something goes wrong
        print(f"Error in get_chart_data for {ubr_level}: {e}")  # Log the error for debugging
        return jsonify({"error": str(e)}), 500




@app.route('/chart/<ubr_level>')
def show_chart(ubr_level):
    # Get the chart data from get_chart_data function
    chart_response = get_chart_data(ubr_level)

    # Check if the status code of the response is 200
    if chart_response.status_code == 200:
        # Get the 'highlight' query parameter from the request (if any)
        highlight_id = request.args.get('highlight')
        
        # Extract the JSON data from the response
        chart_data = chart_response.get_json()
        
        # Pass the highlight ID and chart data to the template
        return render_template(
            'chart.html',
            ubr_level=ubr_level,
            chart_data=json.dumps(chart_data),  # Convert the chart data to a JSON string
            highlight_id=highlight_id
        )
    else:
        # Return an error message if the chart data was not found
        return "UBR Level not found", 404

@app.route('/management')
def management():
    return render_template('management.html')


if __name__ == '__main__':
    app.run(debug=True)
