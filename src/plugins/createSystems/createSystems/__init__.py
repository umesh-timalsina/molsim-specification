"""
This is where the implementation of the plugin code goes.
The createSystems-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import json
import logging

from .gmso_systems import GMSOSystems

from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('createSystems')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class createSystems(PluginBase):
    def main(self):
        core = self.core
        root_node = self.root_node
        active_node = self.active_node

        name = core.get_attribute(active_node, 'name')

        logger.info('ActiveNode at "{0}" has name {1}'.format(core.get_path(active_node), name))

        self.convert_to_nodes(GMSOSystems.typed_ethane())

        commit_info = self.util.save(root_node, self.commit_hash, 'master', 'Python plugin updated the model')
        logger.info('committed :{0}'.format(commit_info))

    def convert_to_nodes(self, topology):
        system = self.core.create_node(
            {
                'parent': self.active_node,
                'base': self.META.get('System')
            }
        )
        self.core.set_attribute(system, name='name', value=topology.name)

        self.logger.info(f'Created system node with name {topology.name}')

        atom_nodes = {}

        atom_type_nodes = self._add_potential_nodes(
            system,
            topology,
            potential_attr='_atom_types',
            target='AtomType'
        )

        bond_type_nodes = self._add_potential_nodes(
            system,
            topology,
            potential_attr='_bond_types',
            target='BondType'
        )

        angle_type_nodes = self._add_potential_nodes(
            system,
            topology,
            potential_attr='_angle_types',
            target='AngleType'
        )

        dihedral_type_nodes = self._add_potential_nodes(
            system,
            topology,
            potential_attr='_dihedral_types',
            target='DihedralType'
        )

        improper_type_nodes = self._add_potential_nodes(
            system,
            topology,
            potential_attr='_improper_types',
            target='ImproperType'
        )

        for atom in topology.sites:
            atom_nodes[id(atom)] = self.core.create_node({
                'parent': system,
                'base': self.META.get('Atom')
            })
            self.core.set_attribute(
                atom_nodes[id(atom)], name='name', value=atom.name
            )
            for key in self.core.get_valid_attribute_names(atom_nodes[id(atom)]):
                json_dict = json.loads(atom.json(by_alias=True))
                if key in json_dict:
                    self.core.set_attribute(
                        atom_nodes[id(atom)],
                        name=key,
                        value=str(json_dict.get(key))
                    )

            if atom.atom_type is not None:
                atype_node = atom_type_nodes[atom.atom_type]
                self.core.set_pointer(
                    atom_nodes[id(atom)],
                    name='potential',
                    target=atype_node
                )

        for bond in topology.bonds:
            atom_1 = atom_nodes[id(bond.connection_members[0])]
            atom_2 = atom_nodes[id(bond.connection_members[1])]
            src = self.core.create_node({
                'parent': atom_1,
                'base': self.META.get('AtomPort')
            })

            dst = self.core.create_node({
                'parent': atom_2,
                'base': self.META.get('AtomPort')
            })

            bond = self.core.create_node({
                'parent': system,
                'base': self.META.get('Bond')
            })

            self.core.set_pointer(bond, name='src', target=src)
            self.core.set_pointer(bond, name='dst', target=dst)

        self._add_connection_nodes(system,
                                   topology,
                                   atom_nodes,
                                   connection_attr='angles',
                                   target='Angle')

        self._add_connection_nodes(system,
                                   topology,
                                   atom_nodes,
                                   connection_attr='dihedrals',
                                   target='Dihedral')

        self._add_connection_nodes(system,
                                   topology,
                                   atom_nodes,
                                   connection_attr='impropers',
                                   target='Improper')

    def _add_potential_nodes(self,
                             parent,
                             topology,
                             potential_attr='_atom_types',
                             target='AtomType'):
        potential_types = getattr(topology, potential_attr)
        potential_type_nodes = {}
        for potential_type in potential_types.values():
            potential_node = self.core.create_node({
                'parent': parent,
                'base': self.META.get(target)
            })
            for key in self.core.get_valid_attribute_names(potential_node):
                json_dict = json.loads(potential_type.json(by_alias=True))
                if key in json_dict:
                    self.core.set_attribute(
                        potential_node,
                        name=key,
                        value=str(json_dict.get(key))
                    )

            potential_type_nodes[potential_type] = potential_attr

        return potential_type_nodes

    def _add_connection_nodes(self,
                              parent,
                              topology,
                              atom_nodes,
                              connection_attr='angles',
                              target='Angle'):
        connections = getattr(topology, connection_attr)
        for connection in connections:
            atoms = [atom_nodes[id(atom)] for atom in connection.connection_members]
            connection_node = self.core.create_node({
                'parent': parent,
                'base': self.META.get(target)
            })
            for atom in atoms:
                self.core.add_member(
                    node=connection_node,
                    name='connectionMembers',
                    member=atom
                )



