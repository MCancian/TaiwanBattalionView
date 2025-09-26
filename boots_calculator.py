"""
BOOTS (Ground Operations) calculation engine
Implements landing operations, ground attacks, and movement from PRD.md
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
import logging
from dataclasses import dataclass

@dataclass
class BOOTSResults:
    """Results from BOOTS calculations"""
    landing_results: pd.DataFrame  # Airborne/Air Assault landing outcomes
    attack_results: pd.DataFrame   # Ground attack outcomes
    movement_results: pd.DataFrame # Unit movement results
    unit_casualties: pd.DataFrame  # Updated unit casualties
    territory_control: pd.DataFrame # Hex control status
    fire_support_effectiveness: Dict[str, float]  # Fire support by mission
    total_landings_attempted: int
    total_landings_successful: int
    total_attacks_attempted: int
    total_attacks_successful: int
    warnings: List[str]

class BOOTSCalculator:
    """BOOTS calculation engine implementing PRD.md sections 522-563"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Unit combat strength values (placeholder - would be defined in config)
        self.unit_combat_strength = {
            'Light': 1.0,
            'Medium': 1.5,
            'Heavy': 2.0,
            'Amphib': 1.2,
            'SOF': 1.8,
            'Towed_Arty': 0.8,
            'SP_Arty': 1.3,
            'C2': 0.5,
            'Recon': 0.7,
            'SHORAD': 0.9,
            'Cargo_Handling': 0.3,
            'Engineer': 1.1,
            'Airborne': 1.3,
            'Air_Assault': 1.4,
            'DOS': 0.2
        }
        
        # Terrain modifiers (placeholder)
        self.terrain_modifiers = {
            'urban': 1.5,
            'forest': 1.2,
            'mountain': 1.8,
            'coastal': 0.9,
            'open': 1.0
        }
        
    def calculate_boots_operations(self,
                                 landed_bns: pd.DataFrame,
                                 green_maneuver: pd.DataFrame,
                                 red_operations: Dict,
                                 blue_operations: Dict,
                                 hex_terrain: Dict[str, str]) -> BOOTSResults:
        """
        Main BOOTS calculation following PRD.md specification lines 525-563
        
        Args:
            landed_bns: BNs that successfully landed from Offload
            green_maneuver: Current Green maneuver unit positions
            red_operations: Red player operations (landings, attacks)
            blue_operations: Blue player operations (movements, fire support)
            hex_terrain: Terrain type by hex coordinate
            
        Returns:
            BOOTSResults with all ground operations
        """
        
        warnings = []
        
        # Step 1: Process Red Airborne/Air Assault Landings
        landing_results = self._process_red_landings(
            red_operations.get('airborne_landings', []),
            red_operations.get('air_assault_landings', []),
            hex_terrain
        )
        
        # Step 2: Process Red Ground Attacks
        attack_results = self._process_red_ground_attacks(
            red_operations.get('ground_attacks', []),
            landed_bns, green_maneuver, hex_terrain
        )
        
        # Step 3: Process Blue Maneuver Movements
        movement_results = self._process_blue_movements(
            blue_operations.get('maneuver_movements', []),
            green_maneuver
        )
        
        # Step 4: Process Blue Fire Support
        fire_support_effectiveness = self._process_blue_fire_support(
            blue_operations.get('fire_support_plans', []),
            landed_bns, green_maneuver, hex_terrain
        )
        
        # Step 5: Calculate Unit Casualties
        unit_casualties = self._calculate_unit_casualties(
            landed_bns, green_maneuver, attack_results, fire_support_effectiveness
        )
        
        # Step 6: Update Territory Control
        territory_control = self._update_territory_control(
            landing_results, attack_results, movement_results
        )
        
        # Calculate summary statistics
        total_landings_attempted = len(red_operations.get('airborne_landings', [])) + len(red_operations.get('air_assault_landings', []))
        total_landings_successful = len(landing_results[landing_results['Success'] == True])
        total_attacks_attempted = len(red_operations.get('ground_attacks', []))
        total_attacks_successful = len(attack_results[attack_results['Outcome'] == 'Success'])
        
        self.logger.info(f"BOOTS Complete: {total_landings_successful}/{total_landings_attempted} landings, "
                        f"{total_attacks_successful}/{total_attacks_attempted} attacks successful")
        
        return BOOTSResults(
            landing_results=landing_results,
            attack_results=attack_results,
            movement_results=movement_results,
            unit_casualties=unit_casualties,
            territory_control=territory_control,
            fire_support_effectiveness=fire_support_effectiveness,
            total_landings_attempted=total_landings_attempted,
            total_landings_successful=total_landings_successful,
            total_attacks_attempted=total_attacks_attempted,
            total_attacks_successful=total_attacks_successful,
            warnings=warnings
        )
        
    def _process_red_landings(self,
                            airborne_landings: List[Dict],
                            air_assault_landings: List[Dict],
                            hex_terrain: Dict[str, str]) -> pd.DataFrame:
        """Process Red airborne and air assault landings (RBOOTT1, RBOOTT2)"""
        
        landing_data = []
        
        # Process airborne landings
        for landing in airborne_landings:
            hex_coord = landing.get('hex')
            bn_count = landing.get('bn_count', 0)
            bn_type = landing.get('bn_type', 'Airborne')
            
            # Simple success calculation (would use Matt's program in reality)
            terrain = hex_terrain.get(hex_coord, 'open')
            terrain_mod = self.terrain_modifiers.get(terrain, 1.0)
            
            # Airborne units are good at landing in difficult terrain
            success_chance = 0.8 / terrain_mod  # Better in difficult terrain
            success = np.random.random() < success_chance
            
            units_landed = bn_count if success else max(0, bn_count - np.random.randint(1, bn_count + 1))
            
            landing_data.append({
                'Operation_Type': 'Airborne',
                'Hex': hex_coord,
                'BN_Type': bn_type,
                'BNs_Attempted': bn_count,
                'BNs_Landed': units_landed,
                'Success': success,
                'Terrain': terrain
            })
            
            self.logger.debug(f"Airborne landing at {hex_coord}: {units_landed}/{bn_count} successful")
        
        # Process air assault landings
        for landing in air_assault_landings:
            hex_coord = landing.get('hex')
            bn_count = landing.get('bn_count', 0)
            bn_type = landing.get('bn_type', 'Air_Assault')
            
            # Air assault units are more flexible
            terrain = hex_terrain.get(hex_coord, 'open')
            terrain_mod = self.terrain_modifiers.get(terrain, 1.0)
            
            success_chance = 0.85  # Generally high success rate
            success = np.random.random() < success_chance
            
            units_landed = bn_count if success else max(0, bn_count - np.random.randint(1, max(1, bn_count // 2)))
            
            landing_data.append({
                'Operation_Type': 'Air_Assault',
                'Hex': hex_coord,
                'BN_Type': bn_type,
                'BNs_Attempted': bn_count,
                'BNs_Landed': units_landed,
                'Success': success,
                'Terrain': terrain
            })
            
            self.logger.debug(f"Air assault landing at {hex_coord}: {units_landed}/{bn_count} successful")
        
        return pd.DataFrame(landing_data)
        
    def _process_red_ground_attacks(self,
                                  ground_attacks: List[Dict],
                                  red_units: pd.DataFrame,
                                  green_units: pd.DataFrame,
                                  hex_terrain: Dict[str, str]) -> pd.DataFrame:
        """Process Red ground attacks (RBOOTT3)"""
        
        attack_data = []
        
        for attack in ground_attacks:
            origin_hex = attack.get('origin_hex')
            target_hex = attack.get('target_hex')
            attacking_bns = attack.get('attacking_bns', [])
            fire_support = attack.get('fire_support', [])
            
            # Calculate attacking force strength
            attack_strength = 0
            for bn_info in attacking_bns:
                bn_type = bn_info.get('type')
                bn_count = bn_info.get('count', 0)
                unit_strength = self.unit_combat_strength.get(bn_type, 1.0)
                attack_strength += bn_count * unit_strength
            
            # Add fire support
            fire_support_strength = 0
            for fs_info in fire_support:
                fs_type = fs_info.get('type')
                fs_count = fs_info.get('count', 0)
                fs_strength = self.unit_combat_strength.get(fs_type, 1.0)
                fire_support_strength += fs_count * fs_strength
            
            total_attack_strength = attack_strength + fire_support_strength * 0.5  # Fire support is support
            
            # Calculate defending force strength (simplified)
            defending_strength = np.random.uniform(0.5, 1.5) * total_attack_strength  # Placeholder
            
            # Apply terrain modifier
            terrain = hex_terrain.get(target_hex, 'open')
            terrain_mod = self.terrain_modifiers.get(terrain, 1.0)
            defending_strength *= terrain_mod  # Defenders benefit from terrain
            
            # Determine outcome
            strength_ratio = total_attack_strength / max(defending_strength, 0.1)
            
            if strength_ratio >= 2.0:
                outcome = 'Success'
                casualties_ratio = 0.1  # Light casualties for overwhelming victory
            elif strength_ratio >= 1.5:
                outcome = 'Partial'
                casualties_ratio = 0.2
            elif strength_ratio >= 0.8:
                outcome = 'Partial'
                casualties_ratio = 0.3
            else:
                outcome = 'Failure'
                casualties_ratio = 0.4  # Heavy casualties for failed attack
            
            attack_data.append({
                'Origin_Hex': origin_hex,
                'Target_Hex': target_hex,
                'Attack_Strength': total_attack_strength,
                'Defending_Strength': defending_strength,
                'Strength_Ratio': strength_ratio,
                'Outcome': outcome,
                'Casualties_Ratio': casualties_ratio,
                'Terrain': terrain,
                'Fire_Support_Used': len(fire_support) > 0
            })
            
            self.logger.debug(f"Attack {origin_hex}→{target_hex}: {outcome} "
                            f"(ratio: {strength_ratio:.2f}, casualties: {casualties_ratio:.1%})")
        
        return pd.DataFrame(attack_data)
        
    def _process_blue_movements(self,
                              movements: List[Dict],
                              green_units: pd.DataFrame) -> pd.DataFrame:
        """Process Blue maneuver unit movements (BBOOTT2)"""
        
        movement_data = []
        
        for movement in movements:
            unit_id = movement.get('unit_id')
            from_to = movement.get('from_to')
            to_to = movement.get('to_to')
            unit_type = movement.get('unit_type')
            unit_count = movement.get('unit_count', 0)
            
            # Check movement restrictions
            can_move = self._check_movement_restrictions(from_to, to_to)
            
            if can_move:
                # Successful movement
                movement_data.append({
                    'Unit_ID': unit_id,
                    'Unit_Type': unit_type,
                    'Unit_Count': unit_count,
                    'From_TO': from_to,
                    'To_TO': to_to,
                    'Success': True,
                    'Reason': 'Movement completed'
                })
                
                self.logger.debug(f"Green {unit_type} moved from TO {from_to} to TO {to_to}")
            else:
                # Failed movement
                movement_data.append({
                    'Unit_ID': unit_id,
                    'Unit_Type': unit_type,
                    'Unit_Count': unit_count,
                    'From_TO': from_to,
                    'To_TO': to_to,
                    'Success': False,
                    'Reason': 'Movement restricted'
                })
                
                self.logger.warning(f"Movement TO {from_to}→{to_to} restricted")
        
        return pd.DataFrame(movement_data)
        
    def _check_movement_restrictions(self, from_to: int, to_to: int) -> bool:
        """Check movement restrictions (TO 3 and TO 4 cannot move to each other)"""
        
        # PRD.md: "Systems and maneuver units can move to any other TO, 
        # except that 3rd and 4th cannot move to each other"
        if (from_to == 3 and to_to == 4) or (from_to == 4 and to_to == 3):
            return False
            
        return True
        
    def _process_blue_fire_support(self,
                                 fire_support_plans: List[Dict],
                                 red_units: pd.DataFrame,
                                 green_units: pd.DataFrame,
                                 hex_terrain: Dict[str, str]) -> Dict[str, float]:
        """Process Blue fire support plans (BBOOTT3)"""
        
        effectiveness = {}
        
        for plan in fire_support_plans:
            plan_id = plan.get('plan_id', 'unknown')
            supporting_units = plan.get('supporting_units', [])
            target_hex = plan.get('target_hex')
            target_type = plan.get('target_type')  # Maneuver, Chokepoints, Artillery, Infrastructure
            
            # Calculate fire support strength
            fs_strength = 0
            for unit_info in supporting_units:
                unit_type = unit_info.get('type')
                unit_count = unit_info.get('count', 0)
                unit_strength = self.unit_combat_strength.get(unit_type, 1.0)
                
                # Artillery units are more effective in fire support
                if 'Arty' in unit_type:
                    fs_strength += unit_count * unit_strength * 1.5
                else:
                    fs_strength += unit_count * unit_strength
            
            # Calculate effectiveness based on target type
            base_effectiveness = min(fs_strength * 10, 90)  # Cap at 90%
            
            # Modify by target type
            if target_type == 'Maneuver':
                target_effectiveness = base_effectiveness * 1.0
            elif target_type == 'Artillery':
                target_effectiveness = base_effectiveness * 1.2  # Better against artillery
            elif target_type == 'Chokepoints':
                target_effectiveness = base_effectiveness * 0.8  # Harder to hit infrastructure
            elif target_type == 'Infrastructure':
                target_effectiveness = base_effectiveness * 0.6
            else:
                target_effectiveness = base_effectiveness * 0.8
            
            effectiveness[plan_id] = min(target_effectiveness, 95)  # Cap at 95%
            
            self.logger.debug(f"Fire support plan {plan_id}: {effectiveness[plan_id]:.1f}% effective "
                            f"against {target_type} at {target_hex}")
        
        return effectiveness
        
    def _calculate_unit_casualties(self,
                                 red_units: pd.DataFrame,
                                 green_units: pd.DataFrame,
                                 attack_results: pd.DataFrame,
                                 fire_support_effectiveness: Dict[str, float]) -> pd.DataFrame:
        """Calculate unit casualties from combat operations"""
        
        casualty_data = []
        
        # Calculate Red casualties from ground attacks
        for _, attack in attack_results.iterrows():
            casualties_ratio = attack['Casualties_Ratio']
            
            # Apply casualties to attacking units (simplified)
            casualty_data.append({
                'Team': 'Red',
                'Operation': 'Ground_Attack',
                'Hex': attack['Target_Hex'],
                'Casualties': int(10 * casualties_ratio),  # Placeholder calculation
                'Reason': f"Attack {attack['Outcome']}"
            })
        
        # Calculate casualties from Blue fire support
        for plan_id, effectiveness in fire_support_effectiveness.items():
            casualties = int(effectiveness / 10)  # Simplified calculation
            
            casualty_data.append({
                'Team': 'Red',
                'Operation': 'Fire_Support',
                'Hex': 'Various',
                'Casualties': casualties,
                'Reason': f"Fire support plan {plan_id}"
            })
        
        return pd.DataFrame(casualty_data)
        
    def _update_territory_control(self,
                                landing_results: pd.DataFrame,
                                attack_results: pd.DataFrame,
                                movement_results: pd.DataFrame) -> pd.DataFrame:
        """Update territory control based on operations"""
        
        control_data = []
        
        # Process successful landings
        successful_landings = landing_results[landing_results['Success'] == True]
        for _, landing in successful_landings.iterrows():
            control_data.append({
                'Hex': landing['Hex'],
                'Control': 'Red',
                'Strength': landing['BNs_Landed'],
                'Source': f"{landing['Operation_Type']} Landing"
            })
        
        # Process successful attacks
        successful_attacks = attack_results[attack_results['Outcome'] == 'Success']
        for _, attack in successful_attacks.iterrows():
            control_data.append({
                'Hex': attack['Target_Hex'],
                'Control': 'Red',
                'Strength': attack['Attack_Strength'],
                'Source': 'Ground Attack'
            })
        
        # Process contested areas (partial attacks)
        partial_attacks = attack_results[attack_results['Outcome'] == 'Partial']
        for _, attack in partial_attacks.iterrows():
            control_data.append({
                'Hex': attack['Target_Hex'],
                'Control': 'Contested',
                'Strength': attack['Attack_Strength'] / 2,
                'Source': 'Partial Attack'
            })
        
        return pd.DataFrame(control_data)
        
    def export_boots_data_for_external_program(self, 
                                             red_operations: Dict,
                                             blue_operations: Dict,
                                             current_positions: pd.DataFrame) -> Dict:
        """Export data for Matt's external BOOTS program"""
        
        export_data = {
            'red_operations': {
                'airborne_landings': red_operations.get('airborne_landings', []),
                'air_assault_landings': red_operations.get('air_assault_landings', []),
                'ground_attacks': red_operations.get('ground_attacks', [])
            },
            'blue_operations': {
                'maneuver_movements': blue_operations.get('maneuver_movements', []),
                'fire_support_plans': blue_operations.get('fire_support_plans', []),
                'bn_allocations': blue_operations.get('bn_allocations', [])
            },
            'current_unit_positions': current_positions.to_dict('records'),
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        return export_data