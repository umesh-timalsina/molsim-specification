import numpy as np
import mbuild as mb
import mbuild.recipes
import unyt as u
import foyer

from gmso.core.box import Box
from gmso.core.topology import Topology
from gmso.core.element import Hydrogen, Oxygen
from gmso.core.atom import Atom
from gmso.core.bond import Bond
from gmso.core.angle import Angle
from gmso.core.atom_type import AtomType
from gmso.core.forcefield import ForceField
from gmso.external import from_mbuild, from_parmed
from gmso.tests.utils import get_path
from gmso.utils.io import get_fn
from gmso.external import from_parmed


class GMSOSystems:
    @staticmethod
    def ar_system():
        ar = mb.Compound(name='Ar')
        packed_system = mb.fill_box(
            compound=ar,
            n_compounds=100,
            box=mb.Box([3, 3, 3])
        )
        ff = ForceField(get_fn('ar.xml'))
        top = from_mbuild(packed_system)

        for site in top.sites:
            site.atom_type = ff.atom_types['Ar']

        top.update_topology()

        return top

    @staticmethod
    def typed_ethane():
        from mbuild.lib.molecules import Ethane
        mb_ethane = Ethane()
        oplsaa = foyer.Forcefield(name='oplsaa')
        pmd_ethane = oplsaa.apply(mb_ethane)
        top = from_parmed(pmd_ethane)
        top.name = 'ethane'
        return top


if __name__ == '__main__':
    typed_ethane = GMSOSystems.typed_ethane()
    for btype in typed_ethane.bond_types:
        print('>>', btype.name)