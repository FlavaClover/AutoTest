--
-- PostgreSQL database dump
--

-- Dumped from database version 14.3
-- Dumped by pg_dump version 14.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: users; Type: TABLE; Schema: public; Owner: zaurbektedeev
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    login character varying(256) NOT NULL,
    last_login timestamp with time zone,
    pwd character varying(1024) NOT NULL,
    salt character varying(1024) NOT NULL
);


ALTER TABLE public.users OWNER TO zaurbektedeev;

--
-- Name: f_add_user(character varying, character varying); Type: FUNCTION; Schema: public; Owner: zaurbektedeev
--

CREATE FUNCTION public.f_add_user(v_login character varying, v_pass character varying) RETURNS SETOF public.users
    LANGUAGE plpgsql
    AS $$
declare
	new_user_id int;
	new_user "users"%rowtype;
begin 
	insert into users(login, pwd) values(v_login, crypt(v_pass, gen_salt('bf'))) returning id into new_user_id;

	return query
	select * from users where id = new_user_id;
end;
$$;


ALTER FUNCTION public.f_add_user(v_login character varying, v_pass character varying) OWNER TO zaurbektedeev;

--
-- Name: f_cancel_session(uuid); Type: FUNCTION; Schema: public; Owner: zaurbektedeev
--

CREATE FUNCTION public.f_cancel_session(v_session uuid) RETURNS void
    LANGUAGE plpgsql
    AS $$
begin 
	update users_sessions set session_expire = (select now()::timestamp) - (15 * interval '1 sec')
	where session_uuid = v_session;
end



$$;


ALTER FUNCTION public.f_cancel_session(v_session uuid) OWNER TO zaurbektedeev;

--
-- Name: f_create_session(bigint); Type: FUNCTION; Schema: public; Owner: zaurbektedeev
--

CREATE FUNCTION public.f_create_session(v_user_id bigint) RETURNS uuid
    LANGUAGE plpgsql
    AS $$
declare 
	v_session uuid;
begin 
	    SELECT md5(random()::text || clock_timestamp()::text)::uuid
    	into v_session; 
    
    	insert into users_sessions (user_id, session_uuid, session_start, session_expire) 
    	values (v_user_id, v_session, (select now()::timestamp), (select now()::timestamp) + (20 * interval '1 minute'));
    
    	update users set last_login = (select now()::timestamp) where id = v_user_id;
    
    
    	return v_session;
end;


$$;


ALTER FUNCTION public.f_create_session(v_user_id bigint) OWNER TO zaurbektedeev;

--
-- Name: f_get_user(character varying, character varying); Type: FUNCTION; Schema: public; Owner: zaurbektedeev
--

CREATE FUNCTION public.f_get_user(v_login character varying, v_pass character varying) RETURNS SETOF public.users
    LANGUAGE plpgsql
    AS $$
begin
	return query
	select * from users where login = v_login and pwd = crypt(v_pass, pwd);
end;
$$;


ALTER FUNCTION public.f_get_user(v_login character varying, v_pass character varying) OWNER TO zaurbektedeev;

--
-- Name: f_get_user_by_session(uuid); Type: FUNCTION; Schema: public; Owner: zaurbektedeev
--

CREATE FUNCTION public.f_get_user_by_session(v_session uuid) RETURNS SETOF public.users
    LANGUAGE plpgsql
    AS $$
begin 
	return query
	select u.id, u.login, u.last_login, u.pwd, u.salt from users u
	inner join users_sessions us on u.id = us.user_id
	where us.session_uuid = v_session and (select now()::timestamp) < session_expire;
	
end;
$$;


ALTER FUNCTION public.f_get_user_by_session(v_session uuid) OWNER TO zaurbektedeev;

--
-- Name: f_update_session(uuid); Type: FUNCTION; Schema: public; Owner: zaurbektedeev
--

CREATE FUNCTION public.f_update_session(v_session uuid) RETURNS void
    LANGUAGE plpgsql
    AS $$
begin

	update users_sessions us set
	session_expire = (select now()::timestamp) + (20 * interval '1 minute')
	where session_uuid = v_session;
end

$$;


ALTER FUNCTION public.f_update_session(v_session uuid) OWNER TO zaurbektedeev;

--
-- Name: problems; Type: TABLE; Schema: public; Owner: zaurbektedeev
--

CREATE TABLE public.problems (
    id bigint NOT NULL,
    task text NOT NULL,
    input_desc text NOT NULL,
    output_desc text NOT NULL
);


ALTER TABLE public.problems OWNER TO zaurbektedeev;

--
-- Name: problems_id_seq; Type: SEQUENCE; Schema: public; Owner: zaurbektedeev
--

CREATE SEQUENCE public.problems_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.problems_id_seq OWNER TO zaurbektedeev;

--
-- Name: problems_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zaurbektedeev
--

ALTER SEQUENCE public.problems_id_seq OWNED BY public.problems.id;


--
-- Name: problems_tests; Type: TABLE; Schema: public; Owner: zaurbektedeev
--

CREATE TABLE public.problems_tests (
    id bigint NOT NULL,
    id_problem bigint,
    input_file bytea NOT NULL,
    output_file bytea NOT NULL
);


ALTER TABLE public.problems_tests OWNER TO zaurbektedeev;

--
-- Name: problems_tests_id_seq; Type: SEQUENCE; Schema: public; Owner: zaurbektedeev
--

CREATE SEQUENCE public.problems_tests_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.problems_tests_id_seq OWNER TO zaurbektedeev;

--
-- Name: problems_tests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zaurbektedeev
--

ALTER SEQUENCE public.problems_tests_id_seq OWNED BY public.problems_tests.id;


--
-- Name: solve_statuses; Type: TABLE; Schema: public; Owner: zaurbektedeev
--

CREATE TABLE public.solve_statuses (
    id integer NOT NULL,
    status character varying(256) NOT NULL
);


ALTER TABLE public.solve_statuses OWNER TO zaurbektedeev;

--
-- Name: solve_statuses_id_seq; Type: SEQUENCE; Schema: public; Owner: zaurbektedeev
--

CREATE SEQUENCE public.solve_statuses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.solve_statuses_id_seq OWNER TO zaurbektedeev;

--
-- Name: solve_statuses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zaurbektedeev
--

ALTER SEQUENCE public.solve_statuses_id_seq OWNED BY public.solve_statuses.id;


--
-- Name: solve_tests; Type: TABLE; Schema: public; Owner: zaurbektedeev
--

CREATE TABLE public.solve_tests (
    id bigint NOT NULL,
    id_solve bigint NOT NULL,
    result boolean,
    actual bytea,
    expected bytea NOT NULL,
    input bytea NOT NULL,
    comment text
);


ALTER TABLE public.solve_tests OWNER TO zaurbektedeev;

--
-- Name: solve_tests_id_seq; Type: SEQUENCE; Schema: public; Owner: zaurbektedeev
--

CREATE SEQUENCE public.solve_tests_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.solve_tests_id_seq OWNER TO zaurbektedeev;

--
-- Name: solve_tests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zaurbektedeev
--

ALTER SEQUENCE public.solve_tests_id_seq OWNED BY public.solve_tests.id;


--
-- Name: solves; Type: TABLE; Schema: public; Owner: zaurbektedeev
--

CREATE TABLE public.solves (
    id bigint NOT NULL,
    id_problem bigint NOT NULL,
    id_user bigint NOT NULL,
    solve_status character varying(256) DEFAULT 'running'::character varying NOT NULL,
    count_ok_tests integer DEFAULT 0 NOT NULL,
    code bytea NOT NULL,
    language character varying(128) NOT NULL
);


ALTER TABLE public.solves OWNER TO zaurbektedeev;

--
-- Name: solves_detailed; Type: VIEW; Schema: public; Owner: zaurbektedeev
--

CREATE VIEW public.solves_detailed AS
 SELECT s.id,
    u.login,
    s.count_ok_tests,
    p.task
   FROM ((public.solves s
     JOIN public.users u ON ((u.id = s.id_user)))
     JOIN public.problems p ON ((p.id = s.id_problem)));


ALTER TABLE public.solves_detailed OWNER TO zaurbektedeev;

--
-- Name: solves_id_seq; Type: SEQUENCE; Schema: public; Owner: zaurbektedeev
--

CREATE SEQUENCE public.solves_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.solves_id_seq OWNER TO zaurbektedeev;

--
-- Name: solves_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zaurbektedeev
--

ALTER SEQUENCE public.solves_id_seq OWNED BY public.solves.id;


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: zaurbektedeev
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO zaurbektedeev;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zaurbektedeev
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: users_sessions; Type: TABLE; Schema: public; Owner: zaurbektedeev
--

CREATE TABLE public.users_sessions (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    session_uuid uuid NOT NULL,
    session_start timestamp with time zone NOT NULL,
    session_expire timestamp with time zone NOT NULL
);


ALTER TABLE public.users_sessions OWNER TO zaurbektedeev;

--
-- Name: users_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: zaurbektedeev
--

CREATE SEQUENCE public.users_sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_sessions_id_seq OWNER TO zaurbektedeev;

--
-- Name: users_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zaurbektedeev
--

ALTER SEQUENCE public.users_sessions_id_seq OWNED BY public.users_sessions.id;


--
-- Name: problems id; Type: DEFAULT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.problems ALTER COLUMN id SET DEFAULT nextval('public.problems_id_seq'::regclass);


--
-- Name: problems_tests id; Type: DEFAULT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.problems_tests ALTER COLUMN id SET DEFAULT nextval('public.problems_tests_id_seq'::regclass);


--
-- Name: solve_statuses id; Type: DEFAULT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.solve_statuses ALTER COLUMN id SET DEFAULT nextval('public.solve_statuses_id_seq'::regclass);


--
-- Name: solve_tests id; Type: DEFAULT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.solve_tests ALTER COLUMN id SET DEFAULT nextval('public.solve_tests_id_seq'::regclass);


--
-- Name: solves id; Type: DEFAULT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.solves ALTER COLUMN id SET DEFAULT nextval('public.solves_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: users_sessions id; Type: DEFAULT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.users_sessions ALTER COLUMN id SET DEFAULT nextval('public.users_sessions_id_seq'::regclass);

--
-- Name: problems_id_seq; Type: SEQUENCE SET; Schema: public; Owner: zaurbektedeev
--

SELECT pg_catalog.setval('public.problems_id_seq', 3, true);


--
-- Name: problems_tests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: zaurbektedeev
--

SELECT pg_catalog.setval('public.problems_tests_id_seq', 8, true);


--
-- Name: solve_statuses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: zaurbektedeev
--

SELECT pg_catalog.setval('public.solve_statuses_id_seq', 1, false);


--
-- Name: solve_tests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: zaurbektedeev
--

SELECT pg_catalog.setval('public.solve_tests_id_seq', 36, true);


--
-- Name: solves_id_seq; Type: SEQUENCE SET; Schema: public; Owner: zaurbektedeev
--

SELECT pg_catalog.setval('public.solves_id_seq', 41, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: zaurbektedeev
--

SELECT pg_catalog.setval('public.users_id_seq', 13, true);


--
-- Name: users_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: zaurbektedeev
--

SELECT pg_catalog.setval('public.users_sessions_id_seq', 152, true);


--
-- Name: problems problems_pkey; Type: CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.problems
    ADD CONSTRAINT problems_pkey PRIMARY KEY (id);


--
-- Name: problems_tests problems_tests_pkey; Type: CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.problems_tests
    ADD CONSTRAINT problems_tests_pkey PRIMARY KEY (id);


--
-- Name: solve_statuses solve_statuses_pkey; Type: CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.solve_statuses
    ADD CONSTRAINT solve_statuses_pkey PRIMARY KEY (id);


--
-- Name: solve_tests solve_tests_pkey; Type: CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.solve_tests
    ADD CONSTRAINT solve_tests_pkey PRIMARY KEY (id);


--
-- Name: solves solves_pkey; Type: CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.solves
    ADD CONSTRAINT solves_pkey PRIMARY KEY (id);


--
-- Name: solve_statuses status_uq; Type: CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.solve_statuses
    ADD CONSTRAINT status_uq UNIQUE (status);


--
-- Name: users users_login_key; Type: CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_login_key UNIQUE (login);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users_sessions users_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.users_sessions
    ADD CONSTRAINT users_sessions_pkey PRIMARY KEY (id);


--
-- Name: problems_tests id_problem_fk; Type: FK CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.problems_tests
    ADD CONSTRAINT id_problem_fk FOREIGN KEY (id_problem) REFERENCES public.problems(id) ON DELETE CASCADE;


--
-- Name: solves id_problem_fk; Type: FK CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.solves
    ADD CONSTRAINT id_problem_fk FOREIGN KEY (id_problem) REFERENCES public.problems(id);


--
-- Name: solve_tests id_solve_fk; Type: FK CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.solve_tests
    ADD CONSTRAINT id_solve_fk FOREIGN KEY (id_solve) REFERENCES public.solves(id);


--
-- Name: solves id_user_fk; Type: FK CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.solves
    ADD CONSTRAINT id_user_fk FOREIGN KEY (id_user) REFERENCES public.users(id);


--
-- Name: solves solve_status_fk; Type: FK CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.solves
    ADD CONSTRAINT solve_status_fk FOREIGN KEY (solve_status) REFERENCES public.solve_statuses(status);


--
-- Name: users_sessions user_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: zaurbektedeev
--

ALTER TABLE ONLY public.users_sessions
    ADD CONSTRAINT user_id_fk FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

