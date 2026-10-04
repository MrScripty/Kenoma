#!/usr/bin/env python3
"""Original data-derived figures; matplotlib/numpy, no third-party artwork."""
import csv,json,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':'kenoma-elbow-evidence-v1','axes.spines.top':False,'axes.spines.right':False})

def trace():
    with (ROOT/'data/openarm_s2_1b_0p5s_bins.csv').open() as f: rows=[{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]
    cols=[('brachioradialis_thickness_normalized_1_mean','Brachioradialis thickness','#276A86'),('biceps_semg_normalized_1_mean','Biceps sEMG','#A35026'),('wrist_contact_force_normalized_1_mean','Wrist-contact force','#6A4B94')]
    fig,axs=plt.subplots(3,1,figsize=(10,7.6),sharex=True,layout=None)
    fig.subplots_adjust(left=.1,right=.96,top=.84,bottom=.31,hspace=.38)
    fig.suptitle('A recorded isometric elbow trial',x=.1,y=.97,ha='left',fontsize=20,fontweight='bold')
    fig.text(.1,.91,'OpenArm Multisensor 2.0  |  Coded participant 2, trial 1b  |  Elbow held at 90°',fontsize=11)
    for ax,(col,label,color) in zip(axs,cols):
        ax.plot([r['mean_elapsed_s'] for r in rows],[r[col] for r in rows],color=color,lw=1.7)
        ax.axhline(0,color='#B6B6B6',lw=.8);ax.axhline(1,color='#B6B6B6',lw=.8,ls=':')
        ax.set_title(label,loc='left',fontsize=11,fontweight='bold',pad=4)
        ax.set_ylabel('Normalized (1)');ax.grid(axis='y',alpha=.16);ax.set_xlim(0,86)
    axs[-1].set_xlabel('Elapsed time from retained trial segment (s)')
    fig.text(.1,.145,'Original figure from recorded, preprocessed signals; 0.5 s sample-weighted means.\n0 = relaxed calibration baseline; 1 = calibration contraction signal. Values are not clipped.\nUltrasound and sEMG measure different muscles. Contact force is not an individual-muscle force.',fontsize=9.2,linespacing=1.5)
    fig.text(.1,.045,'Source: Hallock et al., OpenArm Multisensor 2.0, CC BY 4.0. DOI: 10.1109/TNSRE.2021.3133813\nOne illustrative trial, not a population law, clinical validation, or subject-specific 3D calibration.',fontsize=8.6,color='#424242',linespacing=1.5)
    for ext in ('png','svg'):fig.savefig(OUT/f'openarm_recorded_trial.{ext}',dpi=190,metadata={'Creator':'Kenoma educational data preparation','Date':'2026-10-04'})
    plt.close(fig)

def atlas():
    atlas=json.loads((ROOT/'data/bodyparts3d_right_arm_m.json').read_text());parts=atlas['parts']
    colors={'FJ3368':'#D2C4A1','FJ3349':'#DBCCAA','FJ3391':'#C5B591','FJ1486':'#AD5142','FJ1512':'#D37156','FJ1478':'#E79A74','FJ1480':'#775476','FJ1477':'#A47AA1','FJ1479':'#C899BC','FJ1487':'#548B88'}
    fig=plt.figure(figsize=(10,9),facecolor='white');fig.suptitle('A static right arm anatomical reference',x=.07,y=.97,ha='left',fontsize=20,fontweight='bold')
    fig.text(.07,.915,'Ten named structures from BodyParts3D 4.0. Original atlas pose and topology are preserved.',fontsize=10.5)
    allv=np.concatenate([np.array(p['vertices_m']) for p in parts]); lo=allv.min(0);hi=allv.max(0); mid=(lo+hi)/2;span=(hi-lo).max()
    for i,(label,show,azim) in enumerate([('Bones',parts[:3],-90),('Bones and muscle surfaces',parts,-90)]):
        ax=fig.add_axes([.05+i*.46,.32,.45,.55],projection='3d')
        for p in show:
            v=np.array(p['vertices_m']);f=np.array(p['triangles_zero_based']); poly=Poly3DCollection(v[f],facecolors=colors[p['element_id']],linewidths=0,alpha=1,shade=True,lightsource=LightSource(azdeg=315,altdeg=45))
            poly.set_edgecolor('none');ax.add_collection3d(poly)
        ax.set(xlim=(mid[0]-span*.33,mid[0]+span*.33),ylim=(mid[1]-span*.33,mid[1]+span*.33),zlim=(lo[2]-.015,hi[2]+.015))
        ax.set_box_aspect((.66,.66,1.05));ax.view_init(elev=3,azim=azim);ax.set_axis_off();ax.set_title(label,fontsize=12,pad=0)
    names={'FJ3368':'Humerus','FJ3349':'Radius','FJ3391':'Ulna','FJ1486':'Brachialis','FJ1512':'Biceps short head','FJ1478':'Biceps long head','FJ1480':'Triceps medial head','FJ1477':'Triceps lateral head','FJ1479':'Triceps long head','FJ1487':'Brachioradialis'}
    fig.legend(handles=[Patch(color=colors[p['element_id']],label=names[p['element_id']]) for p in parts],loc='lower left',bbox_to_anchor=(.07,.18),ncol=3,frameon=False,fontsize=9)
    fig.text(.07,.12,'Converted from mm to m for data export. Colors are explanatory additions.\nA reduced reference atlas supplies gross shape; it does not supply a validated elbow joint or muscle mechanics.',fontsize=9,linespacing=1.4)
    fig.text(.07,.045,'BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International.\nNot registered to the OpenArm participant or Arm26. No clinical or subject-specific validation is implied.',fontsize=8.5,color='#424242',linespacing=1.4)
    for ext in ('png','svg'):fig.savefig(OUT/f'bodyparts3d_right_arm.{ext}',dpi=180,metadata={'Creator':'Kenoma educational data preparation','Date':'2026-10-04'})
    plt.close(fig)
if __name__=='__main__':trace();atlas()
