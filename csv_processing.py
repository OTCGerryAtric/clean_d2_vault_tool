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

@st.cache_data
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

@st.cache_data
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

@st.cache_data
def dim_weapon_perk_alignment(dim_weapon_data, manifest_weapon_data):
    # Removed Enhanced from Perks
    for column in dim_weapon_data.columns:
        if column.startswith('Perks'):
            dim_weapon_data[column] = dim_weapon_data[column].str.replace(' Enhanced', '')

    # Get the columns from manifest_weapon_data that start with "slot"
    slot_columns = manifest_weapon_data.columns[manifest_weapon_data.columns.str.startswith("Slot")]

    # Merge the dataframes based on the primary key
    df = dim_weapon_data.merge(manifest_weapon_data[["Weapon Name With Season"] + list(slot_columns)], on="Weapon Name With Season", how="left")

    # Replace blanks with NaN
    df.replace("", float("nan"), inplace=True)

    # Get the columns starting with "Perks" and "Slot"
    perk_columns = df.columns[df.columns.str.startswith("Perks")]
    slot_columns = df.columns[df.columns.str.startswith("Slot")]

    # Iterate over each perk column
    for perk_col in perk_columns:
        matched_slots = []
        # Iterate over each row
        for index, row in df.iterrows():
            perk_value = row[perk_col]  # Get the value from the perk column
            if pd.notnull(perk_value):  # Check if perk value is not NaN
                matched_slot = ""
                # Iterate over each slot column
                for slot_col in slot_columns:
                    slot_value = row[slot_col]  # Get the value from the slot column
                    if pd.notnull(slot_value) and str(perk_value) in str(slot_value):
                        matched_slot = slot_col
                        break  # Break out of the loop if a match is found in any slot column
                matched_slots.append(matched_slot)
            else:
                matched_slots.append("")  # Add empty string for NaN perk values
        df[f"Matched Slot for {perk_col}"] = matched_slots

    # Delete columns starting with "Slot"
    df.drop(columns=df.columns[df.columns.str.startswith("Slot")], inplace=True)

    # Create new columns
    new_columns = []
    for slot in range(1, 5):
        for perk in range(0, 4):
            new_col = f"Slot {slot} Perk {perk}"
            df[new_col] = ""
            new_columns.append(new_col)

    # Get the columns starting with "Matched Slot"
    matched_slot_columns = df.columns[df.columns.str.startswith("Matched Slot")]

    # Iterate over each column and keep only the first 6 characters in the values
    for column in matched_slot_columns:
        df[column] = df[column].str[:6]

    # Replace blanks with NaN
    df.replace("", float("nan"), inplace=True)

    # Check if each column contains only NaN values
    columns_to_delete = []
    for column in matched_slot_columns:
        if df[column].isnull().all():
            columns_to_delete.append(column)

    # Delete the columns
    df.drop(columns=columns_to_delete, inplace=True)

    # Get the columns starting with "Matched Slot"
    matched_slot_columns = df.columns[df.columns.str.startswith("Matched Slot")]

    # Count non-NaN entries in each row for matched_stats_columns
    df['Total Perks'] = df[matched_slot_columns].count(axis=1)

    # Count occurrences of "Slot 1" in each row
    df['Slot 1 Count'] = df.apply(lambda row: row.str.count('Slot 1').sum(), axis=1)
    df['Slot 2 Count'] = df.apply(lambda row: row.str.count('Slot 2').sum(), axis=1)
    df['Slot 3 Count'] = df.apply(lambda row: row.str.count('Slot 3').sum(), axis=1)
    df['Slot 4 Count'] = df.apply(lambda row: row.str.count('Slot 4').sum(), axis=1)

    # Filter out columns that start with "Matched Slot"
    df = df.filter(regex=r'^(?!Matched Slot)')

    # Populate Slot 1 Perk y Columns
    df['Slot 1 Perk 0'] = df['Perks 1']
    df['Slot 1 Perk 1'] = np.where(pd.to_numeric(df['Slot 1 Count'], errors='coerce') >= 2, df['Perks 2'], np.nan)
    df['Slot 1 Perk 2'] = np.where(pd.to_numeric(df['Slot 1 Count'], errors='coerce') >= 3, df['Perks 3'], np.nan)
    df['Slot 1 Perk 3'] = np.where(pd.to_numeric(df['Slot 1 Count'], errors='coerce') >= 4, df['Perks 4'], np.nan)

    # Populate Slot 2 Perk 0 Columns
    for index, row in df.iterrows():
        slot_1_count = row['Slot 1 Count']
        perk_2_sp = int(slot_1_count + 1)
        slot_2_perk_column = 'Perks ' + str(perk_2_sp)
        df.at[index, 'Slot 2 Perk 0'] = row[slot_2_perk_column]

    # Populate Slot 2 Perk 1 Columns
    for index, row in df.iterrows():
        slot_1_count = row['Slot 1 Count']
        perk_2_sp = int(slot_1_count + 2)
        slot_2_perk_column = 'Perks ' + str(perk_2_sp)
        if pd.to_numeric(row['Slot 2 Count'], errors='coerce') >= 2:
            df.at[index, 'Slot 2 Perk 1'] = row[slot_2_perk_column]
        else:
            df.at[index, 'Slot 2 Perk 1'] = np.nan

    # Populate Slot 2 Perk 2 Columns
    for index, row in df.iterrows():
        slot_1_count = row['Slot 1 Count']
        perk_2_sp = int(slot_1_count + 3)
        slot_2_perk_column = 'Perks ' + str(perk_2_sp)
        if pd.to_numeric(row['Slot 2 Count'], errors='coerce') >= 3:
            df.at[index, 'Slot 2 Perk 2'] = row[slot_2_perk_column]
        else:
            df.at[index, 'Slot 2 Perk 2'] = np.nan

    # Populate Slot 2 Perk 3 Columns
    for index, row in df.iterrows():
        slot_1_count = row['Slot 1 Count']
        perk_2_sp = int(slot_1_count + 4)
        slot_2_perk_column = 'Perks ' + str(perk_2_sp)
        if pd.to_numeric(row['Slot 2 Count'], errors='coerce') >= 4:
            df.at[index, 'Slot 2 Perk 3'] = row[slot_2_perk_column]
        else:
            df.at[index, 'Slot 2 Perk 3'] = np.nan

    # Populate Slot 3 Perk 0 Columns
    for index, row in df.iterrows():
        slot_2_count = row['Slot 1 Count'] + row['Slot 2 Count']
        perk_3_sp = int(slot_2_count + 1)
        slot_3_perk_column = 'Perks ' + str(perk_3_sp)
        df.at[index, 'Slot 3 Perk 0'] = row[slot_3_perk_column]

    # Populate Slot 3 Perk 1 Columns
    for index, row in df.iterrows():
        slot_2_count = row['Slot 1 Count'] + row['Slot 2 Count']
        perk_3_sp = int(slot_2_count + 2)
        slot_3_perk_column = 'Perks ' + str(perk_3_sp)
        if pd.to_numeric(row['Slot 3 Count'], errors='coerce') >= 2:
            df.at[index, 'Slot 3 Perk 1'] = row[slot_3_perk_column]
        else:
            df.at[index, 'Slot 3 Perk 1'] = np.nan

    # Populate Slot 3 Perk 2 Columns
    for index, row in df.iterrows():
        slot_2_count = row['Slot 2 Count'] + row['Slot 2 Count']
        perk_3_sp = int(slot_1_count + 3)
        slot_3_perk_column = 'Perks ' + str(perk_3_sp)
        if pd.to_numeric(row['Slot 3 Count'], errors='coerce') >= 3:
            df.at[index, 'Slot 3 Perk 2'] = row[slot_3_perk_column]
        else:
            df.at[index, 'Slot 3 Perk 2'] = np.nan

    # Populate Slot 3 Perk 3 Columns
    for index, row in df.iterrows():
        slot_2_count = row['Slot 2 Count'] + row['Slot 2 Count']
        perk_3_sp = int(slot_1_count + 4)
        slot_3_perk_column = 'Perks ' + str(perk_3_sp)
        if pd.to_numeric(row['Slot 3 Count'], errors='coerce') >= 4:
            df.at[index, 'Slot 3 Perk 3'] = row[slot_3_perk_column]
        else:
            df.at[index, 'Slot 3 Perk 3'] = np.nan

    # Populate Slot 3 Perk 0 Columns
    for index, row in df.iterrows():
        slot_3_count = row['Slot 1 Count'] + row['Slot 2 Count'] + row['Slot 3 Count']
        perk_4_sp = int(slot_3_count + 1)
        slot_4_perk_column = 'Perks ' + str(perk_4_sp)
        if pd.to_numeric(row['Slot 4 Count'], errors='coerce') >= 1:
            df.at[index, 'Slot 4 Perk 0'] = row[slot_4_perk_column]
        else:
            df.at[index, 'Slot 4 Perk 0'] = np.nan

    # Populate Slot 3 Perk 1 Columns
    for index, row in df.iterrows():
        slot_3_count = row['Slot 1 Count'] + row['Slot 2 Count'] + row['Slot 3 Count']
        perk_4_sp = int(slot_3_count + 2)
        slot_4_perk_column = 'Perks ' + str(perk_4_sp)
        if pd.to_numeric(row['Slot 4 Count'], errors='coerce') >= 2:
            df.at[index, 'Slot 4 Perk 1'] = row[slot_4_perk_column]
        else:
            df.at[index, 'Slot 4 Perk 1'] = np.nan

    # Populate Slot 3 Perk 2 Columns
    for index, row in df.iterrows():
        slot_3_count = row['Slot 1 Count'] + row['Slot 2 Count'] + row['Slot 3 Count']
        perk_4_sp = int(slot_3_count + 3)
        slot_4_perk_column = 'Perks ' + str(perk_4_sp)
        if pd.to_numeric(row['Slot 4 Count'], errors='coerce') >= 3:
            df.at[index, 'Slot 4 Perk 2'] = row[slot_4_perk_column]
        else:
            df.at[index, 'Slot 4 Perk 2'] = np.nan

    # Populate Slot 3 Perk 3 Columns
    for index, row in df.iterrows():
        slot_3_count = row['Slot 1 Count'] + row['Slot 2 Count'] + row['Slot 3 Count']
        perk_4_sp = int(slot_3_count + 4)
        slot_4_perk_column = 'Perks ' + str(perk_4_sp)
        if pd.to_numeric(row['Slot 4 Count'], errors='coerce') >= 4:
            df.at[index, 'Slot 4 Perk 3'] = row[slot_4_perk_column]
        else:
            df.at[index, 'Slot 4 Perk 3'] = np.nan

    # Drop Perk Columns
    df = df.drop(columns=['Perks 1', 'Perks 2', 'Perks 3', 'Perks 4', 'Perks 5', 'Perks 6', 'Perks 7',
                                            'Perks 8', 'Perks 9', 'Perks 10', 'Perks 11', 'Perks 12', 'Perks 13', 'Perks 14',
                                            'Perks 15', 'Perks 16', 'Perks 17','Total Perks', 'Slot 1 Count', 'Slot 2 Count',
                                            'Slot 3 Count', 'Slot 4 Count'])

    slot_columns = [column for column in df.columns if column.startswith('Slot')]
    id_vars = [column for column in df.columns if not column.startswith('Slot')]
    df = pd.melt(dim_weapon_data, id_vars=id_vars, value_vars=slot_columns, var_name='Slot', value_name='Perk')
    df = dim_perk_list.loc[dim_perk_list['Perk'].notnull()]
    dim_perk_list['Slot'] = dim_perk_list['Slot'].astype(str).str[:6]
    dim_perk_list['Grouped Slot'] = np.where(dim_perk_list['Slot'].isin(['Slot 3', 'Slot 4']), 'Slot 5', dim_perk_list['Slot'])
    dim_perk_list = dim_perk_list[['Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Hash', 'Weapon Tier',
                                   'Weapon Type', 'Weapon Archetype', 'Weapon Slot', 'Weapon Element', 'Weapon Current Version',
                                   'Weapon Power Cap', 'Is Sunset', 'Masterwork Type', 'Masterwork Tier', 'Crafted', 'Crafted Level',
                                   'Slot', 'Grouped Slot', 'Perk']]

    return df