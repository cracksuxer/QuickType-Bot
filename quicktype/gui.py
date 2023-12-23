import PySimpleGUI as sg


def start_gui():
    sg.theme("DarkAmber")  # Add a touch of color
    # All the stuff inside your window.
    layout = [
        [sg.Text("QuickType bot", size=(30, 1), font=("Helvetica", 25), justification="center")],
        [sg.Text("Browser to use:")],
        [sg.OptionMenu(["Option 1", "Option 2", "Option 3"], default_value="")],
        [],
        [sg.Text("Bot parameters:")],
        [sg.Text("Param"), sg.InputText()],
        [sg.Text("Param 2"), sg.InputText()],
        [sg.Text("Param 3"), sg.InputText()],
        [sg.Button("Start"), sg.Button("Cancel")],
    ]

    # Create the Window
    window = sg.Window("QuickType bot", layout)
    
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Cancel"):  # if user closes window or clicks cancel
            break

        print(f"Event triggered: {event}")
        print("You entered ", values[0])
        print("You selected ", values[1])

    window.close()
