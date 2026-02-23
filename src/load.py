import json
import psycopg
from datetime import date
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, DB_HOST
from src.utils import connect_to_database, log

def save_to_database(json_file, plan_name, start_date):
    
    conn,cur = connect_to_database(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT)

    with open(json_file, 'r', encoding='utf-8') as f:
        training_plan = json.load(f)

    try:
        # Create new training plan
        cur.execute("""
            INSERT INTO training_plans (plan_name, start_date, end_date) 
            VALUES (%s, %s, NULL) 
            RETURNING plan_id;
            """,(plan_name, start_date))

        plan_id = cur.fetchone()[0]
        log(f"Created new plan: {plan_name} (ID: {plan_id})")

        day_mapping = {
            "Day 1": "Monday",
            "Day 3": "Wednesday",
            "Day 5": "Friday"
        }

        for day_key, exercises in training_plan.items():
            day_of_week = day_mapping.get(day_key)
            if not day_of_week:
                log(f"Skipping {day_key} (no mapping)")
                continue
            
            log(f"Processing {day_key} ({day_of_week}):")

            for ex in exercises:
                exercise_name = ex['exercise']

                # Check if exercise already exists in DB
                cur.execute("""
                    SELECT exercise_id 
                    FROM exercises 
                    WHERE exercise_name = %s
                    """, (exercise_name,))
                
                result = cur.fetchone()

                if result:
                    exercise_id = result[0]
                else:
                    # Add new exercise to DB
                    cur.execute("""
                        INSERT INTO exercises (exercise_name, muscle_group)
                        VALUES (%s, NULL)
                        RETURNING exercise_id
                        """, (exercise_name,))
                    exercise_id = cur.fetchone()[0]
                    log(f"Added new exercise: {exercise_name}")
                
                # Add exercise to plan
                reps_json = json.dumps(ex['reps'] if ex['reps'] else None)

                cur.execute("""
                    INSERT INTO plan_exercises(
                        plan_id, exercise_id, day_of_week,
                        warmup_sets, working_sets, reps,
                        planned_weight, rest_between_sets_min,
                        rest_between_sets_max, rest_after_exercise_min,
                        rest_after_exercise_max
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, NULL, %s, %s, %s, %s)
                """,(
                    plan_id,
                    exercise_id,
                    day_of_week,
                    ex.get('warmup_sets'),
                    ex.get('working_sets'),
                    reps_json,
                    ex.get('rest_between_sets_min'),
                    ex.get('rest_between_sets_max'),
                    ex.get('rest_after_exercise_min'),
                    ex.get('rest_after_exercise_max')
                ))

                warmup = ex.get('warmup_sets') or 0
                working = ex.get('working_sets') or 0
                log(f"{exercise_name}: {warmup} + {working} sets, reps={reps_json} added to plan '{plan_name}'")

        conn.commit()
        log(f"Plan '{plan_name}' successfully loaded to database")

    except Exception as e:
        conn.rollback()
        log(f"Error loading plan '{plan_name}' to database", level="ERROR")
        raise
    
    finally:
        cur.close()
        conn.close()
    



