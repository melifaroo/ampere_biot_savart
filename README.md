# GUI Current Control Application

This project is a GUI application designed to control and visualize electrical current parameters. It allows users to set up the current \( I \), choose the type of excitation (either RLC or real), and adjust the \( Kd \) coefficient. The application automatically updates the plot based on the changes made in the controls.

## Project Structure

```
gui-current-control
├── src
│   ├── main.py                # Entry point of the application
│   ├── gui
│   │   ├── app.py             # Main application class
│   │   ├── controls.py        # Control panel for user inputs
│   │   └── plot.py            # Plotting results
│   ├── logic
│   │   ├── calculations.py     # Calculation functions
│   │   └── data.py            # Data management
│   └── assets
│       └── styles.css         # CSS styles for the GUI
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Installation

To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd gui-current-control
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:
```
python src/main.py
```

Once the application is running, you can:

- Adjust the current \( I \) using the provided control.
- Select the type of excitation (RLC or real) from the dropdown menu.
- Modify the \( Kd \) coefficient using the slider.
- The plot will automatically update to reflect the changes made in the controls.

## Contributing

Contributions are welcome! If you have suggestions or improvements, please create a pull request or open an issue.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.