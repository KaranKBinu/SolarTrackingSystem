from django import forms


class SensorDataFilterForm(forms.Form):
    date = forms.DateField(
        label="Date",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Select Date YYYY-MM-DD",
                "type": "date",
            }
        ),
    )
    start_time = forms.TimeField(
        label="Start Time",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Select Time HH:MM",
                "type": "time",
            }
        ),
    )
    end_time = forms.TimeField(
        label="End Time",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Select Time HH:MM",
                "type": "time",
            }
        ),
    )
    voltage_value = forms.FloatField(
        label="Voltage Value",
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Voltage Value to filter",
                "type": "number",
            }
        ),
    )
    servo_angle = forms.FloatField(
        label="Servo Angle",
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Servo Angle to filter",
                "type": "number",
            }
        ),
    )
