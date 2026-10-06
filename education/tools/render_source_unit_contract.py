"""Render a conditional unit/force-path diagram; no physical calibration or solve."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt',type=Path,required=True)
    parser.add_argument('--output-prefix',type=Path,required=True)
    args=parser.parse_args()
    receipt=json.loads(args.receipt.read_text())
    assert receipt['result']=='PASS_EXACT_CONDITIONAL_UNIT_AND_TOPOLOGY_AUDIT'
    assert receipt['physicalCalibrationSelected'] is False
    png=args.output_prefix.with_suffix('.png')
    pdf=args.output_prefix.with_suffix('.pdf')
    if png.exists() or pdf.exists():
        raise FileExistsError('Existing render must not be overwritten')
    fig=plt.figure(figsize=(12,8),facecolor='#f6f8fc')
    ax=fig.add_axes([0,0,1,1]);ax.set_axis_off()
    fig.text(.05,.93,'Conditional units and force paths',fontsize=22,weight='bold',color='#18243d')
    fig.text(.05,.885,'Exact algebra checked. Physical specimen calibration remains missing.',fontsize=13,color='#394a64')
    boxes=[(.05,'1  Supply physical normalizers',
        'C = Tref × Fscale   [N]\nℓ = Lref / Γ   [m]\nΓ is dimensionless; γ = 2 Ns dps is a length.',
        'Missing paired force / area / tare\nand reference length ledger'),
        (.365,'2  Convert one compatible circuit',
        'Smooth PE prefactor: C kpe / K   [N]\nPE width: ℓ / K   [m]; slope: C kpe / ℓ   [N/m]\nSE prefactor: C kse0   [N]; exponent: kse / ℓ   [1/m]',
        'Smooth PE branch only\nPublished parity unresolved'),
        (.68,'3  Declare area and force topology',
        'Parallel capacity: T = H kCB dps Q\nSerial count: adds length / energy; same force\nCauchy = (λ / J) × nominal stress',
        'PCSA vs projected FCSA:\ncosine applied once')]
    for x,title,body,note in boxes:
        ax.add_patch(plt.Rectangle((x,.46),.27,.35,facecolor='white',edgecolor='#c3cce0',lw=1.2))
        fig.text(x+.015,.765,title,fontsize=11.5,weight='bold',color='#183355')
        fig.text(x+.015,.695,body,fontsize=10.3,linespacing=2,color='#243650')
        fig.text(x+.015,.495,note,fontsize=9.3,color='#675321',wrap=True)
    fig.text(.05,.37,'What the audit establishes',fontsize=16,weight='bold',color='#18243d')
    fig.text(.05,.285,
        '12 exact identities     •     4 intended dimensional rejections\n'
        '2 unit-consistent mechanical errors exposed: serial-force multiplication and double pennation projection',
        fontsize=13,linespacing=1.8,color='#243650')
    fig.text(.05,.17,'No empirical calibration, kinetic ODE, tissue solve or convergence comparison.',fontsize=12,color='#675321')
    fig.text(.05,.09,'Frozen base bc4f24a2  |  Source-unit calibration audit  |  2026-10-06',fontsize=10,color='#52627a')
    fig.savefig(png,dpi=160)
    fig.savefig(pdf)
    plt.close(fig)
    print(json.dumps(dict(result='RENDERED_CONDITIONAL_UNIT_DIAGRAM',png=str(png),pdf=str(pdf),
        physicalCalibrationSelected=False,protocolCommit=receipt['protocolCommit'])))


if __name__=='__main__':
    main()
