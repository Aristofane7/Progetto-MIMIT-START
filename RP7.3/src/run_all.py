# -*- coding: utf-8 -*-
"""Orchestratore: rigenera input, coefficienti, AHP, template di raccolta, equazioni, figure, report e log."""
from src import make_demo_data, make_template, equations, figures, build_report
def main():
    make_demo_data.write_inputs(); make_demo_data.write_coefficients(); make_demo_data.write_ahp()
    make_template.build()
    equations.render_all(); figures.make_all()
    out,ntab=build_report.build()
    print("OK ->",out,"(",ntab,"tabelle )")
if __name__=="__main__":
    main()
