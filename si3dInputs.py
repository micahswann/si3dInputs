"""
si3dInputs.py
This script serves to create the files needed for the SI3D model runs. The code is based on previous matlab versions created by Alicia Cortes and Francisco Rueda.
Functions that are present within this script are:
1. bathy4si3d
    This function writes the bathymetry file 'h' for si3d simulations. The code considers canonical and real basins. The use of this function is found next for each of the basins considered:
    if the basin is a real lake use the functions as: bathy4si3d(BasinType,SimName,dx,xg,yg,zg)
    where xg, yg, and zg are 2-D matrices that contain the grid dimensions for the horizontal dimension based on a x=0,y=0 origin, and for the vetical dimension uses the depth of the lake with origin z=0 at the lake's surface amd NEGATIVE z values.
    if the basin is rectangular use the functions as: bathy4si3d(BasinType,SimName,dx,L,B,H)
    if the basin is spherical use the functions as: bathy4si3d(BasinType,SimName,dx,D,H)
    if the basin is cylindrical use the functions as: bathy4si3d(BasinType,SimName,dx,D,H)
    Where L,B,H are the dimensions of length, width, and depth for the rectangular basin. D,H are the diameter and depth respectively for the cylindrical and spherical basins.
    The file name will have the description of the grid size dx and the type of basin. This is for referencing but the user must change this name to 'h' to be able to run simulations in Si3D model
2. initCond4si3d
    This function writes the initial condition file 'si3d_init.txt' for si3d simulations. The code considers constant and variable thickness layers, and the same for the temperature profiles. The use of the function is shown next for each of the scenarios. (4)
    Constant thickness and constant Temperature initCond4si3d(LakeName,SimStartDate,DeltaZ,TempProf,PathSave,NTracers,H,dz,Tc)
    Constant thickness and variable temperature profile initCond4si3d(LakeName,SimStartDate,DeltaZ,TempProf,PathSave,NTracers,H,dz,z_CTD,T_CTD)
    Variable thickness and constant Tempretaure initCond4si3d(LakeName,SimStartDate,DeltaZ,TempProf,PathSave,NTracers,H,dz,Tc,spacingMethod,dz0s,dz0b,dzxs,dzxb)
    Variable thickness and variable temperature profile initCond4si3d(LakeName,SimStartDate,DeltaZ,TempProf,PathSave,NTracers,H,dz,z_CTD,T_CTD,spacingMethod,dz0s,dz0b,dzxs,dzxb)

    NOTE PLEASE keep in mind that for the use of variable temperature profile, the CTD information must cover the whole lake depth. In case the CTD profile is incomplete (z_CTD[-1] < H) then it must be rearranged prior to using this function.

3. LayerGenerator
    This function writes the layer file for the initial conditions 'si3d_layer.txt' for si3d simulations. The code is only used when the option of variable thickness of layers is toggled. This function writes the number of layers and the depth at each layer, which is needed when ibathyf < 0

4. Surfbc4si3d
    This function writes the surface boundary condition file 'surfbc.txt' for si3d simulations. The code includes 3 different methods to input forcing conditions that are coherent with si3d capabilities. 1) The heat budget is estimated among 3 different possibilities. The resulting net heat source is saved within the file along with other atmospheric conditions like wind speed, air temperature, atmospheric pressure, eta and others. 2) Using the shortwave date from site and uses cloud cover to obtain the needed parameters to run a heatbudget model built within si3d. 3) Uses the same input parameters are 2) with the difference that the longwave incoming radiation is used rather than the approximation used by using cloud cover estimations.
    The proper use of this function is shown next for each of the 3 possibilities:
    1) surfbc4si3d(LakeName,surfbcType,days,hr,mins,year,dt,PathSave,HeatBudgetMethod,eta,Hswn,Hlwin,Hlwout,Ta,Pa,RH,Cl,cw,u,v,WaTemp,Pa_P,esMethod)
    2) surfbc4si3d(LakeName,surfbcType,days,hr,mins,year,dt,PathSave,eta,Hswn,Ta,Pa,RH,Cl,cw,u,v)
    3) surfbc4si3d(LakeName,surfbcType,days,hr,mins,year,dt,PathSave,eta,Hswn,Ta,Pa,RH,Hlwin,cw,u,v)
    Where the definition of the variables is:
    u,v horizontal wind velocity components.
    Ta stands for air temperature, Pa for atmospheric pressure, RH relative humidity, eta the light penetration coefficient (secchi depth dependent), CL is cloud cover, WaTemp is the surface water temperature.
    Pa_P is the ratio of the atmospheric pressute at site in comparison to sea pressure, Hswn is the net shortwave radiation, Hlwin and HLwout stand for the incoming and outgoing longwave radiation. Finally, cw stands for wind drag coefficient.

For a better understanding on the use of these functions, the reader is directed to the corresponding repositories that make use of the functions in here. "surfBondCond.py", InitConditions.py", and ""bathymetry.py"

Copy right Sergio A. Valbuena 2021
UC Davis - TERC
February 2021
"""
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import datetime as Dt


def bathy4si3d(BasinType, SimName, dx, PathSave, *args):
    """
    Creates a bathymetry file for SI3D.
    :param BasinType: Integer corresponding to basin type 1: Lake, type 2: rectangular, or type 3: circular.
    :type BasinType: int [1-3]
    :param SimName:
    :type SimName: str
    :param dx:
    :param PathSave:
    :param args:
    :return: (x, y, z) tuple of numpy 2D meshgrids corresponding to x, y, z coordinates of bathymetry data
    """
    dxsave = ' (dx= ' + str(dx) + '),'
    Entry = SimName + dxsave
    if len(Entry) != 27:
        print(
            'ERROR! The length of the header for the bathymetry files must be 27 characters. The current number is ' + str(
                len(Entry)) + ' characters. Please change the SimName accorddingly to match the length')
        sys.exit()
    else:
        print('GOOD! The length of the header is the right length (27)')
    if BasinType == 1:
        basin = 'Lake'
        mindepth = 0
        X = args[0]
        Y = args[1]
        zg = args[2]
        zg = np.flipud(zg)
        idata = zg > mindepth
        zg[idata] = mindepth
        zz = -99 * np.ones(np.shape(zg))
        idata = ~np.isnan(zg)
        zz[idata] = zg[idata] * (-10)
        Z = zz
    elif BasinType == 2:
        basin = 'rectangular'
        L = args[0]
        B = args[1]
        H = args[2]
        x = np.arange(dx, L + dx, dx)
        y = np.arange(dx, B + dx, dx)
        X, Y = np.meshgrid(x, y)
        z = -99 * np.ones(np.shape(X))
        z[:, :] = H * (10)
        Z = z
        del x, y, z
    elif BasinType == 3:
        basin = 'circular'
        R = args[0] / 2
        H = args[1]
        x = np.arange(0, 2 * R + 2 * dx, dx)
        y = np.arange(0, 2 * R + 2 * dx, dx)
        X, Y = np.meshgrid(x, y)
        z = np.empty((len(x), len(y)))
        C = H / R
        for i in range(len(x)):
            for j in range(len(x)):
                A = R ** 2 - (x[i] - R) ** 2 - (y[j] - R) ** 2
                if A < 0:
                    z[i, j] = np.nan
                else:
                    z[i, j] = C * A ** (1 / 2)
        Z = z[0:-1, 0:-1]
        Z = Z * 10
        idata = np.isnan(Z)
        Z[idata] = -99
    else:
        H = 1

    os.chdir(PathSave)
    ny, nx = np.shape(Z)
    filename = 'h' + str(int(dx)) + 'm_' + basin
    fid = open(filename, "w+")
    fid.write("%s" % Entry + '   imx =  ' + str(nx) + ',jmx =  ' + str(ny) + ',ncols = ' + str(nx))
    fid.write("\n")
    H1 = 'HV       V'
    for i in range(1, nx):
        H1 = H1 + '   V'

    fid.write("%s\n" % H1)
    fid.write('%s' % '     ')
    for i in range(1, nx):
        fid.write("%5.0f" % (i + 1))
    fid.write("%5.0f\n" % (nx + 1))
    for i in range(1, ny + 1):
        fid.write("%5d" % (ny - i + 2))
        for item in Z[i - 1, :]:
            fid.write("%5.0f" % item)
        fid.write('\n')

    fid.close()
    print('The bathymetry file was save in ' + PathSave + ' as ' + filename)
    return X, Y, Z


def initCond4si3d(LakeName, SimStartDate, DeltaZ, TempProf, PathSave, NTracers, **kw):
    """
    Creates an initial condition file for SI3D
    :param LakeName:
    :param SimStartDate:
    :param DeltaZ:
    :param TempProf:
    :param PathSave:
    :param NTracers:
    :param kw:
    :return:
    """
    if DeltaZ == 'constant':
        if TempProf == 'constant':
            z = np.arange(0 + kw['dz'] / 2, kw['H'] + kw['dz'], kw['dz'])
            T = kw['Tc'] * np.ones(len(z))
            z *= -1
            dummy2 = 'Source: From constant values                     - '
        elif TempProf == 'variable':
            z = np.arange(0 + kw['dz'] / 2, kw['H'] + kw['dz'], kw['dz'])
            T = np.interp(z, kw['z_CTD'], kw['T_CTD'])
            z *= -1
            dummy2 = 'Source: From CTD_Profile                         - '
        dummy1 = 'Depths (m) not used   Temp (oC)                  - '
        if NTracers != 0:
            dummy1 = 'Depths (m) not used   Temp (oC)   Tracers (g/L) --> - '
    elif DeltaZ == 'variable':
        # Length of initial grid for creating the unevenly spaced grid
        N = 1000
        gridks = np.arange(1, N + 1, 1)
        if TempProf == 'constant':
            if kw['spacingMethod'] == 'exp':
                gridDZ = kw['dz0s'] * kw['dzxs'] ** gridks
                gridZ = np.cumsum(gridDZ)
                igdepth = np.where(gridZ >= kw['H'])
                km = igdepth[0][0]
                kml = km + 2
                surf = np.array([-100, -100])
                zlevel = np.concatenate((surf, gridZ[0:km + 1]))
                Layer = LayerGenerator(zlevel, kml, PathSave)
                zz = np.zeros(len(zlevel) - 1)
                zz[1:] = zlevel[2:]
                zi = -(zz[0:-1] + zz[1:]) / 2
                z = zi
            elif kw['spacingMethod'] == 'sbconc':
                gridkb = np.arange(1, N + 1, 1)
                gridDZs = kw['dz0s'] * kw['dzxs'] ** gridks
                gridZs = np.cumsum(gridDZs)
                gridDZb = kw['dz0b'] * kw['dzxb'] ** gridkb
                gridZb = np.zeros(len(gridDZb) + 1)
                gridZb[0] = kw['H']
                gridZb[1:] = kw['H'] - np.cumsum(gridDZb)
                idepths = gridZs <= kw['H'] * (1 - 1 / kw['n'])
                idepthb = gridZb >= kw['H'] * (1 - 1 / kw['n'])
                gridZbb = gridZb[idepthb]
                gridZss = gridZs[idepths]
                gridZbb = sorted(gridZbb)
                gridZ = np.concatenate((gridZss, gridZbb))
                km = len(gridZ)
                kml = km + 2
                surf = np.array([-100, -100])
                zlevel = np.concatenate((surf, gridZ))
                Layer = LayerGenerator(zlevel, kml, PathSave)
                zz = zlevel[1:]
                zz[0] = 0
                zi = -(zz[0:-1] + zz[1:]) / 2
                z = zi
            elif kw['spacingMethod'] == 'surfvarBotconsta':
                gridkb = np.arange(1, N + 1, 1)
                gridDZs = kw['dz0s'] * kw['dzxs'] ** gridks
                gridZs = np.cumsum(gridDZs)
                idepths = gridZs <= kw['Hn']
                gridZss = gridZs[idepths]
                Href = gridZss[-1]
                gridZb = np.arange(Href + kw['dzc'], kw['H'] + kw['dzc'], kw['dzc'])
                if gridZb[-1] > kw['H']:
                    gridZbb = gridZb
                    gridZbb[-1] = kw['H']
                else:
                    gridZbb = np.concatenate((gridZb, kw['H']))
                gridZ = np.concatenate((gridZss, gridZbb))
                gridZ = np.round(gridZ, 2)
                km = len(gridZ)
                kml = km + 2
                surf = np.array([-100, -100])
                zlevel = np.concatenate((surf, gridZ))
                Layer = LayerGenerator(zlevel, kml, PathSave)
                zz = zlevel[1:]
                zz[0] = 0
                zi = -(zz[0:-1] + zz[1:]) / 2
                z = zi
            T = kw['Tc'] * np.ones(len(z))
            dummy2 = 'Source: From constant values                     - '
        elif TempProf == 'variable':
            if kw['spacingMethod'] == 'exp':
                gridDZ = kw['dz0s'] * kw['dzxs'] ** gridks
                gridZ = np.cumsum(gridDZ)
                igdepth = np.where(gridZ >= kw['H'])
                km = igdepth[0][0]
                kml = km + 2
                surf = np.array([-100, -100])
                zlevel = np.concatenate((surf, gridZ[0:km + 1]))
                Layer = LayerGenerator(zlevel, kml, PathSave)
                zz = np.zeros(len(zlevel) - 1)
                zz[1:] = zlevel[2:]
                zi = -(zz[0:-1] + zz[1:]) / 2
                z = zi
            elif kw['spacingMethod'] == 'sbconc':
                gridkb = np.arange(1, N + 1, 1)
                gridDZs = kw['dz0s'] * kw['dzxs'] ** gridks
                gridZs = np.cumsum(gridDZs)
                gridDZb = kw['dz0b'] * kw['dzxb'] ** gridkb
                gridZb = np.zeros(len(gridDZb) + 1)
                gridZb[0] = kw['H']
                gridZb[1:] = kw['H'] - np.cumsum(gridDZb)
                idepths = gridZs <= kw['H'] * (1 - 1 / kw['n'])
                idepthb = gridZb >= kw['H'] * (1 - 1 / kw['n'])
                gridZbb = gridZb[idepthb]
                gridZss = gridZs[idepths]
                gridZbb = sorted(gridZbb)
                gridZ = np.concatenate((gridZss, gridZbb))
                km = len(gridZ)
                kml = km + 2
                surf = np.array([-100, -100])
                zlevel = np.concatenate((surf, gridZ))
                Layer = LayerGenerator(zlevel, kml, PathSave)
                zz = zlevel[1:]
                zz[0] = 0
                zi = -(zz[0:-1] + zz[1:]) / 2
                z = zi
            elif kw['spacingMethod'] == 'surfvarBotconsta':
                gridkb = np.arange(1, N + 1, 1)
                gridDZs = kw['dz0s'] * kw['dzxs'] ** gridks
                gridZs = np.cumsum(gridDZs)
                gridDZb = kw['dz0b'] * kw['dzxb'] ** gridkb
                gridZb = np.zeros(len(gridDZb) + 1)
                gridZb[0] = kw['H']
                gridZb[1:] = kw['H'] - np.cumsum(gridDZb)
                idepths = gridZs <= kw['Hn']
                gridZss = gridZs[idepths]
                Href = gridZss[-1]
                gridZb = np.arange(Href + kw['dzc'], kw['H'] + kw['dzc'], kw['dzc'])
                if gridZb[-1] > kw['H']:
                    gridZbb = gridZb
                    gridZbb[-1] = kw['H']
                else:
                    gridZbb = np.concatenate((gridZb, kw['H']))
                gridZ = np.concatenate((gridZss, gridZbb))
                gridZ = np.round(gridZ, 2)
                km = len(gridZ)
                kml = km + 2
                surf = np.array([-100, -100])
                zlevel = np.concatenate((surf, gridZ))
                Layer = LayerGenerator(zlevel, kml, PathSave)
                zz = zlevel[1:]
                zz[0] = 0
                zi = -(zz[0:-1] + zz[1:]) / 2
                z = zi
            z *= -1
            T = np.interp(z, kw['z_CTD'], kw['T_CTD'])
            z *= -1
            dummy2 = 'Source: From CTD_Profile                         - '
        dummy1 = 'Depths (m)   Temp (oC)                           - '

    if NTracers != 0:
        dummy1 = 'Depths (m)   Temp (oC)   Tracers (g/L) -->       - '

    # ----------------------- Creation of file ---------------------------------
    os.chdir(PathSave)
    fid = open('si3d_init.txt', 'w+')
    fid.write('%s\n' % 'Initial condition file for si3d model            - ')
    fid.write('%s' % LakeName + '             - ' + '\n')
    fid.write('%s' % 'Simulation starting on ' + SimStartDate + ' UTC    - ' + '\n')
    fid.write('%s\n' % dummy1)
    fid.write('%s\n' % dummy2)
    fid.write('%s\n' % '-------------------------------------------------- ')

    if NTracers == 0:
        fid.write('%10.2f %10.4f \n' % (z[0], T[0]))
        for i in range(0, len(T)):
            fid.write('%10.2f %10.4f \n' % (z[i], T[i]))
        fid.write('%10.2f %10.4f \n' % (z[i], T[i]))
    else:
        _, cols1 = kw['z_Tr'].shape
        _, cols2 = kw['conc_Tr'].shape
        if cols1 != NTracers or cols2 != NTracers or cols1 != cols2:
            print('¡¡¡ERROR!!! The number of tracers ', str(NTracers),
                  ' does not match number of columns in the variables for the depths ', str(cols1),
                  ' and concentrations of the tracers ', str(cols2))
            exit()
        tracers = np.empty((len(z), NTracers)) * np.nan
        for i in range(0, NTracers):
            tracers[:, i] = np.interp(-z, kw['z_Tr'][:, i], kw['conc_Tr'][:, i])
        fid.write('%10.2f %10.4f' % (z[0], T[0]))
        for j in range(0, NTracers):
            fid.write('%11.4f' % tracers[0, j])
        fid.write('\n')
        for i in range(0, len(T)):
            fid.write('%10.2f %10.4f' % (z[i], T[i]))
            for j in range(0, NTracers):
                fid.write('%11.4f' % tracers[i, j])
            fid.write('\n')
        fid.write('%10.2f %10.4f' % (z[i], T[i]))
        for j in range(0, NTracers):
            fid.write('%11.4f' % tracers[i, j])
        fid.write('\n')

    fid.close()
    return T, z

def LayerGenerator(zlevel, kml, PathSave):
    """
    This function is only used when the layer thickness is variable
    :param zlevel:
    :param kml:
    :param PathSave:
    :return:
    """
    os.chdir(PathSave)
    fid = open('si3d_layer.txt', 'wt+')
    fid.write('%s\n' % 'Depths to top of layers in Si3D Grid            ')
    fid.write('%s\n' % '** used if ibathyf in si3d_inp.txt is set to < 0       ')
    fid.write('%s\n' % '------------------------------------------------------ ')
    fid.write('%s' % '   km1   =        ' + str(kml) + '\n')
    for i in range(0, kml):
        fid.write('%10.2f %10.4f \n' % (i + 1, zlevel[i]))

    fid.close()
    Layer = 'Layer file created in the folder' + PathSave + ' with name si3d_layer.txt'
    print(Layer)
    return Layer


def surfbcW4si3d(caseStudy, Time, dt, PathSave, cw, u, v):
    """

    :param caseStudy:
    :param Time:
    :param dt:
    :param PathSave:
    :param cw:
    :param u:
    :param v:
    :return:
    """
    os.chdir(PathSave)
    r = len(Time)
    days = Time / 24
    daystart = Time[0]

    fid = open('surfbcW.txt', 'wt+')
    fid.write('%s\n' % 'Surface boundary condition file for si3d model')
    fid.write('%s' % caseStudy + ' simulations \n')
    fid.write('%s' % 'Time is given in hours from the start date used within the input.txt \n')
    fid.write('%s\n' % '   Time in   // Data format is (10X,G11.2,...) Time cw ua va')
    fid.write('%s' % '   ' + str(dt) + '-min    // SOURCE = ' + caseStudy + ' Met Data \n')
    fid.write('%s' % ' intervals  (Note : file prepared on ' + str(Dt.date.today()) + '\n')
    fid.write('%s' % '   npts = ' + str(r) + '\n')
    for i in range(0, r):
        a0 = (days[i] - daystart) * 24
        a1 = cw[i];  # **** Wind drag coefficient
        a2 = u[i];  # **** Wind speed in the EW direction
        a3 = v[i];  # **** Wind speed in the NS direction
        format = '%10.4f %10.4f %10.4f %10.4f \n'
        fid.write(format % (a0, a1, a2, a3))
    return


def surfbc4si3d(show, LakeName, surfbcType, days, hr, mins, year, dt, PathSave, *args):
    """
    Function to create surface boundary condition using a heat budget method.
    This function preprocess the meteorological parameters and creater a surfbc.txt file
    for SI3D. The file has the inputs for the heatbudget method chosen.
    :param show:
    :param LakeName:
    :param surfbcType:
    :param days:
    :param hr:
    :param mins:
    :param year:
    :param dt:
    :param PathSave:
    :param args:
    :return:
    """
    os.chdir(PathSave)
    r = len(days)
    daystart = days[0]
    # To write the file surfbc for the numerical simulation in si3d
    fid = open('surfbc.txt', 'wt+')
    fid.write('%s\n' % 'Surface boundary condition file for si3d model')
    fid.write('%s' % LakeName + ' simulations \n')
    fid.write('%s' % 'Time is given in hours from ' + str(hr[0]) + ':' + str(mins[0]) + ' hrs on julian day ' + str(
        days[0]) + ',' + str(year) + '\n')

    if surfbcType == 'Preprocess':
        fid.write('%s\n' % '   Time in   // Data format is (10X,G11.2,...) Time attc Hsw Hn cw ua va')
        fid.write('%s' % '   ' + str(dt) + '-min    // SOURCE = ' + LakeName + ' Met Data ' + str(year) + '\n')
        fid.write('%s' % ' intervals  (Note : file prepared on ' + str(
            Dt.date.today()) + 'HeatBudget = ' + HeatBudgetMethod + '\n')
        fid.write('%s' % '   npts = ' + str(r) + '\n')
        HeatBudgetMethod = args[0]
        eta = args[1]
        Hswn = args[2]
        Hlwin = args[3]
        Hlwout = args[4]
        Ta = args[5]
        Pa = args[6]
        RH = args[7] / 100
        Cl = args[8]
        cw = args[9]
        u = args[10]
        v = args[11]
        WaTemp = args[12]
        TimeSim = args[13]

        if HeatBudgetMethod == 'Chapra1995':
            rho0 = 1000
            Lw = 2.6e-6
            cChapra = args[13]
            CbPa_P = 0.61 * cChapra
            esMethod = args[14]
            # Vapor Pressure
            if esMethod == 1:
                es = 6.11 * np.exp(17.3 * Ta / (Ta + 237.3))
            elif esMethod == 2:
                es = 6.11 * np.exp(7.5 * Ta / (Ta + 237.3))
            elif esMethod == 3:
                es3 = 10 ** (9.286 - (2322.38 / (Ta + 273.15)))
            ea = es * RH
            # Longwave radiation
            Hlwn = Hlwin - Hlwout
            # Latent Heat Flux (Negative as it exits)
            fwind = 1.02e-9 * (u ** 2 + v ** 2) ** 0.5
            Hl = -rho0 * Lw * fwind * (es - ea)
            # Sensible heat flux (negative due to consideration of difference between water temp and air temp)
            Hs = -rho0 * Lw * fwind * CbPa_P * (WaTemp - Ta)
            # Net Heat Flux
            Hn = Hswn + Hlwn + Hs + Hl
        elif HeatBudgetMethod == 'AirSea':
            print('UNDER DEVELOPMENT, THIS FUNCTION DOES NOT WORK')
            print('The file has not been created')
            exit()
        elif HeatBudgetMethod == 'TERC':
            print('UNDER DEVELOPMENT, THIS FUNCTION DOES NOT WORK')
            print('The file has not been created')
            exit()
        for i in range(0, r):
            a0 = (days[i] - daystart) * 24
            a1 = eta[i]
            a2 = Hswn[i]
            a3 = Hn[i]
            a4 = cw[j]
            a5 = u[i]
            a6 = v[i]
            format = '%10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f \n'
            fid.write(format % (a0, a1, a2, a3, a4, a5, a6))
    elif surfbcType == 'RunTime1':
        fid.write('%s\n' % '   Time in   // Data format is (10X,G11.2,...) Time attc Hsw Ta Pa hr cc cw ua va')
        fid.write('%s' % '   ' + str(dt) + '-min    // SOURCE = ' + LakeName + ' Met Data ' + str(year) + '\n')
        fid.write('%s' % ' intervals  (Note : file prepared on ' + str(Dt.date.today()) + '\n')
        fid.write('%s' % '   npts = ' + str(r) + '\n')
        eta = args[0]
        Hswn = args[1]
        Ta = args[2]
        Pa = args[3]
        RH = args[4] / 100
        Cl = args[5]
        cw = args[6]
        u = args[7]
        v = args[8]
        TimeSim = args[9]
        for i in range(0, r):
            a0 = (days[i] - daystart) * 24
            a1 = eta[i]  # light attenuation coefficient
            a2 = Hswn[i];  # Penetrative component of heat flux (albedo already taken into account)
            a3 = Ta[i];  # Air temperature
            a4 = Pa[i];  # Atmospheric pressure
            a5 = RH[i];  # relative humidty (fraction)
            a6 = Cl[i];  # cloud cover (fraction)
            a7 = cw[i];  # **** Wind drag coefficient
            a8 = u[i];  # **** Wind speed in the EW direction
            a9 = v[i];  # **** Wind speed in the NS direction
            if a4 >= 100000:
                format = '%10.4f %10.4f %10.4f %10.4f %10.3f %10.4f %10.4f %10.4f %10.4f %10.4f \n'
            else:
                format = '%10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f \n'
            fid.write(format % (a0, a1, a2, a3, a4, a5, a6, a7, a8, a9))
        fig1, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4, ncols=1)
        fig2, (ax5, ax6, ax7, ax8) = plt.subplots(nrows=4, ncols=1)
        fig1.set_size_inches(6, 8)
        fig2.set_size_inches(6, 8)
        ax1.plot(TimeSim, eta)
        ax2.plot(TimeSim, Hswn)
        ax3.plot(TimeSim, Cl)
        ax4.plot(TimeSim, (u ** 2 + v ** 2) ** 0.5)
        ax5.plot(TimeSim, Ta)
        ax6.plot(TimeSim, Pa)
        ax7.plot(TimeSim, RH)
        ax8.plot(TimeSim, cw)

        ax1.set_ylabel(r'$eta$')
        plt.tight_layout()
        ax2.set_ylabel(r'$Hswn\ [Wm^{-2}]$')
        ax3.set_ylabel(r'$Cloud Cover$')
        ax4.set_ylabel(r'$Wspd\ [ms^{-1}]$')
        ax5.set_ylabel(r'$Ta\ [^{\circ}C]$')
        ax6.set_ylabel(r'$Atm\ P\ [Pa]$')
        ax7.set_ylabel(r'$RH$')
        ax8.set_ylabel(r'$Wind\ Drag$')
        ax8.set_xlabel('day of year')
        plt.tight_layout()
        if show:
            plt.show()
        else:
            print('No plot')
    elif surfbcType == 'RunTime2':
        fid.write('%s\n' % '   Time in   // Data format is (10X,G11.2,...) Time attc Hsw Ta Pa hr Hlw cw ua va')
        fid.write('%s' % '   ' + str(dt) + '-min    // SOURCE = ' + LakeName + ' Met Data ' + str(year) + '\n')
        fid.write('%s' % ' intervals  (Note : file prepared on ' + str(Dt.date.today()) + '\n')
        fid.write('%s' % '   npts = ' + str(r) + '\n')
        eta = args[0]
        Hswn = args[1]
        Ta = args[2]
        Pa = args[3]
        RH = args[4] / 100
        Hlwin = args[5]
        cw = args[6]
        u = args[7]
        v = args[8]
        TimeSim = args[9]
        for i in range(0, r):
            a0 = (days[i] - daystart) * 24
            a1 = eta[i]  # light attenuation coefficient
            a2 = Hswn[i]  # Penetrative component of heat flux (albedo already taken into account)
            a3 = Ta[i]  # Air temperature
            a4 = Pa[i]  # Atmospheric pressure
            a5 = RH[i]  # relative humidty (fraction)
            a6 = Hlwin[i]  # Longwave radiation in
            a7 = cw[i]  # **** Wind drag coefficient
            a8 = u[i]  # **** Wind speed in the EW direction
            a9 = v[i]  # **** Wind speed in the NS direction
            if a4 >= 100000:
                format = '%10.4f %10.4f %10.4f %10.4f %10.3f %10.4f %10.4f %10.4f %10.4f %10.4f \n'
            else:
                format = '%10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f \n'
            fid.write(format % (a0, a1, a2, a3, a4, a5, a6, a7, a8, a9))

        fig1, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4, ncols=1)
        fig2, (ax5, ax6, ax7, ax8) = plt.subplots(nrows=4, ncols=1)
        fig1.set_size_inches(6, 8)
        fig2.set_size_inches(6, 8)
        ax1.plot(TimeSim, eta)
        ax2.plot(TimeSim, Hswn)
        ax3.plot(TimeSim, Hlwin)
        ax4.plot(TimeSim, (u ** 2 + v ** 2) ** 0.5)
        ax5.plot(TimeSim, Ta)
        ax6.plot(TimeSim, Pa)
        ax7.plot(TimeSim, RH)
        ax8.plot(TimeSim, cw)

        ax1.set_ylabel(r'$eta$')
        plt.tight_layout()
        ax2.set_ylabel(r'$Hswn\ [Wm^{-2}]$')
        ax3.set_ylabel(r'$Hlwin\ [Wm^{-2}]$')
        ax4.set_ylabel(r'$Wspd\ [ms^{-1}]$')
        ax5.set_ylabel(r'$Ta\ [^{\circ}C]$')
        ax6.set_ylabel(r'$Atm\ P\ [Pa]$')
        ax7.set_ylabel(r'$RH$')
        ax8.set_ylabel(r'$Wind\ Drag$')
        ax8.set_xlabel('day of year')
        plt.tight_layout()
        if show:
            plt.show()
        else:
            print('No plot')

    fid.close()


def HeatBudget(HeatBudgetMethod, eta, Hswn, Hlwin, Hlwout, Ta, Pa, RH, Cl, cw, u, v, WaTemp, cChapra, esMethod):
    if HeatBudgetMethod == 'Chapra1995':
        rho0 = 997
        Lv = 2.5e6
        CbPa_P = 0.61 * cChapra
        wspd = (u ** 2 + v ** 2) ** 0.5
        # Vapor Pressure
        if esMethod == 1:
            es = 6.11 * np.exp(17.3 * Ta / (Ta + 237.3))
            esw = 6.11 * np.exp(17.3 * WaTemp / (WaTemp + 237.3))
        elif esMethod == 2:
            es = 6.11 * np.exp(7.5 * Ta / (Ta + 237.3))
            esw = 6.11 * np.exp(7.5 * WaTemp / (WaTemp + 237.3))
        elif esMethod == 3:
            es = 10 ** (9.286 - (2322.38 / (Ta + 273.15)))
            esw = 10 ** (9.286 - (2322.38 / (WaTemp + 273.15)))
        ea = es * RH
        # Longwave radiation
        Hlwn = Hlwin - Hlwout
        # Latent Heat Flux (Negative as it exits)
        fwind = 1.02e-9 * wspd
        Hl = -rho0 * Lv * fwind * (esw - ea)
        # Sensible heat flux (negative due to consideration of difference between water temp and air temp)
        Hs = -rho0 * Lv * fwind * CbPa_P * (WaTemp - Ta)
        # Net Heat Flux
        Hn = Hswn + Hlwn + Hs + Hl
    elif HeatBudgetMethod == 'AirSea':
        print('UNDER DEVELOPMENT, THIS FUNCTION DOES NOT WORK')
        print('The file has not been created')
        exit()
    elif HeatBudgetMethod == 'TERC':
        print('UNDER DEVELOPMENT, THIS FUNCTION DOES NOT WORK')
        print('The file has not been created')
        exit()
    return Hswn, Hlwn, Hl, Hs, Hn
