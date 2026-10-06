#!/usr/bin/env python3
"""Bounded Apache-2.0 derivative translation of pinned OpenSim Millard kernels.
Original Stanford/author notices and source are retained under data/upstream.
Independent SciPy BPoly/root/ODE paths compare to extracted native kernels/RK4.
No OpenSim runtime, controller, continuum or physiological calibration claim.
"""

# Portions derived from OpenSim: Copyright (c) 2005-2017 Stanford University
# and the Authors. Licensed under Apache-2.0; retained LICENSE and NOTICE
# are in education/data/millard-reference-v1/upstream. This is a modified port.
from pathlib import Path
import csv,json,math,time,platform
import numpy as np
from scipy.interpolate import BPoly
from scipy.optimize import brentq
from scipy.integrate import solve_ivp,quad
from millard_source_oracle import verified_source

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'education/data/millard-reference-v1/review'
PARAMS={'F0_N':100.,'optimal_length_m':.1,'tendon_slack_length_m':.2,'pennation_rad':0.,'vmax_optimal_lengths_per_s':10.,'damping_beta':.1,'tau_activation_s':.01,'tau_deactivation_s':.04,'minimum_activation':.01,'initial_activation':.05,'active':[.4441,.73,1.,1.8123,0.,.8616,1.],'velocity':[1.4,0.,.25,5.,0.,.15,.6,.9],'passive':[0.,.7,.2,2/.7,.75],'tendon':[.049,1.375/.049,2/3,.5]}

def corner(x0,y0,d0,x1,y1,d1,c):
    xc=(y1-y0-x1*d1+x0*d0)/(d0-d1) if abs(d0-d1)>math.sqrt(np.finfo(float).eps) else (x0+x1)/2
    yc=(xc-x1)*d1+y1
    assert (x1-x0)**2+(y1-y0)**2>max((xc-x0)**2+(yc-y0)**2,(xc-x1)**2+(yc-y1)**2)
    return [[x0,x0+c*(xc-x0),x0+c*(xc-x0),x1+c*(xc-x1),x1+c*(xc-x1),x1],[y0,y0+c*(yc-y0),y0+c*(yc-y0),y1+c*(yc-y1),y1+c*(yc-y1),y1]]

def build_curves():
    x0,x1,x2,x3,floor,slope,curv=PARAMS['active'];c=.1+.8*curv;dx=.05*x2;xs=x2-dx;y1=1-slope*(xs-x1);d01=1.25*y1/(x1-x0)
    joints=[(x0,floor,0),((x0+x1)/2,y1/2,d01),((x1+xs)/2,(y1+1)/2,slope),(x2,1,0),((x2+dx+x3)/2,.5,-1/((x3-dx)-(x2+dx))),(x3,floor,0)]
    active={'bounds':[x0,x3,floor,floor,0,0],'segments':[corner(*joints[i],*joints[i+1],c) for i in range(5)]}
    fmax,dc,dnc,di,de,dne,cc,ce=PARAMS['velocity']
    joints=[(-1,0,dc),(-.9,.05*(dnc+dc),dnc),(0,1,di),(.9,fmax-.05*(dne+de),dne),(1,fmax,de)]
    velocity={'bounds':[-1,1,0,fmax,dc,de],'segments':[corner(*joints[i],*joints[i+1],.1+.8*(cc if i<2 else ce)) for i in range(4)]}
    ez,ei,kl,ki,curv=PARAMS['passive'];xz=1+ez;xi=1+ei;delta=min(.1/ki,.1*(xi-xz));xl=xz+delta;yl=kl*delta/2;c=.1+.8*curv
    passive={'bounds':[xz,xi,0,1,0,ki],'segments':[corner(xz,0,0,xl,yl,kl,c),corner(xl,yl,kl,xi,1,ki,c)]}
    ei,ki,toe,curv=PARAMS['tendon'];xi=1+ei;xt=(toe-1)/ki+xi;foot=1+(xt-1)/10;mid=(toe/2-1)/ki+xi;dmid=(toe/2)/(mid-foot);ctrl=foot+.5*(mid-foot);yc=dmid*(ctrl-foot);c=.1+.8*curv
    tendon={'bounds':[1,xt,0,toe,0,ki],'segments':[corner(1,0,0,ctrl,yc,dmid,c),corner(ctrl,yc,dmid,xt,toe,ki,c)]}
    return dict(active=active,velocity=velocity,passive=passive,tendon=tendon)

class Curve:
    def __init__(self,record):
        self.bounds=record['bounds'];self.controls=record['segments'];self.polys=[BPoly(np.asarray(p).T[:,None,:],[0.,1.]) for p in self.controls];self.derivs=[b.derivative() for b in self.polys]
    def value(self,x,derivative=False):
        x0,x1,y0,y1,d0,d1=self.bounds
        if x<=x0:return d0 if derivative else y0+d0*(x-x0)
        if x>=x1:return d1 if derivative else y1+d1*(x-x1)
        j=next(i for i,p in enumerate(self.controls) if x<=p[0][-1]);b=self.polys[j]
        u=brentq(lambda u:float(b(u)[0])-x,0,1,xtol=5e-15,rtol=1e-15)
        if derivative:
            dx,dy=self.derivs[j](u);return float(dy/dx)
        return float(b(u)[1])
    def integral(self,a,b):
        points=sorted(set(p[0][0] for p in self.controls)|set(p[0][-1] for p in self.controls))
        return quad(self.value,a,b,points=[p for p in points if min(a,b)<p<max(a,b)],epsabs=1e-12,epsrel=1e-11)[0]

def activation_rhs(a,u):
    a=float(np.clip(a,.01,1));tau=.01*(.5+1.5*a) if u>a else .04/(.5+1.5*a)
    return (u-a)/tau

def exact_activation(a0,u,t):
    if a0==u:return a0
    if u>a0:
        return brentq(lambda a:.01*(-1.5*(a-a0)-(.5+1.5*u)*math.log((u-a)/(u-a0)))-t,a0,np.nextafter(u,a0),xtol=1e-14)
    r=(a0-u)/(.5+1.5*a0)*math.exp(-(.5+1.5*u)*t/.04)
    return (u+.5*r)/(1-1.5*r)

def write_csv(path,fields,rows):
    with path.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(fields);w.writerows(rows)

def run(output=OUT):
    started=time.monotonic();output=Path(output);manifest=verified_source();records=build_curves();curves={name:Curve(rec) for name,rec in records.items()};L,V,P,T=[curves[n] for n in ['active','velocity','passive','tendon']]
    native=json.loads((output/'native-controls.json').read_text());cp_error=max(float(np.max(np.abs(np.asarray(records[n]['segments'])-np.asarray(native[n]['segments'])))) for n in curves)
    value_error=derivative_error=0.
    with (output/'native-kernels.csv').open() as f:
        for rec in csv.DictReader(f):
            C=curves[rec['curve']];x=float(rec['x']);value_error=max(value_error,abs(C.value(x)-float(rec['value'])));derivative_error=max(derivative_error,abs(C.value(x,True)-float(rec['derivative'])))
    activation_error=0.
    with (output/'native-activation.csv').open() as f:
        for rec in csv.DictReader(f):activation_error=max(activation_error,abs(activation_rhs(float(rec['activation']),float(rec['excitation']))-float(rec['derivative'])))
    samples=np.linspace(.5,1.8,261);fd_error=max(abs(L.value(x,True)-(L.value(x+1e-6)-L.value(x-1e-6))/2e-6) for x in samples)
    inverse=lambda f:brentq(lambda s:T.value(s)-f,1,1.1,xtol=5e-15)
    lmt=.1+.2*inverse(.05);force=L.value(1.1)+P.value(1.1);max_force_residual=0.
    initial_root=brentq(lambda q:.05*L.value(q)+P.value(q)-T.value((lmt-.1*q)/.2),.99,1.01,xtol=5e-15)
    def velocity(a,q,ft):
        nonlocal max_force_residual
        if not np.isfinite(q) or q<=.4441:raise ValueError('fiber length violates lower bound; state/time not advanced')
        fal=L.value(q);fpe=P.value(q)
        def balance(v):return a*fal*V.value(v)+fpe+.1*v-ft
        v=brentq(balance,-10.,10.,xtol=5e-15,rtol=1e-15)
        max_force_residual=max(max_force_residual,100*abs(balance(v)))
        return v
    trajectories={};max_native_difference=max_method_difference=max_refinement_difference=0.;exact_error=0.;held_dense=[]
    for mode in ['held','force-plus','force-minus']:
        grid=np.arange(301 if mode=='held' else 51)*.001
        initial=np.array([.05,1.]) if mode=='held' else np.array([1.,1.1+(1 if mode=='force-plus' else -1)*.0001])
        solutions={}
        for method in ['DOP853','Radau']:
            current=initial.copy();all_values=[]
            intervals=[(0.,.05,.05),(.05,.15,.35),(.15,.3,.05)] if mode=='held' else [(0.,.05,1.)]
            for ti,tf,u in intervals:
                def rhs(t,y):
                    ft=T.value((lmt-.1*y[1])/.2) if mode=='held' else force
                    return [activation_rhs(y[0],u) if mode=='held' else 0.,10*velocity(y[0],y[1],ft)]
                sol=solve_ivp(rhs,[ti,tf],current,method=method,rtol=2e-10,atol=2e-12,dense_output=True,max_step=.002)
                if not sol.success:raise RuntimeError(sol.message)
                if mode=='held' and method=='DOP853':held_dense.append((ti,tf,sol.sol))
                selected=grid[(grid>=ti-1e-14)&(grid<=tf+1e-14)]
                if all_values:selected=selected[1:]
                vals=sol.sol(selected).T;all_values.extend(vals);current=sol.y[:,-1]
            solutions[method]=np.asarray(all_values)
        data=solutions['DOP853'];max_method_difference=max(max_method_difference,float(np.max(np.abs(data-solutions['Radau']))))
        nf=np.genfromtxt(output/f'native-{mode}-fine.csv',delimiter=',',names=True);nc=np.genfromtxt(output/f'native-{mode}-coarse.csv',delimiter=',',names=True)
        assert len(nf)==len(grid) and np.max(abs(nf['time']-grid))<1e-12
        nfv=np.column_stack([nf['activation'],nf['q']]);ncv=np.column_stack([nc['activation'],nc['q']]);max_native_difference=max(max_native_difference,float(np.max(abs(nfv-data))));max_refinement_difference=max(max_refinement_difference,float(np.max(abs(nfv-ncv))))
        rows=[]
        for t,(a,q) in zip(grid,data):
            ft=T.value((lmt-.1*q)/.2) if mode=='held' else force;v=velocity(a,q,ft)
            rows.append([t,a,q,100*ft,v,100*a*L.value(q)*V.value(v),100*P.value(q),100*.1*v])
            if mode=='held':
                if t<=.05:ax=.05
                elif t<=.15:ax=exact_activation(.05,.35,t-.05)
                else:ax=exact_activation(exact_activation(.05,.35,.1),.05,t-.15)
                exact_error=max(exact_error,abs(a-ax))
        trajectories[mode]=np.asarray(rows);write_csv(output/f'python-{mode}.csv',['time','activation','q','tendon_force_N','velocity_normalized','active_force_N','passive_force_N','damping_force_N'],rows)
    total_slope=L.value(1.1,True)+P.value(1.1,True);growth=-10*total_slope/(L.value(1.1)*V.value(0,True)+.1)
    dynamic_fd=(10*velocity(1,1.1+1e-6,force)-10*velocity(1,1.1-1e-6,force))/2e-6
    perturbation_ratios={name:float(abs(trajectories[name][-1,2]-1.1)/.0001) for name in ['force-plus','force-minus']}
    rejected=None
    try:velocity(.05,.4,.05)
    except ValueError as e:rejected={'q':.4,'accepted':False,'advanced_time':False,'message':str(e)}
    assert rejected is not None
    held=trajectories['held'];tf0=(lmt-.1*held[0,2])/.2;tff=(lmt-.1*held[-1,2])/.2
    stored_delta=100*(.1*P.integral(1,held[-1,2])+.2*T.integral(tf0,tff))
    active_power=-held[:,5]*(.1*10*held[:,4]);dissipation=100*.1*(.1*10)*held[:,4]**2
    coarse_work=float(np.trapezoid(active_power-dissipation,held[:,0]))
    def dense_power(t,solution):
        a,q=solution(t);ft=T.value((lmt-.1*q)/.2);v=velocity(a,q,ft)
        return -100*a*L.value(q)*V.value(v)*(.1*10*v)-100*.1*(.1*10)*v*v
    quadratures=[quad(lambda t:dense_power(t,solution),ti,tf,epsabs=1e-11,epsrel=1e-9) for ti,tf,solution in held_dense]
    work=sum(q[0] for q in quadratures);work_error=abs(stored_delta-work)
    summary={'scope':'bounded source-kernel/ODE reproduction, not full OpenSim or human calibration','upstream_commit':manifest['commit'],'parameters':PARAMS,'initial_total_length_m':lmt,'initial_static_residual_N':100*abs(T.value((lmt-.1)/.2)-.05),'force_clamp_N':100*force,'control_point_error':cp_error,'curve_value_error':value_error,'curve_derivative_native_error':derivative_error,'active_derivative_finite_difference_error':fd_error,'activation_kernel_error':activation_error,'activation_exact_branch_error':exact_error,'max_force_balance_residual_N':max_force_residual,'native_fine_vs_DOP853_max_state_error':max_native_difference,'native_coarse_fine_max_state_error':max_refinement_difference,'DOP853_Radau_max_state_error':max_method_difference,'descending_total_slope_normalized':total_slope,'descending_growth_rate_per_s':growth,'growth_rate_finite_difference_per_s':dynamic_fd,'perturbation_magnitude_ratios_at_0_05s':perturbation_ratios,'held_storage_change_J':stored_delta,'held_active_minus_damping_work_J':float(work),'held_work_quadrature_error_J':work_error,'invalid_case':rejected,'wall_seconds':time.monotonic()-started,'python':platform.python_version()}
    checks={'source_controls':cp_error<=2e-12,'source_curve_values':value_error<=2e-12,'source_curve_derivatives':derivative_error<=2e-8,'finite_difference_derivatives':fd_error<=2e-8,'activation_kernel':activation_error<=2e-12,'exact_activation':exact_error<=2e-8,'force_balance':max_force_residual<=1e-7,'matched_time_native':max_native_difference<=2e-6,'native_refinement':max_refinement_difference<=2e-6,'independent_ODE':max_method_difference<=2e-6,'descending_retained':total_slope<0 and growth>0 and min(perturbation_ratios.values())>1,'invalid_rejected':rejected['accepted'] is False and rejected['advanced_time'] is False,'work_balance':work_error<=1e-5}
    summary.update(initial_static_root_q=initial_root,held_coarse_1ms_work_J=coarse_work,held_coarse_1ms_work_error_J=abs(stored_delta-coarse_work),held_adaptive_quadrature_reported_error_J=sum(q[1] for q in quadratures))
    checks['independent_static_initialization']=abs(initial_root-1)<2e-12 and summary['initial_static_residual_N']<=1e-7
    checks={name:bool(value) for name,value in checks.items()}
    summary['checks']=checks;summary['passed']=all(checks.values());(output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2));assert summary['passed'],checks
    return summary

if __name__=='__main__':run()
