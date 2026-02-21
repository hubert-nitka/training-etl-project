-- Sample data for fitness training database
-- This file contains example data to demonstrate the database structure

-- Insert sample exercises
INSERT INTO exercises (exercise_name, muscle_group) VALUES
('Bench Press', 'Chest'),
('Squat', 'Legs'),
('Deadlift', 'Back'),
('Shoulder Press', 'Shoulders'),
('Pull-ups', 'Back'),
('Bicep Curls', 'Arms'),
('Leg Press', 'Legs'),
('Lat Pulldown', 'Back');

-- Insert sample training plans
INSERT INTO training_plans (plan_name, start_date, end_date) VALUES
('Plan Styczeń 2025', '2025-01-01', '2025-01-31'),
('Plan Luty 2025', '2025-02-01', NULL);

-- Insert sample plan exercises for January plan (plan_id = 1)
-- Monday workout
INSERT INTO plan_exercises (plan_id, exercise_id, day_of_week, sets, reps, planned_weight) VALUES
(1, 1, 'Monday', 3, 8, 35.00),
(1, 4, 'Monday', 3, 10, 20.00),
(1, 6, 'Monday', 3, 12, 12.50);

-- Wednesday workout
INSERT INTO plan_exercises (plan_id, exercise_id, day_of_week, sets, reps, planned_weight) VALUES
(1, 2, 'Wednesday', 4, 8, 60.00),
(1, 7, 'Wednesday', 3, 10, 80.00);

-- Friday workout
INSERT INTO plan_exercises (plan_id, exercise_id, day_of_week, sets, reps, planned_weight) VALUES
(1, 3, 'Friday', 3, 6, 80.00),
(1, 5, 'Friday', 3, 8, 0.00),  -- bodyweight
(1, 8, 'Friday', 3, 10, 45.00);

-- Insert sample workout sessions
INSERT INTO workout_sessions (plan_id, session_date, day_of_week) VALUES
(1, '2025-01-06', 'Monday'),
(1, '2025-01-08', 'Wednesday'),
(1, '2025-01-10', 'Friday'),
(1, '2025-01-13', 'Monday');

-- Insert sample session exercises (what was actually performed)
-- Session 1: Monday, 2025-01-06
-- Bench Press - 3 sets
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(1, 1, 1, 8, 35.00, NULL),
(1, 1, 2, 8, 35.00, NULL),
(1, 1, 3, 7, 35.00, 'Struggled on last rep');

-- Shoulder Press - 3 sets
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(1, 4, 1, 10, 20.00, NULL),
(1, 4, 2, 10, 20.00, NULL),
(1, 4, 3, 9, 20.00, 'Slightly tired');

-- Bicep Curls - 3 sets
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(1, 6, 1, 12, 12.50, NULL),
(1, 6, 2, 12, 12.50, NULL),
(1, 6, 3, 11, 12.50, NULL);

-- Session 2: Wednesday, 2025-01-08
-- Squat - 4 sets
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(2, 2, 1, 8, 60.00, NULL),
(2, 2, 2, 8, 60.00, NULL),
(2, 2, 3, 8, 60.00, NULL),
(2, 2, 4, 7, 60.00, 'Last set harder');

-- Leg Press - 3 sets
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(2, 7, 1, 10, 80.00, NULL),
(2, 7, 2, 10, 80.00, NULL),
(2, 7, 3, 10, 80.00, NULL);

-- Session 3: Friday, 2025-01-10
-- Deadlift - 3 sets
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(3, 3, 1, 6, 80.00, NULL),
(3, 3, 2, 6, 80.00, NULL),
(3, 3, 3, 5, 80.00, 'Felt heavy');

-- Pull-ups - 3 sets (bodyweight)
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(3, 5, 1, 8, 0.00, 'Bodyweight'),
(3, 5, 2, 7, 0.00, 'Bodyweight'),
(3, 5, 3, 6, 0.00, 'Bodyweight, getting tired');

-- Lat Pulldown - 3 sets
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(3, 8, 1, 10, 45.00, NULL),
(3, 8, 2, 10, 45.00, NULL),
(3, 8, 3, 9, 45.00, NULL);

-- Session 4: Monday, 2025-01-13
-- Bench Press - weight increased!
INSERT INTO session_exercises (session_id, exercise_id, set_number, reps_completed, weight_used, notes) VALUES
(4, 1, 1, 8, 37.50, 'Increased weight, felt good'),
(4, 1, 2, 8, 37.50, NULL),
(4, 1, 3, 7, 37.50, 'Progress!');
