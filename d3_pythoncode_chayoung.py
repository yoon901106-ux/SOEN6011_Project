__version__ = "1.0.1"

# Version 1.0.0: D2 Final version.
# Version 1.0.1: Fixed the large-angle precision issue.

import tkinter as tk

# Define PI instead of using math.pi.
PI = 3.14159265358979323846


# Define the maximum supported angle to prevent precision loss.
MAX_SUPPORTED_RADIANS = 1_000_000.0


# Define TOLERANCE as a small value used to represent near zero,
# because floating-point results may not be exactly zero.
TOLERANCE = 1e-12

# Set a safe maximum number of iterations to prevent an infinite loop,
# when calculate sin,cos
MAX_ITERATIONS = 50

# -------------------------
# Exceptions
# --------------------------
class InputError(Exception):
      pass

class UndefinedTangentError(Exception):
      pass

# -----------------------
# functions implemented
# -----------------------
def absolute_value(number):
    if number < 0:
        return -number

    return number

# Convert degrees to radians when Degrees is selected.
# 180 degrees = π radians
def convert_to_radians(angle, unit):
    if unit == "Degrees":
        return (angle / 180.0) * PI

    if unit == "Radians":
        return angle

"""
Reduce the angle using the period of tangent. tan(x) repeats every π radians.
Reducing the input improves the accuracy and speed of the Taylor series.
"""
def reduce_angle(angle_in_radians):
    half_pi = PI / 2.0
    reduced_angle = ((angle_in_radians + half_pi) % PI) - half_pi

    return reduced_angle

# ------------------------------------------------------------
# Taylor series calculation
# ------------------------------------------------------------

def calculate_sine_and_cosine(x):
    sine_sign = 1.0
    swap_values = False

    # Reduce the Taylor series input to [0, PI/4].
    if x < 0:
        sine_sign = -1.0
        x = -x

    if x > PI / 4.0:
        x = PI / 2.0 - x
        swap_values = True

    # First terms of the sine and cosine series.
    sine_term = x
    sine_sum = x

    cosine_term = 1.0
    cosine_sum = 1.0

    term_number = 1

    # Repeatedly generate the next sine and cosine terms from the previous terms.
    while term_number <= MAX_ITERATIONS:
        sine_term = (
            -sine_term * x * x
            / (
                (2 * term_number)
                * (2 * term_number + 1)
            )
        )

        cosine_term = (
            -cosine_term * x * x
            / (
                (2 * term_number - 1)
                * (2 * term_number)
            )
        )

        sine_sum = sine_sum + sine_term
        cosine_sum = cosine_sum + cosine_term

        # Stop when both new terms are too small to affect the result.
        if (
            absolute_value(sine_term) < TOLERANCE
            and absolute_value(cosine_term) < TOLERANCE
        ):
            break

        term_number = term_number + 1

    if swap_values:
       return sine_sign * cosine_sum, sine_sum

    return sine_sign * sine_sum, cosine_sum


def calculate_tangent(angle_input, unit):

    # Remove spaces before and after the input.
    # FR-01: Accept one finite real-number angle.
    angle_text = angle_input.strip()


    # FR-05: Handle empty, non-numeric, and non-finite inputs.
    # NFR-06: Detect angles where tan(x) is undefined.
    if angle_text == "":
        raise InputError("Please enter an angle.")

    # Convert the user's text input into a floating-point number.
    # Handle input Exeptions.
    # FR-01: Accept one finite real-number angle.
    # FR-05: Handle empty, non-numeric, and non-finite inputs.
    # NFR-06: Detect angles where tan(x) is undefined.
    try:
        angle = float(angle_text)
    except ValueError as error:
        raise InputError(
            "Please enter a numeric angle, such as 20 or -0.4."
        ) from error

    # Reject NaN.
    if angle != angle:
        raise InputError("Please enter a valid number. 'nan' is not accepted.")

    # FR-02: Convert degree input to radians before the calculation.
    angle_in_radians = convert_to_radians(angle, unit)

    # Reject unsupported large angles and infinity.
    if absolute_value(angle_in_radians) > MAX_SUPPORTED_RADIANS:
        raise InputError(
            "Please enter an angle between -1,000,000 and 1,000,000 "
            "radians or the equivalent value in degrees."
        )


    # FR-03: Calculate tan(x) using the entered angle and selected unit.
    # FR-06: Use exceptions to handle input and calculation errors.
    # NFR-01: Produce an accurate result for defined inputs.
    # NFR-03: Implement the mathematical calculation from scratch.

    # Reduce the angle using the period of tangent. tan(x) repeats every π radians.
    # Reducing the input improves the accuracy and speed of the Taylor series.
    #  -π/2 <=  x  <  π/2
    x = reduce_angle(angle_in_radians)


    # tan(x) is undefined at PI/2 + k*PI.
    half_pi = PI / 2.0
    distance_from_undefined = absolute_value(
        absolute_value(x) - half_pi
    )

    if distance_from_undefined < TOLERANCE:
        raise UndefinedTangentError(
            "tan(x) is undefined at 90° + k × 180°  or  π/2 + k × π."
        )

    # Calculate sine and cosine directly with Taylor series.
    # FR-03: Calculate tan(x) using the entered angle and selected unit.
    # NFR-01: Produce an accurate result for defined inputs.
    sine_value, cosine_value = calculate_sine_and_cosine(x)

    # final check prevents division by a value very close to zero.
    # FR-06: Detect angles where tan(x) is undefined.
    # NFR-06: Use exceptions to handle input and calculation errors.
    if absolute_value(cosine_value) < TOLERANCE:
        raise UndefinedTangentError(
            "tan(x) is undefined because cos(x) is zero."
        )

    tangent_value = sine_value / cosine_value

    return tangent_value


# ------------------------------------------------------------
# Tkinter GUI
# ------------------------------------------------------------

def calculate_button_clicked():

    # Calculate tan(x) with angle_input and selected_unit.
    try:
        angle_input = angle_entry.get()
        selected_unit = unit_variable.get()

        result = calculate_tangent(
            angle_input,
            selected_unit
        )

  # FR-04: show the calculated result clearly in an identified result area.

        # Display the valid result clearly to six decimal places.
        result_variable.set(
            "Result: " + f"{result:.6f}"
        )

    except InputError as error:
        result_variable.set(
            "Input error: " + str(error)
        )

    except UndefinedTangentError as error:
        result_variable.set(
            "Undefined: " + str(error)
        )

    except ArithmeticError:
        # To catche unexpected arithmetic problems, such as an overflow or invalid division during the calculation.
        result_variable.set(
            "Calculation error: Please try a smaller angle."
        )

# Clear the current input and result.
def clear_button_clicked():
    angle_entry.delete(0, tk.END)
    unit_variable.set("Degrees")
    result_variable.set("Result will appear here.")
    angle_entry.focus_set()


# NFR-02: clear labels for the angle, unit, calculation action, and result.
# NFR-04: graphical user interface using Tkinter.
# NFR-05: run using a standard Python interpreter without depending on a particular IDE.
def create_gui():
    global angle_entry
    global unit_variable
    global result_variable

    window = tk.Tk()
    window.title("Tangent Calculator")

    main_frame = tk.Frame(
        window,
        padx=24,
        pady=20
    )
    main_frame.grid(row=0, column=0)

    angle_label = tk.Label(
        main_frame,
        text="Angle:"
    )

    angle_label.grid(
        row=1,
        column=0,
        sticky="w",
        padx=(0, 12),
        pady=6
    )

    angle_entry = tk.Entry(
        main_frame,
        width=24,
        font=("Arial", 11)
    )
    angle_entry.grid(
        row=1,
        column=1,
        pady=6
    )

    unit_label = tk.Label(
        main_frame,
        text="Unit:"
    )
    unit_label.grid(
        row=2,
        column=0,
        sticky="nw",
        padx=(0, 12),
        pady=6
    )

    unit_variable = tk.StringVar(
        value="Degrees"
    )

    unit_frame = tk.Frame(main_frame)
    unit_frame.grid(
        row=2,
        column=1,
        sticky="w",
        pady=6
    )

    degrees_button = tk.Radiobutton(
        unit_frame,
        text="Degrees",
        variable=unit_variable,
        value="Degrees"
    )
    degrees_button.grid(
        row=0,
        column=0,
        padx=(0, 12)
    )

    radians_button = tk.Radiobutton(
        unit_frame,
        text="Radians",
        variable=unit_variable,
        value="Radians"
    )
    radians_button.grid(
        row=0,
        column=1
    )

    button_frame = tk.Frame(main_frame)
    button_frame.grid(
        row=3,
        column=0,
        columnspan=2,
        pady=(15, 12)
    )

    calculate_button = tk.Button(
        button_frame,
        text="Calculate",
        width=11,
        command=calculate_button_clicked
    )
    calculate_button.grid(
        row=0,
        column=0,
        padx=5
    )

    clear_button = tk.Button(
        button_frame,
        text="Clear",
        width=11,
        command=clear_button_clicked
    )
    clear_button.grid(
        row=0,
        column=1,
        padx=5
    )


    result_variable = tk.StringVar(
        value="Result will appear here."
    )

    result_label = tk.Label(
        main_frame,
        textvariable=result_variable,
        width=48,
        height=3,
        wraplength=360,
        justify="left",
        anchor="w",
        relief="sunken",
        padx=10,
        pady=8
    )
    result_label.grid(
        row=4,
        column=0,
        columnspan=2,
        sticky="ew"
    )

    help_label = tk.Label(
        main_frame,
        text=(
            "Tangent is undefined at 90° + k × 180°."
        ),
        justify="left"
    )
    help_label.grid(
        row=5,
        column=0,
        columnspan=2,
        sticky="w",
        pady=(12, 0)
    )

    # Pressing Enter calculates the result.
    # Pressing Escape clears the fields.
    window.bind(
        "<Return>",
        lambda event: calculate_button_clicked()
    )
    window.bind(
        "<Escape>",
        lambda event: clear_button_clicked()
    )

    angle_entry.focus_set()
    window.mainloop()

if __name__ == "__main__":
    create_gui()