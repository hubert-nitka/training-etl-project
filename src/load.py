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

def count_checked_checkboxes(df, exercise_index):
    """
    Counts completed sets for specified exercise
    """
    
    exercise_row = df.iloc[exercise_index]
    
    # Get only checkbox columns (starting with ✓)
    checkbox_cols = [col for col in df.columns if str(col).startswith('✓')]
    
    if not checkbox_cols:
        # Fallback: count all ☑ symbols in the row
        return (exercise_row == '☑').sum()
    
    # Count checked boxes only in checkbox columns
    checked_count = sum(1 for col in checkbox_cols if exercise_row[col] == '☑')
    
    return checked_count


def plan_exists(engine, plan_name):
    """
    Checks if a plan with given name already exists
    """
    
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT plan_id FROM training_plans WHERE plan_name = :plan_name"),
            {"plan_name": plan_name}
        )
        return result.scalar()


def create_new_plan(engine, plan_name, start_date):
    """
    Creates a new training plan and returns its ID
    """
    
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                INSERT INTO training_plans (plan_name, start_date, end_date)
                VALUES (:plan_name, :start_date, NULL)
                RETURNING plan_id
            """),
            {"plan_name": plan_name, "start_date": start_date}
        )
        return result.scalar()


def get_or_create_exercise(engine, exercise_name):
    """
    Gets exercise ID or creates new exercise if it doesn't exist
    """
    
    with engine.begin() as conn:
        # Check if exercise exists
        result = conn.execute(
            text("SELECT exercise_id FROM exercises WHERE exercise_name = :exercise_name"),
            {"exercise_name": exercise_name}
        )
        
        existing_id = result.scalar()
        
        if existing_id:
            return existing_id
        
        # Create new exercise
        result = conn.execute(
            text("""
                INSERT INTO exercises (exercise_name, muscle_group)
                VALUES (:exercise_name, NULL)
                RETURNING exercise_id
            """),
            {"exercise_name": exercise_name}
        )
        
        return result.scalar()


def insert_plan_exercise(engine, plan_id, day_of_week, exercise_data):
    """
    Inserts an exercise into the training plan
    """
    
    reps_json = json.dumps(exercise_data.get('reps') or [])
    
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO plan_exercises(
                    plan_id, exercise_id, day_of_week,
                    warmup_sets, working_sets, reps,
                    planned_weight, rest_between_sets_min,
                    rest_between_sets_max, rest_after_exercise_min,
                    rest_after_exercise_max, trainer_note
                )
                VALUES (
                    :plan_id, :exercise_id, :day_of_week,
                    :warmup_sets, :working_sets, :reps,
                    NULL, :rest_between_sets_min,
                    :rest_between_sets_max, :rest_after_exercise_min,
                    :rest_after_exercise_max, trainer_note
                )
            """),
            {
                "plan_id": plan_id,
                "exercise_id": exercise_data['exercise_id'],
                "day_of_week": day_of_week,
                "warmup_sets": exercise_data.get('warmup_sets'),
                "working_sets": exercise_data.get('working_sets'),
                "reps": reps_json,
                "rest_between_sets_min": exercise_data.get('rest_between_sets_min'),
                "rest_between_sets_max": exercise_data.get('rest_between_sets_max'),
                "rest_after_exercise_min": exercise_data.get('rest_after_exercise_min'),
                "rest_after_exercise_max": exercise_data.get('rest_after_exercise_max'),
                "trainer_note": exercise_data.get('trainer_note')
            }
        )


def get_plan_id(engine, plan_name):
    """
    Gets plan_id for given plan_name
    """
    
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT plan_id FROM training_plans WHERE plan_name = :plan_name"),
            {"plan_name": plan_name}
        )
        return result.scalar()


def log_exercise_added(exercise_name, exercise_data):
    """Logs information about added exercise"""
    
    warmup = exercise_data.get('warmup_sets') or 0
    working = exercise_data.get('working_sets') or 0
    reps_json = json.dumps(exercise_data.get('reps') or [])
    log(f"{exercise_name}: {warmup} + {working} sets, reps={reps_json} added to plan")

def update_plan_exercise(engine, existing_id, exercise_data):
    """
    Updates plan exercise data in plan_exercises DB Table
    """

    reps_json = json.dumps(exercise_data.get('reps') or [])
    
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE plan_exercises
                SET warmup_sets = :warmup_sets, working_sets = :working_sets, reps = :reps,
                    planned_weight = NULL, rest_between_sets_min = :rest_between_sets_min,
                    rest_between_sets_max = :rest_between_sets_max, rest_after_exercise_min = :rest_after_exercise_min,
                    rest_after_exercise_max = :rest_after_exercise_max, trainer_note = :trainer_note
                WHERE plan_exercise_id = :plan_exercise_id
            """),
            {
                "warmup_sets": exercise_data.get('warmup_sets'),
                "working_sets": exercise_data.get('working_sets'),
                "reps": reps_json,
                "rest_between_sets_min": exercise_data.get('rest_between_sets_min'),
                "rest_between_sets_max": exercise_data.get('rest_between_sets_max'),
                "rest_after_exercise_min": exercise_data.get('rest_after_exercise_min'),
                "rest_after_exercise_max": exercise_data.get('rest_after_exercise_max'),
                "trainer_note": exercise_data.get('trainer_note'),
                "plan_exercise_id": existing_id
            }
        )


# ============================================
# MID-LEVEL FUNCTIONS
# ============================================

def create_workout_session(engine, plan_id, session_date, day_of_week):
    """
    Creates new workout session in DB and returns its session_id
    """
    
    with engine.begin() as conn:
        # Check if session already exists
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
        
        existing_id = result.scalar()
        
        if existing_id:
            return existing_id
        
        # Insert new workout session
        result = conn.execute(
            text("""
                INSERT INTO workout_sessions (plan_id, session_date, day_of_week)
                VALUES (:plan_id, :session_date, :day_of_week)
                RETURNING session_id
            """),
            {
                "plan_id": plan_id,
                "session_date": session_date,
                "day_of_week": day_of_week
            }
        )
        
        return result.scalar()


def process_single_exercise(engine, plan_id, day_of_week, exercise):
    """
    Processes a single exercise
    """
    
    # Get or create exercise
    exercise_id = get_or_create_exercise(engine, exercise['exercise'])
    
    # Prepare exercise data
    exercise_data = {
        'exercise_id': exercise_id,
        'warmup_sets': exercise.get('warmup_sets'),
        'working_sets': exercise.get('working_sets'),
        'reps': exercise.get('reps'),
        'rest_between_sets_min': exercise.get('rest_between_sets_min'),
        'rest_between_sets_max': exercise.get('rest_between_sets_max'),
        'rest_after_exercise_min': exercise.get('rest_after_exercise_min'),
        'rest_after_exercise_max': exercise.get('rest_after_exercise_max'),
        'trainer_note': exercise.get('trainer_note')
    }
    
    # Check if exercise already exists for given plan and day of week
    
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT plan_exercise_id
                FROM plan_exercises
                WHERE plan_id = :plan_id
                    AND exercise_id = :exercise_id
                    AND day_of_week = :day_of_week
                """
            ),{
                "plan_id": plan_id,
                "exercise_id": exercise_id,
                "day_of_week": day_of_week
            }
        )

    existing_id = result.scalar()

    if existing_id:
        # Update plan exercise
        update_plan_exercise(engine, existing_id, exercise_data)
        log(f"Plan exercise {exercise['exercise']} [id: {existing_id}] Updated")
    else:
        # Insert into plan
        insert_plan_exercise(engine, plan_id, day_of_week, exercise_data)
        log_exercise_added(exercise['exercise'], exercise_data)


def process_day(engine, plan_id, day_key, day_exercises, day_mapping):
    """
    Processes all exercises for a given day
    """
    
    day_of_week = day_mapping.get(day_key)
    if not day_of_week:
        log(f"Skipping {day_key} (no mapping)")
        return
    
    log(f"Processing {day_key} ({day_of_week}):")
    
    for exercise in day_exercises:
        process_single_exercise(engine, plan_id, day_of_week, exercise)


# ============================================
# MAIN FUNCTIONS
# ============================================

def save_plan_to_database(json_file, plan_name, start_date):
    """
    Saves training plan from JSON file to database
    """
    
    engine = connect_to_database()
    
    try:
        # Load data from JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            training_plan = json.load(f)
        
        # Check if plan already exists
        if plan_exists(engine, plan_name):
            log(f"Plan: '{plan_name}' already exists in database.",
                level="ERROR", echo=True)
            plan_id = get_plan_id(engine, plan_name)
        else:
            plan_id = create_new_plan(engine, plan_name, start_date)
            log(f"Created new plan: {plan_name} (ID: {plan_id})")
        
        # Day mapping dictionary
        day_mapping = {
            "Day 1": "Monday", "Day 2": "Tuesday", "Day 3": "Wednesday",
            "Day 4": "Thursday", "Day 5": "Friday", "Day 6": "Saturday",
            "Day 7": "Sunday"
        }
        
        # Process each day
        for day_key, day_exercises in training_plan.items():
            process_day(engine, plan_id, day_key, day_exercises, day_mapping)
        
        log(f"Plan '{plan_name}' successfully loaded to database")
        
    except Exception as e:
        log(f"Error loading plan '{plan_name}' to database ({e})",
            level="ERROR", echo=True)
        raise
    
    finally:
        engine.dispose()

def save_workout_to_database(workout_file):
    engine = connect_to_database()

    try:

        # Load workout file to pandas DF and cleanup column names

        df = pd.read_excel(workout_file)
        df.columns = df.columns.str.replace(' ', '_').str.replace('(', '').str.replace(')', '')

        # Get plan_name and day_of_week from filename

        workout_path = Path(workout_file)
        parts = workout_path.stem.split("_")
        plan_name = f"{parts[1].title()} {parts[2]}"
        day_of_week = day = parts[3].title()

        # Get plan_id

        plan_id = get_plan_id(engine, plan_name)

        # Get session_date from user (todays date by default)

        session_date = workout_day_selector()

        # Create new session in DB or check if it already exists and return session_id

        session_id = create_workout_session(engine, plan_id, session_date, day_of_week)

        session_exercises = []

        for row in df.itertuples():
            sets_done = count_checked_checkboxes(df, row.Index)
            exercise_id = get_or_create_exercise(engine, row.Exercise)

            # Check Reps column for NaN and return only first value

            reps_all = row.Reps
            if pd.notna(reps_all):
                first_val = str(reps_all).split(',')[0].strip()

                reps = -1 if first_val.lower() == "amrap" else int(first_val)
            else:
                reps = None

            # Check Weight column for NaN

            if pd.notna(row.Weight_kg):
                weight_used = row.Weight_kg
            else:
                weight_used = None

            # Check Notes for NaN

            if pd.notna(row.Notes):
                notes = row.Notes
            else:
                notes = None
            

            ex_details = {
                "session_id": session_id,
                "exercise_id": exercise_id,
                "working_set_number": sets_done,
                "reps": reps,
                "weight_used": weight_used,
                "notes": notes
            }
            session_exercises.append(ex_details)

        # Import session exercises to DB

        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO session_exercises (session_id, exercise_id, working_set_number, reps_completed, weight_used, notes)
                    VALUES (:session_id, :exercise_id, :working_set_number, :reps, :weight_used, :notes)
                    ON CONFLICT (session_id, exercise_id)
                    DO UPDATE SET
                        working_set_number = EXCLUDED.working_set_number,
                        reps_completed = EXCLUDED.reps_completed,
                        weight_used = EXCLUDED.weight_used,
                        notes = EXCLUDED.notes
                """), session_exercises
            )
        print("\nImport completed")
        input("Press Enter to continue...")
    except Exception as e:
        log(f"Error importing workout day to database ({e})",
            level="ERROR", echo=True)
        raise
    
    finally:
        engine.dispose()
