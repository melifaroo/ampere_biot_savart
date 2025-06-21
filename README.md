# Ampere Biot-Savart Nuemann Application (GUI)

This project is an application designed to calculate ampere-forces, magnetic fields and branch impedances for given geometry of circuit (1 phase - 3 phase). It allows users to set up the circuit geometry, short-ciruit current (time-dependent), choose the type of excitation (RLC or 3-phase generator). The application automatically updates the plot based on the changes made in the controls.

## Project Structure

```
gui-current-control
├── src
│   ├── main.py                # Entry point of the application
│   ├── gui
│   │   ├── app.py             # Main application class
│   │   ├── controls_geom.py   # Control panel for user inputs of geometry
│   │   ├── controls_exct.py   # Control panel for user inputs of currents
│   │   └── plot_geom.py       # Plotting panel for geometry
│   │   └── plot_exct.py       # Plotting panel for currents
│   ├── logic
│   │   ├── excittion.py      # Current model
│   │   └── geometry.py       # Geometry model
│   │   └── solution.py       # Calculation logic
│   │   └── presentation.py   # Results plotting
│   └── utils
│       └── formats.py        # Formats convertor utils
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
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