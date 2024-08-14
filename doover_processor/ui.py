import logging
from datetime import datetime, timezone
from pydoover import ui


def construct_ui():

    ui_elems = (
        ui.AlertStream("significantEvent", "Notify me of any problems"),
        ui.NumericVariable("currentFlowRate", "Flow Rate (L/min)"),
        ui.NumericVariable("currentAmperage","Pump Amperage (Amps)"),
        ui.HiddenValue("lastRecordedTime"),
        ui.Submodule("detailsSubmodule", "Details", 
            children=[
                ui.NumericParameter("uplinkIntervalMins", "Reporting Interval (min)"),
                ui.Action("burstMode", "Burst Mode", requires_confirm=True),
                ui.NumericVariable("rawCurrent" , "Raw Current (mA)"),
                ui.NumericVariable("rawFlowCount", "Raw Flow Count (pulse)"),
                ui.NumericVariable("rawBattery", "Node Battery (V)",
                    dec_precision=2,
                    ranges=[
                        ui.Range("Low", 2.5, 3.0, ui.Colour.yellow),
                        ui.Range("Ok", 3.0, 3.3, ui.Colour.blue),
                        ui.Range("Good", 3.3, 4, ui.Colour.green),
                    ],
                ),
                ui.NumericVariable("lastRSSI", "Last RSSI"),
                ui.TextVariable("lastUsedGateway","LoRa Gatway"),
                ui.NumericVariable("signalStrength", "Signal Strength (%)",
                    dec_precision=0,
                    ranges=[
                        ui.Range("Poor", 0, 30, ui.Colour.red),
                        ui.Range("Ok", 30, 60, ui.Colour.blue),
                        ui.Range("Good", 60, 100, ui.Colour.green),
                    ],
                ),
            ] 
        ),
        ui.ConnectionInfo(name="connectionInfo",
            connection_type=ui.ConnectionType.periodic,
            connection_period=(10*60),
            next_connection=(10*60),
            offline_after=(20*60),
        )
    )
    return ui_elems
