# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 22:44:48 2023

@author: Martyna
"""

import numpy as np
import math
from math import sqrt

class Transformacje:

    def __init__(self, model: str = "wgs84"):
        if model == "wgs84":
            self.a = 6378137.0
            self.b = 6356752.31424518
        elif model == "grs80":
            self.a = 6378137.0
            self.b = 6356752.31414036
        else:
            raise NotImplementedError(f"{model} model not implemented")
        self.flattening = (self.a - self.b) / self.a
        self.e2 = sqrt(2 * self.flattening - self.flattening ** 2)
        

    def hirvonen (self, X, Y, Z):
            r = math.sqrt(X**2 + Y**2)
            #print(r)
            fi_n = math.atan(Z/(r*(1-self.e2)))
            eps = 0.000001/3600 *math.pi/180
            fi = fi_n*2
            while np.abs(fi_n - fi) > eps:
                fi = fi_n
                N = self.a/np.sqrt(1-self.e2*np.sin(fi_n)**2)
                h = r/np.cos(fi_n) -N
                fi_n = math.atan(Z/(r*(1-self.e2*(N/(N + h)))))
            lam = math.atan(Y/X)
            h = r/np.cos(fi_n) -N
            return fi, lam, h
    
    
    
    def geodezyjne2XYZ(self,fi, lam, h):
        N = self.a/math.sqrt(1-self.e2*math.sin(fi)**2)
        X = (N + h) * math.cos(fi) * math.cos(lam)
        Y = (N + h) * math.cos(fi) * math.sin(lam)
        Z = (N*(1-self.e2) + h) * math.sin(fi)
        return(X, Y, Z)
    
    
    def neu(self, X0, Y0, Z0, X, Y, Z):
        fi, lam, h = self.hirvonen(X, Y, Z)
        
        delta_X = X - X0
        delta_Y = Y - Y0    
        delta_Z = Z - Z0
        
        R = np.matrix([((-np.sin(fi) * np.cos(lam)), (-np.sin(fi) * np.sin(lam)), (np.cos(fi))),
                       ((-np.sin(lam)), (np.cos(lam)), (0)),
                       (( np.cos(fi) * np.cos(lam)), (np.cos(fi) * np.sin(lam)), (np.sin(fi)))])
    
    
        d = np.matrix([delta_X, delta_Y, delta_Z])
        d = d.T
        neu = R * d
        n = neu[0,0]
        e = neu[1,0]
        u = neu[2,0]
        return(n, e, u)
    
    def u2000(self, fi, lam):
        m = 0.999923
        N = self.a/math.sqrt(1-self.e2*math.sin(fi)**2)
        t = np.tan(fi)
        e_2 = self.e2/(1-self.e2)
        n2 = e_2 * (np.cos(fi))**2
        
        lam = math.degrees(lam)
        if lam>13.5 and lam <16.5:
            s = 5
            lam0 = 15
        elif lam>16.5 and lam <19.5:
            s = 6
            lam0 = 18
        elif lam>19.5 and lam <22.5:
            s = 7
            lam0 = 21
        elif lam>22.5 and lam <25.5:
            s = 8
            lam0 = 24
            
        lam = math.radians(lam)
        lam0 = math.radians(lam0)
        l = lam - lam0
    
        A0 = 1 - (self.e2/4) - ((3*(self.e2**2))/64) - ((5*(self.e2**3))/256)   
        A2 = (3/8) * (self.e2 + ((self.e2**2)/4) + ((15 * (self.e2**3))/128))
        A4 = (15/256) * (self.e2**2 + ((3*(self.e2**3))/4))
        A6 = (35 * (self.e2**3))/3072 
        
    
        sig = self.a * ((A0*fi) - (A2*np.sin(2*fi)) + (A4*np.sin(4*fi)) - (A6*np.sin(6*fi)))
        
        x = sig + ((l**2)/2) * N *np.sin(fi) * np.cos(fi) * (1 + ((l**2)/12) * ((math.cos(fi))**2) * (5 - t**2 + 9*n2 + 4*(n2**2)) + ((l**4)/360) * ((math.cos(fi))**4) * (61 - (58*(t**2)) + (t**4) + (270*n2) - (330 * n2 *(t**2))))
        y = l * (N*math.cos(fi)) * (1 + ((((l**2)/6) * (math.cos(fi))**2) * (1-t**2+n2)) +  (((l**4)/(120)) * (math.cos(fi)**4)) * (5 - (18 * (t**2)) + (t**4) + (14*n2) - (58*n2*(t**2))))
        
        x00 = round(m * x, 3) 
        y00 = round(m * y + (s*1000000) + 500000, 3)
         
        return(x00, y00)
    
    def u1992(self, fi, lam):
        m_0 = 0.9993
        N = self.a/(np.sqrt(1-self.e2 * np.sin(fi)**2))
        t = np.tan(fi)
        e_2 = self.e2/(1-self.e2)
        n2 = e_2 * (np.cos(fi))**2
        
        lam_0 = math.radians(19)
        l = lam - lam_0
        
        A0 = 1 - (self.e2/4) - ((3*(self.e2**2))/64) - ((5*(self.e2**3))/256)   
        A2 = (3/8) * (self.e2 + ((self.e2**2)/4) + ((15 * (self.e2**3))/128))
        A4 = (15/256) * (self.e2**2 + ((3*(self.e2**3))/4))
        A6 = (35 * (self.e2**3))/3072 
        
    
        sig = self.a * ((A0*fi) - (A2*np.sin(2*fi)) + (A4*np.sin(4*fi)) - (A6*np.sin(6*fi)))
        
        x = sig + ((l**2)/2) * N *np.sin(fi) * np.cos(fi) * (1 + ((l**2)/12) * ((math.cos(fi))**2) * (5 - t**2 + 9*n2 + 4*(n2**2)) + ((l**4)/360) * ((math.cos(fi))**4) * (61 - (58*(t**2)) + (t**4) + (270*n2) - (330 * n2 *(t**2))))
        y = l * (N*math.cos(fi)) * (1 + ((((l**2)/6) * (math.cos(fi))**2) * (1-t**2+n2)) +  (((l**4)/(120)) * (math.cos(fi)**4)) * (5 - (18 * (t**2)) + (t**4) + (14*n2) - (58*n2*(t**2))))
        
        x92 = round(m_0*x - 5300000, 3)
        y92 = round(m_0*y + 500000, 3)
        return x92, y92

    def azymut_elewacja(self, X0, Y0, Z0, X, Y, Z):
        n,e,u = self.neu(X0, Y0, Z0, X, Y, Z)

        hz = math.sqrt(e**2 + n**2)  # odleglosc horyzontalna
        el = math.sqrt(e**2 + n**2 + u**2)  # dlugosc wektora
        azymut = math.atan2(e,n)
        elewacja = math.atan2(u,hz)

        if azymut < 0:
            azymut += 2 * math.pi

        return(math.degrees(azymut), math.degrees(elewacja))

    def odleglosc_2D_3D(self, A,B,C,A1,B1,C1):
        dX = A - A1
        dY = B - B1
        dZ = C - C1

        d_2D = sqrt((dX**2) + (dY**2))
        d_3D = sqrt((dX**2) + (dY**2) + (dZ**2))
        return (d_2D, d_3D)
    