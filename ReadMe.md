# Organizational Chart Web Application

## Overview

This web application is a simple and interactive **Organizational Chart** tool built with **Flask**. It allows you to upload an **Excel file** to visualize the organizational hierarchy, search for employees, and filter by various criteria such as work type, division, and city.

## Features

- **Dynamic Organizational Chart**: Displays managers, employees, teams, and CFO leaders in a clear hierarchy
- **Search Functionality**: Quickly locate employees by name
- **Filter Options**: Filter employees by work type, division, or city
- **Excel File Input**: Automatically generates the chart from an uploaded Excel file

## Requirements

- Python 3.7+
- Flask
- Pandas
- OpenPyXL

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/obinopaul/organizational-chart-app.git
   cd organizational-chart-app
   ```

2. Install the required Python libraries:
   ```bash
   pip install flask pandas openpyxl
   ```

## Usage

### Excel File Format

Ensure your Excel file has the following columns:
- `Employee Name`
- `Manager Name`
- `Position`
- `Division`
- `City`
- `Work Type`

### Running the Application

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to `http://127.0.0.1:5000`

3. Upload your Excel file via the web interface

### Example Excel File Data

| Employee Name | Manager Name | Position | Division | City | Work Type |
|--------------|--------------|----------|----------|------|-----------|
| John Doe | Sarah Smith | Team Leader | Finance | New York | Full-time |
| Jane Roe | John Doe | Analyst | Finance | New York | Full-time |
| Sarah Smith | CFO | Manager | Finance | New York | Full-time |
| Bob White | Sarah Smith | Accountant | Finance | Chicago | Part-time |

## Notes

- This app is designed for basic organizational visualization and filtering
- Ensure your Excel file follows the expected format to avoid errors
- The app is a simple, lightweight tool and can be extended for more complex features

## License

This project is open-source and available under the MIT License.

## Contact

For questions or contributions, feel free to open an issue or reach out!"# organizational-chart-app" 
