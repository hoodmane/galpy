###############################################################################
#   KuzminKutuzovStaeckelPotential.py:
#           class that implements a simple Staeckel potential
#           generated by a Kuzmin-Kutuzov potential
#                                   - amp
#               Phi(r)=  ---------------------------
#                        \sqrt{lambda} + \sqrt{nu}
###############################################################################
import numpy

from ..util import conversion  # for prolate spherical coordinate transforms
from ..util import coords
from .Potential import Potential


class KuzminKutuzovStaeckelPotential(Potential):
    """Class that implements the Kuzmin-Kutuzov Staeckel potential

    .. math::

        \\Phi(R,z) = -\\frac{\\mathrm{amp}}{\\sqrt{\\lambda} + \\sqrt{\\nu}}

    (see, e.g., `Batsleer & Dejonghe 1994 <http://adsabs.harvard.edu/abs/1994A%26A...287...43B>`__)

    """
    def __init__(self,amp=1.,ac=5.,Delta=1.,normalize=False,
                 ro=None,vo=None):
        """
        NAME:

            __init__

        PURPOSE:

            initialize a Kuzmin-Kutuzov Staeckel potential

        INPUT:

            amp       - amplitude to be applied to the potential (default: 1); can be a Quantity with units of mass density or Gxmass density

            ac        - axis ratio of the coordinate surfaces; (a/c) = sqrt(-alpha) / sqrt(-gamma) (default: 5.)

            Delta     - focal distance that defines the spheroidal coordinate system (default: 1.); Delta=sqrt(gamma-alpha) (can be Quantity)

            normalize - if True, normalize such that vc(1.,0.)=1., or, if given as a number, such that the force is this fraction of the force necessary to make vc(1.,0.)=1.

           ro=, vo= distance and velocity scales for translation into internal units (default from configuration file)

        OUTPUT:

           (none)

        HISTORY:

           2015-02-15 - Written - Trick (MPIA)

        """
        Potential.__init__(self,amp=amp,ro=ro,vo=vo,amp_units='mass')
        Delta= conversion.parse_length(Delta,ro=self._ro)
        self._ac    = ac
        self._Delta = Delta
        self._gamma = self._Delta**2 / (1.-self._ac**2)
        self._alpha = self._gamma - self._Delta**2
        if normalize or \
                (isinstance(normalize,(int,float)) \
                     and not isinstance(normalize,bool)):
            self.normalize(normalize)
        self.hasC      = True
        self.hasC_dxdv = True

    def _evaluate(self,R,z,phi=0.,t=0.):
        """
        NAME:
            _evaluate
        PURPOSE:
            evaluate the potential at R,z
        INPUT:
            R - Galactocentric cylindrical radius
            z - vertical height
            phi - azimuth
            t - time
        OUTPUT:
            Phi(R,z)
        HISTORY:
            2015-02-15 - Written - Trick (MPIA)
        """
        l,n = coords.Rz_to_lambdanu(R,z,ac=self._ac,Delta=self._Delta)
        return -1./(numpy.sqrt(l) + numpy.sqrt(n))

    def _Rforce(self,R,z,phi=0.,t=0.):
        """
        NAME:
            _Rforce
        PURPOSE:
            evaluate the radial force for this potential
        INPUT:
            R - Galactocentric cylindrical radius
            z - vertical height
            phi - azimuth
            t - time
        OUTPUT:
            the radial force = -dphi/dR
        HISTORY:
            2015-02-13 - Written - Trick (MPIA)
        """
        l,n = coords.Rz_to_lambdanu    (R,z,ac=self._ac,Delta=self._Delta)
        jac = coords.Rz_to_lambdanu_jac(R,z,            Delta=self._Delta)
        dldR = jac[0,0]
        dndR = jac[1,0]
        return - (dldR * self._lderiv(l,n) + \
                  dndR * self._nderiv(l,n))


    def _zforce(self,R,z,phi=0.,t=0.):
        """
        NAME:
            _zforce
        PURPOSE:
            evaluate the vertical force for this potential
        INPUT:
            R - Galactocentric cylindrical radius
            z - vertical height
            phi - azimuth
            t - time
        OUTPUT:
            the vertical force
        HISTORY:
            2015-02-13 - Written - Trick (MPIA)
        """
        l,n = coords.Rz_to_lambdanu    (R,z,ac=self._ac,Delta=self._Delta)
        jac = coords.Rz_to_lambdanu_jac(R,z,            Delta=self._Delta)
        dldz = jac[0,1]
        dndz = jac[1,1]
        return - (dldz * self._lderiv(l,n) + \
                  dndz * self._nderiv(l,n))

    def _R2deriv(self,R,z,phi=0.,t=0.):
        """
        NAME:
            _R2deriv
        PURPOSE:
            evaluate the second radial derivative for this potential
        INPUT:
            R - Galactocentric cylindrical radius
            z - vertical height
            phi - azimuth
            t - time
        OUTPUT:
            the second radial derivative
        HISTORY:
            2015-02-13 - Written - Trick (MPIA)
        """
        l,n    = coords.Rz_to_lambdanu     (R,z,ac=self._ac,Delta=self._Delta)
        jac    = coords.Rz_to_lambdanu_jac (R,z,            Delta=self._Delta)
        hess   = coords.Rz_to_lambdanu_hess(R,z,            Delta=self._Delta)
        dldR   = jac[0,0]
        dndR   = jac[1,0]
        d2ldR2 = hess[0,0,0]
        d2ndR2 = hess[1,0,0]
        return d2ldR2       * self._lderiv(l,n)  + \
               d2ndR2       * self._nderiv(l,n)  + \
               (dldR)**2    * self._l2deriv(l,n) + \
               (dndR)**2    * self._n2deriv(l,n) + \
               2.*dldR*dndR * self._lnderiv(l,n)

    def _z2deriv(self,R,z,phi=0.,t=0.):
        """
        NAME:
            _z2deriv
        PURPOSE:
            evaluate the second vertical derivative for this potential
        INPUT:
            R - Galactocentric cylindrical radius
            z - vertical height
            phi - azimuth
            t- time
        OUTPUT:
            the second vertical derivative
        HISTORY:
            2015-02-13 - Written - Trick (MPIA)
        """
        l,n    = coords.Rz_to_lambdanu    (R,z,ac=self._ac,Delta=self._Delta)
        jac    = coords.Rz_to_lambdanu_jac(R,z,            Delta=self._Delta)
        hess   = coords.Rz_to_lambdanu_hess(R,z,           Delta=self._Delta)
        dldz = jac[0,1]
        dndz = jac[1,1]
        d2ldz2 = hess[0,1,1]
        d2ndz2 = hess[1,1,1]
        return d2ldz2       * self._lderiv(l,n)  + \
               d2ndz2       * self._nderiv(l,n)  + \
               (dldz)**2    * self._l2deriv(l,n) + \
               (dndz)**2    * self._n2deriv(l,n) + \
               2.*dldz*dndz * self._lnderiv(l,n)


    def _Rzderiv(self,R,z,phi=0.,t=0.):
        """
        NAME:
            _Rzderiv
        PURPOSE:
            evaluate the mixed R,z derivative for this potential
        INPUT:
            R - Galactocentric cylindrical radius
            z - vertical height
            phi - azimuth
            t- time
        OUTPUT:
            d2phi/dR/dz
        HISTORY:
            2015-02-13 - Written - Trick (MPIA)
        """
        l,n    = coords.Rz_to_lambdanu    (R,z,ac=self._ac,Delta=self._Delta)
        jac    = coords.Rz_to_lambdanu_jac(R,z,            Delta=self._Delta)
        hess   = coords.Rz_to_lambdanu_hess(R,z,           Delta=self._Delta)
        dldR = jac[0,0]
        dndR = jac[1,0]
        dldz = jac[0,1]
        dndz = jac[1,1]
        d2ldRdz = hess[0,0,1]
        d2ndRdz = hess[1,0,1]
        return d2ldRdz              * self._lderiv(l,n)  + \
               d2ndRdz              * self._nderiv(l,n)  + \
               dldR*dldz            * self._l2deriv(l,n) + \
               dndR*dndz            * self._n2deriv(l,n) + \
               (dldR*dndz+dldz*dndR)* self._lnderiv(l,n)

    def _lderiv(self,l,n):
        """
        NAME:
            _lderiv
        PURPOSE:
            evaluate the derivative w.r.t. lambda for this potential
        INPUT:
            l - prolate spheroidal coordinate lambda
            n - prolate spheroidal coordinate nu
        OUTPUT:
            derivative w.r.t. lambda
        HISTORY:
            2015-02-15 - Written - Trick (MPIA)
        """
        return 0.5/numpy.sqrt(l)/(numpy.sqrt(l)+numpy.sqrt(n))**2

    def _nderiv(self,l,n):
        """
        NAME:
            _nderiv
        PURPOSE:
            evaluate the derivative w.r.t. nu for this potential
        INPUT:
            l - prolate spheroidal coordinate lambda
            n - prolate spheroidal coordinate nu
        OUTPUT:
            derivative w.r.t. nu
        HISTORY:
            2015-02-15 - Written - Trick (MPIA)
        """
        return 0.5/numpy.sqrt(n)/(numpy.sqrt(l)+numpy.sqrt(n))**2

    def _l2deriv(self,l,n):
        """
        NAME:
            _l2deriv
        PURPOSE:
            evaluate the second derivative w.r.t. lambda for this potential
        INPUT:
            l - prolate spheroidal coordinate lambda
            n - prolate spheroidal coordinate nu
        OUTPUT:
            second derivative w.r.t. lambda
        HISTORY:
            2015-02-15 - Written - Trick (MPIA)
        """
        number = -3.*numpy.sqrt(l) - numpy.sqrt(n)
        denom = 4. * l**1.5 * (numpy.sqrt(l)+numpy.sqrt(n))**3
        return number / denom

    def _n2deriv(self,l,n):
        """
        NAME:
            _n2deriv
        PURPOSE:
            evaluate the second derivative w.r.t. nu for this potential
        INPUT:
            l - prolate spheroidal coordinate lambda
            n - prolate spheroidal coordinate nu
        OUTPUT:
            second derivative w.r.t. nu
        HISTORY:
            2015-02-15 - Written - Trick (MPIA)
        """
        number = -numpy.sqrt(l) - 3.*numpy.sqrt(n)
        denom = 4. * n**1.5 * (numpy.sqrt(l)+numpy.sqrt(n))**3
        return number / denom

    def _lnderiv(self,l,n):
        """
        NAME:
            _lnderiv
        PURPOSE:
            evaluate the mixed derivative w.r.t. lambda and nu for this potential
        INPUT:
            l - prolate spheroidal coordinate lambda
            n - prolate spheroidal coordinate nu
        OUTPUT:
            d2phi/dl/dn
        HISTORY:
            2015-02-13 - Written - Trick (MPIA)
        """
        return -0.5/(numpy.sqrt(l) * numpy.sqrt(n) * (numpy.sqrt(l)+numpy.sqrt(n))**3)
