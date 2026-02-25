"""
Load data gathered by webscraper from Training portal into database
"""

import json
from src.utils import connect_to_database, log

# ============================================
# HELPER FUNCTIONS
# ============================================

def plan_exists(cur, plan_name):

    """Checks if a plan with given name already exists"""

    cur.execute("""
        SELECT plan_id FROM training_plans WHERE plan_name = %s
    """, (plan_name,))
    return cur.fetchone()

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
        SELECT exercise_id FROM exercises WHERE exercise_name = %s
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

def log_exercise_added(exercise_name, exercise_data):

    """Logs information about added exercise"""

    warmup = exercise_data.get('warmup_sets') or 0
    working = exercise_data.get('working_sets') or 0
    reps_json = json.dumps(exercise_data.get('reps') or [])
    log(f"{exercise_name}: {warmup} + {working} sets, reps={reps_json} added to plan")

# ============================================
# MID-LEVEL FUNCTIONS
# ============================================

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

def save_to_database(json_file, plan_name, start_date):

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
