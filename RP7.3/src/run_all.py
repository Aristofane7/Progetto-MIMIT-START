# -*- coding: utf-8 -*-
"""Orchestratore: rigenera input dimostrativi, coefficienti, AHP, equazioni, figure, report V1 e log."""
from src import make_demo_data, equations, figures, build_report
def main():
    make_demo_data.write_inputs(); make_demo_data.write_coefficients(); make_demo_data.write_ahp()
    equations.render_all(); figures.make_all()
    out,ntab=build_report.build()
    print("OK ->",out,"(",ntab,"tabelle )")
if __name__=="__main__":
    main()
