# Battalion Type to SVG Mapping

This document records the mapping between the requested battalion types and their corresponding SVG symbols (by slug/filename), plus notes on whether they already exist in the HTML app or need UI wiring.

## Red Battalions

- AAA BN → `air_defence.svg` (slug: `air_defence`)
- Air Def BN → `air_defence.svg` (slug: `air_defence`)
- Attack Helo BN → `attack_helicopters.svg` (slug: `attack_helicopters`)
- CA BN (Amphib) → `amphibious_armoured_assault_carriers_tracked.svg` (slug: `amphibious_armoured_assault_carriers_tracked`)
- CA BN (Heavy) → `armour.svg` (slug: `armour`)
- CA BN (Light) → `infantry.svg` (slug: `infantry`)
- CA BN (Med) → `mechanized_infantry_tracked.svg` (slug: `mechanized_infantry_tracked`)
- Chem Def BN → `cbrn_defence.svg` (slug: `cbrn_defence`)
- Combat Spt BN → `combat_support.svg` (slug: `combat_support`)
- ELINT BN → `target_aquisition_radar_amp_uav.svg` (slug: `target_aquisition_radar_amp_uav`)
- EW BN → `electronic_warfare.svg` (slug: `electronic_warfare`)
- Field Arty BN → `artillery.svg` (slug: `artillery`)
- Field Arty BN (155mm SP) → `self_propelled_artillery_tracked.svg` (slug: `self_propelled_artillery_tracked`)
- Helo Maint/Repair BN → `aircraft_maintenance.svg` (slug: `aircraft_maintenance`)
- Infantry BN (AASLT) → `air_assault_force.svg` (slug: `air_assault_force`)
- Infantry BN (Airborne) → `airborne_infantry.svg` (slug: `airborne_infantry`)
- Cargo Handling → `supply.svg` (slug: `supply`)
- LR Surv BN → `target_aquisition_radar_amp_uav.svg` (slug: `target_aquisition_radar_amp_uav`)
- MRL BN → `rocket_artillery.svg` (slug: `rocket_artillery`)
- NBC Recon BN → `cbrn_defence.svg` (slug: `cbrn_defence`)
- Ops Spt BN → `combat_support.svg` (slug: `combat_support`)
- Pontoon Bridge BN → `construction_engineers.svg` (slug: `construction_engineers`)
- Recon BN → `reconnaissance.svg` (slug: `reconnaissance`)
- SAM BN (med range) → `air_defence_missile_equiped.svg` (slug: `air_defence_missile_equiped`)
- SAM BN (short range) → `short_range_air_defence_mechanized.svg` (slug: `short_range_air_defence_mechanized`)
- Serv Spt BN → `supply_amp_transportation.svg` (slug: `supply_amp_transportation`)
- SIGINT BN → `target_aquisition_radar_amp_uav.svg` (slug: `target_aquisition_radar_amp_uav`)
- Smokescreen BN → `cbrn_defence.svg` (slug: `cbrn_defence`)
- SOF BN → Custom: `sof` (text "SOF" above crossed lines; based on `special_operations_infantry.svg`)
- Transport BN → `transportation.svg` (slug: `transportation`)
- UAV BN → `uav.svg` (slug: `uav`)

## Green Battalions

- Anti-Tank CO → `anti_tank.svg` (slug: `anti_tank`)
- Armored BN → `armour.svg` (slug: `armour`)
- Armored Field Arty BN → `self_propelled_artillery_tracked.svg` (slug: `self_propelled_artillery_tracked`)
- Field Arty BN → `artillery.svg` (slug: `artillery`)
- Infantry BN → `infantry.svg` (slug: `infantry`)
- Marine Anti-Tank CO → `anti_tank.svg` (slug: `anti_tank`)
- Marine Armored BN → `armour.svg` (slug: `armour`)
- Marine BN → `amphibious_infantry.svg` (slug: `amphibious_infantry`)
- Mech Inf BN → `mechanized_infantry_wheeled.svg` (slug: `mechanized_infantry_wheeled`)
- SOF BN → Custom: `sof` (text "SOF" above crossed lines; based on `special_operations_infantry.svg`)

Notes:
- Where a custom or adjusted rendering is needed in the HTML, the `type` will match the slug as closely as possible for clarity, and the drawn symbol will approximate the referenced SVG. Visual tweaks can be refined after verifying with Playwright/Puppeteer screenshots.
