"""
Material Balance Plots
@author: Yohanes Nuwara
@email: ign.nuwara97@gmail.com
"""

import numpy as np
import matplotlib.pyplot as plt

def Efw(cf, cw, swi, p, pi):
    """
    Calculate formation expansion factor
    """
    Efw = ((cf + cw * swi) / (1 - swi)) * (pi - p)
    return (Efw)


def condensate_belowdew(Rs, Rv, Rsi, Rvi, Bo, Bg, Bgi, Np, Gp):
    """
    Calculate the parameters for material balance plot of gas-condensate reservoirs
    below dewpoint pressure

    Input:

    array: Rs, Rv, Bo, Bg, Np, Gp
    float: initial Rs (Rsi), initial Rv (Rvi), initial Bg (Bgi)

    Output: F (array), Eg (array)
    """
    Btg = ((Bg * (1 - (Rs * Rvi))) + (Bo * (Rvi - Rv))) / (1 - (Rv * Rs))  # in RB/STB
    Bto = ((Bo * (1 - (Rv * Rsi))) + (Bg * (Rsi - Rs))) / (1 - (Rv * Rs))  # in RB/scf

    Gi = 0
    F = (Np * ((Bo - (Rs * Bg)) / (1 - (Rv * Rs)))) + ((Gp - Gi) * ((Bg - (Rv * Bo)) / (1 - (Rv * Rs))))
    Eg = Btg - Bgi
    return (F, Eg)


def condensate_abovedew(Bg, Bgi, Gp, Gpi):
    """
    Calculate the parameters for material balance plot of gas-condensate reservoirs
    above dewpoint pressure

    Input:

    array: Bg, Gp
    float: initial Bg, initial Gp

    Output: F (array), Eg (array)
    """
    Eg = Bg - Bgi
    F = Bg * (Gp - Gpi)
    return (F, Eg)

def calculate_undersaturated(p, Bg, Bo, Np, Gp, cf, cw, swi, Rs, Rv, oilfvf=None):
    """
    Calculate Material Balance Parameter of Undersaturated (Volatile and Non-Volatile) Reservoirs

    INPUT: oilfvf = None, 'total' (read NOTE below)

    OUTPUT: Bto, Eo, Efw, F

    NOTE:

    One way to classify first what type of your reservoir is, look at the Rv value
    If you have the data which Rv contains all zeros, means you have a non-volatile
    If Rv not zero, means you have a volatile reservoir

    This program normally runs with all the input data specified. If some of the input data is incomplete,
    for instance Rv and Bo, read this information:

    1.
    If you don't have Bo data, but total oil FVF (Bto) data, specify oilfvf = 'total'

    2.
    In case you are having non-volatile reservoir, if you don't have Rv data, program can still run.

    3.
    In case you are having volatile reservoir, make sure you have Rv data, or the program can't run.
    """
    # initial conditions
    pi = p[0]
    Boi = Bo[0]
    Rsi = Rs[0]

    if oilfvf == 'total':
        Bto = []
        F = []

        for i in range(len(p)):

            if Rv[i] == 0:
                # reservoir is non-volatile undersaturated
                Bto_ = Bo[i]
                F_ = Np[i](Bto_ - Rsi * Bg[i]) + (Gp[i] * Bg[i])

            Bto.append(Bto_)
            F.append(F_)

            if Rv[i] != 0:
                # reservoir is volatile undersaturated
                Bto_ = Bo[i]
                Bo_ = ((Bto_ * (1 - Rv[i] * Rs[i])) - (Bg[i] * (Rsi - Rs[i]))) / (1 - Rv[i] * Rs[i])
                F_ = (Np * ((Bo_ - (Rs * Bg)) / (1 - (Rv * Rs)))) + (Gp * ((Bg - (Rv * Bo_)) / (1 - (Rv * Rs))))

            Bto.append(Bto_)
            F.append(F_)

        Bto = np.array(Bto)
        F = np.array(F)

    if oilfvf == None:
        Bto = []
        F = []

        for i in range(len(p)):

            if Rv[i] == 0:
                # reservoir is non-volatile undersaturated
                Bto_ = Bo[i] + Bg[i] * (Rsi - Rs[i])
                F_ = Np[i](Bo[i] - Rs[i] * Bg[i]) + (Gp[i] * Bg[i])
            Bto.append(Bto_)
            F.append(F_)

            if Rv[i] != 0:
                # reservoir is volatile undersaturated
                Bto_ = ((Bo[i] * (1 - (Rv[i] * Rsi))) + (Bg[i] * (Rsi - Rs[i]))) / (1 - (Rv[i] * Rs[i]))
                F_ = (Np * ((Bo - (Rs * Bg)) / (1 - (Rv * Rs)))) + (Gp * ((Bg - (Rv * Bo)) / (1 - (Rv * Rs))))
            Bto.append(Bto_)
            F.append(F_)

    Bto = np.array(Bto)
    F = np.array(F)

    # calculate Eo+(Boi*Efw)
    Efw = ((cf + (cw * swi)) / (1 - swi)) * (pi - p)
    Eo = Bto - Boi

    return(Bto, Eo, Efw, F)


class condensate():
    """
    Gas Condensate Material Balance Plot
    """

    def plot1(self, Pdp, p, Bg, Bgi, Bo, Np, Gp, Gpi, Rv, Rvi, Rs, Rsi=None):
        """
        Plot 1: F vs Eg

        Input:
        array: p, Bg, Bo, Np, Gp, Rv, Rs
        float: Pdp (dewpoint-pressure), Bgi (initial Bg), Gpi (initial Gp), Rvi (initial Rv), Rsi (initial Rs)

        Specify None to Rsi, if Rs data contains NaN values (no data)
        NaN values populates in the pressure above dewpoint (Pi > Pdp), because there is no liquid in the single-phase gas

        Output:
        array: Eg (x-axis values), F (y-axis values), and plot
        """

        # for above dewpoint pressure
        id_above = np.where(p > Pdp)[0]

        Bg_above = [];
        Gp_above = []

        for i in id_above:
            Bg_above_ = Bg[i]
            Gp_above_ = Gp[i]
            Bg_above.append(Bg_above_);
            Gp_above.append(Gp_above_)

        F_above, Eg_above = condensate_abovedew(np.array(Bg_above), Bgi, np.array(Gp_above), Gpi)

        # for below dewpoint pressure
        id_below = np.where(p <= Pdp)[0]
        if Rsi == None:
            Rsi = 1 / Rvi
        else:
            Rsi = Rsi

        Rs_below = [];
        Rv_below = [];
        Bo_below = [];
        Bg_below = []
        Np_below = [];
        Gp_below = []

        for i in id_below:
            Rs_below_ = Rs[i]
            Rv_below_ = Rv[i]
            Bo_below_ = Bo[i]
            Bg_below_ = Bg[i]
            Np_below_ = Np[i]
            Gp_below_ = Gp[i]

            Rs_below.append(Rs_below_);
            Rv_below.append(Rv_below_);
            Bo_below.append(Bo_below_)
            Bg_below.append(Bg_below_);
            Np_below.append(Np_below_);
            Gp_below.append(Gp_below_)

        F_below, Eg_below = condensate_belowdew(np.array(Rs_below), np.array(Rv_below),
                                                Rsi, Rvi, np.array(Bo_below), np.array(Bg_below),
                                                Bgi, np.array(Np_below), np.array(Gp_below))

        # append F and Eg of the below- and above-dewpoint pressure
        F = np.append(F_above, F_below)
        Eg = np.append(Eg_above, Eg_below)

        # plot
        plt.plot(Eg, F, '.')
        plt.title('Plot 1: F vs Eg')
        plt.xlabel('Eg (RB/scf)');
        plt.ylabel('F (res bbl)')
        plt.xlim(xmin=0);
        plt.ylim(ymin=0)
        plt.show()

        return (F, Eg)

    def plot2(self, Gp, p, z):
        """
        Plot 2: p/z vs Gp

        Input:
        array: Gp, p, z

        Output:
        array: Gp (x-axis values), p_z (y-axis values), plot
        """
        # calculate plotting parameters
        p_z = p / z
        Gp = Gp

        # plotting
        plt.plot(Gp, p_z, '.')
        plt.title('Plot 2: p/z vs Gp')
        plt.xlabel('Gp (scf)');
        plt.ylabel('p/z (psia)')
        plt.xlim(xmin=0);
        plt.ylim(ymin=0)
        plt.show()
        return (Gp, p_z)

    def plot3(self, Pdp, p, Bg, Bgi, Bo, Np, Gp, Gpi, Rv, Rvi, Rs, Rsi=None):
        """
        Plot 1: F/Eg vs Gp

        Input:
        array: p, Bg, Bo, Np, Gp, Rv, Rs
        float: Pdp (dewpoint-pressure), Bgi (initial Bg), Gpi (initial Gp), Rvi (initial Rv), Rsi (initial Rs)

        Specify None to Rsi, if Rs data contains NaN values (no data)
        NaN values populates in the pressure above dewpoint (Pi > Pdp), because there is no liquid in the single-phase gas

        Output:
        array: Gp (x-axis values), F_Eg (y-axis values), and plot
        """
        # for above dewpoint pressure
        id_above = np.where(p > Pdp)[0]

        Bg_above = [];
        Gp_above = []

        for i in id_above:
            Bg_above_ = Bg[i]
            Gp_above_ = Gp[i]
            Bg_above.append(Bg_above_);
            Gp_above.append(Gp_above_)

        F_above, Eg_above = condensate_abovedew(np.array(Bg_above), Bgi, np.array(Gp_above), Gpi)

        # for below dewpoint pressure
        id_below = np.where(p <= Pdp)[0]
        if Rsi == None:
            Rsi = 1 / Rvi
        else:
            Rsi = Rsi

        Rs_below = [];
        Rv_below = [];
        Bo_below = [];
        Bg_below = []
        Np_below = [];
        Gp_below = []

        for i in id_below:
            Rs_below_ = Rs[i]
            Rv_below_ = Rv[i]
            Bo_below_ = Bo[i]
            Bg_below_ = Bg[i]
            Np_below_ = Np[i]
            Gp_below_ = Gp[i]

            Rs_below.append(Rs_below_);
            Rv_below.append(Rv_below_);
            Bo_below.append(Bo_below_)
            Bg_below.append(Bg_below_);
            Np_below.append(Np_below_);
            Gp_below.append(Gp_below_)

        F_below, Eg_below = condensate_belowdew(np.array(Rs_below), np.array(Rv_below),
                                                Rsi, Rvi, np.array(Bo_below), np.array(Bg_below),
                                                Bgi, np.array(Np_below), np.array(Gp_below))

        # append F and Eg of the below- and above-dewpoint pressure
        F = np.append(F_above, F_below)
        Eg = np.append(Eg_above, Eg_below)

        # calculate parameters for plotting
        F_Eg = F / Eg

        plt.plot(Gp, F_Eg)
        plt.show()
        return (Gp, F_Eg)

    def plot6(self, Pdp, p, pi, Bg, Bgi, Bo, Np, Gp, Gpi, cf, cw, swi, Rv, Rvi, Rs, Rsi=None):
        """
        Plot 6: F vs (Eg+Bgi*Efw)

        Input:
        array: p, Bg, Bo, Np, Gp, Rv, Rs
        float: Pdp (dewpoint-pressure), Bgi (initial Bg), Gpi (initial Gp), Rvi (initial Rv), Rsi (initial Rs), pi (initial p), swi (initial sw), cf, cw

        Specify None to Rsi, if Rs data contains NaN values (no data)
        NaN values populates in the pressure above dewpoint (Pi > Pdp), because there is no liquid in the single-phase gas

        Output:
        array: Eg_Bgi_Efw (x-axis values), F (y-axis values), and plot
        """
        # for above dewpoint pressure
        id_above = np.where(p > Pdp)[0]

        Bg_above = [];
        Gp_above = []

        for i in id_above:
            Bg_above_ = Bg[i]
            Gp_above_ = Gp[i]
            Bg_above.append(Bg_above_);
            Gp_above.append(Gp_above_)

        F_above, Eg_above = condensate_abovedew(np.array(Bg_above), Bgi, np.array(Gp_above), Gpi)

        # for below dewpoint pressure
        id_below = np.where(p <= Pdp)[0]
        if Rsi == None:
            Rsi = 1 / Rvi
        else:
            Rsi = Rsi

        Rs_below = [];
        Rv_below = [];
        Bo_below = [];
        Bg_below = []
        Np_below = [];
        Gp_below = []

        for i in id_below:
            Rs_below_ = Rs[i]
            Rv_below_ = Rv[i]
            Bo_below_ = Bo[i]
            Bg_below_ = Bg[i]
            Np_below_ = Np[i]
            Gp_below_ = Gp[i]

            Rs_below.append(Rs_below_);
            Rv_below.append(Rv_below_);
            Bo_below.append(Bo_below_)
            Bg_below.append(Bg_below_);
            Np_below.append(Np_below_);
            Gp_below.append(Gp_below_)

        F_below, Eg_below = condensate_belowdew(np.array(Rs_below), np.array(Rv_below),
                                                Rsi, Rvi, np.array(Bo_below), np.array(Bg_below),
                                                Bgi, np.array(Np_below), np.array(Gp_below))

        # append F and Eg of the below- and above-dewpoint pressure
        F = np.append(F_above, F_below)
        Eg = np.append(Eg_above, Eg_below)

        # calculate parameters for plotting
        Efw = Efw(cf, cw, swi, p, pi)
        Eg_Bgi_Efw = Eg + Bgi * Efw

        # plotting
        plt.plot(Eg_Bgi_Efw, F)
        plt.show()
        return (Eg_Bgi_Efw, F)

    def plot7(self, Gp, p, pi, z, cf, cw, swi):
        """
        Plot 7 (p/z*(1-Efw)) vs Gp

        Input:
        array: Gp, p, z
        float: pi (initial p), swi (initial sw), cf, cw

        Output:
        array: Gp (x-axis values), p_z_Efw (y-axis values), plot
        """
        # calculate plotting parameters
        Efw = Efw(cf, cw, swi, p, pi)
        p_z_Efw = (p / z) * Efw

        # plotting
        plt.plot(Gp, p_z_Efw)
        plt.show()
        return (Gp, p_z_Efw)


class drygas():
    """
    Dry Gas Material Balance Plot
    """

    def plot1(self, Bg, Bgi, Gp, Gpi):
        """
        Plot 1: F vs Eg

        Input:

        array: Bg, Gp
        float: initial Bg, initial Gp

        Output:
        array: Eg (x-axis values), F (y-axis values), and plot
        """
        Eg = Bg - Bgi
        F = Bg * (Gp - Gpi)

        # plotting
        plt.plot(Eg, F, '.')
        plt.title('Plot 1: F vs Eg')
        plt.xlabel('Eg (RB/scf)');
        plt.ylabel('F (res bbl)')
        plt.xlim(xmin=0);
        plt.ylim(ymin=0)
        plt.show()

    def plot2(self, Gp, p, z):
        """
        Plot 2: p/z vs Gp

        Input:
        array: Gp, p, z

        Output:
        array: Gp (x-axis values), p_z (y-axis values), plot
        """
        # calculate plotting parameters
        p_z = p / z
        Gp = Gp

        # plotting
        plt.plot(Gp, p_z, '.')
        plt.title('Plot 2: p/z vs Gp')
        plt.xlabel('Gp (scf)');
        plt.ylabel('p/z (psia)')
        plt.xlim(xmin=0);
        plt.ylim(ymin=0)
        plt.show()
        return (Gp, p_z)

    def plot3(self, Bg, Bgi, Gp, Gpi):
        """
        Plot 3: F/Eg vs Gp

        Input:

        array: Bg, Gp
        float: initial Bg, initial Gp

        Output:
        array: Gp (x-axis values), F_Eg (y-axis values), and plot
        """

        Eg = Bg - Bgi
        F = Bg * (Gp - Gpi)
        F_Eg = F / Eg

        plt.plot(Gp, F_Eg)
        plt.show()
        return (Gp, F_Eg)

    def plot6(self, Bg, Bgi, Gp, Gpi, p, pi, cf, cw, swi):

        """
        Plot 6: F vs (Eg+Bgi*Efw)

        Input:
        array: Bg, Gp, p
        float: Bgi (initial Bg), Gpi (initial Gp), pi (initial p), swi (initial sw), cf, cw

        Output:
        array: Eg_Bgi_Efw (x-axis values), F (y-axis values), and plot
        """

        Eg = Bg - Bgi
        F = Bg * (Gp - Gpi)

        # calculate parameters for plotting
        Efw = Efw(cf, cw, swi, p, pi)
        Eg_Bgi_Efw = Eg + Bgi * Efw

        plt.plot(Eg_Bgi_Efw, F)
        plt.show()
        return (Eg_Bgi_Efw, F)

    def plot7(self, Gp, p, pi, z, cf, cw, swi):
        """
        Plot 7 (p/z*(1-Efw)) vs Gp

        Input:
        array: Gp, p, z
        float: pi (initial p), swi (initial sw), cf, cw

        Output:
        array: Gp (x-axis values), p_z_Efw (y-axis values), plot
        """
        # calculate plotting parameters
        Efw = Efw(cf, cw, swi, p, pi)
        p_z_Efw = (p / z) * Efw

        # plotting
        plt.plot(Gp, p_z_Efw)
        plt.show()
        return (Gp, p_z_Efw)

class undersaturated():
    """
    Undersaturated Oil Reservoir Material Balance Plot
    """
    def plot1(self, p, Bg, Bo, Np, Gp, cf, cw, swi, Rs, Rv):
        """
        Plot 1: F vs Eo+(Bti* Efw)

        Rv is the most important parameter that determines a volatile or non-volatile reservoir
        If you have the data which Rv contains all zeros, means you have a non-volatile
        If Rv not zero, means you have a volatile
        """
        # initial conditions
        pi = p[0]
        Boi = Bo[0]
        Rsi = Rs[0]
        
        # calculate total oil FVF (Bto)
        Bto = ((Bo * (1 - (Rv * Rsi))) + (Bg * (Rsi - Rs))) / (1 - (Rv * Rs))

        # calculate Eo+(Boi*Efw)
        Efw = ((cf + (cw * swi)) / (1 - swi)) * (pi - p)
        Eo = Bto - Boi
        Eo_Bti_Efw = Eo + Boi * Efw

        # calculate reservoir voidage
        F = (Np * ((Bo - (Rs * Bg)) / (1 - (Rv * Rs)))) + (Gp * ((Bg - (Rv * Bo)) / (1 - (Rv * Rs))))

        # plot
        plt.plot(Eo_Bti_Efw, F, '.')
        plt.title('Plot 1: F vs Eo+(Bti* Efw)')
        plt.xlim(xmin=0); plt.ylim(ymin=0)
        plt.xlabel('Eo+(Bti*Efw) (RB/STB)')
        plt.ylabel('F (res bbl)')
        plt.show()

        return(Eo_Bti_Efw, F)

    def plot2(self, p, Bg, Bo, Np, Gp, cf, cw, swi, Rs, Rv):
        """
        Plot 2: F/Eo+(Bti* Efw) vs Np (Waterdrive Diagnostic Plot)

        Rv is the most important parameter that determines a volatile or non-volatile reservoir
        If you have the data which Rv contains all zeros, means you have a non-volatile
        If Rv not zero, means you have a volatile
        """
        # initial conditions
        pi = p[0]
        Boi = Bo[0]
        Rsi = Rs[0]
        
        # calculate total oil FVF (Bto)
        Bto = ((Bo * (1 - (Rv * Rsi))) + (Bg * (Rsi - Rs))) / (1 - (Rv * Rs))

        # calculate Eo+(Boi*Efw)
        Efw = ((cf + (cw * swi)) / (1 - swi)) * (pi - p)
        Eo = Bto - Boi
        Eo_Bti_Efw = Eo + Boi * Efw

        # calculate reservoir voidage
        F = (Np * ((Bo - (Rs * Bg)) / (1 - (Rv * Rs)))) + (Gp * ((Bg - (Rv * Bo)) / (1 - (Rv * Rs))))

        # calculate parameters
        N = F / Eo_Bti_Efw

        plt.plot(Np, N, '.')
        plt.title('Plot 2: F/(Eo+(Bti* Efw)) vs Np')
        plt.xlim(xmin=0); plt.ylim(ymin=0)
        plt.xlabel('Np (STB)');
        plt.ylabel('N (STB)')
        plt.show()

        return(Np, N)

class undersaturated():
    """
    Undersaturated Oil Reservoir Material Balance Plots

    OUTPUT: Matplotlib plot and array for each of the axes
    """
    def plot1(self, p, Bg, Bo, Np, Gp, cf, cw, swi, Rs, Rv, oilfvf=None):
        """
        Plot 1: F vs Eo+(Bti* Efw)
        """
        Bto, Eo, Efw, F = calculate_undersaturated(p, Bg, Bo, Np, Gp, cf, cw, swi, Rs, Rv, oilfvf)
        Boi = Bo[0]
        Eo_Boi_Efw = Eo + Boi * Efw

        # plot
        plt.plot(Eo_Boi_Efw, F, '.')
        plt.title('Plot 1: F vs Eo+(Bti* Efw)')
        plt.xlim(xmin=0);
        plt.ylim(ymin=0)
        plt.xlabel('Eo+(Bti*Efw) (RB/STB)')
        plt.ylabel('F (res bbl)')
        plt.show()

        return(Eo_Boi_Efw, F)

    def plot2(self, p, Bg, Bo, Np, Gp, cf, cw, swi, Rs, Rv, oilfvf):
        """
        Plot 2: F/Eo+(Bti* Efw) vs Np
        """
        Bto, Eo, Efw, F = calculate_undersaturated(p, Bg, Bo, Np, Gp, cf, cw, swi, Rs, Rv, oilfvf)
        Boi = Bo[0]
        Eo_Boi_Efw = Eo + Boi * Efw
        N = F / Eo_Boi_Efw

        # plot
        plt.plot(Np, N, '.')
        plt.title('Plot 2: F/Eo+(Bti* Efw) vs Np')
        plt.xlim(xmin=0);
        plt.ylim(ymin=0)
        plt.xlabel('Np (STB)')
        plt.ylabel('F/Eo+(Bti* Efw) (STB)')
        plt.show()

        return(Eo_Boi_Efw, F)    
    
def regression(x, y):
    import numpy as np
    x = np.array(x);
    y = np.array(y)
    mean_x = np.mean(x)
    mean_y = np.mean(y)
    err_x = x - mean_x
    err_y = y - mean_y
    err_mult = err_x * err_y
    numerator = np.sum(err_mult)
    err_x_squared = err_x ** 2
    denominator = np.sum(err_x_squared)
    slope = numerator / denominator
    intercept = mean_y - B1 * mean_x
    return (intercept, slope)
