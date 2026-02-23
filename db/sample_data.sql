-- Sample data for fitness training database
-- This file contains example data to demonstrate the database structure

BEGIN;

-- Insert sample exercises
INSERT INTO exercises (exercise_name, muscle_group) VALUES
('Bench Press', 'Chest'),
('Squat', 'Legs'),
('Deadlift', 'Back'),
('Shoulder Press', 'Shoulders'),
('Pull-ups', 'Back'),
('Bicep Curls', 'Arms'),
('Leg Press', 'Legs'),
('Lat Pulldown', 'Back'),
('Dumbbell Flyes', 'Chest'),
('Lunges', 'Legs');

-- Insert sample training plans
INSERT INTO training_plans (plan_name, start_date, end_date) VALUES
('Plan Styczeń 2025', '2025-01-01', '2025-01-31'),
('Plan Luty 2025', '2025-02-01', NULL);

-- Insert sample plan exercises for January plan (plan_id = 1)
-- Monday workout
INSERT INTO plan_exercises (plan_id, exercise_id, day_of_week, warmup_sets, working_sets, reps, planned_weight, rest_between_sets_min, rest_between_sets_max, rest_after_exercise_min, rest_after_exercise_max) VALUES
(1, 1, 'Monday', 2, 3, '[8, 8, 8]', 35.00, 120, 180, 120, 120),
(1, 4, 'Monday', 1, 3, '[10, 10, 10]', 20.00, 90, 120, 90, 120),
(1, 6, 'Monday', 1, 3, '[12, 12, 12]', 12.50, 60, 90, 60, 90);

-- Wednesday workout
INSERT INTO plan_exercises (plan_id, exercise_id, day_of_week, warmup_sets, working_sets, reps, planned_weight, rest_between_sets_min, rest_between_sets_max, rest_after_exercise_min, rest_after_exercise_max) VALUES
(1, 2, 'Wednesday', 2, 4, '[8, 8, 8, 8]', 60.00, 150, 180, 120, 180),
(1, 7, 'Wednesday', 1, 3, '[10, 10, 10]', 80.00, 90, 120, 90, 120);

-- Friday workout
INSERT INTO plan_exercises (plan_id, exercise_id, day_of_week, warmup_sets, working_sets, reps, planned_weight, rest_between_sets_min, rest_between_sets_max, rest_after_exercise_min, rest_after_exercise_max) VALUES
(1, 3, 'Friday', 2, 3, '[6, 6, 6]', 80.00, 180, 210, 120, 180),
(1, 5, 'Friday', 1, 3, '[8, 8, 8]', 0.00, 120, 150, 90, 120),
(1, 8, 'Friday', 1, 3, '[10, 10, 10]', 45.00, 90, 120, 60, 90);

-- Insert sample plan exercises for February plan (plan_id = 2)
-- Monday workout
INSERT INTO plan_exercises (plan_id, exercise_id, day_of_week, warmup_sets, working_sets, reps, planned_weight, rest_between_sets_min, rest_between_sets_max, rest_after_exercise_min, rest_after_exercise_max) VALUES
(2, 1, 'Monday', 2, 3, '[8, 8, 8]', 37.50, 120, 180, 120, 120),
(2, 9, 'Monday', 1, 3, '[12, 12, 12]', 15.00, 90, 120, 90, 120);

-- Wednesday workout  
INSERT INTO plan_exercises (plan_id, exercise_id, day_of_week, warmup_sets, working_sets, reps, planned_weight, rest_between_sets_min, rest_between_sets_max, rest_after_exercise_min, rest_after_exercise_max) VALUES
(2, 2, 'Wednesday', 2, 4, '[10, 10, 10, 10]', 65.00, 150, 180, 120, 180),
(2, 10, 'Wednesday', 1, 3, '[12, 12, 12]', 0.00, 90, 120, 90, 120);

-- Friday workout
INSERT INTO plan_exercises (plan_id, exercise_id, day_of_week, warmup_sets, working_sets, reps, planned_weight, rest_between_sets_min, rest_between_sets_max, rest_after_exercise_min, rest_after_exercise_max) VALUES
(2, 3, 'Friday', 2, 3, '[6, 6, 6]', 85.00, 180, 210, 120, 180),
(2, 8, 'Friday', 1, 3, '[10, 10, 10]', 47.50, 90, 120, NULL, NULL);

-- Insert sample workout sessions (actual workouts performed)
-- Week 1 of January
INSERT INTO workout_sessions (plan_id, session_date, day_of_week) VALUES
(1, '2025-01-06', 'Monday'),
(1, '2025-01-08', 'Wednesday'),
(1, '2025-01-10', 'Friday');

-- Week 2 of January
INSERT INTO workout_sessions (plan_id, session_date, day_of_week) VALUES
(1, '2025-01-13', 'Monday'),
(1, '2025-01-15', 'Wednesday'),
(1, '2025-01-17', 'Friday');

-- Week 1 of February
INSERT INTO workout_sessions (plan_id, session_date, day_of_week) VALUES
(2, '2025-02-03', 'Monday'),
(2, '2025-02-05', 'Wednesday');

-- Insert sample session exercises (what was actually performed)
-- Session 1: Monday, 2025-01-06
-- Bench Press - working sets
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(1, 1, 1, 8, 35.00, NULL),
(1, 1, 2, 8, 35.00, NULL),
(1, 1, 3, 7, 35.00, 'Struggled on last rep');

-- Shoulder Press - working sets
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(1, 4, 1, 10, 20.00, NULL),
(1, 4, 2, 10, 20.00, NULL),
(1, 4, 3, 9, 20.00, 'Slightly tired');

-- Bicep Curls - working sets
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(1, 6, 1, 12, 12.50, NULL),
(1, 6, 2, 12, 12.50, NULL),
(1, 6, 3, 11, 12.50, NULL);

-- Session 2: Wednesday, 2025-01-08
-- Squat - working sets
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(2, 2, 1, 8, 60.00, NULL),
(2, 2, 2, 8, 60.00, NULL),
(2, 2, 3, 8, 60.00, NULL),
(2, 2, 4, 7, 60.00, 'Last set harder');

-- Leg Press - working sets
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(2, 7, 1, 10, 80.00, NULL),
(2, 7, 2, 10, 80.00, NULL),
(2, 7, 3, 10, 80.00, NULL);

-- Session 3: Friday, 2025-01-10
-- Deadlift - working sets
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(3, 3, 1, 6, 80.00, NULL),
(3, 3, 2, 6, 80.00, NULL),
(3, 3, 3, 5, 80.00, 'Felt heavy');

-- Pull-ups - working sets (bodyweight)
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(3, 5, 1, 8, 0.00, 'Bodyweight'),
(3, 5, 2, 7, 0.00, 'Bodyweight'),
(3, 5, 3, 6, 0.00, 'Bodyweight, getting tired');

-- Lat Pulldown - working sets
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(3, 8, 1, 10, 45.00, NULL),
(3, 8, 2, 10, 45.00, NULL),
(3, 8, 3, 9, 45.00, NULL);

-- Session 4: Monday, 2025-01-13 (showing progression)
-- Bench Press - weight increased!
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(4, 1, 1, 8, 37.50, 'Increased weight, felt good'),
(4, 1, 2, 8, 37.50, NULL),
(4, 1, 3, 8, 37.50, 'All reps completed - progress!');

-- Shoulder Press
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(4, 4, 1, 10, 20.00, NULL),
(4, 4, 2, 10, 20.00, NULL),
(4, 4, 3, 10, 20.00, 'Felt easier this week');

-- Bicep Curls
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(4, 6, 1, 12, 12.50, NULL),
(4, 6, 2, 12, 12.50, NULL),
(4, 6, 3, 12, 12.50, 'All reps completed');

-- Session 7: Monday, 2025-02-03 (February plan)
-- Bench Press - continued progression
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(7, 1, 1, 8, 37.50, NULL),
(7, 1, 2, 8, 37.50, NULL),
(7, 1, 3, 7, 37.50, 'Good session');

-- Dumbbell Flyes
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(7, 9, 1, 12, 15.00, NULL),
(7, 9, 2, 12, 15.00, NULL),
(7, 9, 3, 11, 15.00, NULL);

COMMIT;