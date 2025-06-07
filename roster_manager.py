import pandas as pd
import streamlit as st
import os
from datetime import datetime

def load_csv(file_path):
    """Load CSV data with error handling"""
    try:
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            st.error(f"File not found: {file_path}")
            return create_empty_dataframe()
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return create_empty_dataframe()

def create_empty_dataframe():
    """Create an empty dataframe with the required columns"""
    columns = ["Player", "Bats", "Average", "HR", "RBI", "Speed", "AtBats", 
               "ContactR", "ContactL", "PowerR", "PowerL", "Vision", "Clutch"]
    
    # Add position columns
    for i in range(1, 7):
        columns.append(f"Position{i}")
    
    return pd.DataFrame(columns=columns)

def save_backup(df, file_path):
    """Create a backup of the current file before saving changes"""
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{os.path.splitext(file_path)[0]}_backup_{timestamp}.csv"
        df.to_csv(backup_path, index=False)
        return backup_path
    return None

def delete_player(df, player_name, file_path):
    """Delete a player from the dataframe and save changes
    
    Args:
        df: DataFrame containing player data
        player_name: Name of the player to delete
        file_path: Path to the CSV file to save changes
        
    Returns:
        tuple: (Updated DataFrame, backup path)
    """
    # Make backup before deletion
    backup_path = save_backup(df, file_path)
    
    # Delete the player
    updated_df = df[df["Player"] != player_name].reset_index(drop=True)
    
    # Save changes
    updated_df.to_csv(file_path, index=False)
    
    return updated_df, backup_path

def delete_players_batch(df, player_names, file_path):
    """Delete multiple players from the dataframe in a single operation
    
    Args:
        df: DataFrame containing player data
        player_names: List of player names to delete
        file_path: Path to the CSV file to save changes
        
    Returns:
        tuple: (Updated DataFrame, backup path)
    """
    # Create backup before any modifications
    backup_path = save_backup(df, file_path)
    
    # Remove all selected players at once for better performance
    updated_df = df[~df["Player"].isin(player_names)].reset_index(drop=True)
    
    # Save the updated dataframe
    updated_df.to_csv(file_path, index=False)
    
    return updated_df, backup_path

def add_player_form_component(df, csv_file):
    """Modular component for adding new players
    
    Args:
        df: DataFrame containing player data
        csv_file: Path to save the updated CSV
    
    Returns:
        Updated DataFrame if player added, original otherwise
    """
    with st.form("add_player_form"):
        col1, col2, col3 = st.columns(3)
        
        # Basic info
        with col1:
            new_player_name = st.text_input("Player Name", value="")
            new_bats = st.selectbox("Bats", options=["", "R", "L", "S"], index=0)
            
            # Position selection - all empty
            new_positions = []
            for i in range(1, 7):
                new_positions.append(st.text_input(f"Position {i}", value=""))
        
        # Stats - all zeroes
        with col2:
            new_avg = st.number_input("Average", value=0.000, format="%.3f", min_value=0.0, max_value=1.0, step=0.001)
            new_hr = st.number_input("HR", value=0, min_value=0)
            new_rbi = st.number_input("RBI", value=0, min_value=0)
            new_speed = st.number_input("Speed", value=0, min_value=0, max_value=99)
            new_at_bats = st.number_input("At Bats", value=0, min_value=0)
        
        # Ratings - all zeroes initially
        with col3:
            new_contact_r = st.number_input("Contact vs Right", value=0, min_value=0, max_value=99)
            new_contact_l = st.number_input("Contact vs Left", value=0, min_value=0, max_value=99)
            new_power_r = st.number_input("Power vs Right", value=0, min_value=0, max_value=99)
            new_power_l = st.number_input("Power vs Left", value=0, min_value=0, max_value=99)
            new_vision = st.number_input("Vision", value=0, min_value=0, max_value=99)
            new_clutch = st.number_input("Clutch", value=0, min_value=0, max_value=99)
        
        add_button = st.form_submit_button("Add Player")
        
        if add_button:
            if not new_player_name:
                st.error("Player name is required")
                return df
            
            if not new_bats:
                st.error("Batting side is required")
                return df
                
            # Create new player data
            new_player = {
                "Player": new_player_name,
                "Bats": new_bats,
                "Average": new_avg,
                "HR": new_hr,
                "RBI": new_rbi,
                "Speed": new_speed,
                "AtBats": new_at_bats,
                "ContactR": new_contact_r,
                "ContactL": new_contact_l,
                "PowerR": new_power_r,
                "PowerL": new_power_l,
                "Vision": new_vision,
                "Clutch": new_clutch
            }
            
            # Add positions
            for i in range(1, 7):
                new_player[f"Position{i}"] = new_positions[i-1]
            
            # Append new player
            updated_df = pd.concat([df, pd.DataFrame([new_player])], ignore_index=True)
            
            # Create backup and save
            backup_path = save_backup(df, csv_file)
            updated_df.to_csv(csv_file, index=False)
            
            if backup_path:
                st.success(f"Player '{new_player_name}' added successfully! Backup created at {backup_path}")
            else:
                st.success(f"Player '{new_player_name}' added successfully!")
            
            return updated_df
            
    return df

def parse_lineup_output(output_text):
    """Parse the raw lineup output into structured data for better display
    
    Args:
        output_text: Raw text output from lineup generation script
        
    Returns:
        dict: Structured lineup data for RHP and LHP
    """
    lineup_data = {
        "RHP": None,
        "LHP": None
    }
    
    # Split the output by the two main sections
    sections = output_text.split("\nLineup vs ")
    
    if len(sections) > 1:
        rhp_section = sections[0].replace("Lineup vs Right-Handed Pitching:", "").strip()
        lhp_section = sections[1].replace("Left-Handed Pitching:", "").strip()
        
        # Convert text tables to dataframes
        try:
            import io
            rhp_df = pd.read_csv(io.StringIO(rhp_section), sep=r'\s{2,}', engine='python')
            lhp_df = pd.read_csv(io.StringIO(lhp_section), sep=r'\s{2,}', engine='python')
            
            lineup_data["RHP"] = rhp_df
            lineup_data["LHP"] = lhp_df
        except Exception:
            # Fallback if parsing fails
            lineup_data["RHP"] = rhp_section
            lineup_data["LHP"] = lhp_section
    
    return lineup_data

def display_lineup_card(lineup_df):
    """Display a lineup in a clean, simple table format with headers
    
    This function takes a DataFrame containing lineup data and renders it as
    a well-formatted table with clear headers. The table shows batting order,
    field position, player name, batting side, and key statistics for each player.
    
    Args:
        lineup_df: DataFrame containing lineup data with columns for Player, Position,
                  Bats, Average, HR, RBI, etc.
    
    Returns:
        None - Output is rendered directly to the Streamlit UI
    """
    # Handle case where input isn't a proper DataFrame (fallback to text display)
    if not isinstance(lineup_df, pd.DataFrame):
        st.text(lineup_df)  # Just show raw text if parsing failed
        return
    
    # Create a copy of the dataframe to manipulate for display
    display_df = lineup_df.copy()
    
    # Add a column for batting order
    display_df.insert(0, 'Order', range(1, len(display_df) + 1))
    
    # Reorder and select columns for display
    columns_to_display = ['Order', 'Position', 'Player', 'Bats', 'Average', 'HR', 'RBI', 'Speed']
    
    # Only include columns that exist in the dataframe
    display_columns = [col for col in columns_to_display if col in display_df.columns]
    
    # Format the display dataframe
    formatted_df = display_df[display_columns].copy()
    
    # Format batting average to 3 decimal places
    if 'Average' in formatted_df.columns:
        formatted_df['Average'] = formatted_df['Average'].apply(lambda x: f"{x:.3f}")
    
    # Rename columns for better display
    column_rename = {
        'Order': '#',
        'Position': 'Pos',
        'Player': 'Player',
        'Bats': 'B',
        'Average': 'AVG',
        'HR': 'HR',
        'RBI': 'RBI',
        'Speed': 'SPD'
    }
    
    # Only rename columns that exist
    rename_dict = {k: v for k, v in column_rename.items() if k in formatted_df.columns}
    formatted_df = formatted_df.rename(columns=rename_dict)
    
    # Display the table with styling
    st.dataframe(
        formatted_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "#": st.column_config.NumberColumn(format="%d", width="small"),
            "Pos": st.column_config.TextColumn(width="small"),
            "B": st.column_config.TextColumn(width="small"),
            "AVG": st.column_config.TextColumn(width="medium"),
            "HR": st.column_config.NumberColumn(width="small"),
            "RBI": st.column_config.NumberColumn(width="small"),
            "SPD": st.column_config.NumberColumn(width="small")
        }
    )
    
    # Add a summary of the lineup's overall stats
    if len(display_df) > 0:
        with st.expander("Lineup Statistics"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_avg = display_df['Average'].mean() if 'Average' in display_df.columns else 0
                total_hr = display_df['HR'].sum() if 'HR' in display_df.columns else 0
                st.metric("Team AVG", f"{avg_avg:.3f}")
                st.metric("Total HR", total_hr)
            
            with col2:
                total_rbi = display_df['RBI'].sum() if 'RBI' in display_df.columns else 0
                avg_speed = display_df['Speed'].mean() if 'Speed' in display_df.columns else 0
                st.metric("Total RBI", total_rbi)
                st.metric("Avg Speed", f"{avg_speed:.1f}")
            
            with col3:
                # Count batters by side
                if 'Bats' in display_df.columns:
                    bats_counts = display_df['Bats'].value_counts()
                    right = bats_counts.get('R', 0)
                    left = bats_counts.get('L', 0)
                    switch = bats_counts.get('S', 0)
                    
                    st.metric("Right-handed", right)
                    st.metric("Left-handed", left) 
                    st.metric("Switch hitters", switch)

def main():
    st.set_page_config(page_title="MLB2K25 Lineup Manager", layout="wide")
    
    st.title("MLB2K25 Lineup Manager")
    
    # File selection
    csv_file = st.text_input("CSV File Path", value="roster.csv")
    
    if not csv_file:
        st.warning("Please enter a CSV file path")
        return
    
    # Load data
    df = load_csv(csv_file)
    
    # Create tabs for different functionality
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Edit Players", "Add Player", "Delete Player", "Preview Lineups", "Data Statistics"])
    
    with tab1:
        st.header("Edit Existing Players")
        
        # Player selection
        player_names = df["Player"].tolist() if not df.empty else []
        player_names.insert(0, "")
        selected_player = st.selectbox("Select a player to edit", options=player_names, key="edit_player_select")
        
        if selected_player:
            player_index = df[df["Player"] == selected_player].index[0]
            
            with st.form("edit_player_form"):
                col1, col2, col3 = st.columns(3)
                
                # Basic info
                with col1:
                    player_name = st.text_input("Player Name", value=selected_player)
                    bats = st.selectbox("Bats", options=["R", "L", "S"], index=["R", "L", "S"].index(df.at[player_index, "Bats"]) if df.at[player_index, "Bats"] in ["R", "L", "S"] else 0)
                    
                    # Position selection
                    positions = []
                    for i in range(1, 7):
                        pos_col = f"Position{i}"
                        pos_val = df.at[player_index, pos_col] if pos_col in df.columns and pd.notna(df.at[player_index, pos_col]) else ""
                        positions.append(st.text_input(f"Position {i}", value=pos_val))
                
                # Stats
                with col2:
                    avg = st.number_input("Average", value=float(df.at[player_index, "Average"]), format="%.3f", min_value=0.0, max_value=1.0, step=0.001)
                    hr = st.number_input("HR", value=int(df.at[player_index, "HR"]), min_value=0)
                    rbi = st.number_input("RBI", value=int(df.at[player_index, "RBI"]), min_value=0)
                    speed = st.number_input("Speed", value=int(df.at[player_index, "Speed"]), min_value=0, max_value=99)
                    at_bats = st.number_input("At Bats", value=int(df.at[player_index, "AtBats"]), min_value=0)
                
                # Ratings
                with col3:
                    contact_r = st.number_input("Contact vs Right", value=int(df.at[player_index, "ContactR"]), min_value=0, max_value=99)
                    contact_l = st.number_input("Contact vs Left", value=int(df.at[player_index, "ContactL"]), min_value=0, max_value=99)
                    power_r = st.number_input("Power vs Right", value=int(df.at[player_index, "PowerR"]), min_value=0, max_value=99)
                    power_l = st.number_input("Power vs Left", value=int(df.at[player_index, "PowerL"]), min_value=0, max_value=99)
                    vision = st.number_input("Vision", value=int(df.at[player_index, "Vision"]), min_value=0, max_value=99)
                    clutch = st.number_input("Clutch", value=int(df.at[player_index, "Clutch"]), min_value=0, max_value=99)
                
                submit_button = st.form_submit_button("Save Changes")
                
                if submit_button:
                    # Update data
                    df.at[player_index, "Player"] = player_name
                    df.at[player_index, "Bats"] = bats
                    df.at[player_index, "Average"] = avg
                    df.at[player_index, "HR"] = hr
                    df.at[player_index, "RBI"] = rbi
                    df.at[player_index, "Speed"] = speed
                    df.at[player_index, "AtBats"] = at_bats
                    df.at[player_index, "ContactR"] = contact_r
                    df.at[player_index, "ContactL"] = contact_l
                    df.at[player_index, "PowerR"] = power_r
                    df.at[player_index, "PowerL"] = power_l
                    df.at[player_index, "Vision"] = vision
                    df.at[player_index, "Clutch"] = clutch
                    
                    # Update positions
                    for i in range(1, 7):
                        pos_col = f"Position{i}"
                        df.at[player_index, pos_col] = positions[i-1]
                    
                    # Create backup and save
                    backup_path = save_backup(df, csv_file)
                    df.to_csv(csv_file, index=False)
                    
                    if backup_path:
                        st.success(f"Player updated successfully! Backup created at {backup_path}")
                    else:
                        st.success("Player updated successfully!")
    
    with tab2:
        st.header("Add New Player")
        df = add_player_form_component(df, csv_file)

    with tab3:
        st.header("Delete Player")
        
        # Player selection for deletion
        if df.empty:
            st.info("No players available to delete.")
        else:
            st.warning("⚠️ Warning: Deletion is permanent and will take effect immediately.")
            
            # Create a more efficient layout
            players_to_delete = st.multiselect(
                "Select player(s) to delete",
                options=df["Player"].tolist(),
                key="delete_player_select"
            )
            
            # Show player details before deletion
            if players_to_delete:
                # Preview what will be deleted
                st.subheader(f"Selected Players ({len(players_to_delete)})")
                selected_data = df[df["Player"].isin(players_to_delete)]
                
                # Display essential columns
                display_columns = ["Player", "Bats", "Average", "HR", "RBI", "Speed"]
                
                # Add position columns
                for i in range(1, 7):
                    pos_col = f"Position{i}"
                    if pos_col in df.columns:
                        display_columns.append(pos_col)
                
                st.dataframe(
                    selected_data[display_columns], 
                    use_container_width=True,
                    hide_index=True
                )
                
                # Delete button with immediate action
                if st.button("Delete Selected Players", key="delete_button", type="primary"):
                    if players_to_delete:
                        # Process deletion in batch for better performance
                        df, backup_path = delete_players_batch(df, players_to_delete, csv_file)
                        
                        # Show toast notification with deletion info
                        num_deleted = len(players_to_delete)
                        message = f"Deleted {num_deleted} player{'s' if num_deleted > 1 else ''}"
                        if backup_path:
                            message += f" (Backup: {os.path.basename(backup_path)})"
                        
                        # Force page refresh after deletion
                        st.toast(message)
                        st.rerun()
    
    with tab4:
        st.header("Preview Generated Lineups")
        
        lineup_col1, lineup_col2 = st.columns([1, 3])
        
        with lineup_col1:
            file_options = {
                "roster.csv": "Current Roster (roster.csv)"
            }
            
            selected_file = st.radio("Select file to use for lineup generation:", 
                                   options=list(file_options.keys()),
                                   format_func=lambda x: file_options[x])
        
        generate_button = st.button("Generate Lineups", key="generate_lineups_button", 
                                   use_container_width=True, type="primary")
    
    if generate_button:
        import subprocess
        import sys
        import tempfile
        
        # Create a spinner to indicate processing
        with st.spinner("Generating optimal lineups..."):
            try:
                # Create a temporary file for the modified script
                with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
                    temp_script_path = temp_file.name
                    
                    with open("generate-lineups.py", "r") as original:
                        content = original.read()
                        # Replace the file path in the main() function
                        modified_content = content.replace(
                            "file_path = 'roster.csv'", 
                            f"file_path = '{selected_file}'"
                        )
                        temp_file.write(modified_content.encode())
                
                # Run the modified lineup generation script
                result = subprocess.run([sys.executable, temp_script_path], 
                                        capture_output=True, text=True, check=True)
                
                # Parse the output
                lineups = parse_lineup_output(result.stdout)
                
                # Clean up temporary file
                if os.path.exists(temp_script_path):
                    os.remove(temp_script_path)
                
                # Display pretty lineups
                lineup_tabs = st.tabs(["vs Right-Handed Pitching", "vs Left-Handed Pitching"])
                
                with lineup_tabs[0]:
                    if lineups["RHP"] is not None:
                        st.subheader("Optimal Lineup vs RHP")
                        display_lineup_card(lineups["RHP"])
                    else:
                        st.info("No lineup data available for RHP")
                
                with lineup_tabs[1]:
                    if lineups["LHP"] is not None:
                        st.subheader("Optimal Lineup vs LHP")
                        display_lineup_card(lineups["LHP"])
                    else:
                        st.info("No lineup data available for LHP")
                
                # Show raw output in expandable section
                with st.expander("View Raw Output"):
                    st.text_area("Command Output", value=result.stdout, height=300)
                    
                    if result.stderr:
                        st.error("Errors:")
                        st.code(result.stderr)
                    
            except subprocess.CalledProcessError as e:
                st.error(f"Error generating lineups: {e}")
                if e.stderr:
                    st.code(e.stderr)
                # Clean up temporary file in case of error
                if 'temp_script_path' in locals() and os.path.exists(temp_script_path):
                    os.remove(temp_script_path)
    
    with tab5:
        st.header("Data Statistics")
        
        if not df.empty:
            stats_col1, stats_col2 = st.columns(2)
            
            with stats_col1:
                st.metric("Total Players", len(df))
                
                # Position distribution
                st.subheader("Position Distribution")
                position_counts = {}
                
                for i in range(1, 7):
                    pos_col = f"Position{i}"
                    if pos_col in df.columns:
                        for pos in df[pos_col].dropna().unique():
                            if pos and pos not in position_counts:
                                position_counts[pos] = len(df[df[pos_col] == pos])
                            elif pos and pos in position_counts:
                                position_counts[pos] += len(df[df[pos_col] == pos])
                
                position_df = pd.DataFrame(list(position_counts.items()), columns=['Position', 'Count'])
                position_df = position_df.sort_values('Count', ascending=False)
                
                st.bar_chart(position_df.set_index('Position'))
                
            with stats_col2:
                # Batting distribution
                st.subheader("Batting Distribution")
                bats_counts = df["Bats"].value_counts().reset_index()
                bats_counts.columns = ['Bats', 'Count']
                
                st.bar_chart(bats_counts.set_index('Bats'))
                
                # Rating averages
                st.subheader("Average Ratings")
                avg_ratings = {
                    "ContactR": df["ContactR"].mean(),
                    "ContactL": df["ContactL"].mean(),
                    "PowerR": df["PowerR"].mean(),
                    "PowerL": df["PowerL"].mean(),
                    "Vision": df["Vision"].mean(),
                    "Clutch": df["Clutch"].mean(),
                    "Speed": df["Speed"].mean()
                }
                
                rating_df = pd.DataFrame(list(avg_ratings.items()), columns=['Rating', 'Average'])
                st.bar_chart(rating_df.set_index('Rating'))
        else:
            st.info("No data available for statistics.")

if __name__ == "__main__":
    main()