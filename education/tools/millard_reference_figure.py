#!/usr/bin/env python3
"""Scientific summary of the bounded Millard reproduction; no arm shape claim."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from millard_reference_benchmark import OUT,build_curves,Curve


def render(destination=OUT):
    destination=Path(destination);s=json.loads((destination/'summary.json').read_text());C={n:Curve(r) for n,r in build_curves().items()}
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,2,figsize=(12,8));fig.subplots_adjust(left=.08,right=.97,bottom=.15,top=.87,hspace=.43,wspace=.29)
    fig.suptitle('Pinned Millard musculotendon reference cases',fontsize=19,y=.97)
    fig.text(.5,.925,'OpenSim 4.5.2 kernels · educational scales · zero pennation · compliant tendon',ha='center',fontsize=11,color='#444444')
    ax=axes[0,0];q=np.linspace(.5,1.7,241);fl=np.array([C['active'].value(x) for x in q]);fp=np.array([C['passive'].value(x) for x in q]);ax.plot(q,fl,label='Active, a = 1',color='#007c91');ax.plot(q,fp,label='Passive',color='#b97015');ax.plot(q,fl+fp,label='Total static',color='#333333',ls='--');ax.axvline(1.1,color='#a33',ls=':',lw=1);ax.set(xlabel='Fiber length / optimal length',ylabel='Force / peak force',title='Original force–length curves');ax.legend(fontsize=9,loc='upper right')
    ax=axes[0,1];v=np.linspace(-1,1,201);ax.plot(v,[C['velocity'].value(x) for x in v],color='#007c91',lw=2);ax.scatter([-1,0,1],[0,1,1.4],color='#333333',s=20);ax.set(xlabel='Velocity / maximum shortening speed',ylabel='Active velocity multiplier',title='Shortening < 0; lengthening > 0');ax.grid(alpha=.2)
    held=np.genfromtxt(destination/'python-held.csv',delimiter=',',names=True);ax=axes[1,0];t=held['time'];u=np.where(t<.05,.05,np.where(t<.15,.35,.05));ax.step(t,u,where='post',label='Excitation input',color='#888888',ls='--');ax.plot(t,held['activation'],label='Activation state',color='#007c91');ax.plot(t,held['tendon_force_N']/100,label='Actual tendon force / 100 N',color='#b97015');ax.set(xlabel='Time (s)',ylabel='Dimensionless level',title='Held length: force is a response');ax.legend(fontsize=9,loc='upper right')
    ax=axes[1,1]
    for name,color,label in [('force-plus','#007c91','Positive perturbation'),('force-minus','#b97015','Negative perturbation')]:
        z=np.genfromtxt(destination/f'python-{name}.csv',delimiter=',',names=True);ax.plot(z['time'],(z['q']-1.1)/1e-4,color=color,label=label)
    ax.set(xlabel='Time (s)',ylabel='Length perturbation / initial magnitude',title='Fixed force: descending instability retained');ax.legend(fontsize=9,loc='center left');ax.grid(alpha=.2)
    fig.text(.08,.072,f"Kernel value error {s['curve_value_error']:.2e}  |  matched-time state error {s['native_fine_vs_DOP853_max_state_error']:.2e}",fontsize=10)
    fig.text(.08,.043,f"Growth rate {s['descending_growth_rate_per_s']:.4f} /s  |  force residual {s['max_force_balance_residual_N']:.2e} N  |  adaptive work error {s['held_work_quadrature_error_J']:.2e} J",fontsize=10)
    fig.text(.08,.015,'Source-kernel and ODE reproduction only; no controller, whole-arm stability, or human calibration claim.',fontsize=9,color='#555555')
    fig.savefig(destination/'reference-cases.png',dpi=200);fig.savefig(destination/'reference-cases.pdf');plt.close(fig)
    print('Rendered PNG and one-page PDF')

if __name__=='__main__':render()
