import mbuild as mb
import foyer


from gmso.core.forcefield import ForceField
from gmso.external import from_mbuild
from gmso.utils.io import get_fn
from gmso.external import from_parmed


class GMSOSystems:

    @staticmethod
    def systems():
        methods = [GMSOSystems.ar_system, GMSOSystems.typed_ethane]
        for method in methods:
            yield method()

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
