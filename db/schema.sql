SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

CREATE TABLE public.exercises (
    exercise_id integer NOT NULL,
    exercise_name character varying(200) NOT NULL,
    muscle_group character varying(100)
);


ALTER TABLE public.exercises OWNER TO postgres;

CREATE SEQUENCE public.exercises_exercise_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exercises_exercise_id_seq OWNER TO postgres;

ALTER SEQUENCE public.exercises_exercise_id_seq OWNED BY public.exercises.exercise_id;

CREATE TABLE public.plan_exercises (
    plan_exercise_id integer NOT NULL,
    plan_id integer NOT NULL,
    exercise_id integer NOT NULL,
    day_of_week character varying(20) NOT NULL,
    warmup_sets integer,
    working_sets integer NOT NULL,
    reps text NOT NULL,
    planned_weight numeric(5,2),
    rest_between_sets_min integer,
    rest_between_sets_max integer,
    rest_after_exercise_min integer,
    rest_after_exercise_max integer
);


ALTER TABLE public.plan_exercises OWNER TO postgres;

CREATE SEQUENCE public.plan_exercises_plan_exercise_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.plan_exercises_plan_exercise_id_seq OWNER TO postgres;

ALTER SEQUENCE public.plan_exercises_plan_exercise_id_seq OWNED BY public.plan_exercises.plan_exercise_id;

CREATE TABLE public.session_exercises (
    session_exercise_id integer NOT NULL,
    session_id integer NOT NULL,
    exercise_id integer NOT NULL,
    working_set_number integer,
    reps_completed integer,
    weight_used numeric(5,2),
    notes text
);


ALTER TABLE public.session_exercises OWNER TO postgres;

CREATE SEQUENCE public.session_exercises_session_exercise_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.session_exercises_session_exercise_id_seq OWNER TO postgres;

ALTER SEQUENCE public.session_exercises_session_exercise_id_seq OWNED BY public.session_exercises.session_exercise_id;

CREATE TABLE public.training_plans (
    plan_id integer NOT NULL,
    plan_name character varying(50) NOT NULL,
    start_date date NOT NULL,
    end_date date
);


ALTER TABLE public.training_plans OWNER TO postgres;

CREATE SEQUENCE public.training_plans_plan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.training_plans_plan_id_seq OWNER TO postgres;

ALTER SEQUENCE public.training_plans_plan_id_seq OWNED BY public.training_plans.plan_id;

CREATE TABLE public.workout_sessions (
    session_id integer NOT NULL,
    plan_id integer NOT NULL,
    session_date date NOT NULL,
    day_of_week character varying(20) NOT NULL
);


ALTER TABLE public.workout_sessions OWNER TO postgres;

CREATE SEQUENCE public.workout_sessions_session_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workout_sessions_session_id_seq OWNER TO postgres;

ALTER SEQUENCE public.workout_sessions_session_id_seq OWNED BY public.workout_sessions.session_id;

ALTER TABLE ONLY public.exercises ALTER COLUMN exercise_id SET DEFAULT nextval('public.exercises_exercise_id_seq'::regclass);

ALTER TABLE ONLY public.plan_exercises ALTER COLUMN plan_exercise_id SET DEFAULT nextval('public.plan_exercises_plan_exercise_id_seq'::regclass);

ALTER TABLE ONLY public.session_exercises ALTER COLUMN session_exercise_id SET DEFAULT nextval('public.session_exercises_session_exercise_id_seq'::regclass);

ALTER TABLE ONLY public.training_plans ALTER COLUMN plan_id SET DEFAULT nextval('public.training_plans_plan_id_seq'::regclass);

ALTER TABLE ONLY public.workout_sessions ALTER COLUMN session_id SET DEFAULT nextval('public.workout_sessions_session_id_seq'::regclass);

ALTER TABLE ONLY public.exercises
    ADD CONSTRAINT exercises_pkey PRIMARY KEY (exercise_id);

ALTER TABLE ONLY public.session_exercises
    ADD CONSTRAINT only_one_exercise_per_session UNIQUE (session_id, exercise_id);

ALTER TABLE ONLY public.plan_exercises
    ADD CONSTRAINT plan_exercises_pkey PRIMARY KEY (plan_exercise_id);

ALTER TABLE ONLY public.session_exercises
    ADD CONSTRAINT session_exercises_pkey PRIMARY KEY (session_exercise_id);

ALTER TABLE ONLY public.training_plans
    ADD CONSTRAINT training_plans_pkey PRIMARY KEY (plan_id);

ALTER TABLE ONLY public.workout_sessions
    ADD CONSTRAINT workout_sessions_pkey PRIMARY KEY (session_id);

ALTER TABLE ONLY public.plan_exercises
    ADD CONSTRAINT plan_exercises_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercises(exercise_id) NOT VALID;

ALTER TABLE ONLY public.plan_exercises
    ADD CONSTRAINT plan_exercises_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.training_plans(plan_id) NOT VALID;

ALTER TABLE ONLY public.session_exercises
    ADD CONSTRAINT session_exercises_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercises(exercise_id) NOT VALID;

ALTER TABLE ONLY public.session_exercises
    ADD CONSTRAINT session_exercises_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.workout_sessions(session_id) NOT VALID;

ALTER TABLE ONLY public.workout_sessions
    ADD CONSTRAINT workout_sessions_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.training_plans(plan_id) NOT VALID;

ALTER TABLE ONLY public.plan_exercises
    ADD CONSTRAINT one_exercise_per_day_per_plan UNIQUE (plan_id, exercise_id, day_of_week);