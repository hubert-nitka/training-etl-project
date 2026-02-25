import psycopg
import pandas as pd
from datetime import datetime
from config import WORKOUT_XLSX_PATH
from pathlib import Path
from src.utils import connect_to_database, clear_screen, get_session_date_from_user
from tabulate import tabulate

def plan_selector():

    conn = connect_to_database(return_cursor=False)

    query = """
        SELECT plan_id, plan_name, start_date, end_date
        FROM training_plans
        ORDER BY start_date DESC
        LIMIT 6;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    # Check if there is any data
    if df.empty:
        print("No training plans found!")
        input("Press Enter to continue...")
        return None

    display_df = df[['plan_name', 'start_date', 'end_date']].copy()

    display_df.insert(0, 'Nr', range(1, len(df) + 1))
    display_df.columns = display_df.columns.str.replace('_',' ')
    display_df.columns = display_df.columns.str.title()

    while True:

        clear_screen()
        print("Available Plans:\n")

        print(tabulate(display_df, 
                    headers='keys',
                    tablefmt='github',
                    showindex=False,
                    colalign=("center","left", "center", "center")))
                    
        print("\n0. Cancel")
        choice = int(input("\nSelect plan: "))

        match choice:
            case x if 1<= x <= len(df):
                clear_screen()
                return int(df.iloc[(x-1),0]), str(df.iloc[(x-1),1])

            case 0:
                break

            case _:
                print("\nInvalid choice! Please select one of the available plans by number.")
                input("Press Enter to continue...")


def workout_day_selector_export(plan_id, plan_name):

    conn, engine = connect_to_database(return_cursor=False, return_engine=True)

    query = f"""
        SELECT day_of_week
        FROM (
            SELECT DISTINCT 
                day_of_week,
                CASE day_of_week
                    WHEN 'Monday' THEN 1
                    WHEN 'Tuesday' THEN 2
                    WHEN 'Wednesday' THEN 3
                    WHEN 'Thursday' THEN 4
                    WHEN 'Friday' THEN 5
                    WHEN 'Saturday' THEN 6
                    WHEN 'Sunday' THEN 7
                END AS day_order
            FROM plan_exercises
            WHERE plan_id = %s
        ) AS sub
        ORDER BY day_order;
    """

    df = pd.read_sql(query, engine, params=(plan_id,))

    df.insert(0, 'Nr', range(1, len(df) + 1))
    df.columns = df.columns.str.replace('_',' ')
    df.columns = df.columns.str.title()

    conn.close()

    

    while True:

        clear_screen()
        print(f"Available workout days within selected plan '{plan_name}':\n")

        print(tabulate(df, 
                        headers='keys',
                        tablefmt='github',
                        showindex=False,
                        colalign=("center","left")))
                    
        print("\n0. Cancel")
        choice = int(input("\nSelect plan: "))

        match choice:
            case x if 1<= x <= len(df):
                clear_screen()
                return str(df.iloc[(x-1),1])

            case 0:
                break

            case _:
                print("\nInvalid choice! Please select one of the available plans by number.")
                input("Press Enter to continue...")

def workout_day_selector_import(workout_folder=WORKOUT_XLSX_PATH):
    """
    Lists all .xlsx workout files using pandas and allows user to select one.
    Returns selected filename or None if cancelled.
    """
    folder_path = Path(workout_folder)

    # Check for workout folder
    if not folder_path.exists():
        print(f"Folder '{workout_folder}' does not exist!")
        input("Press Enter to continue...")
        return None

    # Find and list all files sorted by date (newest on top)
    files = sorted(
        folder_path.glob("*.xlsx"), 
        key=lambda f: f.stat().st_mtime, 
        reverse=True
    )

    # Check if there are any workout files
    if not files:
        print(f"No workout files found in folder '{workout_folder}!'")
        input("Press Enter to continue...")
        return None

    # Create DataFrame with file information
    data = []
    for file in files:
        mod_time = datetime.fromtimestamp(file.stat().st_mtime)
        mod_str = mod_time.strftime("%Y-%m-%d %H:%M")
        size_kb = file.stat().st_size / 1024
        data.append({
            'filename': file.name,
            'full_path': str(file.absolute()),
            'last_modified': mod_str
        })
    
    df = pd.DataFrame(data)
    df.insert(0, '#', range(1, len(df) + 1))

    while True:
        clear_screen()
        
        print("Available workout files:\n")
        
        display_df = df[['#', 'filename', 'last_modified']].copy()
        display_df.columns = ['#', 'File Name', 'Last Modified']
        
        print(tabulate(display_df,
                      headers='keys',
                      tablefmt='github',
                      showindex=False,
                      colalign=('center', 'left', 'center')))
        
        print("\n0. Cancel")

        choice = int(input(f"\nSelect file: "))
        
        match choice:
            case x if 1<= x <= len(df):
                selected = df[df['#'] == choice].iloc[0]
                return selected['full_path']  

            case 0:
                break

            case _:
                print("\nInvalid choice! Please select one of the available plans by number.")
                input("Press Enter to continue...")

def workout_day_selector():
    while True:
        date = get_session_date_from_user()

        if date is not None:
            return date
