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

def main():
    st.set_page_config(page_title="MLB 2K25 Lineup Manager", layout="wide")
    
    st.title("MLB2K25 Lineup Manager")
    
    # File selection
    csv_file = st.text_input("CSV File Path", value="roster.csv")
    
    if not csv_file:
        st.warning("Please enter a CSV file path")
        return
    
    # Load data
    df = load_csv(csv_file)
    
    # Create tabs for different functionality
    tab1, tab2, tab3, tab4 = st.tabs(["Edit Players", "Add Player", "Preview Lineups", "Data Statistics"])
    
    with tab1:
        st.header("Edit Existing Players")
        
        # Player selection
        player_names = df["Player"].tolist() if not df.empty else []
        player_names.insert(0, "")
        selected_player = st.selectbox("Select a player to edit", options=player_names)
        
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
        
        with st.form("add_player_form"):
            col1, col2, col3 = st.columns(3)
            
            # Basic info
            with col1:
                new_player_name = st.text_input("Player Name")
                new_bats = st.selectbox("Bats", options=["R", "L", "S"])
                
                # Position selection
                new_positions = []
                for i in range(1, 7):
                    new_positions.append(st.text_input(f"Position {i}", value=""))
            
            # Stats
            with col2:
                new_avg = st.number_input("Average", value=0.000, format="%.3f", min_value=0.0, max_value=1.0, step=0.001)
                new_hr = st.number_input("HR", value=0, min_value=0)
                new_rbi = st.number_input("RBI", value=0, min_value=0)
                new_speed = st.number_input("Speed", value=50, min_value=0, max_value=99)
                new_at_bats = st.number_input("At Bats", value=0, min_value=0)
            
            # Ratings
            with col3:
                new_contact_r = st.number_input("Contact vs Right", value=50, min_value=0, max_value=99)
                new_contact_l = st.number_input("Contact vs Left", value=50, min_value=0, max_value=99)
                new_power_r = st.number_input("Power vs Right", value=50, min_value=0, max_value=99)
                new_power_l = st.number_input("Power vs Left", value=50, min_value=0, max_value=99)
                new_vision = st.number_input("Vision", value=50, min_value=0, max_value=99)
                new_clutch = st.number_input("Clutch", value=50, min_value=0, max_value=99)
            
            add_button = st.form_submit_button("Add Player")
            
            if add_button:
                if not new_player_name:
                    st.error("Player name is required")
                else:
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
                    df = pd.concat([df, pd.DataFrame([new_player])], ignore_index=True)
                    
                    # Create backup and save
                    backup_path = save_backup(df, csv_file)
                    df.to_csv(csv_file, index=False)
                    
                    if backup_path:
                        st.success(f"Player added successfully! Backup created at {backup_path}")
                    else:
                        st.success("Player added successfully!")
    
    with tab3:
        st.header("Preview Generated Lineups")
        
        if st.button("Generate Lineups"):
            import subprocess
            import sys
            
            try:
                # Run the lineup generation script
                result = subprocess.run([sys.executable, "generate-lineups.py"], 
                                        capture_output=True, text=True, check=True)
                
                # Display the output
                st.text_area("Lineup Results", value=result.stdout, height=500)
                
                if result.stderr:
                    st.error("Errors during lineup generation:")
                    st.code(result.stderr)
            except subprocess.CalledProcessError as e:
                st.error(f"Error running lineup generator: {e}")
                if e.stderr:
                    st.code(e.stderr)
    
    with tab4:
        st.header("Data Statistics")
        
        if not df.empty:
            st.write(f"Total players: {len(df)}")
            
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
            
            # Allow CSV download
            st.subheader("Export Data")
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="mlb2k25_export.csv",
                mime="text/csv"
            )
        else:
            st.info("No data available for statistics.")

if __name__ == "__main__":
    main()