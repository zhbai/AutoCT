#!/usr/bin/env python

import nibabel as nib
import numpy as np
import os
import sys
from math import sqrt, fabs, acos, floor
from types import SimpleNamespace

np_type = np.double

NIFTI_L2R=1    # Left to Right        
NIFTI_R2L=2    # Right to Left
NIFTI_P2A=3    # Posterior to Anterior
NIFTI_A2P=4    # nterior to Posterior
NIFTI_I2S=5    # Inferior to Superior 
NIFTI_S2I=6    # Superior to Inferior 

DT_UINT8     =              2
DT_INT16     =              4
DT_INT32     =              8
DT_FLOAT32   =             16
DT_COMPLEX64 =             32
DT_FLOAT64   =             64
DT_RGB24     =            128

DT_INT8      =            256     
DT_UINT16    =            512     
DT_UINT32    =            768     
DT_INT64     =           1024     
DT_UINT64    =           1280     
DT_FLOAT128  =           1536     
DT_COMPLEX128=           1792     
DT_COMPLEX256=           2048     
DT_RGBA32    =           2304     


# From ./3ddata.h
ORI_R2L_TYPE = 0 # "Right-to-Left"
ORI_L2R_TYPE = 1 # "Left-to-Right"
ORI_P2A_TYPE = 2 # "Posterior-to-Anterior"
ORI_A2P_TYPE = 3 # "Anterior-to-Posterior"
ORI_I2S_TYPE = 4 # "Inferior-to-Superior"
ORI_S2I_TYPE = 5 # "Superior-to-Inferior"

# THD_set_daxes_to_dicomm thd_editdaxes.c:124
def THD_set_daxes_to_dicomm(daxes):
    if daxes.xxorient == ORI_R2L_TYPE or daxes.xxorient == ORI_L2R_TYPE:
         daxes.to_dicomm[0][0] = 1.0 
    elif daxes.xxorient == ORI_P2A_TYPE or daxes.xxorient == ORI_A2P_TYPE:
         daxes.to_dicomm[1][0] = 1.0
    else:
         assert daxes.xxorient == ORI_I2S_TYPE or daxes.xxorient == ORI_S2I_TYPE 
         daxes.to_dicomm[2][0] = 1.0

    if daxes.yyorient == ORI_R2L_TYPE or daxes.yyorient == ORI_L2R_TYPE:
         daxes.to_dicomm[0][1] = 1.0 
    elif daxes.yyorient == ORI_P2A_TYPE or daxes.yyorient == ORI_A2P_TYPE:
         daxes.to_dicomm[1][1] = 1.0
    else:
         assert daxes.yyorient == ORI_I2S_TYPE or daxes.yyorient == ORI_S2I_TYPE 
         daxes.to_dicomm[2][1] = 1.0

    if daxes.zzorient == ORI_R2L_TYPE or daxes.zzorient == ORI_L2R_TYPE:
         daxes.to_dicomm[0][2] = 1.0 
    elif daxes.zzorient == ORI_P2A_TYPE or daxes.zzorient == ORI_A2P_TYPE:
         daxes.to_dicomm[1][2] = 1.0
    else:
         assert daxes.zzorient == ORI_I2S_TYPE or daxes.zzorient == ORI_S2I_TYPE 
         daxes.to_dicomm[2][2] = 1.0

def _datum(datatype):
   switcher = { 
        DT_FLOAT32: 3 # MRI_float line 182 in thd_niftiread.c
   } 

   # BR-1003 return switcher[datatype]
   return 3 
  
def nifti_datatype_sizes(datatype):
   nb=ss=0 
   switcher = { 
        DT_INT8:     (1, 0), 
        DT_UINT8:    (1, 0), 

        DT_INT16:    (2, 2), 
        DT_UINT16:   (2, 2), 

        DT_INT32:    (4, 4),
        DT_UINT32:   (4, 4),
        DT_FLOAT32:  (4, 4),

        DT_FLOAT64:  (8, 8),
        DT_INT64:    (8, 8),
        DT_UINT64:   (8, 8),
   } 

   nb,sb = switcher[datatype.item()]
   return nb, sb
 
def MAT_DET(A):
  return A[0][0]*A[1][1]*A[2][2]\
         - A[0][0]*A[1][2]*A[2][1]\
         - A[1][0]*A[0][1]*A[2][2]\
         + A[1][0]*A[0][2]*A[2][1]\
         + A[2][0]*A[0][1]*A[1][2]\
         - A[2][0]*A[0][2]*A[1][1]

def LOAD_MAT(A,a11,a12,a13,a21,a22,a23,a31,a32,a33):
  A[0][0] = a11; A[0][1] = a12
  A[0][2] = a13; A[1][0] = a21
  A[1][1] = a22; A[1][2] = a23
  A[2][0] = a31; A[2][1] = a32; A[2][2] = a33

def LOAD_MAT44(AA,a11,a12,a13,a14,a21,a22,a23,a24,a31,a32,a33,a34):
  AA[0][0]=a11; AA[0][1]=a12; AA[0][2]=a13; AA[0][3]=a14
  AA[1][0]=a21; AA[1][1]=a22; AA[1][2]=a23; AA[1][3]=a24
  AA[2][0]=a31; AA[2][1]=a32; AA[2][2]=a33; AA[2][3]=a34
  AA[3][0]=AA[3][1]=AA[3][2]=0.0; AA[3][3]=1.0

def nifti_quatern_to_dmat44(qb, qc, qd, qx, qy, qz, dx, dy, dz, qfac):
    R = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], np_type)
    b = qb
    c = qc
    d = qd
    R[3][0] = R[3][1] = R[3][2] = 0.0
    R[3][3] = 1.0
    a = 1.0 - (b * b + c * c + d * d)
    # if( a < 1.e-7l ){                 # special case
    if True:
        a = 1.0 / sqrt(b * b + c * c + d * d)
        b *= a  # normalize (b,c,d)
        c *= a
        d *= a
        a = 0.0  # a = 0 ==> 180 degree rotation
    else:
        a = sqrt(a)  # angle = 2*arccos(a)

    # xd = (dx > 0.0) ? dx : 1.0l      
    xd = dx if dx > 0.0 else 1.0  # make sure are positive 
    yd = dy if dy > 0.0 else 1.0
    zd = dz if dz > 0.0 else 1.0

    if qfac < 0.0:  # left handedness
        zd = -zd

    R[0][0] = (a * a + b * b - c * c - d * d) * xd
    constant = 2.0
    R[0][1] = constant * (b * c - a * d) * yd
    R[0][2] = constant * (b * d + a * c) * zd
    R[1][0] = constant * (b * c + a * d) * xd
    R[1][1] = (a * a + c * c - b * b - d * d) * yd
    R[1][2] = constant * (c * d - a * b) * zd
    R[2][0] = constant * (b * d - a * c) * xd
    R[2][1] = constant * (c * d + a * b) * yd
    R[2][2] = (a * a + d * d - c * c - b * b) * zd

    # load offsets 
    R[0][3] = qx
    R[1][3] = qy
    R[2][3] = qz
    return R

def nifti_dmat44_inverse(R):
    r11 = R[0][0]
    r12 = R[0][1]
    r13 = R[0][2]  # [ r11 r12 r13 v1 ]
    r21 = R[1][0]
    r22 = R[1][1]
    r23 = R[1][2]  # [ r21 r22 r23 v2 ]
    r31 = R[2][0]
    r32 = R[2][1]
    r33 = R[2][2]  # [ r31 r32 r33 v3 ]
    v1 = R[0][3]
    v2 = R[1][3]
    v3 = R[2][3]  # [  0   0   0   1 ]

    deti = r11 * r22 * r33 - r11 * r32 * r23 - r21 * r12 * r33 + r21 * r32 * r13 + r31 * r12 * r23 - r31 * r22 * r13
    Q = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], np_type)

    if deti != 0.0:  deti = 1.0 / deti
    # TODO: 1.0 / -1.1920928955078125 = -0.8388608 should be $69 = -0.83886079999999996

    Q[0][0] = deti * (r22 * r33 - r32 * r23)
    Q[0][1] = deti * (-r12 * r33 + r32 * r13)
    Q[0][2] = deti * (r12 * r23 - r22 * r13)
    Q[0][3] = deti * (-r12 * r23 * v3 + r12 * v2 * r33 + r22 * r13 * v3
                      - r22 * v1 * r33 - r32 * r13 * v2 + r32 * v1 * r23)

    Q[1][0] = deti * (-r21 * r33 + r31 * r23)
    Q[1][1] = deti * (r11 * r33 - r31 * r13)
    Q[1][2] = deti * (-r11 * r23 + r21 * r13)
    Q[1][3] = deti * (r11 * r23 * v3 - r11 * v2 * r33 - r21 * r13 * v3
                      + r21 * v1 * r33 + r31 * r13 * v2 - r31 * v1 * r23)

    Q[2][0] = deti * (r21 * r32 - r31 * r22)
    Q[2][1] = deti * (-r11 * r32 + r31 * r12)
    Q[2][2] = deti * (r11 * r22 - r21 * r12)
    Q[2][3] = deti * (-r11 * r22 * v3 + r11 * r32 * v2 + r21 * r12 * v3
                        - r21 * r32 * v1 - r31 * r12 * v2 + r31 * r22 * v1)

    Q[3][0] = Q[3][1] = Q[3][2] = 0.0
    # Q[3][3] = (deti == 0.0l) ? 0.0 : 1.0; # failure flag if deti == 0
    Q[3][3] = 0.0 if deti == 0.0 else 1.0;  # failure flag if deti == 0
    return Q

def FIXED_FLOAT(x):
    return x if np.isfinite(x) else 0.0

def nifti_dmat33_determ(R):
   r11 = R[0][0]; r12 = R[0][1]; r13 = R[0][2]
   r21 = R[1][0]; r22 = R[1][1]; r23 = R[1][2]
   r31 = R[2][0]; r32 = R[2][1]; r33 = R[2][2]
   return (r11*r22*r33-r11*r32*r23-r21*r12*r33+r21*r32*r13+r31*r12*r23-r31*r22*r13)

def nifti_dmat33_rownorm(A):
   r1 = fabs(A[0][0])+fabs(A[0][1])+fabs(A[0][2])
   r2 = fabs(A[1][0])+fabs(A[1][1])+fabs(A[1][2])
   r3 = fabs(A[2][0])+fabs(A[2][1])+fabs(A[2][2])
   if r1 < r2: r1 = r2
   if r1 < r3: r1 = r3 
   return r1

def nifti_dmat33_colnorm(A):
   r1 = fabs(A[0][0])+fabs(A[1][0])+fabs(A[2][0])
   r2 = fabs(A[0][1])+fabs(A[1][1])+fabs(A[2][1])
   r3 = fabs(A[0][2])+fabs(A[1][2])+fabs(A[2][2])
   if r1 < r2: r1 = r2
   if r1 < r3: r1 = r3
   return r1

def nifti_dmat33_inverse(R):
   Q  = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)
   r11 = R[0][0]; r12 = R[0][1]; r13 = R[0][2]
   r21 = R[1][0]; r22 = R[1][1]; r23 = R[1][2]
   r31 = R[2][0]; r32 = R[2][1]; r33 = R[2][2]

   deti = r11*r22*r33-r11*r32*r23-r21*r12*r33 + r21*r32*r13+r31*r12*r23-r31*r22*r13 

   if deti != 0.0: deti = 1.0 / deti

   Q[0][0] = deti*(r22*r33-r32*r23)
   Q[0][1] = deti*(-r12*r33+r32*r13)
   Q[0][2] = deti*(r12*r23-r22*r13)

   Q[1][0] = deti*(-r21*r33+r31*r23)
   Q[1][1] = deti*(r11*r33-r31*r13)
   Q[1][2] = deti*(-r11*r23+r21*r13)

   Q[2][0] = deti*(r21*r32-r31*r22)
   Q[2][1] = deti*(-r11*r32+r31*r12)
   Q[2][2] = deti*(r11*r22-r21*r12)
   return Q


def nifti_dmat33_polar(A):
   Z = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)
   dif = 1.0
   k = 0 

   X = A.copy()

   gam = nifti_dmat33_determ(X) ;

   while(gam == 0.0):
     gam = 0.00001 * (0.001 + nifti_dmat33_rownorm(X))
     X[0][0] += gam; X[1][1] += gam; X[2][2] += gam 
     gam = nifti_dmat33_determ(X)

   while True:
     Y = nifti_dmat33_inverse(X) ;

     if dif > 0.3:
       alp = sqrt(nifti_dmat33_rownorm(X) * nifti_dmat33_colnorm(X))
       bet = sqrt(nifti_dmat33_rownorm(Y) * nifti_dmat33_colnorm(Y))
       gam = sqrt( bet / alp );
       gmi = 1.0 / gam;
     else:
       gam = gmi = 1.0 

     Z[0][0] = 0.5 * (gam*X[0][0] + gmi*Y[0][0]);
     Z[0][1] = 0.5 * (gam*X[0][1] + gmi*Y[1][0]);
     Z[0][2] = 0.5 * (gam*X[0][2] + gmi*Y[2][0]);
     Z[1][0] = 0.5 * (gam*X[1][0] + gmi*Y[0][1]);
     Z[1][1] = 0.5 * (gam*X[1][1] + gmi*Y[1][1]);
     Z[1][2] = 0.5 * (gam*X[1][2] + gmi*Y[2][1]);
     Z[2][0] = 0.5 * (gam*X[2][0] + gmi*Y[0][2]);
     Z[2][1] = 0.5 * (gam*X[2][1] + gmi*Y[1][2]);
     Z[2][2] = 0.5 * (gam*X[2][2] + gmi*Y[2][2]);

     dif = fabs(Z[0][0]-X[0][0]) + fabs(Z[0][1]-X[0][1]) + \
           fabs(Z[0][2]-X[0][2]) + fabs(Z[1][0]-X[1][0]) + \
           fabs(Z[1][1]-X[1][1]) + fabs(Z[1][2]-X[1][2]) + \
           fabs(Z[2][0]-X[2][0]) + fabs(Z[2][1]-X[2][1]) + \
           fabs(Z[2][2]-X[2][2])

     k = k+1
     if k > 100 or dif < 3.e-6: break
     X = Z

   return Z

def nifti_dmat44_to_quatern(R):
    P = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)
    Q = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)

    qx = R[0][3]; qy = R[1][3]; qz = R[2][3]

    r11 = R[0][0]; r12 = R[0][1]; r13 = R[0][2]
    r21 = R[1][0]; r22 = R[1][1]; r23 = R[1][2]
    r31 = R[2][0]; r32 = R[2][1]; r33 = R[2][2]

    xd = sqrt(r11*r11 + r21*r21 + r31*r31)
    yd = sqrt(r12*r12 + r22*r22 + r32*r32)
    zd = sqrt(r13*r13 + r23*r23 + r33*r33)

    if xd == 0.0: 
       r11 = 1.0; r21 = r31 = 0.0; xd = 1.0

    if yd == 0.0:
       r22 = 1.0; r12 = r32 = 0.0; yd = 1.0

    if zd == 0.0:
       r33 = 1.0; r13 = r23 = 0.0; zd = 1.0
 
    dx = xd; dy = yd; dz = zd

    r11 /= xd; r21 /= xd; r31 /= xd
    r12 /= yd; r22 /= yd; r32 /= yd
    r13 /= zd; r23 /= zd; r33 /= zd

    Q[0][0] = r11; Q[0][1] = r12; Q[0][2] = r13
    Q[1][0] = r21; Q[1][1] = r22; Q[1][2] = r23
    Q[2][0] = r31; Q[2][1] = r32; Q[2][2] = r33

    # nifti_dmat44_to_quatern at nifti/nifti2/nifti2_io.c:1756
    P = nifti_dmat33_polar(Q) 

    r11 = P[0][0]; r12 = P[0][1]; r13 = P[0][2]
    r21 = P[1][0]; r22 = P[1][1]; r23 = P[1][2]
    r31 = P[2][0]; r32 = P[2][1]; r33 = P[2][2]

    zd = r11*r22*r33-r11*r32*r23-r21*r12*r33 + r21*r32*r13+r31*r12*r23-r31*r22*r13  # should be -1 or 1 

    if zd > 0:
      qfac = 1.0
    else:
     qfac = -1.0
     r13 = -r13; r23 = -r23; r33 = -r33 

    a = r11 + r22 + r33 + 1.0

    if a > 0.5:
     a = 0.5 * sqrt(a)
     b = 0.25 * (r32-r23) / a
     c = 0.25 * (r13-r31) / a
     d = 0.25 * (r21-r12) / a
    else:
     xd = 1.0 + r11 - (r22+r33)  # 4*b*b
     yd = 1.0 + r22 - (r11+r33)  # 4*c*c 
     zd = 1.0 + r33 - (r11+r22)  # 4*d*d

     if xd > 1.0:
       b = 0.5 * sqrt(xd)
       c = 0.25* (r12+r21) / b
       d = 0.25* (r13+r31) / b
       a = 0.25* (r32-r23) / b
     elif yd > 1.0:
       c = 0.5 * sqrt(yd)
       b = 0.25* (r12+r21) / c
       d = 0.25* (r23+r32) / c
       a = 0.25* (r13-r31) / c
     else:
       d = 0.5 * sqrt(zd)
       b = 0.25* (r13+r31) / d
       c = 0.25* (r23+r32) / d
       a = 0.25* (r21-r12) / d
     # to be mathematically consistent, this would include a = -a 
     if a < 0.0:
       b=-b; c=-c; d=-d;

    qb=b; qc=c; qd=d
    return qb, qc, qd, qx, qy, qz, dx, dy, dz, qfac

def populate_nifti_image(dset):
    nim = SimpleNamespace()
    assert dset.daxes.nzz > 1
    nim.ndim = 3
    type0 = 3   # TODO: MRI_float: DSET_BRICK_TYPE(dset,0);
    assert type0 == 3
    nim.datatype = 16
    nim.nbyper = 4
    fac0 = 0    # TODO: DSET_BRICK_FACTOR(dset,0)
    assert fac0 == 0
    nim.scl_slope = fac0
    nim.scl_inter = 0 
    ORIENT_xyz = "xxyyzzg"
    ORIENT_sign = "+--++-"
    axcode = [-1, -1, -1]
    axnum = [-1, -1, -1]
    axcode[0] = ORIENT_xyz[dset.daxes.xxorient]; axnum[0] = dset.daxes.nxx
    axcode[1] = ORIENT_xyz[dset.daxes.yyorient]; axnum[1] = dset.daxes.nyy
    axcode[2] = ORIENT_xyz[dset.daxes.zzorient]; axnum[2] = dset.daxes.nzz
    axsign = [-1, -1, -1]
    axsign[0] = ORIENT_sign[dset.daxes.xxorient]
    axsign[1] = ORIENT_sign[dset.daxes.yyorient]
    axsign[2] = ORIENT_sign[dset.daxes.zzorient]
    axstep = [-1, -1, -1]
    axstart = [-1, -1, -1]
    axstep[0] = dset.daxes.xxdel; axstart[0] = dset.daxes.xxorg
    axstep[1] = dset.daxes.yydel; axstart[1] = dset.daxes.yyorg
    axstep[2] = dset.daxes.zzdel; axstart[2] = dset.daxes.zzorg

    nif_x_axnum = nif_y_axnum = nif_z_axnum = 0

    for ii in range(3):
       if axcode[ii] == 'x':
          nif_x_axnum = ii
       elif axcode[ii] == 'y':
          nif_y_axnum = ii
       else: 
          nif_z_axnum = ii

    nim.qto_xyz = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], np_type)

    nim.pixdim = [0, 0, 0, 0, 0, 0, 0, 0]
    nim.dx = nim.pixdim[1] = fabs(axstep[0])
    nim.dy = nim.pixdim[2] = fabs(axstep[1])
    nim.dz = nim.pixdim[3] = fabs(axstep[2])
    nim.du = nim.pixdim[5] = 0
    nim.dv = nim.pixdim[6] = 0
    nim.dw = nim.pixdim[7] = 0

    nim.qto_xyz[0][nif_x_axnum] = -axstep[nif_x_axnum]
    nim.qto_xyz[1][nif_y_axnum] = -axstep[nif_y_axnum]
    nim.qto_xyz[2][nif_z_axnum] = axstep[nif_z_axnum]

    nim.qoffset_x = -axstart[nif_x_axnum]
    nim.qoffset_y = -axstart[nif_y_axnum]
    nim.qoffset_z = axstart[nif_z_axnum]

    nim.qto_xyz[0][3] = nim.qoffset_x
    nim.qto_xyz[1][3] = nim.qoffset_y
    nim.qto_xyz[2][3] = nim.qoffset_z

    nim.sto_xyz = dset.daxes.ijk_to_dicom_real.copy()

    for ii in range(2):
        for jj in range(4):
            nim.sto_xyz[ii][jj] = -(nim.sto_xyz[ii][jj]);

    # update qform too with struct copy from sform
    nim.qto_xyz = nim.sto_xyz.copy()

    # nifti_dmat44_to_quatern at nifti/nifti2/nifti2_io.c:1756
    nim.quatern_b, nim.quatern_c, nim.quatern_d, dumqx, \
      dumqy, dumqz, dumdx, dumdy, dumdz, nim.qfac =  nifti_dmat44_to_quatern(nim.qto_xyz)
    
    nim.qto_ijk = nifti_dmat44_inverse(nim.qto_xyz) 

    nim.nt = nim.nu = nim.nv = nim.nw = 1
    nim.nx = axnum[0]
    nim.ny = axnum[1]
    nim.nz = axnum[2]
    nim.nu = dset.dblk.nvals
    assert nim.nu == 1
    assert nim.nt <= 1
    nim.dim = [0, 0, 0, 0, 0, 0, 0, 0]
    nim.dim[0] = nim.ndim
    nim.dim[1] = nim.nx
    nim.dim[2] = nim.ny
    nim.dim[3] = nim.nz
    nim.dim[4] = nim.nt  # RWC: at most one of nt and nu is > 1 
    nim.dim[5] = nim.nu
    nim.dim[6] = nim.nv
    nim.dim[7] = nim.nw

    nim.nvox = nim.nx * nim.ny * nim.nz * nim.nt * nim.nu * nim.nv * nim.nw 
    nim.freq_dim = nim.phase_dim = 0 
    nim.slice_dim = 0
    nim.time_units = 0
    nim.qform_code = 1  # TODO implement space_to_NIFTI_code(dset); thd_niftiwrite.c:576
    nim.cal_min = nim.cal_max = 0 ;
    nim.nifti_type = 1 ;
    nim.xyz_units = 0
    return nim

def nifti_convert_n1hdr2nim(header):
    nhdr = SimpleNamespace(**dict(list(header.items())))
    dim = nhdr.dim = np.array(nhdr.dim, np.int64)
    pixdim = nhdr.pixdim
    nim = SimpleNamespace()
    nim.ndim = dim[0];
    nim.nx = dim[1]
    nim.ny = dim[2]
    nim.nz = dim[3]
    nim.nt = dim[4]
    nim.nu = dim[5]
    nim.nv = dim[6]
    nim.nw = dim[7]
    nim.nvox = dim[1] * dim[2] * dim[3]  # 9175040

    # set the type of data in voxels and how many bytes per voxel */
    nim.datatype = nhdr.datatype ;
    nim.nbyper, nim.swapsize = nifti_datatype_sizes(nim.datatype)
    if nim.nbyper == 0: raise Exception("bad datatype")

    # set the grid spacings 
    nim.dx = pixdim[1]
    nim.dy = pixdim[2]
    nim.dz = pixdim[3]
    nim.dt = pixdim[4]
    nim.du = pixdim[5]
    nim.dv = pixdim[6]
    nim.dw = pixdim[7]

    ni_ver = 1  # NIFTI_VERSION(nhdr)
    nim.qform_code = nhdr.qform_code

    if not ni_ver or nhdr.qform_code <= 0:
        nim.qto_xyz = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], np_type)
        nim.qto_xyz[0][0] = nim.dx  # grid spacings
        nim.qto_xyz[1][1] = nim.dy  # along diagonal
        nim.qto_xyz[2][2] = nim.dz
        nim.qto_xyz[0][1] = nim.qto_xyz[0][2] = nim.qto_xyz[0][3] = 0.0  # off diagonal is zero
        nim.qto_xyz[1][0] = nim.qto_xyz[1][2] = nim.qto_xyz[1][3] = 0.0
        nim.qto_xyz[2][0] = nim.qto_xyz[2][1] = nim.qto_xyz[2][3] = 0.0
        nim.qto_xyz[3][0] = nim.qto_xyz[3][1] = nim.qto_xyz[3][2] = 0.0
        nim.qto_xyz[3][3] = 1.0
    else:
        nim.quatern_b = FIXED_FLOAT(nhdr.quatern_b)
        nim.quatern_c = FIXED_FLOAT(nhdr.quatern_c)
        nim.quatern_d = FIXED_FLOAT(nhdr.quatern_d)

        nim.qoffset_x = FIXED_FLOAT(nhdr.qoffset_x)
        nim.qoffset_y = FIXED_FLOAT(nhdr.qoffset_y)
        nim.qoffset_z = FIXED_FLOAT(nhdr.qoffset_z)
        nim.qfac = -1.0 if pixdim[0] < 0.0 else 1.0  # left-handedness? 

        # nifti_quatern_to_dmat44
        # qb=1, qc=0, qd=0, qx=-124.51171875, qy=-38, qz=-184.60000610351562, 
        # dx=0.48828125, dy=0.48828125, dz=5, qfac=-1) at nifti/nifti2/nifti2_io.c:1617
        nim.qto_xyz = nifti_quatern_to_dmat44(nim.quatern_b, nim.quatern_c, nim.quatern_d, nim.qoffset_x, nim.qoffset_y,
                                          nim.qoffset_z, nim.dx, nim.dy, nim.dz, nim.qfac)

    nim.qto_ijk = nifti_dmat44_inverse(nim.qto_xyz)

    nim.sform_code = nhdr.sform_code

    if not ni_ver or nim.sform_code <= 0:
        raise Exception("no sform ...")
        pass
    
    # BR-1003 assert nim.qform_code == 1, str(nim.qform_code)
    # BR-1003 assert nim.sform_code == 1, str(nim.sform_code)

    nim.sto_xyz = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], np_type)
    nim.sto_xyz[0][0] = nhdr.srow_x[0]
    nim.sto_xyz[0][1] = nhdr.srow_x[1]
    nim.sto_xyz[0][2] = nhdr.srow_x[2]
    nim.sto_xyz[0][3] = nhdr.srow_x[3]

    nim.sto_xyz[1][0] = nhdr.srow_y[0]
    nim.sto_xyz[1][1] = nhdr.srow_y[1]
    nim.sto_xyz[1][2] = nhdr.srow_y[2]
    nim.sto_xyz[1][3] = nhdr.srow_y[3]

    nim.sto_xyz[2][0] = nhdr.srow_z[0]
    nim.sto_xyz[2][1] = nhdr.srow_z[1]
    nim.sto_xyz[2][2] = nhdr.srow_z[2]
    nim.sto_xyz[2][3] = nhdr.srow_z[3]
    nim.sto_xyz[3][0]=nim.sto_xyz[3][1]=nim.sto_xyz[3][2] = 0.0
    nim.sto_xyz[3][3]= 1.0
    nim.sto_ijk = nifti_dmat44_inverse(nim.sto_xyz)
    
    if ni_ver:
       nim.scl_slope  = 1 # TODO FIXED_FLOAT(nhdr.scl_slope) 
       nim.scl_inter  = FIXED_FLOAT( nhdr.scl_inter) 

       nim.intent_code = nhdr.intent_code 
       nim.intent_p1 = FIXED_FLOAT( nhdr.intent_p1 ) 
       nim.intent_p2 = FIXED_FLOAT( nhdr.intent_p2 ) 
       nim.intent_p3 = FIXED_FLOAT( nhdr.intent_p3 ) 
       nim.toffset   = FIXED_FLOAT( nhdr.toffset ) 

       # memcpy(nim.intent_name,nhdr.intent_name,15); nim.intent_name[15] = '\0';

       nim.xyz_units  = nhdr.xyzt_units & 0x07
       nim.time_units = nhdr.xyzt_units & 0x38 

       nim.freq_dim  = nhdr.dim_info & 0x03
       nim.phase_dim = (nhdr.dim_info >> 2) & 0x03
       nim.slice_dim = (nhdr.dim_info >> 4) & 0x03

       nim.slice_code = nhdr.slice_code
       nim.slice_start = nhdr.slice_start
       nim.slice_end  = nhdr.slice_end
       nim.slice_duration = FIXED_FLOAT(nhdr.slice_duration) 
       nim.cal_min = FIXED_FLOAT(nhdr.cal_min)
       nim.cal_max = FIXED_FLOAT(nhdr.cal_max)
       nim.iname_offset  = nhdr.vox_offset
       if nim.iname_offset < header.sizeof_hdr: nim.iname_offset = header.sizeof_hdr 
       nim.num_ext = 0
       nim.ext_list = []
       return nim


def nifti_read_extensions(nim, fp, remain):
    return nim

def nifti_image_read(nii_file):
    img = nib.load(nii_file)
    ni_ver = 1
    nim = nifti_convert_n1hdr2nim(img.header)
    nim.img = img
    return nim

def nifti_dmat33_mul(A , B):
   C = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)
   for i in range(3):
       for j in range(3):
           C[i][j] = A[i][0] * B[0][j] + A[i][1] * B[1][j] + A[i][2] * B[2][j] ;

   return C ;

def nifti_mat44_inverse(R):
   return nifti_dmat44_inverse(R) 

def nifti_dmat44_to_orientation(R):
    xi = R[0][0]; xj = R[0][1]; xk = R[0][2]
    yi = R[1][0]; yj = R[1][1]; yk = R[1][2]
    zi = R[2][0]; zj = R[2][1]; zk = R[2][2]
    val = sqrt(xi*xi + yi*yi + zi*zi)
    xi /= val; yi /= val; zi /= val
    val = sqrt(xj*xj + yj*yj + zj*zj)
    xj /= val; yj /= val; zj /= val

    val = xi*xj + yi*yj + zi*zj    # dot product between i and j
    if fabs(val) > 1.e-4:
       raise Exception("not handling fabs > 1.e-4")

    # normalize k axis; if it is zero, make it the cross product i x j
    val = sqrt(xk*xk + yk*yk + zk*zk)

    if val == 0.0:
        xk = yi*zj-zi*yj; yk = zi*xj-zj*xi; zk=xi*yj-yi*xj
    else:
        xk /= val; yk /= val; zk /= val


    val = xj*xk + yj*yk + zj*zk    # dot product between j and k
    if fabs(val) > 1.e-4:
       raise Exception("not handling fabs > 1.e-4")

    Q = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np.int16)
    Q[0][0] = xi; Q[0][1] = xj; Q[0][2] = xk
    Q[1][0] = yi; Q[1][1] = yj; Q[1][2] = yk
    Q[2][0] = zi; Q[2][1] = zj; Q[2][2] = zk
    # at this point, Q is the rotation matrix from (i,j,k) to (x,y,z) axes
    detQ = nifti_dmat33_determ(Q) 
    vbest = -666.0; ibest=pbest=qbest=rbest=1; jbest=2; kbest=3 
    for i in range(1, 4):
        for j in range(1, 4):
            if i == j: continue
       	    for k in range(1, 4):
                if i == k or j == k: continue 
                P = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)
                for p in [-1, 1]:
                    for q in [-1, 1]:
                        for r in [-1, 1]:
                            P[0][i-1] = p; P[1][j-1] = q; P[2][k-1] = r
                            detP = nifti_dmat33_determ(P)
                            if detP * detQ <= 0.0: continue
                            M = nifti_dmat33_mul(P,Q) ;
                            val = M[0][0] + M[1][1] + M[2][2]

                            if val > vbest:
                               vbest = val
                               ibest = i; jbest = j; kbest = k
                               pbest = p; qbest = q; rbest = r

    # TODO DEFAULT 0 if key is not in switcher
    switcher = {
       1: NIFTI_L2R,
      -1: NIFTI_R2L,
       2: NIFTI_P2A,
      -2: NIFTI_A2P,
       3: NIFTI_I2S,
      -3: NIFTI_S2I
    }
    i = switcher[ibest*pbest]
    j = switcher[jbest*qbest]
    k = switcher[kbest*rbest]
    icod, jcod, kcod = (i, j, k)
    return icod, jcod, kcod

def MAT44_VEC(AA,x,y,z): 
 a = AA[0][0]*(x) + AA[0][1]*(y) + AA[0][2]*(z) + AA[0][3]
 b = AA[1][0]*(x) + AA[1][1]*(y) + AA[1][2]*(z) + AA[1][3]
 c = AA[2][0]*(x) + AA[2][1]*(y) + AA[2][2]*(z) + AA[2][3]
 return a, b, c

##
# URGENT: check if this is called in  THD_open_nifti  as pwr message below.
# We know it is called iduring apply ...
#
# This is where I am ...
# THD_open_nifti 
#   EDIT_dset_items
#     =>  THD_set_dicom_box
####
# file thd_matdaxes.c, line 107
def THD_set_dicom_box(dax):
   nx1 = dax.nxx - 1.0; ny1 = dax.nyy - 1.0; nz1 = dax.nzz - 1.0
   x,y,z = MAT44_VEC(dax.ijk_to_dicom, 0, 0, 0)  # (0,0,0) corner 
   temp = SimpleNamespace(xbot=x, xtop=x, ybot=y, ytop=y, zbot=z, ztop=z)

   # this macro checks the (a,b,c) corner and updates the bot/top values */
   def BT(a,b,c):
       x,y,z = MAT44_VEC(dax.ijk_to_dicom, a, b, c)  # (0,0,0) corner 
       temp.xbot = min(temp.xbot,x); temp.xtop = max(temp.xtop,x)
       temp.ybot = min(temp.ybot,y); temp.ytop = max(temp.ytop,y)
       temp.zbot = min(temp.zbot,z); temp.ztop = max(temp.ztop,z)

   BT(nx1, 0 , 0); BT(0 ,ny1, 0); BT(nx1,ny1, 0)
   BT(0 , 0 ,nz1); BT(nx1, 0 ,nz1); BT(0 ,ny1,nz1); BT(nx1,ny1,nz1)
   dax.dicom_xxmin = temp.xbot; dax.dicom_xxmax = temp.xtop
   dax.dicom_yymin = temp.ybot; dax.dicom_yymax = temp.ytop
   dax.dicom_zzmin = temp.zbot; dax.dicom_zzmax = temp.ztop

def r_dxyz_mod_dataxes(dx, dy, dz, daxin, daxout, bound_type):
    if dx <= 0.0 or dy <= 0.0 or dz <= 0.0: 
        raise Exception("Handle this")  # having duplicated the structures

    rex = dx if daxout.xxdel > 0 else  -dx # signed voxel sizes 
    rey = dy if daxout.yydel > 0 else -dy
    rez = dz if daxout.zzdel > 0 else -dz

    if bound_type == 1:
        raise Exception("Handle bound type == 1")  # having duplicated the structures
    
    assert bound_type == 0
    lxx = daxin.nxx * daxin.xxdel;        # signed lengths of data box */
    lyy = daxin.nyy * daxin.yydel;
    lzz = daxin.nzz * daxin.zzdel;

    daxout.nxx = int(lxx/rex + 0.499)  # so this is > 0 
    daxout.nyy = int(lyy/rey + 0.499)
    daxout.nzz = int(lzz/rez + 0.499)

    # go from old edge to old center, then back out to new edge 
    daxout.xxorg = daxin.xxorg + 0.5*(lxx - daxin.xxdel) - 0.5*(daxout.nxx - 1)*rex
    daxout.yyorg = daxin.yyorg + 0.5*(lyy - daxin.yydel) - 0.5*(daxout.nyy - 1)*rey
    daxout.zzorg = daxin.zzorg + 0.5*(lzz - daxin.zzdel) - 0.5*(daxout.nzz - 1)*rez

    # dave new dimensions 
    daxout.xxdel = rex
    daxout.yydel = rey
    daxout.zzdel = rez

    # create a new bounding box                        
    # (note that xxdel<0 implies we must swap min/max) 
    daxout.xxmin = daxout.xxorg
    daxout.xxmax = daxout.xxorg + (daxout.nxx-1)*daxout.xxdel
    if daxout.xxmin > daxout.xxmax:
        tmp = daxout.xxmin
        daxout.xxmin = daxout.xxmax
        daxout.xxmax = tmp

    daxout.yymin = daxout.yyorg
    daxout.yymax = daxout.yyorg + (daxout.nyy-1)*daxout.yydel
    if daxout.yymin > daxout.yymax:
        tmp = daxout.yymin
        daxout.yymin = daxout.yymax
        daxout.yymax = tmp

    daxout.zzmin = daxout.zzorg;
    daxout.zzmax = daxout.zzorg + (daxout.nzz-1)*daxout.zzdel
    if daxout.zzmin > daxout.zzmax: 
        tmp = daxout.zzmin
        daxout.zzmin = daxout.zzmax
        daxout.zzmax = tmp

def THD_mat44_mul(A , B):
   C = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], np_type)
   for i in range(3):
       for j in range(4):
           C[i][j] = A[i][0] * B[0][j] + A[i][1] * B[1][j] + A[i][2] * B[2][j] + A[i][3] * B[3][j] 

   C[3][0] = C[3][1] = C[3][2] = 0.0 ; C[3][3] = 1.0
   return C

def THD_daxes_to_mat44(dax):
    ijk_to_dxyz = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], np_type)
    dxyz_to_dicom = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], np_type)

    # ijk_to_dxyz: transforms (i,j,k) to dataset (x,y,z) coords 

    LOAD_MAT44(ijk_to_dxyz,
               dax.xxdel , 0.0       , 0.0       , dax.xxorg,
               0.0       , dax.yydel , 0.0       , dax.yyorg,
               0.0       , 0.0       , dax.zzdel , dax.zzorg)

    # set to_dicomm (takes dataset order xyz to DICOM order xyz) 
    # THD_set_daxes_to_dicomm at thd_editdaxes.c:124
    # ABDOU
    THD_set_daxes_to_dicomm(dax)

    # dxyz_to_dicom: transforms dataset (x,y,z) coords to DICOM coords 

    LOAD_MAT44(dxyz_to_dicom,
               dax.to_dicomm[0][0], dax.to_dicomm[0][1], dax.to_dicomm[0][2], 0.0,
               dax.to_dicomm[1][0], dax.to_dicomm[1][1], dax.to_dicomm[1][2], 0.0,
               dax.to_dicomm[2][0], dax.to_dicomm[2][1], dax.to_dicomm[2][2], 0.0)

    # dax->ijk_to_dicom: transforms (i,j,k) to DICOM (x,y,z) */
    dax.ijk_to_dicom = THD_mat44_mul(dxyz_to_dicom , ijk_to_dxyz)

    # and the inverse transformation: DICOM (x,y,z) to indexes (i,j,k) */
    dax.dicom_to_ijk = nifti_mat44_inverse(dax.ijk_to_dicom)
    THD_set_dicom_box(dax)


# NEED TO HANDLE code above line 662 in edt_dsetitems.c 
# thd_matdaxes.c: int THD_daxes_to_mat44( THD_dataxes *dax )
# ./thd_editdaxes.c: THD_set_daxes_bbox( THD_dataxes *daxes )
# ./thd_matdaxes.c:void THD_set_dicom_box( THD_dataxes *dax )

'''
    apply_dataxes calls edt_dsetitems.c
    case ADN_nxyz, case ADN_xyzdel. case ADN_xyzorg are triggered.
    redo_daxes = 1 cause new_xyzorg==new_xyzdel=1
    redo_bricks = 1 cause new_nxyz  
    TODO: check if new_xyzorg==new_xyzdel=1,new_nxyz=1 now assuming they are. 
'''
def apply_dataxes(dset, dax):
    ivnxyz = [dax.nxx, dax.nyy, dax.nzz]
    fvorg = [dax.xxorg, dax.yyorg, dax.zzorg]
    fvdel = [dax.xxdel, dax.yydel, dax.zzdel]

    # if new_nxyz
    daxes = dset.daxes
    dkptr = dset.dblk.diskptr
    daxes.nxx = dkptr.dimsizes[0] = ivnxyz[0]
    daxes.nyy = dkptr.dimsizes[1] = ivnxyz[1]
    daxes.nzz = dkptr.dimsizes[2] = ivnxyz[2]

    # if redo_daxes and new_xyzorg 
    daxes.xxorg = fvorg[0]
    daxes.yyorg = fvorg[1]
    daxes.zzorg = fvorg[2]

    # if redo_daxes and new_xyzdel
    daxes.xxdel = fvdel[0]
    daxes.yydel = fvdel[1]
    daxes.zzdel = fvdel[2]

    # set bounding box and to_dicomm matrix for this dataset
    set_daxes_bbox(daxes)
    daxes.to_dicomm = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)
    THD_daxes_to_mat44(daxes) 
    daxes.ijk_to_dicom_real = daxes.ijk_to_dicom 
    THD_set_dicom_box(daxes)
    THD_set_daxes_to_dicomm(daxes)

    # if redo_bricks 
    old_nvals = dset.dblk.nvals
    nvals = old_nvals 

# THD_patch_brickim (dset=0x5577823408e0) at thd_loaddblk.c:1252
def THD_patch_brickim(dset):
    nfix = 0
    dx = fabs(dset.daxes.xxdel)
    dy = fabs(dset.daxes.yydel)
    dz = fabs(dset.daxes.zzdel)
    dm = dx + dy + dz 
    dm = 1.0 if dm == 0.0 else dm * 0.5

    if dx == 0.0: nfix += 1 
    if dy == 0.0: nfix += 2
    if dz == 0.0: nfix += 4 
    assert nfix == 0

# THD_compute_oblique_angle (ijk_to_dicom44=..., verbose=0) at thd_coords.c:724
def THD_compute_oblique_angle(ijk_to_dicom44):
   dxtmp = sqrt ( ijk_to_dicom44[0][0] * ijk_to_dicom44[0][0] +
                  ijk_to_dicom44[1][0] * ijk_to_dicom44[1][0] + 
                  ijk_to_dicom44[2][0] * ijk_to_dicom44[2][0]) 
   
   xmax = max(fabs(ijk_to_dicom44[0][0]),fabs(ijk_to_dicom44[1][0]),fabs(ijk_to_dicom44[2][0])) / dxtmp ;
   
   dytmp = sqrt ( ijk_to_dicom44[0][1] * ijk_to_dicom44[0][1] +
                  ijk_to_dicom44[1][1] * ijk_to_dicom44[1][1] + 
                  ijk_to_dicom44[2][1] * ijk_to_dicom44[2][1] ) ;
   
   ymax = max(fabs(ijk_to_dicom44[0][1]),
              fabs(ijk_to_dicom44[1][1]), 
              fabs(ijk_to_dicom44[2][1])) / dytmp ;
   
   dztmp = sqrt ( ijk_to_dicom44[0][2] * ijk_to_dicom44[0][2] +
                  ijk_to_dicom44[1][2] * ijk_to_dicom44[1][2] + 
                  ijk_to_dicom44[2][2] * ijk_to_dicom44[2][2] ) ;
   
   zmax = max(fabs(ijk_to_dicom44[0][2]),
               fabs(ijk_to_dicom44[1][2]), 
               fabs(ijk_to_dicom44[2][2])) / dztmp ;
   
   fig_merit = min(xmax,ymax,zmax) ;
   ang_merit = acos (fig_merit) * 180.0 / 3.141592653 ;
   # ABDOU DATASET2 1
   # assert fabs(ang_merit) <= .01, str(fabs(ang_merit))
   if fabs(ang_merit) > .01:
       pass
   else:
      ang_merit = 0.0
   return ang_merit

# THD_report_obliquity (dset=0x5577823408e0) at thd_coords.c:1139
def THD_report_obliquity(dset):
    '''
      checks angle and calls THD_compute_oblique_angle in same file  thd_coords.c 
      compute angle of greatest obliquity given transformation matrix

    '''
    # ABDOU DATASET2 1.1
    # assert THD_compute_oblique_angle(dset.daxes.ijk_to_dicom_real) == 0.0
    THD_compute_oblique_angle(dset.daxes.ijk_to_dicom_real)

# THD_open_one_dataset (pathname=0x7fff99093704 "swapped.nii.gz") at thd_opendset.c:243
def THD_open_one_dataset(nii_file):
    dset = THD_open_nifti(nii_file) ;
    THD_patch_brickim(dset)
    THD_report_obliquity(dset)
    return dset

# thd_niftiread.c
# TODO REVISIT
def THD_open_nifti(nii_file):
    nim = nifti_image_read(nii_file)
    ntt, nbuc = (nim.nt, nim.nu)

    if ntt > 1 and nbuc > 1:
       raise Exception("AFNI can't deal with 5 dimensional NIfTI")

    if nim.nz <= 0: nim.nz = 1
    nvals = max(ntt,nbuc)
    if nim.nv > 1: nvals *= nim.nv;
    if nim.nw > 1: nvals *= nim.nw
    if ntt > 1:
        ntt = nvals 
    else:
        nbuc = nvals

    if not np.isfinite(nim.scl_slope) or not np.isfinite(nim.scl_inter):
       raise Exception("bad scl_slope or scl_inter")  # TODO This is a warning ...

    scale_data = nim.scl_slope != 0.0 and nim.scl_inter != 0.0 ;
    datum = _datum(nim.datatype.item())
    statcode = 0 # How is this going to be used? Relevant?

    #if nim.qform_code > 0 and nim.sform_code > 0:
    if nim.qform_code <=  0 or nim.sform_code <= 0: raise Exception("...")

    R1 = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)
    LOAD_MAT(R1, nim.qto_xyz[0][0],
                nim.qto_xyz[0][1],
                nim.qto_xyz[0][2],
                nim.qto_xyz[1][0],
                nim.qto_xyz[1][1],
                nim.qto_xyz[1][2],
                nim.qto_xyz[2][0],
                nim.qto_xyz[2][1],
                nim.qto_xyz[2][2])

    qdet = MAT_DET(R1)
    R2 = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)
    LOAD_MAT(R2, 
             nim.sto_xyz[0][0], nim.sto_xyz[0][1], nim.sto_xyz[0][2],
             nim.sto_xyz[1][0], nim.sto_xyz[1][1], nim.sto_xyz[1][2],
             nim.sto_xyz[2][0], nim.sto_xyz[2][1], nim.sto_xyz[2][2]) 
    sdet = MAT_DET(R2)
    use_sform = 1   # TODO using sform by default
    if not use_sform: raise Exception("Only supports sform")
    form_code = nim.sform_code;
    # if use_sform
    orimap = [ 6 , 1 , 0 , 2 , 3 , 4 , 5] 
    oritmp = nifti_dmat44_to_orientation(nim.sto_xyz)
    orixyz = [ orimap[oritmp[0]], orimap[oritmp[1]], orimap[oritmp[2]] ]
    ORIENT_xyz   = "xxyyzzg"  # DICOM directions are
    ORIENT_xyzint = [1,1, 2,2, 3,3, 666]

    if ORIENT_xyz[orixyz[0]] == 'z':
       orgx = nim.sto_xyz[ORIENT_xyzint[orixyz[0]] - 1][3]
    else:
       orgx = - nim.sto_xyz[ORIENT_xyzint[orixyz[0]] - 1][3]

    if ORIENT_xyz[orixyz[1]] == 'z':
       orgy = nim.sto_xyz[ORIENT_xyzint[orixyz[1]] - 1][3]
    else:
       orgy = - nim.sto_xyz[ORIENT_xyzint[orixyz[1]] - 1][3]

    if ORIENT_xyz[orixyz[2]] == 'z':
       orgz = nim.sto_xyz[ORIENT_xyzint[orixyz[2]] - 1][3]
    else:
       orgz = - nim.sto_xyz[ORIENT_xyzint[orixyz[2]] - 1][3]
    
    orgxyz = [orgx, orgy, orgz]
    dxtmp = sqrt(nim.sto_xyz[0][0] * nim.sto_xyz[0][0] +
                 nim.sto_xyz[1][0] * nim.sto_xyz[1][0] +
                 nim.sto_xyz[2][0] * nim.sto_xyz[2][0])
    xmax = max(fabs(nim.sto_xyz[0][0]),fabs(nim.sto_xyz[1][0]),fabs(nim.sto_xyz[2][0])) / dxtmp
    dytmp = sqrt (nim.sto_xyz[0][1] * nim.sto_xyz[0][1] +
                  nim.sto_xyz[1][1] * nim.sto_xyz[1][1] +
                  nim.sto_xyz[2][1] * nim.sto_xyz[2][1]) 
    ymax = max(fabs(nim.sto_xyz[0][1]),fabs(nim.sto_xyz[1][1]),fabs(nim.sto_xyz[2][1])) / dytmp 
    dztmp = sqrt( nim.sto_xyz[0][2] * nim.sto_xyz[0][2] +
                  nim.sto_xyz[1][2] * nim.sto_xyz[1][2] +
                  nim.sto_xyz[2][2] * nim.sto_xyz[2][2])
    zmax = max(fabs(nim.sto_xyz[0][2]),fabs(nim.sto_xyz[1][2]),fabs(nim.sto_xyz[2][2])) / dztmp

    # TODO THESE LOOK LIKE NO LONER BEING USED
    fig_merit = min(xmax,ymax,zmax)
    ang_merit = acos(fig_merit) * 180.0 / 3.141592653

    # TODO 
    NIFTI_UNITS_METER = 1000 
    NIFTI_UNITS_MICRON = 2000
    
    if nim.xyz_units == NIFTI_UNITS_METER:
       dxtmp *= 1000.0; dytmp *= 1000.0; dztmp *= 1000.0
    elif nim.xyz_units == NIFTI_UNITS_MICRON:
       dxtmp *= 0.001; dytmp *= 0.001; dztmp *= 0.001

    ORIENT_sign = "+--++-"

    dxyz = [dxtmp if ORIENT_sign[orixyz[0]]=='+' else -dxtmp,
            dytmp if ORIENT_sign[orixyz[1]]=='+' else -dytmp,
            dztmp if ORIENT_sign[orixyz[2]]=='+' else -dztmp]

    ijk_to_dicom44 = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], np_type)
    LOAD_MAT44(ijk_to_dicom44, 
               -nim.sto_xyz[0][0],  
               -nim.sto_xyz[0][1],  # coefficients,    
               -nim.sto_xyz[0][2],  # since AFNI works 
               -nim.sto_xyz[0][3],
               -nim.sto_xyz[1][0],  # with RAI coords, 
               -nim.sto_xyz[1][1],  # but NIFTI uses   
               -nim.sto_xyz[1][2],  # LPI coordinates. 
               -nim.sto_xyz[1][3],
               nim.sto_xyz[2][0],   # [Which is my own] 
               nim.sto_xyz[2][1],   # [damn fault!!!!!] 
               nim.sto_xyz[2][2],
               nim.sto_xyz[2][3])

    #  make an AFNI dataset
    # is this important? iview = 0 # NIFTI_code_to_view(nim->sform_code, NULL) 
    # is this important? datum = 3; prefix="swapped.nii.gz";statcode=0
    # is this important? THD_init_diskptr_names( dset->dblk->diskptr , THD_filepath(pathnew) , NULL , prefix , dset->view_type , True );`
    # is this important? dset->idcode.str[0] = 'N' dset->idcode.str[1] = 'I' ; dset->idcode.str[2] = 'I' ;
    '''
    edt_dsetitems.c
    new_prefix,new_nxyz, new_xyzorg,new_xyzdel, ew_xyzorient, new_datum_all are all set
    EDIT_dset_items( dset ,
                        ADN_prefix      , prefix ,
                        ADN_datum_all   , datum ,
                        ADN_nxyz        , nxyz ,
                        ADN_xyzdel      , dxyz ,
                        ADN_xyzorg      , orgxyz ,
                        ADN_view_type   , iview ,
                        ADN_xyzorient   , orixyz ,
                        ADN_malloc_type , DATABLOCK_MEM_MALLOC ,
                        ADN_type        , (statcode != 0) ? HEAD_FUNC_TYPE
                                                          : HEAD_ANAT_TYPE ,
    '''
    nxyz = [nim.nx, nim.ny, nim.nz]                # grid dimensions
    dset = create_dset(nxyz, dxyz, orgxyz, orixyz)
    set_daxes_bbox(dset.daxes)
    
    assert ntt == 1
    if ntt > 2: raise Exception("ntt > 2 Not expecting a time dependent dataset")

    dset.daxes.ijk_to_dicom_real = ijk_to_dicom44;
    '''
    statcode = 0
    EDIT_dset_items( dset ,
                     ADN_nvals     , nbuc ,
                     ADN_datum_all , datum ,
                     ADN_func_type , (statcode != 0) ? FUNC_BUCK_TYPE : ANAT_BUCK_TYPE ,
                     ADN_none ) ;
    '''
    # nvals is really nbuc which is 1 , datum_array is just datum which is 3 
    # dset.dblk.nvals = dset.dblk.diskptr.nvals = nvals 
    assert nvals == nbuc == 1
    dset.dblk.nvals = dset.dblk.diskptr.nvals = nbuc 
    assert datum == 3
    THD_init_datablock_brick(dset.dblk, nvals, datum) 
    dset.func_type = "ANAT_BUCK_TYPE"  # TODO double check which EDIT_dset_items is called. 
    assert dset.dblk.diskptr.storage_mode == 10 # STORAGE_BY_NIFTI
    # byteorder should be set while computing nim  for now using 1
    # assert dset.dblk.diskptr.byte_order == nim.byteorder  
    assert dset.dblk.diskptr.byte_order == 1
    dset.img = nim.img
    return dset 

# ./thd_editdaxes.c: THD_set_daxes_bbox( THD_dataxes *daxes )
def set_daxes_bbox(daxes): # set bounding box for this dataset
        daxes.xxmin = daxes.xxorg
        daxes.xxmax = daxes.xxorg + (daxes.nxx-1) * daxes.xxdel

        if daxes.xxmin > daxes.xxmax:
           temp = daxes.xxmin
           daxes.xxmin = daxes.xxmax; daxes.xxmax = temp

        daxes.yymin = daxes.yyorg
        daxes.yymax = daxes.yyorg + (daxes.nyy-1) * daxes.yydel

        if daxes.yymin > daxes.yymax:
           temp = daxes.yymin
           daxes.yymin = daxes.yymax; daxes.yymax = temp

        daxes.zzmin = daxes.zzorg
        daxes.zzmax = daxes.zzorg + (daxes.nzz-1) * daxes.zzdel

        if daxes.zzmin > daxes.zzmax:
           temp = daxes.zzmin ;
           daxes.zzmin = daxes.zzmax; daxes.zzmax = temp

# mri_new_vol_empty (nx=512, ny=512, nz=35, kind=MRI_float) at mri_new.c:26
def mri_new_vol_empty(nx, ny, nz, kind):
    # mri_new_7D_generic( nx,ny,nz , 1,1,1,1 , kind , TRUE)
    # mri_new_7D_generic (nx=512, ny=512, nz=35, nt=1, nu=1, nv=1, nw=1, kind=MRI_float, make_space=0) at mri_new.c:44
    nt = nu = nv = nw = 1
    newim = SimpleNamespace()
    newim.nx = nx
    newim.ny = ny; newim.nxy= nx*ny 
    newim.nz = nz
    newim.nt = nt
    newim.nu = nu
    newim.nv = nv
    newim.nw = nw
    newim.nxyz  = nx*ny*nz
    newim.nxyzt = nx*ny*nz*nt
    newim.nvox  = newim.nxyzt*nu*nv*nw
    newim.kind = kind
    newim.name = None 
    newim.dx = newim.dy = newim.dz = newim.dt = newim.du = newim.dv = 1.0  # default dimensions 
    newim.dw = -666.0   # 05 Feb 2001 - flag that dimensions aren't set 
    newim.xo = newim.yo = newim.zo = newim.to = newim.uo = newim.vo = newim.wo = 0.0 # default offsets 
    newim.was_swapped = 0  # 07 Mar 2002 - flag that bytes were swapped 
    newimvdim = 0
    newim.fname = None
    newim.foffset = newim.fondisk = 0
    newim.comments = None
    npix = newim.nvox
    # case kind == MRI_float:   newim->pixel_size = sizeof(float)
    newim.pixel_size = 4 # size in bytes
    newim.im = None
    return newim
     
# thd_initdblk.c:1200
def THD_init_datablock_brick(dblk, ntype, btype):
    # this nvals ... from edt_setitems ...
    assert ntype == 1 and btype == 3
    itype = btype
    nx = dblk.diskptr.dimsizes[0]
    ny = dblk.diskptr.dimsizes[1]
    nz = dblk.diskptr.dimsizes[2]
    nvals = dblk.nvals; assert nvals == 1
    dblk.brick_bytes = []
    dblk.brick_fac = 0
    dblk.total_bytes = 0
    dblk.total_bytes = 0
    dblk.brick = SimpleNamespace(num=0, nall=32, imarr=[])

    # starting sub-brick creations
    typ = itype
    qim = mri_new_vol_empty(nx,ny,nz,typ)  # image with no data 
    dblk.brick.imarr.append(qim)
    dblk.brick.num = 1
    dblk.brick_bytes.append(qim.pixel_size * qim.nvox) 
    dblk.total_bytes += dblk.brick_bytes[0]

def dup_blk(blk):
        dblk = SimpleNamespace()
        dkptr = dblk.diskptr = SimpleNamespace()
        dkptr.dimsizes=[-1, -1, -1]
        dkptr.storage_mode = blk.diskptr.storage_mode 
        dkptr.byte_order = blk.diskptr.byte_order 

def create_dset(nxyz, xyzdel, xyzorg, xyzorient,smode=10, byteorder=1):
        dset = SimpleNamespace()
        dset.dblk = SimpleNamespace()
        dkptr = dset.dblk.diskptr = SimpleNamespace()
        daxes = dset.daxes = SimpleNamespace()
        dkptr.dimsizes=[-1, -1, -1]
        dkptr.storage_mode = smode 
        dkptr.byte_order = byteorder 
        daxes.nxx = dkptr.dimsizes[0] = nxyz[0]
        daxes.nyy = dkptr.dimsizes[1] = nxyz[1]
        daxes.nzz = dkptr.dimsizes[2] = nxyz[2]

        daxes.xxdel = xyzdel[0]
        daxes.yydel = xyzdel[1]
        daxes.zzdel = xyzdel[2]

        daxes.xxorg = xyzorg[0]
        daxes.yyorg = xyzorg[1]
        daxes.zzorg = xyzorg[2]

        daxes.xxorient = xyzorient[0]
        daxes.yyorient = xyzorient[1]
        daxes.zzorient = xyzorient[2]

        daxes.to_dicomm = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)
        # THD_set_daxes_bbox(daxes)  is named set_daxes_bbox rename it.
        set_daxes_bbox(dset.daxes)
        THD_daxes_to_mat44(daxes)
        daxes.ijk_to_dicom_real = daxes.ijk_to_dicom
        THD_set_dicom_box(daxes)
        THD_set_daxes_to_dicomm(daxes) 

        # TODO? assuming nvals = 1 and datum_array == 3  basically 1 brick and kind==MRIFloat
        dset.dblk.nvals = 1
        THD_init_datablock_brick(dset.dblk, 1, 3)
        return dset

def dup_daxes(ain):
        daxes = SimpleNamespace()
        daxes.nxx = ain.nxx
        daxes.nyy = ain.nyy
        daxes.nzz = ain.nzz
        daxes.xxdel = ain.xxdel
        daxes.yydel = ain.yydel
        daxes.zzdel = ain.zzdel
        daxes.xxorg = ain.xxorg
        daxes.yyorg = ain.yyorg
        daxes.zzorg = ain.zzorg
        daxes.xxorient = ain.xxorient
        daxes.yyorient = ain.yyorient
        daxes.zzorient = ain.zzorient
        daxes.xxmin = ain.xxmin 
        daxes.xxmax = ain.xxmax
        daxes.yymin = ain.yymin 
        daxes.yymax = ain.yymax
        daxes.zzmin = ain.zzmin 
        daxes.zzmax = ain.zzmax
        return daxes 

def print_daxes(daxes):
        print("daxes:")
        print("                 (nxx, nyy, nzz):", (daxes.nxx, daxes.nyy, daxes.nzz))
        print("           (xxorg, yyorg, zzorg):", (daxes.xxorg, daxes.yyorg, daxes.zzorg))
        print("           (xxdel, yydel, zzdel):", (daxes.xxdel, daxes.yydel, daxes.zzdel))
        print("           (xxmin, yymin, zzmin):", (daxes.xxmin, daxes.yymin, daxes.zzmin))
        print("           (xxmax, yymax, zzmax):", (daxes.xxmax, daxes.yymax, daxes.zzmax))
        print("    (xxorient,yyorient,zzorient):", (daxes.xxorient, daxes.yyorient, daxes.zzorient))

def print_dset(dset):
        daxes = dset.daxes
        print("daxes:")
        print("                 (nxx, nyy, nzz):", (daxes.nxx, daxes.nyy, daxes.nzz))
        print("           (xxorg, yyorg, zzorg):", (daxes.xxorg, daxes.yyorg, daxes.zzorg))
        print("           (xxdel, yydel, zzdel):", (daxes.xxdel, daxes.yydel, daxes.zzdel))
        print("           (xxmin, yymin, zzmin):", (daxes.xxmin, daxes.yymin, daxes.zzmin))
        print("           (xxmax, yymax, zzmax):", (daxes.xxmax, daxes.yymax, daxes.zzmax))
        print("    (xxorient,yyorient,zzorient):", (daxes.xxorient, daxes.yyorient, daxes.zzorient))


ORI_R2L_TYPE = 0
ORI_L2R_TYPE = 1
ORI_P2A_TYPE = 2
ORI_A2P_TYPE = 3
ORI_I2S_TYPE = 4
ORI_S2I_TYPE = 5

# ABDOU DATASET2 2 
# ./thd_coords.c:567
def THD_dicom_card_xform(dset , tmat, dics):
    assert dset.daxes.xxorient == ORI_L2R_TYPE or dset.daxes.xxorient == ORI_R2L_TYPE, str(dset.daxes.xxorient)
    assert dset.daxes.yyorient == ORI_A2P_TYPE or dset.daxes.yyorient == ORI_P2A_TYPE, str(dset.daxes.yyorient)
    assert dset.daxes.zzorient == ORI_I2S_TYPE or dset.daxes.zzorient == ORI_S2I_TYPE, str(dset.daxes.zzorient)
    tmat[0][0] = dset.daxes.xxdel; tmat[0][1] = tmat[0][2] = 0.0
    dics[0] = dset.daxes.xxorg
    
    tmat[1][1] = dset.daxes.yydel;tmat[1][0] = tmat[1][2] = 0.0
    dics[1] = dset.daxes.yyorg
    
    tmat[2][2] = dset.daxes.zzdel; tmat[2][0] = tmat[2][1] = 0.0
    dics[2] = dset.daxes.zzorg

#  thd_coords.c:1221
# EXPECTED: np.array([[-1, 0, 0, 124.255859], [0, 1, 0, 38.2558594], [0, 0, 1, -186.600006], [0, 0, 0, 1]], np_type)
def THD_make_cardinal(dset):
   tmat = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)
   tvec  = np.array([0, 0, 0], np_type)
   THD_dicom_card_xform(dset , tmat, tvec)
   Tc = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], np_type)
   LOAD_MAT44(Tc, 
              tmat[0][0], tmat[0][1], tmat[0][2], tvec[0],
              tmat[1][0], tmat[1][1], tmat[1][2], tvec[1],
              tmat[2][0], tmat[2][1], tmat[2][2], tvec[2])
   dset.daxes.ijk_to_dicom_real = Tc;

def LOAD_DIAG_MAT(A,x,y,z):
   A[0][0] = x
   A[1][1] = y
   A[2][2] = z
   A[0][1] = A[0][2] = A[1][0] = A[1][2] = A[2][0] = A[2][1] = 0.0 

#def TRANSPOSE_MAT(A) \
# ( tempA_mat33.mat[0][0] = (A).mat[0][0] , \
#   tempA_mat33.mat[1][0] = (A).mat[0][1] , \
#   tempA_mat33.mat[2][0] = (A).mat[0][2] , \
#   tempA_mat33.mat[0][1] = (A).mat[1][0] , \
#   tempA_mat33.mat[1][1] = (A).mat[1][1] , \
#   tempA_mat33.mat[2][1] = (A).mat[1][2] , \
#   tempA_mat33.mat[0][2] = (A).mat[2][0] , \
#   tempA_mat33.mat[1][2] = (A).mat[2][1] , \
#   tempA_mat33.mat[2][2] = (A).mat[2][2] , tempA_mat33 )

def MATVEC(A,x): 
   return [ A[0][0] * x[0] + A[0][1] * x[1] + A[0][2] * x[2],
            A[1][0] * x[0] + A[1][1] * x[1] + A[1][2] * x[2],
            A[2][0] * x[0] + A[2][1] * x[1] + A[2][2] * x[2]]

def SUB_FVEC3(a,b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]

def ADD_FVEC3(a,b):
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


def NEGATE_FVEC3(a):
    return [-a[0], -a[1], -a[2]]

def MAT_INV(A):
    tempRWC = 1.0 / MAT_DET(A)
    tempA = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)
    tempA[1][1] = (A[0][0]*A[2][2]-A[0][2]*A[2][0]) * tempRWC
    tempA[2][2] = (A[0][0]*A[1][1]-A[0][1]*A[1][0]) * tempRWC
    tempA[2][0] = (A[1][0]*A[2][1]-A[1][1]*A[2][0]) * tempRWC
    tempA[1][2] = (-A[0][0]*A[1][2]+A[0][2]*A[1][0]) * tempRWC
    tempA[0][1] = (-A[0][1]*A[2][2]+A[0][2]*A[2][1]) * tempRWC
    tempA[0][0] = (A[1][1]*A[2][2]-A[1][2]*A[2][1]) * tempRWC
    tempA[2][1] = (-A[0][0]*A[2][1]+A[0][1]*A[2][0]) * tempRWC
    tempA[1][0] = (-A[1][0]*A[2][2]+A[1][2]*A[2][0]) * tempRWC
    tempA[0][2] = (A[0][1]*A[1][2]-A[0][2]*A[1][1]) * tempRWC
    return tempA 

def AFNI_make_voxmap(inmap, old_daxes, new_daxes):
   # THD_mat33 old_scale , old_3dmm_to_dicomm , dd_trans  , new_scale , new_dicomm_to_3dmm , mt ; /* temp matrix */
   old_scale = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)
   new_scale = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)

   # old_scale = old_3dmm_to_dicomm = dd_trans = new_scale = new_dicomm_to_3dmm = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np_type)
   # THD_fvec3 dd_base , new_origin , old_origin , vt0,vt1,vt2 ;
   # dd_base = new_origin = old_origin  = vt0 = vt1 = vt2 = [0, 0, 0]

   dd_trans = inmap.mfor 

   LOAD_DIAG_MAT(old_scale, old_daxes.xxdel, old_daxes.yydel , old_daxes.zzdel)
   LOAD_DIAG_MAT(new_scale, 1.0/new_daxes.xxdel, 1.0/new_daxes.yydel, 1.0/new_daxes.zzdel)
   old_3dmm_to_dicomm = old_daxes.to_dicomm.copy()
   new_dicomm_to_3dmm = np.transpose(new_daxes.to_dicomm.copy()) # TRANSPOSE_MAT(new_daxes.to_dicomm) 
   dd_base = inmap.bvec 

   new_origin = [new_daxes.xxorg, new_daxes.yyorg, new_daxes.zzorg]
   old_origin = [old_daxes.xxorg, old_daxes.yyorg, old_daxes.zzorg]

   mt = np.multiply(old_3dmm_to_dicomm, old_scale) # MAT_MUL(old_3dmm_to_dicomm , old_scale);   do_nothing(0)
   mt = np.multiply(dd_trans, mt)                  # MAT_MUL(dd_trans , mt);                    do_nothing(0)
   mt = np.multiply(new_dicomm_to_3dmm, mt)        # MAT_MUL(new_dicomm_to_3dmm , mt);          do_nothing(0)
   mt = np.multiply(new_scale, mt)                 # MAT_MUL(new_scale , mt);                   do_nothing(0)

   vt0 = MATVEC(old_3dmm_to_dicomm, old_origin)
   vt0 = MATVEC(dd_trans , vt0)
   vt0 = MATVEC(new_dicomm_to_3dmm, vt0)
   vt0 = MATVEC(new_scale , vt0)

   vt1 = MATVEC(new_dicomm_to_3dmm, dd_base)
   vt1 = MATVEC(new_scale, vt1) 

   vt2 = MATVEC(new_scale, new_origin) # want vt1 + vt2 - vt0 
   vt2 = ADD_FVEC3(vt1, vt2)
   vt2 = SUB_FVEC3(vt2, vt0)

   newmap = SimpleNamespace()
   newmap.type = 0  # MAPPING_LINEAR_TYPE
   newmap.mfor = mt
   newmap.mbac = np.linalg.inv(mt)  # MAT_INV(mt)
   newmap.bvec = vt2
   newmap.svec = MATVEC(newmap.mbac,newmap.bvec)
   newmap.svec = NEGATE_FVEC3(newmap.svec)
   return newmap

# thd_warps.c:27
def AFNI_make_voxwarp(inwarp, old_dset, new_dset):
    assert inwarp.type == 0
    newwarp = SimpleNamespace()
    newwarp.rig_bod = SimpleNamespace()
    temp = newwarp.rig_bod.warp = SimpleNamespace()
    new_daxes = new_dset.daxes   # SHOULD THIS BE A DEEP COPY
    temp = newwarp.rig_bod.warp = AFNI_make_voxmap(inwarp.rig_bod.warp, old_dset.daxes, new_daxes)
    temp.type = inwarp.type 
    temp.bot = [0, 0, 0]
    temp.top = [new_daxes.nxx-1, new_daxes.nyy-1, new_daxes.nzz-1]
    return newwarp
 
   
def DSET_load(dset):
   assert 1 == 0

def AFNI_lmap_to_zslice_float(rig_bod_warp, resam_mode, old_daxes, bold, new_daxes, zk_fix, bslice):
    assert bold is not None and bslice is not None
    assert resam_mode == 0
    dmap = rig_bod_warp
    mt = dmap.mbac
    vt = dmap.svec 
    xi_bot = dmap.bot[0]; xi_top = dmap.top[0] 
    yj_bot = dmap.bot[1]; yj_top = dmap.top[1]
    zk_bot = dmap.bot[2]; zk_top = dmap.top[2] 
    assert zk_fix >= zk_bot and zk_fix <= zk_top 
    nxold = old_daxes.nxx;  nxnew = new_daxes.nxx 
    nyold = old_daxes.nyy;  nynew = new_daxes.nyy
    nzold = old_daxes.nzz;  nznew = new_daxes.nzz ;
    jstep = nxold
    kstep = nxold * nyold
    xi_new = xi_bot-1
    yj_new = yj_bot-1
    zk_new = zk_fix
    fxi_base = mt[0][0] * xi_new + mt[0][1] * yj_new + mt[0][2] * zk_new - vt[0]
    fyj_base = mt[1][0] * xi_new + mt[1][1] * yj_new + mt[1][2] * zk_new - vt[1]

    fzk_base = mt[2][0] * xi_new + mt[2][1] * yj_new + mt[2][2] * zk_new - vt[2]

    dfxi_outer = mt[0][1] 
    dfyj_outer = mt[1][1]
    dfzk_outer = mt[2][1] 

    dfxi_inner = mt[0][0]  # inner loop is in x = 0 
    dfyj_inner = mt[1][0]
    dfzk_inner = mt[2][0]
 
    fxi_top = nxold - 0.51;  fxi_bot = -0.49
    fyj_top = nyold - 0.51;  fyj_bot = -0.49
    fzk_top = nzold - 0.51;  fzk_bot = -0.49

    def FXYZTMP(xx, yy, zz):
        fxi_tmp = mt[0][0] * xx + mt[0][1] * yy + mt[0][2] * zz - vt[0] 
        fyj_tmp = mt[1][0] * xx + mt[1][1] * yy + mt[1][2] * zz - vt[1]
        fzk_tmp = mt[2][0] * xx + mt[2][1] * yy + mt[2][2] * zz - vt[2]
        return fxi_tmp, fyj_tmp, fzk_tmp

    fxi_tmp, fyj_tmp, fzk_tmp = fxi_tmp, fyj_tmp, fzk_tmp = FXYZTMP(xi_bot,yj_bot,zk_new) ;
    fxi_max = fxi_min = fxi_tmp ;
    fyj_max = fyj_min = fyj_tmp ;
    fzk_max = fzk_min = fzk_tmp ;

    fxi_tmp, fyj_tmp, fzk_tmp = FXYZTMP(xi_top,yj_bot,zk_new) ;
    xi_max = max(fxi_max,fxi_tmp) ; fxi_min = min(fxi_min,fxi_tmp) ;
    fyj_max = max(fyj_max,fyj_tmp) ; fyj_min = min(fyj_min,fyj_tmp) ;
    fzk_max = max(fzk_max,fzk_tmp) ; fzk_min = min(fzk_min,fzk_tmp) ;

    fxi_tmp, fyj_tmp, fzk_tmp = FXYZTMP(xi_bot,yj_top,zk_new) ;
    fxi_max = max(fxi_max,fxi_tmp) ; fxi_min = min(fxi_min,fxi_tmp) ;
    fyj_max = max(fyj_max,fyj_tmp) ; fyj_min = min(fyj_min,fyj_tmp) ;
    fzk_max = max(fzk_max,fzk_tmp) ; fzk_min = min(fzk_min,fzk_tmp) ;

    fxi_tmp, fyj_tmp, fzk_tmp = FXYZTMP(xi_top,yj_top,zk_new) ;
    fxi_max = max(fxi_max,fxi_tmp) ; fxi_min = min(fxi_min,fxi_tmp) ;
    fyj_max = max(fyj_max,fyj_tmp) ; fyj_min = min(fyj_min,fyj_tmp) ;
    fzk_max = max(fzk_max,fzk_tmp) ; fzk_min = min(fzk_min,fzk_tmp) ;


    any_outside = (fxi_min < fxi_bot) or (fxi_max > fxi_top) or (fyj_min < fyj_bot) or (fyj_max > fyj_top) or (fzk_min < fzk_bot) or (fzk_max > fzk_top)
    all_outside = 0

    if any_outside: 
        all_outside = (fxi_max < fxi_bot) or (fxi_min > fxi_top) or (fyj_max < fyj_bot) or (fyj_min > fyj_top) or (fzk_max < fzk_bot) or (fzk_min > fzk_top)

    assert any_outside == False
    assert all_outside == 0
    fxi_base += 0.5; fyj_base += 0.5; fzk_base += 0.5
    fxi_top = nxold - 0.01; fxi_bot = 0.0 
    fyj_top = nyold - 0.01; fyj_bot = 0.0
    fzk_top = nzold - 0.01; fzk_bot = 0.0

    ZZZ = 1.e-5  

    def THREEZ(x,y,z):
           return x + 2 * y + 4 * z

    x = 1 if fabs(dfxi_outer) < ZZZ else 0
    y = 1 if fabs(dfyj_outer) < ZZZ else 0
    z = 1 if fabs(dfzk_outer) < ZZZ else 0
    tho = THREEZ(x,y,z) 

    # TODO check tho == XY_ZERO || tho == XZ_ZERO || tho == YZ_ZERO 
    x = 1 if fabs(dfxi_inner) < ZZZ else 0
    y = 1 if fabs(dfyj_inner) < ZZZ else 0
    z = 1 if fabs(dfzk_inner) < ZZZ else 0
    thz = THREEZ(x,y,z)
    # TODAY ABDOU
    
    # case YZ_ZERO
    YZ_ZERO = 6

    ib = []
    nib = xi_top
    xi_old = -1

    assert thz == YZ_ZERO
    if thz == YZ_ZERO:
        def IBASE(i,j,k):
             return i+j*jstep+k*kstep

        fxi_old = fxi_base + dfxi_outer; ub = IBASE(nxold,0,0) 
        xi_new = xi_bot
        while xi_new <= xi_top:
            fxi_old += dfxi_inner
            xi_old = floor(fxi_old)
            ib.append(IBASE(xi_old,0,0))
            xi_new += 1

    OUTADD= 100  # define OUTADD  100
    thz += OUTADD * any_outside 
    yj_new = yj_bot

    while yj_new <= yj_top:
        fxi_base += dfxi_outer
        fxi_old = fxi_base

        if zk_fix == 5:
           holder = fyj_base
        fyj_base += dfyj_outer
        fyj_old = fyj_base
        fzk_base += dfzk_outer
        fzk_old = fzk_base

        out_ind = xi_bot + yj_new * nxnew

        # case thz is YZ_ZERO
        yj_old = floor(fyj_old); zk_old = floor(fzk_old)

        ob = IBASE(0,yj_old,zk_old) ;
        xi_new = xi_bot

        # HOLA ABDOU: RESTORE THIS: while xi_new <= xi_top:
        while xi_new <= xi_top:
            old_val = bold[ib[xi_new] + ob]
            bslice[out_ind] = old_val
            out_ind += 1
            xi_new  += 1

        yj_new += 1

def AFNI_dataset_slice(dset, fixed_axis, fixed_index, ival, resam_mode):
    assert resam_mode == 0
    assert fixed_axis == 3 

    typ = "MRI_float" # (ival < 0 ) ? MRI_short : DSET_BRICK_TYPE(dset,ival) ;
    daxes = dset.daxes
    nxx   = daxes.nxx
    nyy   = daxes.nyy
    nzz   = daxes.nzz

    newim = SimpleNamespace() # mri_new( nxx , nyy , typ ) ;
    newim.nxx = nxx
    newim.nyy = nyy
    newim.typ = typ
    newim.dx = fabs(daxes.xxdel)
    newim.dy = fabs(daxes.yydel)
    newim.dz = fabs(daxes.zzdel)

    ### AES_NEW
    parent_to_child_warp = dset.warp
    parent_to_child_warp.rig_bod = SimpleNamespace()
    temp = parent_to_child_warp.rig_bod.warp = SimpleNamespace()
    temp.mfor = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    temp.mbac = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    temp.bvec = [0, 0, 0]
    temp.svec = [0, 0, 0]
    temp.bot = [-9999, -9999, -9999]
    temp.top = [9999, 9999, 9999]

    parent_dset = dset.warp_parent 
    qwarp = AFNI_make_voxwarp(parent_to_child_warp, parent_dset, dset)
    dset.vox_warp= qwarp 
    dset.vox_warp.type = "WARP_AFFINE_TYPE"
    #bslice = [] # This is where the bytes are going
    #bslice = [0] * (yj_top + 1) * (xi_top + 1)
    # TODAY ABDOU
    bslice = [0] * nxx * nyy
    bold = dset.img.get_fdata().transpose()
    shape = bold.shape
    bold = bold.reshape((shape[0] * shape[1] * shape[2],))
    AFNI_lmap_to_zslice_float(dset.vox_warp.rig_bod.warp, 
               resam_mode, parent_dset.daxes,
               bold,
               dset.daxes,
               fixed_index,
               bslice)
    return bslice 

# ./rickr/r_new_resam_dset.c:284
def r_fill_resampled_data_brick(dset):
    nx = dset.daxes.nxx;  ny = dset.daxes.nyy;  nz = dset.daxes.nzz;
    nv = dset.dblk.diskptr.nvals;
    nxy  = nx * ny;
    nxyz = nx * ny * nz;
    dsize = 4  #  mri_datum_size( DSET_BRICK_TYPE(dset, ival) 
    
    assert nv == 1   # One brick.
    ival = nv - 1
    slices = []
    
    for slize in range(nz):
       bslice = AFNI_dataset_slice(dset, 3, slize, 0, 0)
       slices.append(bslice)
       zk_fix = slize
       if zk_fix == 0 or zk_fix == 87 or  zk_fix == 174:
           arr = np.array(bslice)
    return slices

# nifti/nifti2/nifti2_io.c:7357
def nifti_convert_nim2n1hdr(nim):
    # TODO: compute these
    nim.dt = 0
    nim.xyzt_units = 2
    nim.time_units = 0 
    nim.iname_offset = 2720
    nim.toffset = 0

    assert nim.qform_code > 0 
    assert nim.xyzt_units == 2

    hdr = nib.nifti1.Nifti1Header()
    hdr['vox_offset'] = nim.iname_offset
    hdr['xyzt_units'] = 2 # SPACE_TIME_TO_XYZT( nim->xyz_units, nim->time_units ) ;
    hdr['toffset'] = nim.toffset

    dim = hdr['dim']
    dim[0] = nim.ndim ;
    dim[1] = nim.nx; dim[2] = nim.ny; dim[3] = nim.nz 
    dim[4] = nim.nt; dim[5] = nim.nu; dim[6] = nim.nv 
    dim[7] = nim.nw
    pixdim = hdr['pixdim']
    pixdim[0] = 0.0 ;
    pixdim[1] = nim.dx; pixdim[2] = nim.dy
    pixdim[3] = nim.dz; pixdim[4] = nim.dt
    pixdim[5] = nim.du; pixdim[6] = nim.dv;
    pixdim[7] = nim.dw;

    hdr['datatype'] = nim.datatype
    hdr['bitpix'] = 8 * nim.nbyper

    pixdim[1] = fabs(pixdim[1])
    pixdim[2] = fabs(pixdim[2])
    pixdim[3] = fabs(pixdim[3])
    pixdim[4] = fabs(pixdim[4])
    pixdim[5] = fabs(pixdim[5])
    pixdim[6] = fabs(pixdim[6])
    pixdim[7] = fabs(pixdim[7])

    if nim.qform_code > 0:
       hdr['qform_code'] = nim.qform_code
       # hdr['quatern_b'] = nim.quatern_b
       # hdr['quatern_c'] = nim.quatern_c
       # hdr['quatern_d'] = nim.quatern_d
       # hdr['qoffset_x'] = nim.qoffset_x
       # hdr['qoffset_y'] = nim.qoffset_y
       # hdr['qoffset_z'] = nim.qoffset_z 
       pixdim[0] = 1.0 if nim.qfac >= 0.0 else -1.0

    return hdr
   
def do_resample(in_file, out_file):
    np.set_printoptions(precision=30, suppress=True)
    nii_file = in_file
    dset = THD_open_one_dataset(nii_file) 
    
    daxin = dset.daxes
    daxout = SimpleNamespace(**daxin.__dict__) # dup_daxes(dset.daxes) 
    daxout.dicom_to_ijk=daxin.dicom_to_ijk.copy()
    daxout.ijk_to_dicom=daxin.ijk_to_dicom.copy()
    daxout.ijk_to_dicom_real=daxin.ijk_to_dicom_real.copy()

    bound_type = 0
    r_dxyz_mod_dataxes(1.0, 1.0, 1.0, daxin, daxout, bound_type)
    dout = SimpleNamespace()

    dout.dblk = SimpleNamespace(**dset.dblk.__dict__)  # Deep copy is needed here
    dout.dblk.diskptr=SimpleNamespace(**dset.dblk.diskptr.__dict__) # dout.dblk.diskptr.dimsizes.copy()
    dout.dblk.diskptr.dimsizes = dout.dblk.diskptr.dimsizes.copy()

    dout.dblk.diskptr.storage_mode = 10 # STORAGE_BY_NIFTI 
    dout.daxes = SimpleNamespace(**daxin.__dict__)
    dout.daxes.dicom_to_ijk=daxin.dicom_to_ijk.copy()
    dout.daxes.ijk_to_dicom=daxin.ijk_to_dicom.copy()
    dout.daxes.ijk_to_dicom_real=daxin.ijk_to_dicom_real.copy()
    apply_dataxes(dout, daxout)

    dout.wod_flag = True
    dout.wod_daxes = dup_daxes(dset.daxes)   # ????
    dout.warp = SimpleNamespace(type=0) # IDENTITY_WARP type=WARP_AFFINE_TYPE
    dout.warp_parent = dset
    img = dout.img = dset.img
    dout.dblk.diskptr.byte_order = 1
    dout.dblk.diskptr.storage_mode = 2 # STORAGE_BY_BRICK
    THD_daxes_to_mat44(dout.daxes)
    THD_make_cardinal(dout)
    slices = r_fill_resampled_data_brick(dout)
    nim = populate_nifti_image(dout)
    arrays = []
    for slize in slices:
        ## MODIFIED FOR BR-1003 arr = np.array(slize).reshape(dout.daxes.nxx, dout.daxes.nyy)
        arr = np.array(slize).reshape(nim.ny, nim.nx)
        arrays.append(arr)

    slices = np.array(arrays)
    slices = slices.transpose()
    header = nifti_convert_nim2n1hdr(nim)
    newimg = img.__class__(slices, header=header, affine=nim.sto_xyz)
    nib.save(newimg, out_file)

def do_reorient(in_file, out_file):
    from nipype.interfaces.image import Reorient
    reorient = Reorient(orientation='LAS')
    reorient.inputs.in_file = in_file 
    res = reorient.run()
    os.rename(res.outputs.out_file, out_file)

if __name__ == '__main__':
    temp_file1 = 'python_resampled.nii.gz'
    do_resample(sys.argv[1], temp_file1)
    temp_file2 = 'python_resampled_and_oriented.nii.gz'
    do_reorient(temp_file1, temp_file2)
