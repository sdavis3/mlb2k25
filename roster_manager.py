# Import necessary libraries
import pandas as pd             # For data manipulation and analysis
import streamlit as st          # For creating web applications
import os                       # For file operations
from datetime import datetime   # For timestamping backups

def load_csv(file_path):
    """Load CSV data with error handling
    
    Attempts to load a CSV file as a pandas DataFrame, with graceful handling
    of common failure cases like missing files or malformed data.
    
    Args:
        file_path: Path to the CSV file to be loaded
        
    Returns:
        DataFrame containing the loaded CSV data, or an empty DataFrame with 
        the required columns if loading fails
    """
    try:
        # Check if the file exists before attempting to load
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            # If file doesn't exist, show error and return empty DataFrame
            st.error(f"File not found: {file_path}")
            return create_empty_dataframe()
    except Exception as e:
        # Handle any other exceptions during loading
        st.error(f"Error loading file: {e}")
        return create_empty_dataframe()

def create_empty_dataframe():
    """Create an empty dataframe with the required columns
    
    Generates a properly structured but empty DataFrame with all the necessary
    columns for player data, ensuring consistent structure even when starting fresh.
    
    Returns:
        Empty DataFrame with all required columns for player data
    """
    # Define the core player attribute columns
    columns = ["Player", "Bats", "Average", "HR", "RBI", "Speed", "AtBats", 
               "ContactR", "ContactL", "PowerR", "PowerL", "Vision", "Clutch"]
    
    # Add position columns (up to 6 possible positions per player)
    for i in range(1, 7):
        columns.append(f"Position{i}")
    
    # Return empty DataFrame with predefined columns
    return pd.DataFrame(columns=columns)

def save_backup(df, file_path):
    """Create a backup of the current file before saving changes
    
    Creates a timestamped backup copy of the file before modifying it,
    providing data safety in case of accidental changes or corrupted data.
    
    Args:
        df: DataFrame to backup
        file_path: Path to the original file
        
    Returns:
        Path to the created backup file, or None if backup couldn't be created
    """
    # Only attempt backup if the original file exists
    if os.path.exists(file_path):
        # Generate timestamp for unique backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create backup filename by adding timestamp before extension
        backup_path = f"{os.path.splitext(file_path)[0]}_backup_{timestamp}.csv"
        # Save backup copy
        df.to_csv(backup_path, index=False)
        return backup_path
    return None

def delete_player(df, player_name, file_path):
    """Delete a player from the dataframe and save changes
    
    Removes a single player from the roster by name, creates a backup
    of the original data, and saves the updated roster to disk.
    
    Args:
        df: DataFrame containing player data
        player_name: Name of the player to delete
        file_path: Path to the CSV file to save changes
        
    Returns:
        tuple: (Updated DataFrame, backup path)
    """
    # Make backup before deletion for data safety
    backup_path = save_backup(df, file_path)
    
    # Delete the player by filtering for all rows except the one to delete
    updated_df = df[df["Player"] != player_name].reset_index(drop=True)
    
    # Save changes to disk
    updated_df.to_csv(file_path, index=False)
    
    # Return both updated data and backup information
    return updated_df, backup_path

def delete_players_batch(df, player_names, file_path):
    """Delete multiple players from the dataframe in a single operation
    
    Removes multiple players in a single batch operation, which is more efficient
    than deleting them one by one. Creates a backup before making changes.
    
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
    # The ~ operator inverts the boolean mask, keeping only non-matching rows
    updated_df = df[~df["Player"].isin(player_names)].reset_index(drop=True)
    
    # Save the updated dataframe
    updated_df.to_csv(file_path, index=False)
    
    # Return both updated data and backup path
    return updated_df, backup_path

def add_player_form_component(df, csv_file):
    """Modular component for adding new players
    
    Creates a form with all necessary fields for adding a new player to the roster.
    Handles validation, data processing, and saving to disk with backups.
    
    Args:
        df: DataFrame containing player data
        csv_file: Path to save the updated CSV
    
    Returns:
        Updated DataFrame if player added, original DataFrame otherwise
    """
    # Create a form that batches all inputs until submission
    with st.form("add_player_form"):
        # Split form into 3 columns for better organization
        col1, col2, col3 = st.columns(3)
        
        # Basic info column
        with col1:
            # Player name input (empty by default)
            new_player_name = st.text_input("Player Name", value="")
            # Batting stance selection (empty default with R/L/S options)
            new_bats = st.selectbox("Bats", options=["", "R", "L", "S"], index=0)
            
            # Position selection - all empty fields by default
            # Players can have up to 6 different positions
            new_positions = []
            for i in range(1, 7):
                new_positions.append(st.text_input(f"Position {i}", value=""))
        
        # Stats column - all zeroes by default
        with col2:
            # Batting average with 3 decimal places format
            new_avg = st.number_input("Average", value=0.000, format="%.3f", min_value=0.0, max_value=1.0, step=0.001)
            # Home runs
            new_hr = st.number_input("HR", value=0, min_value=0)
            # Runs batted in
            new_rbi = st.number_input("RBI", value=0, min_value=0)
            # Speed rating (0-99 scale)
            new_speed = st.number_input("Speed", value=0, min_value=0, max_value=99)
            # At bats count
            new_at_bats = st.number_input("At Bats", value=0, min_value=0)
        
        # Ratings column - all zeroes initially
        with col3:
            # Contact ratings split by pitcher handedness
            new_contact_r = st.number_input("Contact vs Right", value=0, min_value=0, max_value=99)
            new_contact_l = st.number_input("Contact vs Left", value=0, min_value=0, max_value=99)
            # Power ratings split by pitcher handedness
            new_power_r = st.number_input("Power vs Right", value=0, min_value=0, max_value=99)
            new_power_l = st.number_input("Power vs Left", value=0, min_value=0, max_value=99)
            # Vision rating affects ability to see and hit pitches
            new_vision = st.number_input("Vision", value=0, min_value=0, max_value=99)
            # Clutch rating affects performance in high-pressure situations
            new_clutch = st.number_input("Clutch", value=0, min_value=0, max_value=99)
        
        # Submit button for the form
        add_button = st.form_submit_button("Add Player")
        
        # Process form data after submission
        if add_button:
            # Validate required fields
            if not new_player_name:
                st.error("Player name is required")
                return df
            
            if not new_bats:
                st.error("Batting side is required")
                return df
                
            # Create new player data dictionary with all fields
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
            
            # Add position fields to player data
            for i in range(1, 7):
                new_player[f"Position{i}"] = new_positions[i-1]
            
            # Append new player to the DataFrame
            # Using concat instead of append (which is deprecated)
            updated_df = pd.concat([df, pd.DataFrame([new_player])], ignore_index=True)
            
            # Create backup and save changes
            backup_path = save_backup(df, csv_file)
            updated_df.to_csv(csv_file, index=False)
            
            # Show success message with backup info if available
            if backup_path:
                st.success(f"Player '{new_player_name}' added successfully! Backup created at {backup_path}")
            else:
                st.success(f"Player '{new_player_name}' added successfully!")
            
            # Return the updated DataFrame
            return updated_df
            
    # If form wasn't submitted or validation failed, return original DataFrame
    return df

def parse_lineup_output(output_text):
    """Parse the raw lineup output into structured data for better display
    
    Converts the plain text output from the lineup generation script into
    structured DataFrame objects that can be displayed in the UI. Handles
    both right-handed and left-handed pitcher lineups.
    
    Args:
        output_text: Raw text output from lineup generation script
        
    Returns:
        dict: Structured lineup data for RHP and LHP
    """
    # Initialize output structure
    lineup_data = {
        "RHP": None,  # Right-handed pitcher lineup
        "LHP": None   # Left-handed pitcher lineup
    }
    
    # Split the output by the two main sections
    sections = output_text.split("\nLineup vs ")
    
    if len(sections) > 1:
        # Extract and clean the RHP section
        rhp_section = sections[0].replace("Lineup vs Right-Handed Pitching:", "").strip()
        # Extract and clean the LHP section
        lhp_section = sections[1].replace("Left-Handed Pitching:", "").strip()
        
        # Try to convert text tables to dataframes
        try:
            # Use StringIO to treat text as a file for pandas read_csv
            import io
            # Parse with regex separator to handle variable whitespace
            rhp_df = pd.read_csv(io.StringIO(rhp_section), sep=r'\s{2,}', engine='python')
            lhp_df = pd.read_csv(io.StringIO(lhp_section), sep=r'\s{2,}', engine='python')
            
            # Store parsed DataFrames in the output dictionary
            lineup_data["RHP"] = rhp_df
            lineup_data["LHP"] = lhp_df
        except Exception:
            # Fallback if parsing fails - just use the raw text
            lineup_data["RHP"] = rhp_section
            lineup_data["LHP"] = lhp_section
    
    return lineup_data

def display_lineup_card(lineup_df):
    """Display a lineup in a clean, simple table format with headers
    
    Creates a well-formatted table display of a lineup with consistent
    column formatting, headers, and supplementary statistics. Includes
    special handling for formatting values and calculating team stats.
    
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
    
    # Create a copy of the dataframe to avoid modifying the original
    display_df = lineup_df.copy()
    
    # Add a column for batting order (1-based indexing)
    display_df.insert(0, 'Order', range(1, len(display_df) + 1))
    
    # Define columns to display in preferred order
    columns_to_display = ['Order', 'Position', 'Player', 'Bats', 'Average', 'HR', 'RBI', 'Speed']
    
    # Only include columns that exist in the dataframe
    # This makes the function more robust to varying input formats
    display_columns = [col for col in columns_to_display if col in display_df.columns]
    
    # Format the display dataframe with only the selected columns
    formatted_df = display_df[display_columns].copy()
    
    # Format batting average to 3 decimal places for better readability
    if 'Average' in formatted_df.columns:
        formatted_df['Average'] = formatted_df['Average'].apply(lambda x: f"{x:.3f}")
    
    # Rename columns for better display
    column_rename = {
        'Order': '#',         # More compact batting order indicator
        'Position': 'Pos',    # Shorter field position label
        'Player': 'Player',   # Keep player name as is
        'Bats': 'B',          # Single letter for batting side
        'Average': 'AVG',     # Standard baseball abbreviation
        'HR': 'HR',           # Standard baseball abbreviation
        'RBI': 'RBI',         # Standard baseball abbreviation 
        'Speed': 'SPD'        # Shorter speed label
    }
    
    # Only rename columns that exist in our filtered dataframe
    rename_dict = {k: v for k, v in column_rename.items() if k in formatted_df.columns}
    formatted_df = formatted_df.rename(columns=rename_dict)
    
    # Display the table with custom styling for each column
    st.dataframe(
        formatted_df,
        use_container_width=True,  # Use full width of container
        hide_index=True,           # Hide default index
        column_config={
            # Configure column widths and formats for consistency
            "#": st.column_config.NumberColumn(format="%d", width="small"),
            "Pos": st.column_config.TextColumn(width="small"),
            "B": st.column_config.TextColumn(width="small"),
            "AVG": st.column_config.TextColumn(width="medium"),
            "HR": st.column_config.NumberColumn(width="small"),
            "RBI": st.column_config.NumberColumn(width="small"),
            "SPD": st.column_config.NumberColumn(width="small")
        }
    )
    
    # Add a summary of the lineup's overall stats in an expandable section
    if len(display_df) > 0:
        with st.expander("Lineup Statistics"):
            # Organize statistics into three columns
            col1, col2, col3 = st.columns(3)
            
            # First column: Batting average and home runs
            with col1:
                # Calculate team batting average (mean of all players)
                avg_avg = display_df['Average'].mean() if 'Average' in display_df.columns else 0
                # Calculate total home runs (sum of all players)
                total_hr = display_df['HR'].sum() if 'HR' in display_df.columns else 0
                # Display metrics with appropriate formatting
                st.metric("Team AVG", f"{avg_avg:.3f}")
                st.metric("Total HR", total_hr)
            
            # Second column: RBIs and speed
            with col2:
                # Calculate total RBIs for the lineup
                total_rbi = display_df['RBI'].sum() if 'RBI' in display_df.columns else 0
                # Calculate average speed rating
                avg_speed = display_df['Speed'].mean() if 'Speed' in display_df.columns else 0
                # Display metrics with appropriate formatting
                st.metric("Total RBI", total_rbi)
                st.metric("Avg Speed", f"{avg_speed:.1f}")
            
            # Third column: Batting side distribution
            with col3:
                # Count batters by side (R/L/S) if data is available
                if 'Bats' in display_df.columns:
                    bats_counts = display_df['Bats'].value_counts()
                    # Get counts with fallback to 0 if not present
                    right = bats_counts.get('R', 0)    # Right-handed batters
                    left = bats_counts.get('L', 0)     # Left-handed batters
                    switch = bats_counts.get('S', 0)   # Switch hitters
                    
                    # Display counts as metrics
                    st.metric("Right-handed", right)
                    st.metric("Left-handed", left) 
                    st.metric("Switch hitters", switch)

def main():
    """Main application function for the MLB2K25 Lineup Manager
    
    Sets up the Streamlit interface, handles navigation through tabs,
    and coordinates all the functionality for managing player data and
    generating lineups.
    """
    # Configure the page with a title and wide layout for better display
    st.set_page_config(page_title="MLB2K25 Lineup Manager", layout="wide")
    
    # Set the main app title
    st.title("MLB2K25 Lineup Manager")
    
    # File selection input for choosing which CSV to work with
    csv_file = st.text_input("CSV File Path", value="roster.csv")
    
    # Validate file path input
    if not csv_file:
        st.warning("Please enter a CSV file path")
        return
    
    # Load data from the selected file
    df = load_csv(csv_file)
    
    # Create tabs for different functionality
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Edit Players",       # Tab for editing existing players
        "Add Player",         # Tab for adding new players
        "Delete Player",      # Tab for removing players
        "Preview Lineups",    # Tab for generating and viewing lineups
        "Data Statistics"     # Tab for viewing roster statistics
    ])
    
    # TAB 1: EDIT PLAYERS
    with tab1:
        st.header("Edit Existing Players")
        
        # Player selection dropdown
        player_names = df["Player"].tolist() if not df.empty else []
        player_names.insert(0, "")  # Add blank option at beginning
        selected_player = st.selectbox("Select a player to edit", options=player_names, key="edit_player_select")
        
        # Only show edit form if a player is selected
        if selected_player:
            # Get the index of the selected player in the DataFrame
            player_index = df[df["Player"] == selected_player].index[0]
            
            # Create a form for editing player data
            with st.form("edit_player_form"):
                # Split form into three columns for better organization
                col1, col2, col3 = st.columns(3)
                
                # COLUMN 1: Basic info
                with col1:
                    # Player name field (pre-filled with current value)
                    player_name = st.text_input("Player Name", value=selected_player)
                    
                    # Batting stance selection
                    # Default to current value if valid, otherwise first option
                    bats = st.selectbox(
                        "Bats", 
                        options=["R", "L", "S"], 
                        index=["R", "L", "S"].index(df.at[player_index, "Bats"]) 
                              if df.at[player_index, "Bats"] in ["R", "L", "S"] else 0
                    )
                    
                    # Position selection fields (up to 6)
                    positions = []
                    for i in range(1, 7):
                        pos_col = f"Position{i}"
                        # Get current value if it exists and is not NaN
                        pos_val = df.at[player_index, pos_col] if pos_col in df.columns and pd.notna(df.at[player_index, pos_col]) else ""
                        positions.append(st.text_input(f"Position {i}", value=pos_val))
                
                # COLUMN 2: Stats
                with col2:
                    # Batting average with 3 decimal place format
                    avg = st.number_input(
                        "Average", 
                        value=float(df.at[player_index, "Average"]), 
                        format="%.3f", 
                        min_value=0.0, 
                        max_value=1.0, 
                        step=0.001
                    )
                    # Home runs
                    hr = st.number_input("HR", value=int(df.at[player_index, "HR"]), min_value=0)
                    # Runs batted in
                    rbi = st.number_input("RBI", value=int(df.at[player_index, "RBI"]), min_value=0)
                    # Speed rating (0-99 scale)
                    speed = st.number_input("Speed", value=int(df.at[player_index, "Speed"]), min_value=0, max_value=99)
                    # At bats count
                    at_bats = st.number_input("At Bats", value=int(df.at[player_index, "AtBats"]), min_value=0)
                
                # COLUMN 3: Ratings
                with col3:
                    # Contact ratings against RHP/LHP
                    contact_r = st.number_input("Contact vs Right", value=int(df.at[player_index, "ContactR"]), min_value=0, max_value=99)
                    contact_l = st.number_input("Contact vs Left", value=int(df.at[player_index, "ContactL"]), min_value=0, max_value=99)
                    # Power ratings against RHP/LHP
                    power_r = st.number_input("Power vs Right", value=int(df.at[player_index, "PowerR"]), min_value=0, max_value=99)
                    power_l = st.number_input("Power vs Left", value=int(df.at[player_index, "PowerL"]), min_value=0, max_value=99)
                    # Vision and clutch ratings
                    vision = st.number_input("Vision", value=int(df.at[player_index, "Vision"]), min_value=0, max_value=99)
                    clutch = st.number_input("Clutch", value=int(df.at[player_index, "Clutch"]), min_value=0, max_value=99)
                
                # Form submission button
                submit_button = st.form_submit_button("Save Changes")
                
                # Process form data after submission
                if submit_button:
                    # Update all player data fields
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
                    
                    # Update position fields
                    for i in range(1, 7):
                        pos_col = f"Position{i}"
                        df.at[player_index, pos_col] = positions[i-1]
                    
                    # Create backup and save changes
                    backup_path = save_backup(df, csv_file)
                    df.to_csv(csv_file, index=False)
                    
                    # Show success message
                    if backup_path:
                        st.success(f"Player updated successfully! Backup created at {backup_path}")
                    else:
                        st.success("Player updated successfully!")
    
    # TAB 2: ADD PLAYER
    with tab2:
        st.header("Add New Player")
        # Use modular component for adding new players
        # This updates df if a new player is added
        df = add_player_form_component(df, csv_file)

    # TAB 3: DELETE PLAYER
    with tab3:
        st.header("Delete Player")
        
        # Check if there are any players to delete
        if df.empty:
            st.info("No players available to delete.")
        else:
            # Warning about permanent deletion
            st.warning("⚠️ Warning: Deletion is permanent and will take effect immediately.")
            
            # Player multi-select for choosing players to delete
            players_to_delete = st.multiselect(
                "Select player(s) to delete",
                options=df["Player"].tolist(),
                key="delete_player_select"
            )
            
            # Only show preview and delete button if players are selected
            if players_to_delete:
                # Preview section showing which players will be deleted
                st.subheader(f"Selected Players ({len(players_to_delete)})")
                selected_data = df[df["Player"].isin(players_to_delete)]
                
                # Choose key columns for preview display
                display_columns = ["Player", "Bats", "Average", "HR", "RBI", "Speed"]
                
                # Add position columns if they exist
                for i in range(1, 7):
                    pos_col = f"Position{i}"
                    if pos_col in df.columns:
                        display_columns.append(pos_col)
                
                # Display selected players as a preview table
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
                        
                        # Create a user-friendly message
                        num_deleted = len(players_to_delete)
                        message = f"Deleted {num_deleted} player{'s' if num_deleted > 1 else ''}"
                        if backup_path:
                            message += f" (Backup: {os.path.basename(backup_path)})"
                        
                        # Show notification and force page refresh
                        st.toast(message)
                        st.rerun()
    
    # TAB 4: PREVIEW LINEUPS
    with tab4:
        st.header("Preview Generated Lineups")
        
        # Split into columns for controls and results
        lineup_col1, lineup_col2 = st.columns([1, 3])
        
        # Control column
        with lineup_col1:
            # File selection for lineup generation
            file_options = {
                "roster.csv": "Current Roster (roster.csv)"
            }
            
            # Radio buttons for file selection
            selected_file = st.radio("Select file to use for lineup generation:", 
                                   options=list(file_options.keys()),
                                   format_func=lambda x: file_options[x])
        
        # Generate button (outside columns for full width)
        generate_button = st.button("Generate Lineups", key="generate_lineups_button", 
                                   use_container_width=True, type="primary")
    
    # Lineup generation process (triggered by button)
    if generate_button:
        # Import needed modules
        import subprocess
        import sys
        import tempfile
        
        # Show a spinner during processing
        with st.spinner("Generating optimal lineups..."):
            try:
                # Create a temporary file for the modified script
                # This avoids modifying the original script file
                with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
                    temp_script_path = temp_file.name
                    
                    # Read the original script
                    with open("generate-lineups.py", "r") as original:
                        content = original.read()
                        # Modify the file path in the content
                        modified_content = content.replace(
                            "file_path = 'roster.csv'", 
                            f"file_path = '{selected_file}'"
                        )
                        # Write modified content to temporary file
                        temp_file.write(modified_content.encode())
                
                # Run the modified lineup generation script as a subprocess
                result = subprocess.run([sys.executable, temp_script_path], 
                                        capture_output=True, text=True, check=True)
                
                # Parse the text output into structured data
                lineups = parse_lineup_output(result.stdout)
                
                # Clean up temporary file
                if os.path.exists(temp_script_path):
                    os.remove(temp_script_path)
                
                # Create tabs for different lineup types
                lineup_tabs = st.tabs(["vs Right-Handed Pitching", "vs Left-Handed Pitching"])
                
                # Display RHP lineup in first tab
                with lineup_tabs[0]:
                    if lineups["RHP"] is not None:
                        st.subheader("Optimal Lineup vs RHP")
                        display_lineup_card(lineups["RHP"])
                    else:
                        st.info("No lineup data available for RHP")
                
                # Display LHP lineup in second tab
                with lineup_tabs[1]:
                    if lineups["LHP"] is not None:
                        st.subheader("Optimal Lineup vs LHP")
                        display_lineup_card(lineups["LHP"])
                    else:
                        st.info("No lineup data available for LHP")
                
                # Show raw output in expandable section for debugging
                with st.expander("View Raw Output"):
                    st.text_area("Command Output", value=result.stdout, height=300)
                    
                    # Show errors if any occurred
                    if result.stderr:
                        st.error("Errors:")
                        st.code(result.stderr)
                    
            except subprocess.CalledProcessError as e:
                # Handle errors from the subprocess
                st.error(f"Error generating lineups: {e}")
                if e.stderr:
                    st.code(e.stderr)
                # Clean up temporary file in case of error
                if 'temp_script_path' in locals() and os.path.exists(temp_script_path):
                    os.remove(temp_script_path)
    
    # TAB 5: DATA STATISTICS
    with tab5:
        st.header("Data Statistics")
        
        # Only show statistics if there's data
        if not df.empty:
            # Split into two columns for better layout
            stats_col1, stats_col2 = st.columns(2)
            
            # Left column statistics
            with stats_col1:
                # Total players count
                st.metric("Total Players", len(df))
                
                # Position distribution chart
                st.subheader("Position Distribution")
                position_counts = {}
                
                # Count players by position across all position columns
                for i in range(1, 7):
                    pos_col = f"Position{i}"
                    if pos_col in df.columns:
                        # For each unique position, count players who can play it
                        for pos in df[pos_col].dropna().unique():
                            # Only count non-empty positions
                            if pos and pos not in position_counts:
                                position_counts[pos] = len(df[df[pos_col] == pos])
                            elif pos and pos in position_counts:
                                position_counts[pos] += len(df[df[pos_col] == pos])
                
                # Create DataFrame for the chart and sort by frequency
                position_df = pd.DataFrame(list(position_counts.items()), columns=['Position', 'Count'])
                position_df = position_df.sort_values('Count', ascending=False)
                
                # Display bar chart of position distribution
                st.bar_chart(position_df.set_index('Position'))
                
            # Right column statistics
            with stats_col2:
                # Batting side distribution
                st.subheader("Batting Distribution")
                bats_counts = df["Bats"].value_counts().reset_index()
                bats_counts.columns = ['Bats', 'Count']
                
                # Display bar chart of batting side distribution
                st.bar_chart(bats_counts.set_index('Bats'))
                
                # Average ratings across the roster
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
                
                # Create and display bar chart of average ratings
                rating_df = pd.DataFrame(list(avg_ratings.items()), columns=['Rating', 'Average'])
                st.bar_chart(rating_df.set_index('Rating'))
        else:
            # Message when no data is available
            st.info("No data available for statistics.")

# Entry point of the application
if __name__ == "__main__":
    main()