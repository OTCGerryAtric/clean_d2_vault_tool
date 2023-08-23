import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from typing import Any

# Set Page Config
st.set_page_config(page_title="Destiny 2 Vault Tool", page_icon=None, layout="wide", initial_sidebar_state="expanded",
                   menu_items=None)

# Define Session State
class SessionState:
    def __init__(self, **kwargs: Any):
        self.__dict__.update(kwargs)

# Load Manifest Data
from csv_processing import manifest_weapon_data


# Define Navigation Bar
def navigation():
    st.sidebar.title('Navigation')
    selection = st.sidebar.selectbox("Go to",
                                     ['Home', 'Vault Summary', 'Weapon Analysis', 'Weapon Comparison', 'Weapon Perks',
                                      'Build Tool'])
    return selection


# Define Filters
def apply_all_filters(df, selected_tier, selected_type, selected_archetype, selected_slot, selected_element,
                      selected_sunset):
    # Apply filters here
    if len(selected_tier) > 0:
        df = df.loc[df['Weapon Tier'].isin(selected_tier)]
    if selected_type != 'Select all':
        df = df.loc[df['Weapon Type'] == selected_type]
    if selected_archetype != 'Select all':
        df = df.loc[df['Weapon Archetype'] == selected_archetype]
    if selected_slot != 'Select all':
        df = df.loc[df['Weapon Slot'] == selected_slot]
    if selected_element != 'Select all':
        df = df.loc[df['Weapon Element'] == selected_element]
    if selected_sunset == 'Yes':
        df = df.loc[df['Is Sunset'] == 'No']
    if selected_sunset == 'Yes':
        df = df.loc[df['Is Sunset'] == 'No']
    return df

def apply_reduced_filters(df, selected_tier, selected_sunset):
    # Apply filters here
    if len(selected_tier) > 0:
        df = df.loc[df['Weapon Tier'].isin(selected_tier)]
    if selected_sunset == 'Yes':
        df = df.loc[df['Is Sunset'] == 'No']
    return df

def weapon_type_filter(manifest_weapon_data, selected_tier):
    if len(selected_tier) > 0:
        weapon_type_filter_df = sorted(
            manifest_weapon_data[manifest_weapon_data['Weapon Tier'].isin(selected_tier)]['Weapon Type'].unique())
    else:
        weapon_type_filter_df = sorted(manifest_weapon_data['Weapon Type'].unique())
    return weapon_type_filter_df

def weapon_archetype_filter(manifest_weapon_data, selected_tier, selected_type):
    if len(selected_tier) > 0 and selected_type != 'Select all':
        weapon_archetype_filter_df = sorted(
            manifest_weapon_data[(manifest_weapon_data['Weapon Tier'].isin(selected_tier)) &
                                 (manifest_weapon_data['Weapon Type'] == selected_type)]['Weapon Archetype'].unique())
    elif len(selected_tier) > 0:
        weapon_archetype_filter_df = sorted(
            manifest_weapon_data[manifest_weapon_data['Weapon Tier'].isin(selected_tier)]['Weapon Archetype'].unique())
    elif selected_type != 'Select all':
        weapon_archetype_filter_df = sorted(
            manifest_weapon_data[manifest_weapon_data['Weapon Type'] == selected_type]['Weapon Archetype'].unique())
    else:
        weapon_archetype_filter_df = sorted(manifest_weapon_data['Weapon Archetype'].unique())
    return weapon_archetype_filter_df

def weapon_slot_filter(manifest_weapon_data, selected_tier, selected_type, selected_archetype):
    if len(selected_tier) > 0 and selected_type != 'Select all' and selected_archetype != 'Select all':
        weapon_slot_filter_df = sorted(manifest_weapon_data[(manifest_weapon_data['Weapon Tier'].isin(selected_tier)) &
                                                            (manifest_weapon_data['Weapon Type'] == selected_type) &
                                                            (manifest_weapon_data[
                                                                 'Weapon Archetype'] == selected_archetype)][
                                           'Weapon Slot'].unique())
    elif len(selected_tier) > 0 and selected_type != 'Select all':
        weapon_slot_filter_df = sorted(manifest_weapon_data[(manifest_weapon_data['Weapon Tier'].isin(selected_tier)) &
                                                            (manifest_weapon_data['Weapon Type'] == selected_type)][
                                           'Weapon Slot'].unique())
    elif len(selected_tier) > 0 and selected_archetype != 'Select all':
        weapon_slot_filter_df = sorted(manifest_weapon_data[(manifest_weapon_data['Weapon Tier'].isin(selected_tier)) &
                                                            (manifest_weapon_data[
                                                                 'Weapon Archetype'] == selected_archetype)][
                                           'Weapon Slot'].unique())
    elif selected_type != 'Select all' and selected_archetype != 'Select all':
        weapon_slot_filter_df = sorted(manifest_weapon_data[(manifest_weapon_data['Weapon Type'] == selected_type) &
                                                            (manifest_weapon_data[
                                                                 'Weapon Archetype'] == selected_archetype)][
                                           'Weapon Slot'].unique())
    elif selected_type != 'Select all':
        weapon_slot_filter_df = sorted(
            manifest_weapon_data[manifest_weapon_data['Weapon Type'] == selected_type]['Weapon Slot'].unique())
    elif selected_archetype != 'Select all':
        weapon_slot_filter_df = sorted(
            manifest_weapon_data[manifest_weapon_data['Weapon Archetype'] == selected_archetype][
                'Weapon Slot'].unique())
    elif len(selected_tier) > 0:
        weapon_slot_filter_df = sorted(
            manifest_weapon_data[manifest_weapon_data['Weapon Tier'].isin(selected_tier)]['Weapon Slot'].unique())
    else:
        weapon_slot_filter_df = sorted(manifest_weapon_data['Weapon Slot'].unique())
    return weapon_slot_filter_df


def weapon_element_filter(manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot):
    if len(selected_tier) > 0:
        weapon_element_filter_df = manifest_weapon_data[
            manifest_weapon_data['Weapon Tier'].isin(selected_tier)]
    else:
        weapon_element_filter_df = manifest_weapon_data.copy()

    if selected_type != 'Select all':
        weapon_element_filter_df = weapon_element_filter_df.loc[
            weapon_element_filter_df['Weapon Type'] == selected_type]
    if selected_archetype != 'Select all':
        weapon_element_filter_df = weapon_element_filter_df.loc[
            weapon_element_filter_df['Weapon Archetype'] == selected_archetype]
    if selected_slot != 'Select all':
        weapon_element_filter_df = weapon_element_filter_df.loc[
            weapon_element_filter_df['Weapon Slot'] == selected_slot]

    weapon_element_filter_df = sorted(weapon_element_filter_df['Weapon Element'].unique())

    return weapon_element_filter_df


def sidebar():
    # Set Up Unique Non Dependant Lists
    unique_tier = ['Exotic', 'Legendary', 'Rare', 'Common', 'Basic']  # Free Choice
    selected_tier = st.sidebar.multiselect('Select Tiers', unique_tier, default=unique_tier[1],
                                           help='Select the Tiers to Look At. Can Select Multiple. Select None For All')

    unique_type = weapon_type_filter(manifest_weapon_data, selected_tier)
    unique_type.insert(0, 'Select all')
    selected_type = st.sidebar.selectbox('Select a Type', unique_type,
                                         help="Select the Weapon Type. Can Only Select One As The Stats Categories by Weapon Type. 'Select All' To See Full Weapon List")

    unique_archetype = weapon_archetype_filter(manifest_weapon_data, selected_tier, selected_type)
    unique_archetype.insert(0, 'Select all')
    selected_archetype = st.sidebar.selectbox('Select an Archetype', unique_archetype, help='Select Weapon Archetype')

    unique_slot = weapon_slot_filter(manifest_weapon_data, selected_tier, selected_type, selected_archetype)
    unique_slot.insert(0, 'Select all')
    selected_slot = st.sidebar.selectbox('Select a Weapon Slot', unique_slot, help="Select the Weapon Slot")

    unique_element = weapon_element_filter(manifest_weapon_data, selected_tier, selected_type, selected_archetype,
                                           selected_slot)
    unique_element.insert(0, 'Select all')
    selected_element = st.sidebar.selectbox('Select an Element', unique_element,
                                            help='Select the Elements to Look At. Can Select Multiple. Select None For All')

    exclude_sunset = ['Yes', 'No']
    selected_sunset = st.sidebar.selectbox('Exclude Sunset Weapons', exclude_sunset, index=0,
                                           help='Include or Exclude Sunset Weapons')

    return selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset


def main():
    # Setup Session States
    session_state = SessionState(dim_weapon_data=None, dim_armor_data=None)

    # Setup DIM Uploads
    from csv_processing import load_dim_weapon_data, load_dim_armor_data

    # Setup DIM Uploads
    with st.expander('DIM File Uploader', expanded=False):
        col1, col2 = st.columns([1, 1])
        uploaded_weapon_file = col1.file_uploader("DIM Weapon Uploader", type="csv")
        if uploaded_weapon_file is not None:
            session_state.dim_weapon_data = load_dim_weapon_data(uploaded_weapon_file, manifest_weapon_data)
        uploaded_armor_file = col2.file_uploader("DIM Armor Uploader", type="csv")
        if uploaded_armor_file is not None:
            session_state.dim_armor_data = load_dim_armor_data(uploaded_armor_file)

    # Determine the selected page based on navigation
    selection = navigation()

    # Add a Filter Title in the Sidebar
    st.sidebar.title('Filters')

    # Setup Sidebar Filters
    selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset = sidebar()

    # Define the page functions
    def home_page(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot,
                  selected_element, selected_sunset):
        st.title('Home Page')

        # Set up columns for multiselect
        col1, col2, col3, col4, col5 = st.columns(5)

        # Create hyperlink for DIM
        selected_url_1 = "https://www.bungie.net/7/en/Destiny"
        link_text_1 = "Register with Bungie (if you haven't already)"
        # Use st.write to display the formatted hyperlink text
        col1.write(f'<a href="{selected_url_1}" target="_blank">{link_text_1}</a>', unsafe_allow_html=True)

        # Create hyperlink for DIM
        selected_url_2 = "https://app.destinyitemmanager.com/settings"
        link_text_2 = 'Where to download DIM Data'
        # Use st.write to display the formatted hyperlink text
        col2.write(f'<a href="{selected_url_2}" target="_blank">{link_text_2}</a>', unsafe_allow_html=True)

        # Create hyperlink for DIM Beta
        selected_url_3 = "https://beta.destinyitemmanager.com/settings"
        link_text_3 = 'Where to download DIM Data (BETA)'
        # Use st.write to display the formatted hyperlink text
        col3.write(f'<a href="{selected_url_3}" target="_blank">{link_text_3}</a>', unsafe_allow_html=True)

        # Create hyperlink for DIM Beta
        selected_url_4 = "https://www.light.gg/"
        link_text_4 = 'Light.gg'
        # Use st.write to display the formatted hyperlink text
        col4.write(f'<a href="{selected_url_4}" target="_blank">{link_text_4}</a>', unsafe_allow_html=True)

        # Create hyperlink for DIM Beta
        selected_url_5 = "https://d2foundry.gg/"
        link_text_5 = 'D2Foundry'
        # Use st.write to display the formatted hyperlink text
        col5.write(f'<a href="{selected_url_5}" target="_blank">{link_text_5}</a>', unsafe_allow_html=True)

        with st.expander('How To Use', expanded=False):
            st.write(
                'There are many amazing resources for Destiny 2, but I always hoard too many weapons and armour (sorry, from the UK!!)')
            st.write('')
            st.write('')
            st.write(
                'For that reason (and to learn coding) I put this together to be able to easily take a look at what you own and use other resources to see what to keep / shard')
            st.write('')
            st.write('')
            st.write('There are 4 screens that you can use to help, which are,')
            st.write('   1. Vault Summary - Look at Weapons / Armour that you own - https://youtu.be/hqw8e7br-Zg')
            st.write('   2. Weapon Analysis - Weapons Database with and one click to D2 Foundry and Light.gg - https://youtu.be/9sbJda9ByQ8')
            st.write('   3. Weapon Comparison - Compare a weapon to others - https://youtu.be/ZTOvZJ3k8hs')
            st.write('   4. Weapon Perks - Look for Perk Combinations - https://youtu.be/4WfAhQCYK3Y')
            st.write('')
            st.write(
                "I've done a few videos (links above), but these are the things to do first, if you want to use everything")
            st.write('')
            st.write(
                "   1. Make sure you are registered with Bungie (link above). Click on 'My Account', then 'Join Up'")
            st.write('   2. Sign in to the excellent Destiny Item Manager (DIM) (links above)')
            st.write('   3. Download Files from DIM - https://youtu.be/spEjSFjn9RE')
            st.write('   3. Sign in to the also excellent light.gg (links above)')
            st.write(
                "   4. Just want to also mention D2foundry.gg. You don't need to sign in, but this site is amazing")
            st.write('')
            st.write('Once this is all done, then click on the DIM links and download Weapon and Armor CSV files')
            st.write('')
            st.write('Finally, click on the DIM File Uploader at the top of the file and upload the two files')
            st.write('')
            st.write("This really doesn't take long, I promise!")

        with st.expander('About Me', expanded=False):
            st.write('Destiny player since the start. Gamer tag is OTC Gerry Atric, part of The Iron Wolves clan, and can be found regularly failing jumping puzzles on Xbox. Also on Twitter.')
            st.write('Any suggestions / feedback, please let me know. I hope you find it useful.')

    def vault_summary(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype,
                      selected_slot, selected_element, selected_sunset):
        st.title('Vault Summary')

        # Import Required Functions
        from data_preperation import weapon_type_output_without_dim, weapon_type_output_with_dim, load_dim_weapon_data, \
            owned_counted_list, not_owned_list, armor_type_count

        # Setup Overall Metrics
        col1, col2, col3, col4 = st.columns([4, 4, 4, 6])

        # Setup DIM Weapon Data, if uploaded
        if uploaded_weapon_file is not None:
            dim_weapon_data_2 = session_state.dim_weapon_data
            dim_weapon_data_3 = session_state.dim_weapon_data

        # Populate Col 1 Metric
        if uploaded_weapon_file is not None:
            col1.metric(label='Total Weapons Owned', value=len(session_state.dim_weapon_data),
                        help='Count Of All Weapons Owned')
        else:
            col1.metric(label='Total Weapons Owned', value='Load DIM Data', help='Count Of All Weapons Owned')

        # Populate Col 2 Metric
        if uploaded_armor_file is not None:
            col2.metric(label='Total Armor Pieces Owned', value=len(session_state.dim_armor_data),
                        help='Count Of All Armor Owned')
        else:
            col2.metric(label='Total Armor Pieces Owned', value='Load DIM Data', help='Count Of All Armor Owned')

        # Populate Col 3 Metric
        if uploaded_weapon_file and uploaded_armor_file is not None:
            col3.metric(label='Total Items Owned',
                        value=len(session_state.dim_weapon_data) + len(session_state.dim_armor_data),
                        help='Total Item Count')
        else:
            col3.metric(label='Total Items Owned', value='Load DIM Data', help='Total Item Count')

        with st.expander('Weapon Details', expanded=True):

            # Set up columns for multiselect
            col1, col2, col3 = st.columns([12, 4, 4])

            # Setup Weapon Details
            if uploaded_weapon_file is not None:
                dim_weapon_data = apply_reduced_filters(session_state.dim_weapon_data, selected_tier, selected_sunset)
                filtered_manifest_weapon_data = apply_reduced_filters(manifest_weapon_data, selected_tier,
                                                                      selected_sunset)
                filtered_manifest_weapon_data = weapon_type_output_with_dim(filtered_manifest_weapon_data,
                                                                            dim_weapon_data)
                col1.write('Weapons Available (with owned count)')
                col1.dataframe(filtered_manifest_weapon_data, use_container_width=True)
            else:
                filtered_manifest_weapon_data = apply_reduced_filters(manifest_weapon_data, selected_tier,
                                                                      selected_sunset)
                filtered_manifest_weapon_data = weapon_type_output_without_dim(filtered_manifest_weapon_data)
                col1.write('Available Weapons (upload DIM file to show owned)')
                col1.dataframe(filtered_manifest_weapon_data, use_container_width=True)

            # Setup Weapon Owned
            if uploaded_weapon_file is not None:
                dim_weapon_data_2 = apply_all_filters(dim_weapon_data_2, selected_tier, selected_type,
                                                      selected_archetype, selected_slot, selected_element,
                                                      selected_sunset)
                dim_weapon_data_2 = owned_counted_list(dim_weapon_data_2)
                dim_weapon_data_2 = dim_weapon_data_2.reset_index(drop=True)  # Reset the index
                col2.write('Weapons Owned (with count)')
                col2.dataframe(dim_weapon_data_2, use_container_width=True)
            else:
                col2.write('Upload DIM Weapon Data')

            # Setup Missing Weapon Details
            if uploaded_weapon_file is not None:
                dim_weapon_data_3 = apply_all_filters(dim_weapon_data_3, selected_tier, selected_type,
                                                      selected_archetype, selected_slot, selected_element,
                                                      selected_sunset)
                filtered_manifest_weapon_data_2 = apply_all_filters(manifest_weapon_data, selected_tier, selected_type,
                                                                    selected_archetype, selected_slot, selected_element,
                                                                    selected_sunset)
                dim_weapon_data_3 = not_owned_list(filtered_manifest_weapon_data_2, dim_weapon_data_3)
                dim_weapon_data_3 = pd.DataFrame(dim_weapon_data_3, columns=['Weapon Name'])
                col3.write('Weapons Not Owned')
                col3.dataframe(dim_weapon_data_3, use_container_width=True)
            else:
                filtered_manifest_weapon_data_2 = apply_all_filters(manifest_weapon_data, selected_tier, selected_type,
                                                                    selected_archetype, selected_slot, selected_element,
                                                                    selected_sunset)
                filtered_manifest_weapon_data_2 = filtered_manifest_weapon_data_2['Weapon Name']
                col3.write('All Weapons (Upload DIM Data)')
                col3.dataframe(filtered_manifest_weapon_data_2, use_container_width=True)

        # Setup Armor Section
        with st.expander('Armor Details', expanded=False):

            # Set up columns for multiselect
            col1, col2 = st.columns([10, 2])

            if uploaded_armor_file is not None:
                dim_armor_data = armor_type_count(session_state.dim_armor_data)
                col1.write('Armor, by Type, Character and Tier')
                col1.dataframe(dim_armor_data, use_container_width=True)
            else:
                pass

    def weapon_analysis(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype,
                        selected_slot, selected_element, selected_sunset):
        st.title('Weapon Analysis')

        # Import functions
        from data_preperation import load_weapon_type_data, create_grid_table, create_hyperlinks_v1

        # Set up data from and apply sidebar filter
        manifest_data_filtered_pg2 = apply_all_filters(manifest_weapon_data, selected_tier, selected_type,
                                                       selected_archetype, selected_slot, selected_element,
                                                       selected_sunset)

        if uploaded_weapon_file is not None:
            dim_weapon_filtered_data = apply_all_filters(session_state.dim_weapon_data, selected_tier, selected_type,
                                                         selected_archetype, selected_slot, selected_element,
                                                         selected_sunset)

        # Set up counts
        unique_filtered_manifest_weapons_count = manifest_data_filtered_pg2[['Weapon Name', 'Weapon Power Cap']]
        unique_filtered_manifest_weapons_count = unique_filtered_manifest_weapons_count.drop_duplicates()
        unique_filtered_manifest_weapons_count = len(unique_filtered_manifest_weapons_count)

        # Set up DIM counts
        if uploaded_weapon_file is not None:
            dim_total_weapons_owned = len(dim_weapon_filtered_data)
            dim_total_unique_weapons_owned = dim_weapon_filtered_data[['Weapon Name', 'Weapon Power Cap']]
            dim_total_unique_weapons_owned = len(dim_total_unique_weapons_owned.drop_duplicates())
            dim_weapon_unique_count = dim_weapon_filtered_data[['Weapon Name', 'Weapon Power Cap']]
            dim_weapon_unique_count = len(dim_weapon_unique_count.drop_duplicates())
        else:
            pass

        with st.expander('Weapon Summary', expanded=True):
            # Set up columns for multiselect
            col1, col2, col3, col4, col5 = st.columns(5)

            # Set up counts
            try:
                col1.metric(label='Total Weapons Owned', value=format(dim_total_weapons_owned, ','),
                            help='Count Of All Weapons Owned')
            except Exception:
                col1.metric(label='Total Weapons Owned', value='Upload DIM Data', help='Count Of All Weapons Owned')

            try:
                col2.metric(label='Unique Weapons Owned', value=format(dim_total_unique_weapons_owned, ','),
                            help='Count of Unique Weapons. Excludes Duplicates Where Weapons Share Same Name And Power Cap, e.g. Dark Decider')
            except Exception:
                col2.metric(label='Unique Weapons Owned', value='Upload DIM Data',
                            help='Count of Unique Weapons. Excludes Duplicates Where Weapons Share Same Name And Power Cap, e.g. Dark Decider')

            try:
                col3.metric(label='Unique Weapons Available (Filtered)',
                            value=format(unique_filtered_manifest_weapons_count, ','),
                            help='Count Of Weapons Available (Filtered)')
            except Exception:
                pass

            try:
                col4.metric(label='Unique Weapons Owned (Filtered)', value=format(dim_weapon_unique_count, ','),
                            help='Count of Unique Weapons. Excludes Duplicates Where Weapons Share Same Name And Power Cap')
            except Exception:
                col4.metric(label='Unique Weapons Owned (Filtered)', value='Upload DIM Data',
                            help='Count of Unique Weapons. Excludes Duplicates Where Weapons Share Same Name And Power Cap')

            try:
                col5.metric(label='% Filtered Weapons Owned',
                            value=f"{round((dim_weapon_unique_count * 100 / unique_filtered_manifest_weapons_count), 1)}%",
                            help='Percentage of Weapons Owned')
            except Exception:
                col5.metric(label='% Filtered Weapons Owned', value='Upload DIM Data',
                            help='Percentage of Weapons Owned')

        with st.expander('Weapon Database', expanded=True):
            # Set up columns for multiselect
            col1, col2, col3, col4, col5 = st.columns(5)

            # Create table, based on selected weapon type
            if selected_type != 'Select all':
                manifest_data_filtered_pg2 = load_weapon_type_data(manifest_data_filtered_pg2, selected_type)
            else:
                manifest_data_filtered_pg2 = manifest_data_filtered_pg2[
                    ['Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Hash', 'Weapon Tier',
                     'Weapon Type', 'Weapon Archetype',
                     'Weapon Slot', 'Weapon Element', 'Weapon Current Version', 'Weapon Power Cap', 'Is Sunset']]

            if uploaded_weapon_file is not None:
                weapon_count = session_state.dim_weapon_data.groupby('Weapon Hash').size().reset_index(name='count')
                manifest_data_filtered_pg2 = manifest_data_filtered_pg2.merge(weapon_count, on='Weapon Hash',
                                                                              how='left')
                manifest_data_filtered_pg2.insert(1, 'Count', manifest_data_filtered_pg2.pop('count'))

            # Create table
            grid_table = create_grid_table(manifest_data_filtered_pg2, selected_tier, selected_type, selected_archetype,
                                           selected_slot, selected_element, selected_sunset)

            # Create hyperlinks
            create_hyperlinks_v1(manifest_data_filtered_pg2, grid_table, col1, col2, col3, col4)

    def weapon_comparison(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype,
                          selected_slot, selected_element, selected_sunset):
        st.title('Weapon Comparison')

        # Import functions
        from data_preperation import load_weapon_type_data, create_grid_table, create_hyperlinks_v2

        # Set up data from and apply sidebar filter
        manifest_data_filtered_pg3 = apply_all_filters(manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset)

        # Set up columns for multiselect
        col1, col2, col3, col4, col5 = st.columns([2, 2, 4, 2, 2])

        # Select Season
        season_list = sorted(manifest_data_filtered_pg3['Weapon Season'].unique(), reverse=True)
        season_list.insert(0, 'Select all')
        selected_season = col1.selectbox('Select Season To Filter Weapons For Comparison', season_list)

        # Set up Weapon Comparator List
        if selected_season == 'Select all':
            weapon_name_list = sorted(manifest_data_filtered_pg3['Weapon Name With Season'].unique())
            weapon_selected_name = col2.selectbox('Select Weapon For Comparison', weapon_name_list)
        else:
            pg3_name_list = manifest_data_filtered_pg3.loc[manifest_data_filtered_pg3['Weapon Season'] == selected_season]
            weapon_name_list = sorted(pg3_name_list['Weapon Name With Season'].unique())
            weapon_selected_name = col2.selectbox('Select Weapon For Comparison', weapon_name_list)

        # Update Sidebar
        comparison_weapon_type = manifest_weapon_data.loc[manifest_weapon_data['Weapon Name With Season'] == weapon_selected_name, 'Weapon Type'].iloc[0]
        comparison_weapon_archetype = manifest_weapon_data.loc[manifest_weapon_data['Weapon Name With Season'] == weapon_selected_name, 'Weapon Archetype'].iloc[0]
        manifest_data_filtered_pg3 = manifest_data_filtered_pg3.loc[manifest_data_filtered_pg3['Weapon Type'] == comparison_weapon_type]
        manifest_data_filtered_pg3 = manifest_data_filtered_pg3.loc[manifest_data_filtered_pg3['Weapon Archetype'] == comparison_weapon_archetype]

        # Create List for Comparison
        weapon_list = sorted(manifest_data_filtered_pg3['Weapon Name With Season'].unique())
        if weapon_selected_name in weapon_name_list:
            weapon_list.remove(weapon_selected_name)
        weapon_compare_list = col3.multiselect('Select Weapon To Compare', weapon_list)

        # Set up comparison type
        comparison_type = col4.selectbox('Choose The Type Of Comparison', ['Absolute', 'Relative'])

        # Create DataFrame
        if len(weapon_compare_list) > 0:
            comparison_df = manifest_data_filtered_pg3.loc[
                manifest_data_filtered_pg3['Weapon Name With Season'].isin(weapon_compare_list)]
        else:
            comparison_df = manifest_data_filtered_pg3
            comparison_df = comparison_df[comparison_df['Weapon Name With Season'] != weapon_selected_name]

        filtered_df = manifest_data_filtered_pg3.loc[
            manifest_data_filtered_pg3['Weapon Name With Season'] == weapon_selected_name]

        # Clean Up Database
        printing_df = pd.concat([filtered_df, comparison_df], ignore_index=True)

        # Create table, based on selected weapon type
        if comparison_weapon_type != 'Select all':
            printing_df = load_weapon_type_data(printing_df, comparison_weapon_type)
        else:
            printing_df = printing_df[
                ['Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Hash', 'Weapon Tier', 'Weapon Type',
                 'Weapon Archetype', 'Weapon Slot',
                 'Weapon Element', 'Weapon Current Version', 'Weapon Power Cap', 'Is Sunset']]

        if comparison_type == 'Relative':
            if comparison_weapon_type == 'Grenade Launcher' or selected_type == 'Rocket Launcher':
                first_index = printing_df.columns.get_loc("Blast Radius")
            else:
                first_index = printing_df.columns.get_loc("Impact")
            for col in printing_df.iloc[:, first_index:].columns:
                # subtract the first row value from the subsequent rows and store in new column
                printing_df.loc[1:, col] = printing_df.loc[1:, col] - printing_df.loc[0, col]
        else:
            pass

        with st.expander('Weapon Comparison', expanded=True):
            if uploaded_weapon_file is not None:
                weapon_count = session_state.dim_weapon_data.groupby('Weapon Hash').size().reset_index(name='count')
                printing_df = printing_df.merge(weapon_count, on='Weapon Hash', how='left')
                printing_df.insert(1, 'Count', printing_df.pop('count'))

            # Create table
            grid_table = create_grid_table(printing_df, selected_tier, selected_type, selected_archetype, selected_slot,
                                           selected_element, selected_sunset)

        # Create hyperlinks
        create_hyperlinks_v2(printing_df, grid_table, col5)

    def weapon_perks(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype,
                     selected_slot, selected_element, selected_sunset):
        st.title('Weapon Perks')

        # Import functions
        from data_preperation import load_weapon_type_data, create_grid_table, create_hyperlinks_v2

        # Set up data from and apply sidebar filter
        manifest_data_filtered_pg4 = apply_all_filters(manifest_weapon_data, selected_tier, selected_type,
                                                       selected_archetype, selected_slot, selected_element,
                                                       selected_sunset)

        # Set up columns for multiselect
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])

        # Search for Slot 3 Selection
        slot3_cols = manifest_data_filtered_pg4.filter(regex='^Slot 3').columns
        slot3_perks = sorted(manifest_data_filtered_pg4.filter(regex='^Slot 3').stack().unique())
        slot_3 = col1.multiselect('Select Perk(s) in Slot 3', slot3_perks)
        if len(slot_3) > 0:
            slot_3_list = manifest_data_filtered_pg4[slot3_cols].apply(
                lambda x: any(item in x.values for item in slot_3), axis=1)
            manifest_data_filtered_pg4 = manifest_data_filtered_pg4.loc[slot_3_list]
        slot_3_count = col1.metric('Filtered Data Count', len(manifest_data_filtered_pg4))

        # Search for Slot 4 Selection
        slot4_cols = manifest_data_filtered_pg4.filter(regex='^Slot 4').columns
        slot4_perks = sorted(manifest_data_filtered_pg4.filter(regex='^Slot 4').stack().unique())
        slot_4 = col2.multiselect('Select Perk(s) in Slot 4', slot4_perks)
        if len(slot_4) > 0:
            slot_4_list = manifest_data_filtered_pg4[slot4_cols].apply(
                lambda x: any(item in x.values for item in slot_4), axis=1)
            manifest_data_filtered_pg4 = manifest_data_filtered_pg4.loc[slot_4_list]
        slot_4_count = col2.metric('Filtered Data Count', len(manifest_data_filtered_pg4))

        # Search for Slot 2 Selection
        slot2_cols = manifest_data_filtered_pg4.filter(regex='^Slot 2').columns
        slot2_perks = sorted(manifest_data_filtered_pg4.filter(regex='^Slot 2').stack().unique())
        slot_2 = col3.multiselect('Select Perk(s) in Slot 2', slot2_perks)
        if len(slot_2) > 0:
            slot_2_list = manifest_data_filtered_pg4[slot2_cols].apply(
                lambda x: any(item in x.values for item in slot_2), axis=1)
            manifest_data_filtered_pg4 = manifest_data_filtered_pg4.loc[slot_2_list]
        slot_2_count = col3.metric('Filtered Data Count', len(manifest_data_filtered_pg4))

        # Search for Slot 1 Selection
        slot1_cols = manifest_data_filtered_pg4.filter(regex='^Slot 1').columns
        slot1_perks = sorted(manifest_data_filtered_pg4.filter(regex='^Slot 1').stack().unique())
        slot_1 = col4.multiselect('Select Perk(s) in Slot 1', slot1_perks)
        if len(slot_1) > 0:
            slot_1_list = manifest_data_filtered_pg4[slot1_cols].apply(
                lambda x: any(item in x.values for item in slot_1), axis=1)
            manifest_data_filtered_pg4 = manifest_data_filtered_pg4.loc[slot_1_list]
        slot_1_count = col4.metric('Filtered Data Count', len(manifest_data_filtered_pg4))

        # Create table, based on selected weapon type
        if selected_type != 'Select all':
            manifest_data_filtered_pg4 = load_weapon_type_data(manifest_data_filtered_pg4, selected_type)
        else:
            manifest_data_filtered_pg4 = manifest_data_filtered_pg4[
                ['Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Hash', 'Weapon Tier', 'Weapon Type',
                 'Weapon Archetype', 'Weapon Slot',
                 'Weapon Element', 'Weapon Current Version', 'Weapon Power Cap', 'Is Sunset']]

        if uploaded_weapon_file is not None:
            weapon_count = session_state.dim_weapon_data.groupby('Weapon Hash').size().reset_index(name='count')
            manifest_data_filtered_pg4 = manifest_data_filtered_pg4.merge(weapon_count, on='Weapon Hash', how='left')
            manifest_data_filtered_pg4.insert(1, 'Count', manifest_data_filtered_pg4.pop('count'))

        with st.expander('Available Weapons', expanded=True):

            # Create table
            grid_table = create_grid_table(manifest_data_filtered_pg4, selected_tier, selected_type, selected_archetype,
                                           selected_slot, selected_element, selected_sunset)

            # Create hyperlinks
            create_hyperlinks_v2(manifest_data_filtered_pg4, grid_table, col5)

        with st.expander('Owned Weapons', expanded=True):
            st.write('Hello')

    def build_tool(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot,
                   selected_element, selected_sunset):
        st.title('Build Tool')
        st.title('')
        st.title('Coming Soon')

    # Call the selected page function
    page = {
        'Home': lambda: home_page(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype,
                                  selected_slot, selected_element, selected_sunset),
        'Vault Summary': lambda: vault_summary(session_state, manifest_weapon_data, selected_tier, selected_type,
                                               selected_archetype, selected_slot, selected_element, selected_sunset),
        'Weapon Analysis': lambda: weapon_analysis(session_state, manifest_weapon_data, selected_tier, selected_type,
                                                   selected_archetype, selected_slot, selected_element, selected_sunset),
        'Weapon Comparison': lambda: weapon_comparison(session_state, manifest_weapon_data, selected_tier,
                                                       selected_type, selected_archetype, selected_slot,
                                                       selected_element, selected_sunset),
        'Weapon Perks': lambda: weapon_perks(session_state, manifest_weapon_data, selected_tier, selected_type,
                                             selected_archetype, selected_slot, selected_element, selected_sunset),
        'Build Tool': lambda: build_tool(session_state, manifest_weapon_data, selected_tier, selected_type,
                                         selected_archetype, selected_slot, selected_element, selected_sunset),
    }[selection]

    page()


if __name__ == '__main__':
    main()