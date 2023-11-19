# Note:   Compute discharge
# Author: Kleomenis Katevas (kkatevas@brave.com)
# Date:   06/02/2023


def compute_power_performance(df, current_col="current", voltage_col="voltage"):
    # input is a df with columns: timestamp (sec), current (mA), voltage (V)

    power = df[current_col] * df[voltage_col]  # in mW
    time_diff = df.timestamp.diff().fillna(0) / 3600  # in hours

    # energy
    energy = power * time_diff  # in mWh
    total_energy_mWh = energy.sum()  # in mWh

    # discharge
    discharge = df[current_col] * time_diff  # in mAh
    total_discharge_mAh = discharge.sum()  # in mAh

    return total_energy_mWh, total_discharge_mAh
