import streamlit as st
import pandas as pd

@st.cache_data
def load_manifest_data(file):
    # Load file
    full_manifest_data = pd.read_csv(file)

    # Re-Order Columns
    cols = full_manifest_data.columns.tolist()
    first_cols = ['Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Hash', 'Weapon Tier', 'Weapon Type', 'Weapon Archetype',  'Weapon Slot', 'Weapon Element',
                  'Weapon Current Version', 'Weapon Power Cap', 'Is Sunset']
    remaining_cols = [col for col in cols if col not in first_cols]
    full_manifest_data = full_manifest_data[first_cols + remaining_cols]
    full_manifest_data = full_manifest_data.rename(columns={'Weapon Range': 'Range'})
    return full_manifest_data

manifest_weapon_load = load_manifest_data('data/Master Weapon Manifest.csv')
manifest_weapon_data = manifest_weapon_load

def load_dim_weapon_data(file, manifest_weapon_data):
    dim_weapon_import = pd.read_csv(file)
    dim_weapon_import = pd.merge(dim_weapon_import, manifest_weapon_data[['Weapon Hash', 'Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Tier',
                                                                               'Weapon Type', 'Weapon Archetype', 'Weapon Slot', 'Weapon Element', 'Weapon Current Version',
                                                                               'Weapon Power Cap', 'Is Sunset']], left_on='Hash', right_on='Weapon Hash', how='left')

    cols = dim_weapon_import.columns.tolist()
    first_cols = ['Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Hash', 'Weapon Tier', 'Weapon Type', 'Weapon Archetype', 'Weapon Slot', 'Weapon Element',
                  'Weapon Current Version', 'Weapon Power Cap', 'Is Sunset']
    remaining_cols = [col for col in cols if col not in first_cols]
    dim_weapon_import = dim_weapon_import[first_cols + remaining_cols]
    dim_weapon_import = dim_weapon_import.drop(
        columns=['Name', 'Id', 'Hash', 'Tag', 'Source', 'Tier', 'Type', 'Category', 'Element', 'Power', 'Power Limit', 'Owner', 'Locked', 'Equipped', 'Year', 'Season', 'Event', 'Recoil',
                 'AA', 'Impact', 'Range', 'Zoom', 'Blast Radius', 'Velocity', 'Stability', 'ROF', 'Reload', 'Mag', 'Handling', 'Charge Time', 'Guard Resistance', 'Draw Time', 'Accuracy',
                 'Charge Rate', 'Guard Efficiency', 'Swing Speed', 'Shield Duration', 'Kill Tracker', 'Foundry', 'Loadouts', 'Notes', 'Perks 0'])

    dim_perk_columns = dim_weapon_import.filter(regex='^Perks').columns
    dim_weapon_import[dim_perk_columns] = dim_weapon_import[dim_perk_columns].replace(to_replace='\*', value='', regex=True)
    return dim_weapon_import

def load_dim_armor_data(file):
    cols_to_use = ['Name', 'Hash', 'Id', 'Tier', 'Type', 'Equippable', 'Energy Capacity', 'Mobility (Base)', 'Resilience (Base)', 'Recovery (Base)', 'Discipline (Base)', 'Intellect (Base)', 'Strength (Base)', 'Total (Base)']
    col_names = {'Id': 'id', 'Equippable': 'Character', 'Energy Capacity': 'MW_Tier', 'Mobility (Base)': 'base_mob', 'Resilience (Base)': 'base_res', 'Recovery (Base)': 'base_rec', 'Discipline (Base)': 'base_dis',
                 'Intellect (Base)': 'base_int', 'Strength (Base)': 'base_str', 'Total (Base)': 'base_total'}
    file = pd.read_csv(file, usecols=cols_to_use)
    file = file.rename(columns=col_names)
    file['Type'] = file['Type'].replace({'Hunter Cloak', 'Warlock Bond', 'Titan Mark'}, 'Class Item').replace('Chest Armor', 'Chest').replace('Leg Armor', 'Legs')
    file["base_mob_res"] = file['base_mob'] + file['base_res']
    file["base_mob_rec"] = file['base_mob'] + file['base_rec']
    file["base_res_rec"] = file['base_res'] + file['base_rec']
    file["base_group_1"] = file['base_mob'] + file['base_res'] + file['base_rec']
    file["base_group_2"] = file['base_dis'] + file['base_int'] + file['base_str']
    file["mw_mob"] = file['base_mob'] + 2
    file["mw_res"] = file['base_res'] + 2
    file["mw_rec"] = file['base_rec'] + 2
    file["mw_dis"] = file['base_dis'] + 2
    file["mw_int"] = file['base_int'] + 2
    file["mw_str"] = file['base_str'] + 2
    file["mw_total"] = file['base_total'] + 12
    file["mw_mob_res"] = file['mw_mob'] + file['mw_res']
    file["mw_mob_rec"] = file['mw_mob'] + file['mw_rec']
    file["mw_res_rec"] = file['mw_res'] + file['mw_rec']
    file["mw_group_1"] = file['mw_mob'] + file['mw_res'] + file['mw_rec']
    file["mw_group_2"] = file['mw_dis'] + file['mw_int'] + file['mw_str']
    return file