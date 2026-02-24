import psycopg
import pandas as pd
from src.utils import connect_to_database, clear_screen
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
                print("\nInvalid choice! Please select one of the available planse by number.")
                input("Press Enter to continue...")


def workout_day_selector(plan_id, plan_name):

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
                print("\nInvalid choice! Please select one of the available planse by number.")
                input("Press Enter to continue...")