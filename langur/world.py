
# # Container for connectors basically
# from typing import List, Set, Type
# from langur.commands.command import Command
# from langur.connectors.connector import Connector


# class World:
#     def __init__(self, connectors: list[Connector] = None):
#         '''
#         An interface with the "real-world", primarily via Actionables, which define specific actions that
#         can be performed to read or write to real-world systems.
#         '''
#         self.connectors = connectors if connectors else []
    
#     def register_connector(self, connector: Connector):
#         if not isinstance(connector, Connector):
#             raise RuntimeError("Tried to register object as connector which is not an instance of Connector")
#         self.connectors.append(connector)

#     def query_connector(self, variant: Type[Connector]) -> Connector:
#         # jank for now
#         for connector in self.connectors:
#             if isinstance(connector, variant):
#                 return connector
#         return None

#     def __str__(self):
#         s = f"World with {len(self.connectors)} connectors:\n"
#         for connector in self.connectors:
#             s += str(connector) + "\n"
#         return s

#     def get_possible_commands(self) -> list[Type[Command]]:
#         '''Get a list of all types of instructions for the actionables in this world'''
#         potential_command_types: Set[Type[Command]] = set()
#         for connector in self.connectors:
#             potential_command_types.update(connector.get_command_types())
        
#         #print('Potential commands:', potential_command_types)
        
#         available_command_types = []
#         # Include only command types for which all connector requirements are met
#         for command_type in potential_command_types:
#             #print('Checking availability for:', command_type)
#             requirements_met = True
#             for required_connector_type in command_type.get_connector_types():
#                 if not self.query_connector(required_connector_type):
#                     #print('Required connector type missing:', required_connector_type)
#                     requirements_met = False
#                     break
#             if requirements_met:
#                 available_command_types.append(command_type)

#         return available_command_types

#     def overview(self) -> str:
#         # for now trivial impl
#         return "\n\n".join([connector.overview() for connector in self.connectors])