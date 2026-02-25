"""
Load data gathered by webscraper from Training portal into database
"""

import json
import pandas as pd
from datetime import datetime, date
from pathlib import Path
from sqlalchemy import text
from src.utils import connect_to_database, log
from src.ui import workout_day_selector

# ============================================
# HELPER FUNCTIONS
# ============================================

def plan_exists(cur, plan_name):

    """Checks if a plan with given name already exists"""

    cur.execute("""
        SELECT plan_id FROM training_plans WHERE plan_name = %s
    """, (plan_name,))
    return cur.fetchone()

import pandas as pd

def count_checked_checkboxes(df, exercise_index):
    """
    Counts completed sets for specified exercise
    """
    
    exercise_row = df.iloc[exercise_index]
    
    # Get only checkbox columns ( starting with ✓)
    checkbox_cols = [col for col in df.columns if col.startswith('✓')]
    
    if not checkbox_cols:
        # Fallback: count all ☑ symbols in the row
        return (exercise_row == '☑').sum()
    
    # Count checked boxes only in checkbox columns
    checked_count = sum(1 for col in checkbox_cols if exercise_row[col] == '☑')
    
    return checked_count

def create_new_plan(cur, plan_name, start_date):

    """Creates a new training plan and returns its ID"""

    cur.execute("""
        INSERT INTO training_plans (plan_name, start_date, end_date)
        VALUES (%s, %s, NULL)
        RETURNING plan_id;
    """, (plan_name, start_date))

    return cur.fetchone()[0]

def get_or_create_exercise(cur, exercise_name):

    """Gets exercise ID or creates new exercise if it doesn't exist"""

    cur.execute("""
        SELECT exercise_id 
        FROM exercises 
        WHERE exercise_name = %s
    """, (exercise_name,))

    result = cur.fetchone()
    if result:
        return result[0]

    # Exercise doesn't exist - add new one

    cur.execute("""
        INSERT INTO exercises (exercise_name, muscle_group)
        VALUES (%s, NULL)
        RETURNING exercise_id
    """, (exercise_name,))
    exercise_id = cur.fetchone()[0]
    log(f"Added new exercise: {exercise_name}")
    return exercise_id

def insert_plan_exercise(cur, plan_id, day_of_week, exercise_data):

    """Inserts an exercise into the training plan"""

    reps_json = json.dumps(exercise_data.get('reps') or [])

    cur.execute("""
        INSERT INTO plan_exercises(
            plan_id, exercise_id, day_of_week,
            warmup_sets, working_sets, reps,
            planned_weight, rest_between_sets_min,
            rest_between_sets_max, rest_after_exercise_min,
            rest_after_exercise_max
        )
        VALUES (%s, %s, %s, %s, %s, %s, NULL, %s, %s, %s, %s)
    """, (
        plan_id,
        exercise_data['exercise_id'],
        day_of_week,
        exercise_data.get('warmup_sets'),
        exercise_data.get('working_sets'),
        reps_json,
        exercise_data.get('rest_between_sets_min'),
        exercise_data.get('rest_between_sets_max'),
        exercise_data.get('rest_after_exercise_min'),
        exercise_data.get('rest_after_exercise_max')
    ))

def get_plan_id(engine, plan_name):
    """
    Gets plan_id for given plan_name
    """

    query = text("""
        SELECT plan_id
        FROM training_plans
        WHERE plan_name = :plan_name
    """)

    with engine.connect() as conn:
        return conn.execute(query, {"plan_name": plan_name}).scalar()

def log_exercise_added(exercise_name, exercise_data):

    """Logs information about added exercise"""

    warmup = exercise_data.get('warmup_sets') or 0
    working = exercise_data.get('working_sets') or 0
    reps_json = json.dumps(exercise_data.get('reps') or [])
    log(f"{exercise_name}: {warmup} + {working} sets, reps={reps_json} added to plan")

# ============================================
# MID-LEVEL FUNCTIONS
# ============================================

def create_workout_session(engine, plan_id, session_date, day_of_week):
    """
    Creates new workout session in DB and returns it's session_id
    """

    # Check if session already exists

    query = f"""
            SELECT session_id
            FROM workout_sessions
            WHERE plan_id = %s
            AND session_date = %s
            AND day_of_week = %s
        """
    

    session_df = pd.DataFrame([{
        'plan_id': plan_id,
        'session_date': session_date,
        'day_of_week': day_of_week
    }])
    
    session_df.to_sql(
        'workout_sessions',
        engine,
        if_exists='append',
        index=False
    )
    
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT session_id 
                FROM workout_sessions 
                WHERE plan_id = :plan_id 
                AND session_date = :session_date
                AND day_of_week = :day_of_week
            """),
            {
                "plan_id": plan_id,
                "session_date": session_date,
                "day_of_week": day_of_week
            }
        )
        session_id = result.scalar()
    
    return session_id

def process_single_exercise(cur, plan_id, day_of_week, exercise):

    """Processes a single exercise"""

    # Get or create exercise

    exercise_id = get_or_create_exercise(cur, exercise['exercise'])

    # Prepare exercise data

    exercise_data = {
        'exercise_id': exercise_id,
        'warmup_sets': exercise.get('warmup_sets'),
        'working_sets': exercise.get('working_sets'),
        'reps': exercise.get('reps'),
        'rest_between_sets_min': exercise.get('rest_between_sets_min'),
        'rest_between_sets_max': exercise.get('rest_between_sets_max'),
        'rest_after_exercise_min': exercise.get('rest_after_exercise_min'),
        'rest_after_exercise_max': exercise.get('rest_after_exercise_max')
    }

    # Insert into plan

    insert_plan_exercise(cur, plan_id, day_of_week, exercise_data)
    log_exercise_added(exercise['exercise'], exercise_data)

def process_day(cur, plan_id, day_key, day_exercises, day_mapping):

    """Processes all exercises for a given day"""

    day_of_week = day_mapping.get(day_key)
    if not day_of_week:
        log(f"Skipping {day_key} (no mapping)")
        return

    log(f"Processing {day_key} ({day_of_week}):")

    for exercise in day_exercises:
        process_single_exercise(cur, plan_id, day_of_week, exercise)

# ============================================
# MAIN FUNCTION
# ============================================

def save_plan_to_database(json_file, plan_name, start_date):

    """
    Saves training plan from JSON file to database

    Args:
        json_file: Path to JSON file with training plan
        plan_name: Name of the plan (e.g., "February 2026")
        start_date: Start date of the plan (datetime.date object)
    """

    conn, cur = connect_to_database()

    try:

        # Load data from JSON file

        with open(json_file, 'r', encoding='utf-8') as f:
            training_plan = json.load(f)

        # Check if plan already exists

        if plan_exists(cur, plan_name):
            log(f"Plan: '{plan_name}' already exists in database. Aborting.",
                level="ERROR", echo=True)
            return

        # Create new plan

        plan_id = create_new_plan(cur, plan_name, start_date)
        log(f"Created new plan: {plan_name} (ID: {plan_id})")

        # Day mapping dictionary

        day_mapping = {
            "Day 1": "Monday", "Day 2": "Tuesday", "Day 3": "Wednesday",
            "Day 4": "Thursday", "Day 5": "Friday", "Day 6": "Saturday",
            "Day 7": "Sunday"
        }

        # Process each day

        for day_key, day_exercises in training_plan.items():
            process_day(cur, plan_id, day_key, day_exercises, day_mapping)

        # Commit transaction

        conn.commit()
        log(f"Plan '{plan_name}' successfully loaded to database")

    except Exception as e:
        conn.rollback()
        log(f"Error loading plan '{plan_name}' to database ({e})",
            level="ERROR", echo=True)
        raise

    finally:
        cur.close()
        conn.close()

def save_workout_to_database(workout_file):
    conn, engine = connect_to_database(return_cursor=False, return_engine=True)
    df = pd.read_excel(workout_file)
    sets = count_checked_checkboxes(df,1)
    print(df)
    print(f"\nReps: {sets}")
    workout_path = Path(workout_file)
    parts = workout_path.stem.split("_")
    plan_name = f"{parts[1].title()} {parts[2]}"
    print(plan_name)
    plan_id = get_plan_id(engine, plan_name)
    
    print(f"Plan id: {plan_id}")
    """
    day_of_week = day = parts[3].title()
    print(f"Day: {day_of_week}")
    conn.close()
    session_date = workout_day_selector()
    print(session_date)
    session_id = create_workout_session(engine, plan_id, session_date, day_of_week)
    """
