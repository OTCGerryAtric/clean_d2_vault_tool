import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

from csv_processing import manifest_weapon_data
from csv_processing import load_dim_weapon_data
from csv_processing import load_dim_armor_data

def weapon_type_count(file):
    df = file.groupby('Weapon Type').agg({'Weapon Name': ['count', 'nunique']})
    df.columns = ['Total Count', 'Unique Count']
    df = df.reset_index().sort_values(by='Total Count', ascending=False)
    return df

def weapon_type_element_count(file):
    df = file.groupby(['Weapon Type', 'Weapon Element']).agg({'Weapon Name': ['count', 'nunique']})
    df.columns = ['Total Count', 'Unique Count']
    df = df.reset_index().sort_values(by=['Weapon Type', 'Weapon Element'])
    return df

def weapon_type_output_without_dim(manifest_weapon_data):
    df_merge = weapon_type_count(manifest_weapon_data)
    df_2 = weapon_type_element_count(manifest_weapon_data)

    weapon_elements = ['Kinetic', 'Stasis', 'Strand', 'Arc', 'Solar', 'Void']
    for element in weapon_elements:
        element_count_1 = df_2[df_2['Weapon Element'] == element].set_index('Weapon Type')['Unique Count']
        df_merge[element] = df_merge['Weapon Type'].apply(lambda x: '{}'.format(element_count_1.get(x, 0)))
    return df_merge

def weapon_type_output_with_dim(manifest_weapon_data, file):
    df_1 = weapon_type_count(manifest_weapon_data)
    df_2 = weapon_type_count(file)
    df_merge = pd.merge(df_2, df_1, on='Weapon Type', how='left')
    df_merge = df_merge.drop(columns=('Total Count_y'))
    df_merge = df_merge.rename(columns={'Total Count_x': 'Total Owned', 'Unique Count_x': 'Unique Owned', 'Unique Count_y': 'Unique Available'})
    df_3 = weapon_type_element_count(manifest_weapon_data)
    df_4 = weapon_type_element_count(file)

    weapon_elements = ['Kinetic', 'Stasis', 'Strand', 'Arc', 'Solar', 'Void']
    for element in weapon_elements:
        element_count_1 = df_4[df_4['Weapon Element'] == element].set_index('Weapon Type')['Unique Count']
        element_count_2 = df_3[df_3['Weapon Element'] == element].set_index('Weapon Type')['Unique Count']
        df_merge[element] = df_merge['Weapon Type'].apply(lambda x: '{} (of {})'.format(element_count_1.get(x, 0), element_count_2.get(x, 0)))
    return df_merge

import numpy as np

def armor_type_count(file):
    sort_order = ['Helmet', 'Gauntlets', 'Chest', 'Legs', 'Class Item']
    df = file.groupby(['Character', 'Type', 'Tier']).agg({'id': ['count']})
    df.columns = ['Total Count']
    df = df.reset_index()

    # Create a MultiIndex for the columns with 'Character' and 'Tier'
    df_pivot = df.pivot(index='Type', columns=('Character', 'Tier'), values='Total Count')
    df_pivot = df_pivot.reindex(sort_order)  # Sort the index column based on the sort_order list

    # Add row and column totals and transpose
    df_pivot['Total'] = df_pivot.sum(axis=1)  # Add row total column
    df_pivot.loc['Total'] = df_pivot.sum()  # Add column total row
    df_pivot = df_pivot.transpose()

    return df_pivot


def not_owned_list(manifest_weapon_data, dim_weapon_data):
    df_1 = dim_weapon_data['Weapon Name'].unique()
    df_2 = manifest_weapon_data[~manifest_weapon_data['Weapon Name'].isin(df_1)]['Weapon Name'].unique()
    return df_2

def owned_counted_list(dim_weapon_data):
    df = dim_weapon_data.groupby('Weapon Name').agg({'Weapon Name': ['count']})
    df.columns = ['Count']
    df = df.reset_index().sort_values(by='Count', ascending=False)
    return df

def load_weapon_type_data(file, selected_type):
    # Define first_cols
    first_cols = ['Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Hash', 'Weapon Tier', 'Weapon Type', 'Weapon Archetype', 'Weapon Slot', 'Weapon Element',
                  'Weapon Current Version', 'Weapon Power Cap', 'Is Sunset']

    type_1_list = pd.DataFrame(file, columns=['Impact', 'Range', 'Stability', 'Handling', 'Reload Speed', 'Aim Assistance', 'Zoom', 'Airborne Effectiveness', 'Recoil Direction', 'Rounds Per Minute', 'Magazine'])
    type_2_list = pd.DataFrame(file, columns=['Impact', 'Accuracy', 'Stability', 'Handling', 'Reload Speed', 'Aim Assistance', 'Zoom', 'Airborne Effectiveness', 'Recoil Direction', 'Draw Time'])
    type_3_list = pd.DataFrame(file, columns=['Impact', 'Range', 'Stability', 'Handling', 'Reload Speed', 'Aim Assistance', 'Zoom', 'Airborne Effectiveness', 'Recoil Direction', 'Charge Time', 'Magazine'])
    type_4_list = pd.DataFrame(file, columns=['Blast Radius', 'Velocity', 'Stability', 'Handling', 'Reload Speed', 'Aim Assistance', 'Zoom', 'Airborne Effectiveness', 'Recoil Direction', 'Rounds Per Minute',
                                              'Magazine'])
    type_5_list = pd.DataFrame(file, columns=['Impact', 'Range', 'Shield Duration', 'Handling', 'Reload Speed', 'Aim Assistance', 'Airborne Effectiveness', 'Rounds Per Minute', 'Charge Time', 'Magazine'])
    type_6_list = pd.DataFrame(file, columns=['Impact', 'Swing Speed', 'Guard Efficiency', 'Guard Resistance', 'Charge Rate', 'Ammo Capacity'])

    # Create Additional Filters for Weapon Type
    type_map = {
        'Auto Rifle': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Hand Cannon': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Machine Gun': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Pulse Rifle': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Scout Rifle': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Shotgun': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Sidearm': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Sniper Rifle': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Submachine Gun': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Trace Rifle': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Combat Bow': pd.concat([pd.DataFrame(file, columns=first_cols), type_2_list], axis=1),
        'Fusion Rifle': pd.concat([pd.DataFrame(file, columns=first_cols), type_3_list], axis=1),
        'Linear Fusion Rifle': pd.concat([pd.DataFrame(file, columns=first_cols), type_3_list], axis=1),
        'Grenade Launcher': pd.concat([pd.DataFrame(file, columns=first_cols), type_4_list], axis=1),
        'Rocket Launcher': pd.concat([pd.DataFrame(file, columns=first_cols), type_4_list], axis=1),
        'Glaive': pd.concat([pd.DataFrame(file, columns=first_cols), type_5_list], axis=1),
        'Sword': pd.concat([pd.DataFrame(file, columns=first_cols), type_6_list], axis=1),
    }

    # Return the selected type from the type_map dictionary
    return type_map[selected_type]

def create_grid_table(file, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset):
    # Set up the GridOptionsBuilder object
    gridOptionsBuilder = GridOptionsBuilder.from_dataframe(file)

    # Set first column as index
    gridOptionsBuilder.configure_first_column_as_index(headerText='Weapon Name (S)')

    # Add single select box
    gridOptionsBuilder.configure_selection(selection_mode='single', use_checkbox=True)

    # Hide Unneeded Columns
    gridOptionsBuilder.configure_column('Weapon Name', resizable=True, hide=True)
    gridOptionsBuilder.configure_column('Weapon Season', resizable=True, hide=True)
    gridOptionsBuilder.configure_column('Weapon Current Version', resizable=True, hide=True)
    gridOptionsBuilder.configure_column('Weapon Power Cap', resizable=True, hide=True)

    # Size Columns
    columns_to_configure = file
    for column in columns_to_configure:
        gridOptionsBuilder.configure_column(column, resizable=True, width=90)
    gridOptionsBuilder.configure_column('Weapon Name With Season', resizable=True, width=250)
    gridOptionsBuilder.configure_column('Weapon Hash', resizable=True, width=125)
    gridOptionsBuilder.configure_column('Weapon Tier', resizable=True, width=125)
    gridOptionsBuilder.configure_column('Weapon Type', resizable=True, width=125)
    gridOptionsBuilder.configure_column('Weapon Archetype', resizable=True, width=150)
    gridOptionsBuilder.configure_column('Weapon Slot', resizable=True, width=125)
    gridOptionsBuilder.configure_column('Weapon Element', resizable=True, width=135)

    # Hide columns where the filter is selected
    if len(selected_tier) == 1:
        gridOptionsBuilder.configure_column('Weapon Tier', resizable=True, hide=True)

    if selected_type != 'Select all':
        gridOptionsBuilder.configure_column('Weapon Type', resizable=True, hide=True)

    if selected_archetype != 'Select all':
        gridOptionsBuilder.configure_column('Weapon Archetype', resizable=True, hide=True)

    if selected_slot != 'Select all':
        gridOptionsBuilder.configure_column('Weapon Slot', resizable=True, hide=True)

    if selected_element != 'Select all':
        gridOptionsBuilder.configure_column('Weapon Element', resizable=True, hide=True)

    if selected_sunset == 'Yes':
        gridOptionsBuilder.configure_column('Is Sunset', resizable=True, hide=True)

    # Build and display the grid table
    gridOptions = gridOptionsBuilder.build()
    grid_table = AgGrid(file, gridOptions=gridOptions, height=400, theme='balham')
    # Return the grid table object
    return grid_table

def create_hyperlinks_v1(dataframe, grid_table, col1, col2, col3, col4):
    # Create hyperlink for light.gg
    try:
        hyperlink_df = dataframe[['Weapon Name', 'Weapon Hash']]
        sel_row_1 = grid_table.selected_rows
        selected_hash_1 = sel_row_1[0]["Weapon Hash"]
        hyperlink_df = hyperlink_df.loc[hyperlink_df['Weapon Hash'] == selected_hash_1]
        selected_name_1 = hyperlink_df['Weapon Name'].iloc[0]
        selected_url_1 = "https://www.light.gg/db/items/{}/{}".format(selected_hash_1, selected_name_1)
        hyperlink_text_1 = "Light.gg - {}".format(selected_name_1)
        link_text_1 = '[{}]({})'.format(hyperlink_text_1, selected_url_1.replace(' ', '%20'))
        # Use st.write to display the formatted hyperlink text
        col1.write(link_text_1, unsafe_allow_html=True)
    except Exception:
        col1.write('Select Weapon to see Light.gg link', unsafe_allow_html=True)

    # Create hyperlink for D2 Foundry
    try:
        hyperlink_df = dataframe[['Weapon Name', 'Weapon Hash']]
        sel_row_2 = grid_table.selected_rows
        selected_hash_2 = sel_row_2[0]["Weapon Hash"]
        hyperlink_df = hyperlink_df.loc[hyperlink_df['Weapon Hash'] == selected_hash_2]
        selected_name_2 = hyperlink_df['Weapon Name'].iloc[0]
        selected_url_2 = "https://d2foundry.gg/w/{}".format(selected_hash_2)
        hyperlink_text_2 = "D2 Foundry - {}".format(selected_name_2)
        link_text_2 = '[{}]({})'.format(hyperlink_text_2, selected_url_2.replace(' ', '%20'))
        # Use st.write to display the formatted hyperlink text
        col2.write(link_text_2, unsafe_allow_html=True)
    except Exception:
        col2.write('Select Weapon to see D2 Foundry link', unsafe_allow_html=True)

    # Create hyperlink for DIM
    try:
        selected_url_3 = "https://app.destinyitemmanager.com/"
        link_text_3 = 'Destiny Item Manager (DIM)'
        # Use st.write to display the formatted hyperlink text
        col3.write(f'<a href="{selected_url_3}" target="_blank">{link_text_3}</a>', unsafe_allow_html=True)
    except Exception:
        pass

    # Create hyperlink for DIM Beta
    try:
        selected_url_4 = "https://beta.destinyitemmanager.com/"
        link_text_4 = 'BETA - Destiny Item Manager (DIM)'
        # Use st.write to display the formatted hyperlink text
        col4.write(f'<a href="{selected_url_4}" target="_blank">{link_text_4}</a>', unsafe_allow_html=True)
    except Exception:
        pass

def create_hyperlinks_v2(dataframe, grid_table, col5):
    # Create hyperlink for light.gg
    try:
        hyperlink_df = dataframe[['Weapon Name', 'Weapon Hash']]
        sel_row_1 = grid_table.selected_rows
        selected_hash_1 = sel_row_1[0]["Weapon Hash"]
        hyperlink_df = hyperlink_df.loc[hyperlink_df['Weapon Hash'] == selected_hash_1]
        selected_name_1 = hyperlink_df['Weapon Name'].iloc[0]
        selected_url_1 = "https://www.light.gg/db/items/{}/{}".format(selected_hash_1, selected_name_1)
        hyperlink_text_1 = "Light.gg - {}".format(selected_name_1)
        link_text_1 = '[{}]({})'.format(hyperlink_text_1, selected_url_1.replace(' ', '%20'))
        # Use st.write to display the formatted hyperlink text
        col5.write(link_text_1, unsafe_allow_html=True)
    except Exception:
        col5.write('Select Weapon to see Light.gg link', unsafe_allow_html=True)

    # Create hyperlink for D2 Foundry
    try:
        hyperlink_df = dataframe[['Weapon Name', 'Weapon Hash']]
        sel_row_2 = grid_table.selected_rows
        selected_hash_2 = sel_row_2[0]["Weapon Hash"]
        hyperlink_df = hyperlink_df.loc[hyperlink_df['Weapon Hash'] == selected_hash_2]
        selected_name_2 = hyperlink_df['Weapon Name'].iloc[0]
        selected_url_2 = "https://d2foundry.gg/w/{}".format(selected_hash_2)
        hyperlink_text_2 = "D2 Foundry - {}".format(selected_name_2)
        link_text_2 = '[{}]({})'.format(hyperlink_text_2, selected_url_2.replace(' ', '%20'))
        # Use st.write to display the formatted hyperlink text
        col5.write(link_text_2, unsafe_allow_html=True)
    except Exception:
        col5.write('Select Weapon to see D2 Foundry link', unsafe_allow_html=True)

    # Create hyperlink for DIM
    try:
        selected_url_3 = "https://app.destinyitemmanager.com/"
        link_text_3 = 'Destiny Item Manager (DIM)'
        # Use st.write to display the formatted hyperlink text
        col5.write(f'<a href="{selected_url_3}" target="_blank">{link_text_3}</a>', unsafe_allow_html=True)
    except Exception:
        pass

    # Create hyperlink for DIM Beta
    try:
        selected_url_4 = "https://beta.destinyitemmanager.com/"
        link_text_4 = 'BETA - Destiny Item Manager (DIM)'
        # Use st.write to display the formatted hyperlink text
        col5.write(f'<a href="{selected_url_4}" target="_blank">{link_text_4}</a>', unsafe_allow_html=True)
    except Exception:
        pass