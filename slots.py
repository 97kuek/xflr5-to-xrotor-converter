# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets

class MainWindowSlots:
    """Slots for the main window."""

    def add_section(self, section_class):
        """Add a new section tab."""
        section = section_class()
        self.aero_sections.addTab(section, str(self.aero_sections.count() + 1))

    def delete_section(self):
        """Delete the current section tab."""
        self.aero_sections.removeTab(self.aero_sections.currentIndex())

    def build(self):
        """Build the XROTOR file from the section data."""
        count = self.aero_sections.count()
        output_aero_data = ''
        for i in range(count):
            section = self.aero_sections.widget(i)
            output_aero_data += "\n"
            output_aero_data += f" Section {i+1}   r/R = {section.r_R}\n"
            output_aero_data += " ====================================================================\n"
            output_aero_data += f" Zero-lift alpha (deg):  {section.aero_logic.zero_lift_alpha:<2.2f}        Minimum Cd           : {section.aero_logic.min_cd:<2.4f}\n"
            output_aero_data += f" d(Cl)/d(alpha)       :  {section.aero_logic.dcl_dalpha:<2.3f}        Cl at minimum Cd     : {section.aero_logic.cl_at_min_cd:<2.3f}\n"
            output_aero_data += f" d(Cl)/d(alpha)@stall :  {section.aero_logic.dcl_dalpha_stall:<2.3f}        d(Cd)/d(Cl**2)       : {section.aero_logic.dcd_ddcl:<2.4f}\n"
            output_aero_data += f" Maximum Cl           :  {section.aero_logic.max_cl:<2.2f}         Reference Re number  :  {section.aero_logic.re:<6.1f}\n"
            output_aero_data += f" Minimum Cl           : {section.aero_logic.min_cl:<2.2f}         Re scaling exponent  : -0.4000\n"
            output_aero_data += f" Cl increment to stall: {section.aero_logic.cl_increment_to_stall:<2.3f}         Cm                   : -0.100\n"
            output_aero_data += "                                      Mcrit                :  0.800\n"
            output_aero_data += " ====================================================================\n"

        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "/home")
        if fname:
            with open(fname, mode='w') as f:
                f.write(output_aero_data)
