#!/usr/bin/env python3
"""Apache-2.0 derivative harness: extract pinned OpenSim kernels, not its runtime.
Upstream copyright/licensing and unchanged snapshots reside in the upstream folder.
Authored storage, Bernstein evaluation, bisection and RK4 are explicitly separate.
"""

# Portions derived from OpenSim: Copyright (c) 2005-2017 Stanford University
# and the Authors. Licensed under Apache-2.0; retained LICENSE and NOTICE
# are in education/data/millard-reference-v1/upstream. This is a modified port.
from pathlib import Path
import hashlib,json,re,subprocess,tempfile

ROOT=Path(__file__).resolve().parents[2]
UP=ROOT/'education/data/millard-reference-v1/upstream'

def verified_source():
    manifest=json.loads((UP/'manifest.json').read_text())
    for rec in manifest['files']:
        assert hashlib.sha256((UP/rec['local_name']).read_bytes()).hexdigest()==rec['sha256'], rec
    return manifest

def definition(text, name, return_type, qualifier):
    pattern=re.escape(return_type)+r'\s+'+re.escape(qualifier)+r'\s*'+re.escape(name)+r'\s*\('
    match=re.search(pattern,text)
    if not match: raise ValueError(name)
    start=match.start(); brace=text.index('{',match.end()); level=1; end=brace+1
    # Remove comments only for brace counting, preserving character positions.
    clean=re.sub(r'/\*.*?\*/|//[^\n]*',lambda m:re.sub(r'[^\n]',' ',m.group()),text,flags=re.S)
    while level:
        if clean[end]=='{': level+=1
        if clean[end]=='}': level-=1
        end+=1
    return text[start:end]

PREAMBLE=r'''
#include <array>
#include <vector>
#include <cmath>
#include <limits>
#include <string>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <stdexcept>
#include <algorithm>
#define SimTK_ERRCHK_ALWAYS(c,...) do {if(!(c)) throw std::runtime_error("source validation");} while(0)
#define SimTK_ERRCHK1_ALWAYS(c,...) SimTK_ERRCHK_ALWAYS(c)
#define SimTK_ERRCHK2_ALWAYS(c,...) SimTK_ERRCHK_ALWAYS(c)
#define SimTK_ERRCHK3_ALWAYS(c,...) SimTK_ERRCHK_ALWAYS(c)
namespace SimTK {
constexpr double Eps=std::numeric_limits<double>::epsilon();
struct Vec6:std::array<double,6>{Vec6(double a,double b,double c,double d,double e,double f):std::array<double,6>{a,b,c,d,e,f}{}};
template<class T> using Array_=std::vector<T>;
}
using namespace std; using namespace SimTK;
class SegmentedQuinticBezierToolkit {
public: struct ControlPointsXY {Vec6 x,y;};
static ControlPointsXY calcQuinticBezierCornerControlPoints(double,double,double,double,double,double,double);
};
double bern(double u,const Vec6& p) {
 double t=1-u;return p[0]*pow(t,5)+5*p[1]*u*pow(t,4)+10*p[2]*u*u*t*t*t+10*p[3]*u*u*u*t*t+5*p[4]*pow(u,4)*t+p[5]*pow(u,5);
}
double deriv(double u,const Vec6&p){double t=1-u;return 5*((p[1]-p[0])*pow(t,4)+4*(p[2]-p[1])*u*t*t*t+6*(p[3]-p[2])*u*u*t*t+4*(p[4]-p[3])*u*u*u*t+(p[5]-p[4])*pow(u,4));}
struct SmoothSegmentedFunction {
 Array_<Vec6> X,Y; double x0,x1,y0,y1,d0,d1;
 SmoothSegmentedFunction(Array_<Vec6> x,Array_<Vec6> y,double a,double b,double c,double d,double e,double f,bool,bool,string):X(x),Y(y),x0(a),x1(b),y0(c),y1(d),d0(e),d1(f){}
 pair<double,double> value(double x)const{
  if(x<=x0)return {y0+d0*(x-x0),d0};if(x>=x1)return {y1+d1*(x-x1),d1};
  size_t j=0;while(j+1<X.size()&&x>X[j][5])++j;
  double lo=0,hi=1;for(int k=0;k<54;++k){double mid=(lo+hi)*.5;if(bern(mid,X[j])<x)lo=mid;else hi=mid;}
  double u=(lo+hi)*.5;return {bern(u,Y[j]),deriv(u,Y[j])/deriv(u,X[j])};
 }
};
class MuscleFirstOrderActivationDynamicModel {
public: static double clamp(double lo,double x,double hi){return max(lo,min(x,hi));} double get_minimum_activation()const{return .01;} double get_activation_time_constant()const{return .01;} double get_deactivation_time_constant()const{return .04;}
double calcDerivative(double,double)const;
};
'''
POSTAMBLE=r'''
int main(int argc,char**argv){
 if(argc!=2)return 2;string dir=argv[1];
 auto L=createFiberActiveForceLengthCurve(.4441,.73,1,1.8123,0,.8616,1,false,"active");
 auto V=createFiberForceVelocityCurve(1.4,0,.25,5,0,.15,.6,.9,false,"velocity");
 auto P=createFiberForceLengthCurve(0,.7,.2,2/.7,.75,false,"passive");
 auto T=createTendonForceLengthCurve(.049,1.375/.049,2./3,.5,false,"tendon");
 vector<SmoothSegmentedFunction*> curves{L,V,P,T}; vector<string> names{"active","velocity","passive","tendon"};
 ofstream cp(dir+"/native-controls.json");cp<<setprecision(17)<<"{";
 for(int i=0;i<4;++i){auto C=curves[i];if(i)cp<<",";cp<<"\""<<names[i]<<"\":{\"bounds\":["<<C->x0<<","<<C->x1<<","<<C->y0<<","<<C->y1<<","<<C->d0<<","<<C->d1<<"],\"segments\":[";
 for(size_t j=0;j<C->X.size();++j){if(j)cp<<",";cp<<"[";for(int axis=0;axis<2;++axis){if(axis)cp<<",";cp<<"[";for(int k=0;k<6;++k){if(k)cp<<",";cp<<(axis?C->Y[j][k]:C->X[j][k]);}cp<<"]";}cp<<"]";}cp<<"]}";}cp<<"}\n";
 ofstream samples(dir+"/native-kernels.csv");samples<<setprecision(17)<<"curve,x,value,derivative\n";
 for(int i=0;i<4;++i){double a=curves[i]->x0-.05,b=curves[i]->x1+.05;for(int k=0;k<=120;++k){double x=a+(b-a)*k/120;auto z=curves[i]->value(x);samples<<names[i]<<","<<x<<","<<z.first<<","<<z.second<<"\n";}}
 MuscleFirstOrderActivationDynamicModel activation;
 ofstream ad(dir+"/native-activation.csv");ad<<setprecision(17)<<"activation,excitation,derivative\n";
 for(double a:{0.,.01,.05,.2,.5,1.,1.1})for(double u:{.01,.05,.35,1.})ad<<a<<","<<u<<","<<activation.calcDerivative(a,u)<<"\n";
 auto inverseT=[&](double force){double lo=1,hi=1.1;for(int k=0;k<60;++k){double s=(lo+hi)/2;if(T->value(s).first<force)lo=s;else hi=s;}return (lo+hi)/2;};
 double lmt=.1+.2*inverseT(.05), force=L->value(1.1).first+P->value(1.1).first;
 auto velocity=[&](double a,double q,double f){double lo=-10,hi=10;auto balance=[&](double v){return calcFiberForce(100,a,L->value(q).first,V->value(v).first,P->value(q).first,v,.1)/100-f;};if(balance(lo)>0||balance(hi)<0)throw runtime_error("unbracketed velocity");for(int k=0;k<55;++k){double v=(lo+hi)*.5;if(balance(v)<0)lo=v;else hi=v;}return (lo+hi)*.5;};
 for(double dt:{.0001,.00005}){
  string suffix=dt==.0001?"coarse":"fine";
  for(int mode=0;mode<3;++mode){
   string name=mode==0?"held":mode==1?"force-plus":"force-minus";
   ofstream out(dir+"/native-"+name+"-"+suffix+".csv");out<<setprecision(17)<<"time,activation,q,tendon_force_N,velocity_normalized\n";
   array<double,2> z{mode==0?.05:1.,mode==0?1.:1.1+(mode==1?1:-1)*.0001};
   int steps=lround((mode==0?.3:.05)/dt);
   auto rhs=[&](const array<double,2>& y,double u){if(y[1]<=.4441)throw runtime_error("lower fiber bound");double ft=mode==0?T->value((lmt-.1*y[1])/.2).first:force;return array<double,2>{mode==0?activation.calcDerivative(y[0],u):0.,10*velocity(y[0],y[1],ft)};};
   for(int k=0;k<=steps;++k){double time=k*dt;double ft=mode==0?T->value((lmt-.1*z[1])/.2).first:force;double v=velocity(z[0],z[1],ft);if(k%lround(.001/dt)==0)out<<time<<","<<z[0]<<","<<z[1]<<","<<100*ft<<","<<v<<"\n";if(k==steps)break;
    double mid=(k+.5)*dt;double u=mid<.05?.05:mid<.15?.35:.05;
    auto a=rhs(z,u),tmp=z;for(int j=0;j<2;++j)tmp[j]=z[j]+.5*dt*a[j];auto b=rhs(tmp,u);for(int j=0;j<2;++j)tmp[j]=z[j]+.5*dt*b[j];auto c=rhs(tmp,u);for(int j=0;j<2;++j)tmp[j]=z[j]+dt*c[j];auto d=rhs(tmp,u);for(int j=0;j<2;++j)z[j]+=dt*(a[j]+2*b[j]+2*c[j]+d[j])/6;
   }
  }
 }
 cout<<"Pinned source kernels and six RK4 cases completed\n";
 delete L;delete V;delete P;delete T;
}
'''

def run(destination):
    verified_source();destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    factory=(UP/'SmoothSegmentedFunctionFactory.cpp').read_text()
    toolkit=(UP/'SegmentedQuinticBezierToolkit.cpp').read_text()
    code='// Modified derivative: extracted source kernels with authored benchmark shim.\n'+factory[:factory.index('//=============================================================================')]+PREAMBLE
    code+=definition(toolkit,'calcQuinticBezierCornerControlPoints','SegmentedQuinticBezierToolkit::ControlPointsXY','SegmentedQuinticBezierToolkit::')+'\n'
    code+=definition(factory,'scaleCurviness','double','SmoothSegmentedFunctionFactory::').replace('SmoothSegmentedFunctionFactory::','',1)+'\n'
    for name in ['createFiberActiveForceLengthCurve','createFiberForceVelocityCurve','createFiberForceLengthCurve','createTendonForceLengthCurve']:
        code+=definition(factory,name,'SmoothSegmentedFunction*','SmoothSegmentedFunctionFactory::').replace('SmoothSegmentedFunctionFactory::','',1)+'\n'
    code+=definition((UP/'MuscleFirstOrderActivationDynamicModel.cpp').read_text(),'calcDerivative','double','MuscleFirstOrderActivationDynamicModel::')+'\n'
    for name in ['calcFiberForceActive','calcFiberForcePassiveElastic','calcFiberForcePassiveDamping','calcFiberForce']:
        code+=definition((UP/'Millard2012EquilibriumMuscle.cpp').read_text(),name,'double','')+'\n'
    code+=POSTAMBLE
    with tempfile.TemporaryDirectory(prefix='kenoma-millard-native-') as tmp:
        cpp=Path(tmp)/'oracle.cpp';binary=Path(tmp)/'oracle';cpp.write_text(code)
        proc=subprocess.run(['g++','-std=c++17','-O2',str(cpp),'-o',str(binary)],capture_output=True,text=True)
        (destination/'native-build.log').write_text(proc.stdout+proc.stderr);proc.check_returncode()
        # Preserve generated translation unit for review; source bodies unchanged.
        (destination/'native-oracle.cpp').write_text(code)
        proc=subprocess.run([str(binary),str(destination)],capture_output=True,text=True)
        (destination/'native-run.log').write_text(proc.stdout+proc.stderr);proc.check_returncode()
    return code

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();run(args.output)
