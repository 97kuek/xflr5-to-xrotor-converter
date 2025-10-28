# -*- coding: utf-8 -*-

import os
import re
import math
import numpy as np

class AeroLogic:
    """This class handles the data loading, parsing, and aerodynamic calculations."""

    def __init__(self):
        self.polar_file = ''
        self.zero_lift_alpha = 0
        self.dcl_dalpha = 0
        self.dcl_dalpha_stall = 0
        self.max_cl = 0
        self.min_cl = 0
        self.cl_increment_to_stall = 0
        self.min_cd = 0
        self.cl_at_min_cd = 0
        self.dcd_ddcl = 0
        self.re = 0
        self.r_R = 0
        self.alpha_list = []
        self.cl_list = []
        self.cd_list = []

    def _load_polar_or_csv(self, path):
        """Robust loader: try polar text, then CSV fallback"""
        # --- First try as XFLR5 polar text ---
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            # Read Re from line 8 at a fixed position (legacy logic)
            Re_line = lines[7]
            Re = float(Re_line[29:33]) * 1e6
            re_val = math.floor(Re)
            # Skip the first 11 lines, space-separated
            aero = np.loadtxt(fname=path, skiprows=11).T
            return aero, re_val
        except Exception:
            pass  # Fallback to CSV

        # --- CSV/any text fallback ---
        # Extract only numbers from each line using regex and assume they are alpha, Cl, Cd in that order
        rows = []
        float_pat = re.compile(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?')  # 1.23, -4, 5e-3 etc.
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for ln in f:
                nums = float_pat.findall(ln)
                if len(nums) >= 3:
                    try:
                        a = float(nums[0])
                        cl = float(nums[1])
                        cd = float(nums[2])
                        rows.append([a, cl, cd])
                    except Exception:
                        # Skip this line
                        continue

        if len(rows) < 2:
            raise ValueError("Could not extract the first 3 columns (alpha, Cl, Cd) from the CSV. Few lines with at least 3 numbers were found.")

        data = np.asarray(rows, dtype=float)   # shape: (N, 3)
        aero = data.T                          # shape: (3, N) = [alpha, Cl, Cd]^T

        # Estimate Re from the filename (e.g., T1_Re0.110_M0.00.csv -> 0.110e6)
        re_val = 0
        m = re.search(r"Re([0-9.]+)", os.path.basename(path))
        if m:
            try:
                re_val = math.floor(float(m.group(1)) * 1e6)
            except Exception:
                re_val = 0

        return aero, re_val

    def calculate_model(self):
        """Calculate the aerodynamic model from the loaded polar data."""
        def get_close_index(t, s):
            delta = [abs(i - s) for i in t]
            return delta.index(min(delta))

        aero, re_val = self._load_polar_or_csv(self.polar_file)
        self.re = re_val

        # Filter data points based on the slope of the Cd-Cl curve
        # This is to identify the linear region of the lift curve
        check_posi = [i for i in range(len(aero[2]) - 1)
                      if (aero[2][i + 1] - aero[2][i]) / (aero[1][i + 1] - aero[1][i]) >= 0.05 and aero[1][i] > 0]
        cl_list = [aero[1][i] for i in range(len(aero[2]) - 1)
                   if abs((aero[2][i + 1] - aero[2][i]) / (aero[1][i + 1] - aero[1][i])) < 0.05]
        cd_list = [aero[2][i] for i in range(len(aero[2]) - 1)
                   if abs((aero[2][i + 1] - aero[2][i]) / (aero[1][i + 1] - aero[1][i])) < 0.05]
        self.cl_list = [aero[1][i] for i in range(len(aero[2]) - 1)]
        self.cd_list = [aero[2][i] for i in range(len(aero[2]) - 1)]
        self.alpha_list = [aero[0][i] * math.pi / 180 for i in range(len(aero[2]) - 1)]
        alpha_list = [aero[0][i] for i in range(len(aero[2]) - 1)
                      if abs((aero[2][i + 1] - aero[2][i]) / (aero[1][i + 1] - aero[1][i])) < 0.05]
        alpha_list_posi = [aero[0][i] for i in check_posi]
        cl_list_posi = [aero[1][i] for i in check_posi]

        # Perform a 2nd degree polynomial fit of the drag polar (Cd vs Cl)
        # Cd = a*Cl^2 + b*Cl + c
        res2 = np.polyfit(cl_list, cd_list, 2)
        # Cl at minimum Cd is -b / (2a)
        self.cl_at_min_cd = -res2[1] / (2 * res2[0])
        # Minimum Cd is c - b^2 / (4a)
        self.min_cd = -res2[1]**2 / (4 * res2[0]) + res2[2]
        # d(Cd)/d(Cl^2) is 'a'
        self.dcd_ddcl = res2[0]

        # Calculate the lift curve slope (dCl/dalpha) and zero-lift angle of attack
        cl_index = get_close_index(cl_list, self.cl_at_min_cd)
        cl_delta_deg = (cl_list[cl_index + 1] - cl_list[cl_index]) / (alpha_list[cl_index + 1] - alpha_list[cl_index])
        self.dcl_dalpha = float(cl_delta_deg * 180 / math.pi)
        alpha = alpha_list[cl_index]
        # alpha_CL=0 = alpha_j - CL_j / k
        self.zero_lift_alpha = float(alpha - cl_list[cl_index] / cl_delta_deg)

        # Maximum and minimum Cl
        self.max_cl = cl_list[-1]
        self.min_cl = cl_list[0]

        # Stall characteristics
        self.dcl_dalpha_stall = (max(cl_list_posi) - cl_list[-1]) / (
            alpha_list_posi[cl_list_posi.index(max(cl_list_posi))] - alpha_list[-1]) * 180 / math.pi
        self.cl_increment_to_stall = max(cl_list_posi) - cl_list[-1]

