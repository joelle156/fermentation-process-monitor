
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator


class BioprocessMonitor:
    def __init__(self, filepath, ph_lims, temperature_lims):

        self.filepath = filepath
        self.ph_lims = ph_lims
        self.temperature_lims = temperature_lims

    def extract_batch(self, batch_id):
        # Returns data corresponding to a batch #
        df = pd.read_csv(self.filepath)
        df_batch = df[df["batch_id"] == batch_id]
        return df_batch

    def optimal_ph_mask(self, df_batch):
        # Returns mask where True is within the acceptable range #
        ph_mask = (df_batch["pH"] >= self.ph_lims[0]) & (df_batch["pH"] <= self.ph_lims[1])
        return ph_mask

    def optimal_temperature_mask(self, df_batch):
        # Returns mask where True is within the acceptable range #
        temperature_mask = (df_batch["temperature_C"] >= self.temperature_lims[0]) & (
                df_batch["temperature_C"] <= self.temperature_lims[1])
        return temperature_mask

    def get_n_batches(self):
        # Returns number of batches #
        df = pd.read_csv(self.filepath)
        return len(set(df["batch_id"]))

    def export_dashboard(self, batch_id, filepath):

        df_batch = self.extract_batch(batch_id)
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 10), dpi=200, layout="constrained")
        (ax_top_left, ax_top_right), (ax_bottom_left, ax_bottom_right) = axes

        # Concentrations versus time, top left plot #
        ax_top_left.scatter(
            df_batch["time_h"],
            df_batch["C_glucose_g_L^-1"],
            color="tab:olive",
            marker="o",
            label="Glucose [g/L]",
        )
        ax_top_left.scatter(
            df_batch["time_h"],
            df_batch["C_biomass_g_L^-1"],
            color="tab:orange",
            marker="^",
            label="Biomass [g/L]",
        )
        ax_top_left.scatter(
            df_batch["time_h"],
            df_batch["C_product_g_L^-1"],
            color="tab:purple",
            marker="v",
            label="Product [g/L]",
        )
        ax_top_left.set_ylabel("Concentration [g/L]", fontsize=10)
        ax_top_left.legend(loc="upper right", fontsize=10)

        # Temperature versus time, top right plot #
        temperature_mask = self.optimal_temperature_mask(df_batch)

        ax_top_right.scatter(
            df_batch.loc[temperature_mask, "time_h"],
            df_batch.loc[temperature_mask, "temperature_C"],
            color="tab:green",
            marker="o",
            label="Optimal"
        )
        ax_top_right.scatter(
            df_batch.loc[~temperature_mask, "time_h"],
            df_batch.loc[~temperature_mask, "temperature_C"],
            color="tab:red",
            marker="x",
            label="Sub-Optimal"
        )
        ax_top_right.set_ylabel("Temperature [C]", fontsize=10)
        ax_top_right.legend(loc="upper right", fontsize=10)

        # pH versus time, bottom left plot #
        ph_mask = self.optimal_ph_mask(df_batch)

        ax_bottom_left.scatter(
            df_batch.loc[ph_mask, "time_h"],
            df_batch.loc[ph_mask, "pH"],
            color="tab:green",
            marker="o",
            label="Optimal"
        )
        ax_bottom_left.scatter(
            df_batch.loc[~ph_mask, "time_h"],
            df_batch.loc[~ph_mask, "pH"],
            color="tab:red",
            marker="x",
            label="Sub-Optimal"
        )
        ax_bottom_left.set_ylabel("pH", fontsize=10)
        ax_bottom_left.legend(loc="upper right", fontsize=10)

        # Dissolved Oxygen versus time, bottom right plot #
        ax_bottom_right.scatter(
            df_batch["time_h"],
            df_batch["DO_percent"],
            color="tab:blue",
            marker="o",
        )
        ax_bottom_right.set_ylabel("Dissolved Oxygen (DO) [%]", fontsize=10)

        for ax in np.ravel(axes):
            ax.xaxis.set_major_locator(MultipleLocator(6))
            ax.set_xlabel("Time [h]", fontsize=10)

        # Save and close Figure #
        fig.savefig(filepath)
        plt.close(fig)

    def export_summary(self, filepath):

        df = pd.read_csv(self.filepath)
        summary_table = []

        # for loop so the values are calculated/extracted for each batch ID #
        for batch_id, df_batch in df.groupby("batch_id"):
            ph_mask = self.optimal_ph_mask(df_batch)
            temperature_mask = self.optimal_temperature_mask(df_batch)

            # Calculates optimal percent #
            ph_optimal_percent = round(ph_mask.sum() / len(df_batch) * 100, 2)
            temperature_optimal_percent = round(temperature_mask.sum() / len(df_batch) * 100, 2)

            # Extract the concentration at the final time #
            final_time = df_batch.sort_values("time_h").iloc[-1]
            final_concentration = final_time["C_product_g_L^-1"]

            # Add data to empty table generated earlier #
            summary_table.append(
                {
                    "batch_id": batch_id,
                    "ph_optimal_percent": ph_optimal_percent,
                    "temperature_optimal_percent": temperature_optimal_percent,
                    "C_product_g_L^-1_final": final_concentration
                }
            )
        # Export #
        df_table = pd.DataFrame(summary_table)
        df_table.to_csv(filepath, index=False)
