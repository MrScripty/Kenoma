// Modified derivative: extracted source kernels with authored benchmark shim.
/* -------------------------------------------------------------------------- *
 *                OpenSim:  SmoothSegmentedFunctionFactory.cpp                *
 * -------------------------------------------------------------------------- *
 * The OpenSim API is a toolkit for musculoskeletal modeling and simulation.  *
 * See http://opensim.stanford.edu and the NOTICE file for more information.  *
 * OpenSim is developed at Stanford University and supported by the US        *
 * National Institutes of Health (U54 GM072970, R24 HD065690) and by DARPA    *
 * through the Warrior Web program.                                           *
 *                                                                            *
 * Copyright (c) 2005-2017 Stanford University and the Authors                *
 * Author(s): Matthew Millard                                                 *
 *                                                                            *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may    *
 * not use this file except in compliance with the License. You may obtain a  *
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0.         *
 *                                                                            *
 * Unless required by applicable law or agreed to in writing, software        *
 * distributed under the License is distributed on an "AS IS" BASIS,          *
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   *
 * See the License for the specific language governing permissions and        *
 * limitations under the License.                                             *
 * -------------------------------------------------------------------------- */

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
SegmentedQuinticBezierToolkit::ControlPointsXY
    SegmentedQuinticBezierToolkit::calcQuinticBezierCornerControlPoints(
        double x0,
        double y0,
        double dydx0,
        double x1,
        double y1,
        double dydx1,
        double curviness)
{
    SimTK_ERRCHK_ALWAYS( (curviness>=0 && curviness <= 1) , 
        "SegmentedQuinticBezierToolkit::calcQuinticBezierCornerControlPoints", 
        "Error: double argument curviness must be between 0.0 and 1.0.");


    //1. Calculate the location where the two lines intersect
    // (x-x0)*dydx0 + y0 = (x-x1)*dydx1 + y1
    //   x*(dydx0-dydx1) = y1-y0-x1*dydx1+x0*dydx0
    //                 x = (y1-y0-x1*dydx1+x0*dydx0)/(dydx0-dydx1);

    double xC = 0;
    double yC = 0;
    double rootEPS = sqrt(SimTK::Eps);
    if(abs(dydx0-dydx1) > rootEPS){
        xC = (y1-y0-x1*dydx1+x0*dydx0)/(dydx0-dydx1);    
    }else{
        xC = (x1+x0)/2;
    }

    yC = (xC-x1)*dydx1 + y1;
    //Check to make sure that the inputs are consistent with a corner, and will
    //not produce an 's' shaped section. To check this we compute the sides of
    //a triangle that is formed by the two points that the user entered, and 
    //also the intersection of the 2 lines the user entered. If the distance
    //between the two points the user entered is larger than the distance from
    //either point to the intersection location, this function will generate a
    //'C' shaped curve. If this is not true, an 'S' shaped curve will result, 
    //and this function should not be used.

    double xCx0 = (xC-x0);
    double yCy0 = (yC-y0);
    double xCx1 = (xC-x1);
    double yCy1 = (yC-y1);
    double x0x1 = (x1-x0);
    double y0y1 = (y1-y0);

    double a = xCx0*xCx0 + yCy0*yCy0;
    double b = xCx1*xCx1 + yCy1*yCy1;
    double c = x0x1*x0x1 + y0y1*y0y1;

    //This error message needs to be better.
    SimTK_ERRCHK_ALWAYS( ((c > a) && (c > b)), 
        "SegmentedQuinticBezierToolkit::calcQuinticBezierCornerControlPoints", 
        "The intersection point for the two lines defined by the input"
        "parameters must be consistent with a C shaped corner.");

    /*
    //New mid point control code, which spreads the curve out more gradually    
    double deltaX   = (xC-xyPts(0,0));    
    double deltaY   = (yC-xyPts(0,1));
    double sinCPi   = sin(curviness*SimTK::Pi);

    //First two midpoints
    xyPts(1,0) = x0 + (curviness - 0.25*sinCPi)*deltaX;
    xyPts(1,1) = y0 + (curviness - 0.25*sinCPi)*deltaY;
    xyPts(2,0) = x0 + (curviness + 0.25*sinCPi)*deltaX;
    xyPts(2,1) = y0 + (curviness + 0.25*sinCPi)*deltaY;

    //Second two midpoints
    deltaX   = (xC-xyPts(5,0));    
    deltaY   = (yC-xyPts(5,1));

    xyPts(3,0) = xyPts(5,0) + (curviness - 0.25*sinCPi)*deltaX;
    xyPts(3,1) = xyPts(5,1) + (curviness - 0.25*sinCPi)*deltaY;
    xyPts(4,0) = xyPts(5,0) + (curviness + 0.25*sinCPi)*deltaX;
    xyPts(4,1) = xyPts(5,1) + (curviness + 0.25*sinCPi)*deltaY;
    */
    
    //Original code - leads to 2 localized corners
    double x0_mid = x0 + curviness*(xCx0);
    double y0_mid = y0 + curviness*(yCy0);

    //Second two midpoints
    double x1_mid = x1 + curviness*(xCx1);
    double y1_mid = y1 + curviness*(yCy1);
    
    SimTK::Vec6 xPts(x0, x0_mid, x0_mid, x1_mid, x1_mid, x1);
    SimTK::Vec6 yPts(y0, y0_mid, y0_mid, y1_mid, y1_mid, y1);

    return SegmentedQuinticBezierToolkit::ControlPointsXY{xPts, yPts};
}
double scaleCurviness(double curviness)
{
    double c = 0.1 + 0.8*curviness;
    return c;
}
SmoothSegmentedFunction* 
    createFiberActiveForceLengthCurve(double x0, double x1, double x2, 
    double x3, double ylow,  double dydx, double curviness,
    bool computeIntegral, const std::string& curveName)
{
    //Ensure that the inputs are within a valid range
    double rootEPS = sqrt(SimTK::Eps);
    SimTK_ERRCHK1_ALWAYS( (x0>=0 && x1>x0+rootEPS  
                        && x2>x1+rootEPS && x3>x2+rootEPS),
        "SmoothSegmentedFunctionFactory::createFiberActiveForceLengthCurve",
        "%s: This must be true: 0 < lce0 < lce1 < lce2 < lce3",
        curveName.c_str());
    SimTK_ERRCHK1_ALWAYS( ylow >= 0,
        "SmoothSegmentedFunctionFactory::createFiberActiveForceLengthCurve",
        "%s: shoulderVal must be greater than, or equal to 0",
        curveName.c_str());
    double dydxUpperBound = (1-ylow)/(x2-x1);
    SimTK_ERRCHK2_ALWAYS(dydx >= 0 && dydx < dydxUpperBound,
        "SmoothSegmentedFunctionFactory::createFiberActiveForceLengthCurve",
        "%s: plateauSlope must be greater than 0 and less than %f",
        curveName.c_str(),dydxUpperBound);
    SimTK_ERRCHK1_ALWAYS( (curviness >= 0 && curviness <= 1),
        "SmoothSegmentedFunctionFactory::createFiberActiveForceLengthCurve",
        "%s: curviness must be between 0 and 1",
        curveName.c_str());

    std::string name = curveName;
    name.append(".createFiberActiveForceLengthCurve");



    //Translate the users parameters into Bezier curves
    double c = scaleCurviness(curviness);

    //The active force length curve is made up of 5 elbow shaped sections. 
    //Compute the locations of the joining point of each elbow section.

    //Calculate the location of the shoulder
       double xDelta = 0.05*x2; //half the width of the sarcomere 0.0259, 
                               //but TM.Winter's data has a wider shoulder than
                               //this

       double xs    = (x2-xDelta);//x1 + 0.75*(x2-x1);
   
   //Calculate the intermediate points located on the ascending limb
       double y0    = 0;   
       double dydx0 = 0;

       double y1    = 1 - dydx*(xs-x1);
       double dydx01= 1.25*(y1-y0)/(x1-x0);//(y1-y0)/(x1-(x0+xDelta));

       double x01   = x0 + 0.5*(x1-x0); //x0 + xDelta + 0.5*(x1-(x0+xDelta));
       double y01   = y0 + 0.5*(y1-y0);
   
   //Calculate the intermediate points of the shallow ascending plateau
       double x1s   = x1 + 0.5*(xs-x1);
       double y1s   = y1 + 0.5*(1-y1);
       double dydx1s= dydx;
   
       //double dydx01c0 = 0.5*(y1s-y01)/(x1s-x01) + 0.5*(y01-y0)/(x01-x0);
       //double dydx01c1 = 2*( (y1-y0)/(x1-x0));
       //double dydx01(1-c)*dydx01c0 + c*dydx01c1; 
       
       //x2 entered
       double y2 = 1;
       double dydx2 = 0;
   
   //Descending limb
       //x3 entered
       double y3 = 0;
       double dydx3 = 0;
       
       double x23 = (x2+xDelta) + 0.5*(x3-(x2+xDelta)); //x2 + 0.5*(x3-x2);
       double y23 = y2 + 0.5*(y3-y2);
             
       //double dydx23c0 = 0.5*((y23-y2)/(x23-x2)) + 0.5*((y3-y23)/(x3-x23));
       //double dydx23c1 = 2*(y3-y2)/(x3-x2);
       double dydx23   = (y3-y2)/((x3-xDelta)-(x2+xDelta)); 
       //(1-c)*dydx23c0 + c*dydx23c1; 
    
    //Compute the locations of the control points
       SegmentedQuinticBezierToolkit::ControlPointsXY p0 = SegmentedQuinticBezierToolkit::
           calcQuinticBezierCornerControlPoints(x0,ylow,dydx0,x01,y01,dydx01,c);
       SegmentedQuinticBezierToolkit::ControlPointsXY p1 = SegmentedQuinticBezierToolkit::
          calcQuinticBezierCornerControlPoints(x01,y01,dydx01,x1s,y1s,dydx1s,c);
       SegmentedQuinticBezierToolkit::ControlPointsXY p2 = SegmentedQuinticBezierToolkit::
          calcQuinticBezierCornerControlPoints(x1s,y1s,dydx1s,x2, y2, dydx2,c);
       SegmentedQuinticBezierToolkit::ControlPointsXY p3 = SegmentedQuinticBezierToolkit::
           calcQuinticBezierCornerControlPoints(x2, y2, dydx2,x23,y23,dydx23,c);
       SegmentedQuinticBezierToolkit::ControlPointsXY p4 = SegmentedQuinticBezierToolkit::
           calcQuinticBezierCornerControlPoints(x23,y23,dydx23,x3,ylow,dydx3,c);
                                    
        SimTK::Array_<SimTK::Vec6> ctrlPtsX {
            p0.x,
            p1.x,
            p2.x,
            p3.x,
            p4.x
        };

        SimTK::Array_<SimTK::Vec6> ctrlPtsY {
            p0.y,
            p1.y,
            p2.y,
            p3.y,
            p4.y
        };

        //std::string curveName = muscleName;
        //curveName.append("_fiberActiveForceLengthCurve");
        SmoothSegmentedFunction* mclCrvFcn = 
            new SmoothSegmentedFunction(
                ctrlPtsX,
                ctrlPtsY,
                x0,
                x3,
                ylow,
                ylow,
                0,
                0,
                computeIntegral,
                true,
                curveName);
        return mclCrvFcn;
}
SmoothSegmentedFunction* 
    createFiberForceVelocityCurve(double fmaxE, 
    double dydxC, double dydxNearC, 
    double dydxIso, 
    double dydxE, double dydxNearE,
    double concCurviness,double eccCurviness,
    bool computeIntegral, const std::string& curveName)
{
    //Ensure that the inputs are within a valid range
    SimTK_ERRCHK1_ALWAYS( fmaxE > 1.0, 
        "SmoothSegmentedFunctionFactory::createFiberForceVelocityCurve",
        "%s: fmaxE must be greater than 1",curveName.c_str());
    SimTK_ERRCHK1_ALWAYS( (dydxC >= 0.0 && dydxC < 1), 
        "SmoothSegmentedFunctionFactory::createFiberForceVelocityCurve",
        "%s: dydxC must be greater than or equal to 0"
        "and less than 1",curveName.c_str());
    SimTK_ERRCHK1_ALWAYS( (dydxNearC > dydxC && dydxNearC <= 1), 
        "SmoothSegmentedFunctionFactory::createFiberForceVelocityCurve",
        "%s: dydxNearC must be greater than or equal to 0"
        "and less than 1",curveName.c_str());
    SimTK_ERRCHK2_ALWAYS( dydxIso > 1, 
        "SmoothSegmentedFunctionFactory::createFiberForceVelocityCurve",
        "%s: dydxIso must be greater than (fmaxE-1)/1 (%f)",curveName.c_str(),
                                                            ((fmaxE-1.0)/1.0));
    SimTK_ERRCHK2_ALWAYS( (dydxE >= 0.0 && dydxE < (fmaxE-1)), 
        "SmoothSegmentedFunctionFactory::createFiberForceVelocityCurve",
        "%s: dydxE must be greater than or equal to 0"
        "and less than fmaxE-1 (%f)",curveName.c_str(),(fmaxE-1));
    SimTK_ERRCHK2_ALWAYS( (dydxNearE >= dydxE && dydxNearE < (fmaxE-1)), 
        "SmoothSegmentedFunctionFactory::createFiberForceVelocityCurve",
        "%s: dydxNearE must be greater than or equal to dydxE"
        "and less than fmaxE-1 (%f)",curveName.c_str(),(fmaxE-1));
    SimTK_ERRCHK1_ALWAYS( (concCurviness <= 1.0 && concCurviness >= 0), 
        "SmoothSegmentedFunctionFactory::createFiberForceVelocityCurve",
        "%s: concCurviness must be between 0 and 1",curveName.c_str());
    SimTK_ERRCHK1_ALWAYS( (eccCurviness <= 1.0 && eccCurviness >= 0), 
        "SmoothSegmentedFunctionFactory::createFiberForceVelocityCurve",
        "%s: eccCurviness must be between 0 and 1",curveName.c_str());

    std::string name = curveName;
    name.append(".createFiberForceVelocityCurve");

    //Translate the users parameters into Bezier point locations
    double cC = scaleCurviness(concCurviness);
    double cE = scaleCurviness(eccCurviness);
    
    //Compute the concentric control point locations
    double xC   = -1;
    double yC   = 0;
    
    double xNearC = -0.9;
    double yNearC = yC + 0.5*dydxNearC*(xNearC-xC) + 0.5*dydxC*(xNearC-xC);

    double xIso = 0;
    double yIso = 1;

    double xE   = 1;
    double yE   = fmaxE;

    double xNearE = 0.9;
    double yNearE = yE + 0.5*dydxNearE*(xNearE-xE) + 0.5*dydxE*(xNearE-xE);


    SegmentedQuinticBezierToolkit::ControlPointsXY concPts1 = SegmentedQuinticBezierToolkit::
        calcQuinticBezierCornerControlPoints(xC,yC,dydxC, 
                                            xNearC, yNearC,dydxNearC,cC);
    SegmentedQuinticBezierToolkit::ControlPointsXY concPts2 = SegmentedQuinticBezierToolkit::
        calcQuinticBezierCornerControlPoints(xNearC,yNearC,dydxNearC, 
                                             xIso,  yIso,  dydxIso,  cC);
    SegmentedQuinticBezierToolkit::ControlPointsXY eccPts1 = SegmentedQuinticBezierToolkit::
        calcQuinticBezierCornerControlPoints(xIso,      yIso,    dydxIso, 
                                             xNearE,  yNearE,  dydxNearE, cE);

    SegmentedQuinticBezierToolkit::ControlPointsXY eccPts2 = SegmentedQuinticBezierToolkit::
        calcQuinticBezierCornerControlPoints(xNearE, yNearE, dydxNearE, 
                                                 xE,     yE,     dydxE, cE);

    SimTK::Array_<SimTK::Vec6> ctrlPtsX {
        concPts1.x,
        concPts2.x,
        eccPts1.x,
        eccPts2.x
    };

    SimTK::Array_<SimTK::Vec6> ctrlPtsY {
        concPts1.y,
        concPts2.y,
        eccPts1.y,
        eccPts2.y
    };

    //std::string curveName = muscleName;
    //curveName.append("_fiberForceVelocityCurve");
    SmoothSegmentedFunction* mclCrvFcn = 
        new SmoothSegmentedFunction(
            ctrlPtsX,
            ctrlPtsY,
            xC,
            xE,
            yC,
            yE,
            dydxC,
            dydxE,
            computeIntegral,
            true,
            curveName);
    return mclCrvFcn;
}
SmoothSegmentedFunction* 
    createFiberForceLengthCurve(double eZero, double eIso, 
                                double kLow, double kIso, double curviness,
                             bool computeIntegral, const std::string& curveName)
{
    
    //Check the input arguments
    SimTK_ERRCHK1_ALWAYS( eIso > eZero , 
        "SmoothSegmentedFunctionFactory::createFiberForceLength", 
        "%s: The following must hold: eIso  > eZero",curveName.c_str());

    SimTK_ERRCHK2_ALWAYS( kIso > (1.0/(eIso-eZero)) , 
       "SmoothSegmentedFunctionFactory::createFiberForceLength", 
       "%s: kiso must be greater than 1/(eIso-eZero) (%f)",
       curveName.c_str(),(1.0/(eIso-eZero)));

    SimTK_ERRCHK1_ALWAYS(kLow > 0.0 && kLow < 1/(eIso-eZero),
        "SmoothSegmentedFunctionFactory::createFiberForceLength", 
        "%s: kLow must be greater than 0 and less than or equal to 1",
        curveName.c_str());

    SimTK_ERRCHK1_ALWAYS( (curviness>=0 && curviness <= 1) , 
        "SmoothSegmentedFunctionFactory::createFiberForceLength", 
        "%s: curviness must be between 0.0 and 1.0",curveName.c_str());

    std::string callerName = curveName;
    callerName.append(".createFiberForceLength");

    //Translate the user parameters to quintic Bezier points
    /*
    double c = scaleCurviness(curviness);
    double x0 = 1.0 + e0;
    double y0 = 0;
    double dydx0 = 0;
    double x1 = 1.0 + e1;
    double y1 = 1;
    double dydx1 = kiso;

    SimTK::Matrix ctrlPts = SegmentedQuinticBezierToolkit::
        calcQuinticBezierCornerControlPoints(x0,y0,dydx0,x1,y1,dydx1,c,callerName);

    SimTK::Matrix mX(6,1), mY(6,1);
    mX(0) = ctrlPts(0);
    mY(0) = ctrlPts(1);
    */

        //Translate the user parameters to quintic Bezier points
    double c = scaleCurviness(curviness);
    double xZero = 1+eZero;
    double yZero = 0;
    
    double xIso = 1 + eIso;
    double yIso = 1;
    
    double deltaX = min(0.1*(1.0/kIso), 0.1*(xIso-xZero));

    double xLow     = xZero + deltaX;
    double xfoot    = xZero + 0.5*(xLow-xZero);
    double yfoot    = 0;
    double yLow     = yfoot + kLow*(xLow-xfoot);

    //Compute the Quintic Bezier control points
    SegmentedQuinticBezierToolkit::ControlPointsXY p0 = SegmentedQuinticBezierToolkit::
     calcQuinticBezierCornerControlPoints(xZero, yZero, 0,
                                           xLow, yLow,  kLow,c);
    
    SegmentedQuinticBezierToolkit::ControlPointsXY p1 = SegmentedQuinticBezierToolkit::
     calcQuinticBezierCornerControlPoints(xLow, yLow, kLow,
                                          xIso, yIso, kIso, c);

    SimTK::Array_<SimTK::Vec6> ctrlPtsX {
        p0.x,
        p1.x
    };
    SimTK::Array_<SimTK::Vec6> ctrlPtsY {
        p0.y,
        p1.y
    };
    

    //std::string curveName = muscleName;
    //curveName.append("_tendonForceLengthCurve");
    //Instantiate a muscle curve object
    SmoothSegmentedFunction* mclCrvFcn = new SmoothSegmentedFunction(
        ctrlPtsX,
        ctrlPtsY,
        xZero,
        xIso,
        yZero,
        yIso,
        0.0,
        kIso,
        computeIntegral,
        true,
        curveName);

    return mclCrvFcn;
}
SmoothSegmentedFunction* 
          createTendonForceLengthCurve( double eIso, double kIso, 
                                        double fToe, double curviness,
                                        bool computeIntegral, 
                                        const std::string& curveName)
{
    //Check the input arguments
    //eIso>0 
    SimTK_ERRCHK2_ALWAYS( eIso>0 , 
        "SmoothSegmentedFunctionFactory::createTendonForceLengthCurve", 
        "%s: eIso must be greater than 0, but %f was entered", 
        curveName.c_str(),eIso);

    SimTK_ERRCHK2_ALWAYS( (fToe>0 && fToe < 1) , 
        "SmoothSegmentedFunctionFactory::createTendonForceLengthCurve", 
        "%s: fToe must be greater than 0 and less than 1, but %f was entered", 
        curveName.c_str(),fToe);

    SimTK_ERRCHK3_ALWAYS( kIso > (1/eIso) , 
       "SmoothSegmentedFunctionFactory::createTendonForceLengthCurve", 
       "%s : kIso must be greater than 1/eIso, (%f), but kIso (%f) was entered", 
        curveName.c_str(), (1/eIso),kIso);

    SimTK_ERRCHK2_ALWAYS( (curviness>=0 && curviness <= 1) , 
        "SmoothSegmentedFunctionFactory::createTendonForceLengthCurve", 
        "%s : curviness must be between 0.0 and 1.0, but %f was entered"
        , curveName.c_str(),curviness);

    std::string callerName = curveName;
    callerName.append(".createTendonForceLengthCurve");

    //Translate the user parameters to quintic Bezier points
    double c = scaleCurviness(curviness);
    double x0 = 1.0;
    double y0 = 0;
    double dydx0 = 0;

    double xIso = 1.0 + eIso;
    double yIso = 1;
    double dydxIso = kIso;

    //Location where the curved section becomes linear
    double yToe = fToe;
    double xToe = (yToe-1)/kIso + xIso;


    //To limit the 2nd derivative of the toe region the line it tends to
    //has to intersect the x axis to the right of the origin
        double xFoot = 1.0+(xToe-1.0)/10.0;
        double yFoot = 0;
        //double dydxToe = (yToe-yFoot)/(xToe-xFoot);

    //Compute the location of the corner formed by the average slope of the
    //toe and the slope of the linear section
    double yToeMid = yToe*0.5;
    double xToeMid = (yToeMid-yIso)/kIso + xIso;
    double dydxToeMid = (yToeMid-yFoot)/(xToeMid-xFoot);

    //Compute the location of the control point to the left of the corner
    double xToeCtrl = xFoot + 0.5*(xToeMid-xFoot); 
    double yToeCtrl = yFoot + dydxToeMid*(xToeCtrl-xFoot);



    //Compute the Quintic Bezier control points
    SegmentedQuinticBezierToolkit::ControlPointsXY p0 = SegmentedQuinticBezierToolkit::
     calcQuinticBezierCornerControlPoints(x0,y0,dydx0,
                                        xToeCtrl,yToeCtrl,dydxToeMid,c);
    SegmentedQuinticBezierToolkit::ControlPointsXY p1 = SegmentedQuinticBezierToolkit::
     calcQuinticBezierCornerControlPoints(xToeCtrl, yToeCtrl, dydxToeMid,
                                              xToe,     yToe,    dydxIso, c);

    SimTK::Array_<SimTK::Vec6> ctrlPtsX {
        p0.x,
        p1.x
    };
    SimTK::Array_<SimTK::Vec6> ctrlPtsY {
        p0.y,
        p1.y
    };

    //std::string curveName = muscleName;
    //curveName.append("_tendonForceLengthCurve");
    //Instantiate a muscle curve object
   SmoothSegmentedFunction* mclCrvFcn = 
         new SmoothSegmentedFunction(
            ctrlPtsX,
            ctrlPtsY,
            x0,
            xToe,
            y0,
            yToe,
            dydx0,
            dydxIso,
            computeIntegral,
            true,
            curveName);

    return mclCrvFcn;
}
double MuscleFirstOrderActivationDynamicModel::
calcDerivative(double activation, double excitation) const
{
    activation = clamp(get_minimum_activation(), activation, 1.0);

    double tau = (excitation > activation) ?
        get_activation_time_constant() * (0.5 + 1.5*activation) : 
        get_deactivation_time_constant() / (0.5 + 1.5*activation);

    return (excitation - activation) / tau;
}
double calcFiberForceActive(double fiso, double a, double fal, double fv)
{
    return fiso * (a * fal * fv);
}
double calcFiberForcePassiveElastic(double fiso, double fpe)
{
    return fiso * fpe;
}
double calcFiberForcePassiveDamping(
    double fiso,
    double dlceN,
    double beta)
{
    return fiso * beta * dlceN;
}
double calcFiberForce(
    double fiso,
    double a,
    double fal,
    double fv,
    double fpe,
    double dlceN,
    double beta)
{
    return calcFiberForceActive(fiso, a, fal, fv) +
           (calcFiberForcePassiveElastic(fiso, fpe) +
            calcFiberForcePassiveDamping(fiso, dlceN, beta));
}

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
