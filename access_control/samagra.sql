
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: SCHEMA "public"; Type: COMMENT; Schema: -; Owner: wfiivtismscrpe
--

COMMENT ON SCHEMA "public" IS 'standard public schema';


--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS "plpgsql" WITH SCHEMA "pg_catalog";


--
-- Name: EXTENSION "plpgsql"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "plpgsql" IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: wfiivtismscrpe
--

CREATE TABLE "public"."alembic_version" (
    "version_num" character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO wfiivtismscrpe;

--
-- Name: app_contexts; Type: TABLE; Schema: public; Owner: wfiivtismscrpe
--

CREATE TABLE "public"."app_contexts" (
    "id" integer NOT NULL,
    "name" character varying(80) NOT NULL,
    "_context_credentials" "text",
    "application_id" integer,
    "created_on" timestamp without time zone,
    "last_update" timestamp without time zone,
    "is_active" boolean
);


ALTER TABLE public.app_contexts OWNER TO wfiivtismscrpe;

--
-- Name: app_contexts_id_seq; Type: SEQUENCE; Schema: public; Owner: wfiivtismscrpe
--

CREATE SEQUENCE "public"."app_contexts_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.app_contexts_id_seq OWNER TO wfiivtismscrpe;

--
-- Name: app_contexts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wfiivtismscrpe
--

ALTER SEQUENCE "public"."app_contexts_id_seq" OWNED BY "public"."app_contexts"."id";


--
-- Name: applications; Type: TABLE; Schema: public; Owner: wfiivtismscrpe
--

CREATE TABLE "public"."applications" (
    "id" integer NOT NULL,
    "name" character varying(80) NOT NULL,
    "created_on" timestamp without time zone,
    "last_update" timestamp without time zone,
    "_white_listed_ips" "text"
);


ALTER TABLE public.applications OWNER TO wfiivtismscrpe;

--
-- Name: applications_id_seq; Type: SEQUENCE; Schema: public; Owner: wfiivtismscrpe
--

CREATE SEQUENCE "public"."applications_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.applications_id_seq OWNER TO wfiivtismscrpe;

--
-- Name: applications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wfiivtismscrpe
--

ALTER SEQUENCE "public"."applications_id_seq" OWNED BY "public"."applications"."id";


--
-- Name: categories; Type: TABLE; Schema: public; Owner: wfiivtismscrpe
--

CREATE TABLE "public"."categories" (
    "id" integer NOT NULL,
    "name" character varying(80) NOT NULL,
    "created_on" timestamp without time zone,
    "last_update" timestamp without time zone
);


ALTER TABLE public.categories OWNER TO wfiivtismscrpe;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: wfiivtismscrpe
--

CREATE SEQUENCE "public"."categories_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.categories_id_seq OWNER TO wfiivtismscrpe;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wfiivtismscrpe
--

ALTER SEQUENCE "public"."categories_id_seq" OWNED BY "public"."categories"."id";


--
-- Name: user_scope_mappings; Type: TABLE; Schema: public; Owner: wfiivtismscrpe
--

CREATE TABLE "public"."user_scope_mappings" (
    "id" integer NOT NULL,
    "role" character varying(80) NOT NULL,
    "scope_id" integer,
    "created_on" timestamp without time zone,
    "last_update" timestamp without time zone
);


ALTER TABLE public.user_scope_mappings OWNER TO wfiivtismscrpe;

--
-- Name: user_scope_mappings_id_seq; Type: SEQUENCE; Schema: public; Owner: wfiivtismscrpe
--

CREATE SEQUENCE "public"."user_scope_mappings_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_scope_mappings_id_seq OWNER TO wfiivtismscrpe;

--
-- Name: user_scope_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wfiivtismscrpe
--

ALTER SEQUENCE "public"."user_scope_mappings_id_seq" OWNED BY "public"."user_scope_mappings"."id";


--
-- Name: scopes; Type: TABLE; Schema: public; Owner: wfiivtismscrpe
--

CREATE TABLE "public"."scopes" (
    "id" integer NOT NULL,
    "name" character varying(80) NOT NULL,
    "parent_scope_id" integer,
    "created_on" timestamp without time zone,
    "last_update" timestamp without time zone,
    "category_id" integer
);


ALTER TABLE public.scopes OWNER TO wfiivtismscrpe;

--
-- Name: scopes_id_seq; Type: SEQUENCE; Schema: public; Owner: wfiivtismscrpe
--

CREATE SEQUENCE "public"."scopes_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.scopes_id_seq OWNER TO wfiivtismscrpe;

--
-- Name: scopes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wfiivtismscrpe
--

ALTER SEQUENCE "public"."scopes_id_seq" OWNED BY "public"."scopes"."id";


--
-- Name: users; Type: TABLE; Schema: public; Owner: wfiivtismscrpe
--

CREATE TABLE "public"."users" (
    "id" integer NOT NULL,
    "username" character varying(80) NOT NULL,
    "first_name" character varying(80),
    "last_name" character varying(80),
    "mobile_number" character varying(80),
    "created_on" timestamp without time zone,
    "last_update" timestamp without time zone,
    "is_deleted" boolean,
    "email_verified" boolean,
    "email" character varying(80) NOT NULL,
    "password" "bytea"
);


ALTER TABLE public.users OWNER TO wfiivtismscrpe;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: wfiivtismscrpe
--

CREATE SEQUENCE "public"."users_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO wfiivtismscrpe;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wfiivtismscrpe
--

ALTER SEQUENCE "public"."users_id_seq" OWNED BY "public"."users"."id";


--
-- Name: users_user_scope_mappings; Type: TABLE; Schema: public; Owner: wfiivtismscrpe
--

CREATE TABLE "public"."users_user_scope_mappings" (
    "role_id" integer,
    "user_id" integer
);


ALTER TABLE public.users_user_scope_mappings OWNER TO wfiivtismscrpe;

--
-- Name: app_contexts id; Type: DEFAULT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."app_contexts" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."app_contexts_id_seq"'::"regclass");


--
-- Name: applications id; Type: DEFAULT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."applications" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."applications_id_seq"'::"regclass");


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."categories" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."categories_id_seq"'::"regclass");


--
-- Name: user_scope_mappings id; Type: DEFAULT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."user_scope_mappings" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."user_scope_mappings_id_seq"'::"regclass");


--
-- Name: scopes id; Type: DEFAULT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."scopes" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."scopes_id_seq"'::"regclass");


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."users" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."users_id_seq"'::"regclass");


--
-- Name: app_contexts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: wfiivtismscrpe
--

SELECT pg_catalog.setval('"public"."app_contexts_id_seq"', 2, true);


--
-- Name: applications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: wfiivtismscrpe
--

SELECT pg_catalog.setval('"public"."applications_id_seq"', 3, true);


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: wfiivtismscrpe
--

SELECT pg_catalog.setval('"public"."categories_id_seq"', 8, true);


--
-- Name: user_scope_mappings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: wfiivtismscrpe
--

SELECT pg_catalog.setval('"public"."user_scope_mappings_id_seq"', 2, true);


--
-- Name: scopes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: wfiivtismscrpe
--

SELECT pg_catalog.setval('"public"."scopes_id_seq"', 40, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: wfiivtismscrpe
--

SELECT pg_catalog.setval('"public"."users_id_seq"', 21, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."alembic_version"
    ADD CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num");


--
-- Name: app_contexts app_contexts_name_key; Type: CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."app_contexts"
    ADD CONSTRAINT "app_contexts_name_key" UNIQUE ("name");


--
-- Name: app_contexts app_contexts_pkey; Type: CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."app_contexts"
    ADD CONSTRAINT "app_contexts_pkey" PRIMARY KEY ("id");


--
-- Name: applications applications_name_key; Type: CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."applications"
    ADD CONSTRAINT "applications_name_key" UNIQUE ("name");


--
-- Name: applications applications_pkey; Type: CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."applications"
    ADD CONSTRAINT "applications_pkey" PRIMARY KEY ("id");


--
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."categories"
    ADD CONSTRAINT "categories_name_key" UNIQUE ("name");


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."categories"
    ADD CONSTRAINT "categories_pkey" PRIMARY KEY ("id");


--
-- Name: user_scope_mappings user_scope_mappings_name_key; Type: CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."user_scope_mappings"
    ADD CONSTRAINT "user_scope_mappings_name_key" UNIQUE ("name");


--
-- Name: user_scope_mappings user_scope_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."user_scope_mappings"
    ADD CONSTRAINT "user_scope_mappings_pkey" PRIMARY KEY ("id");


--
-- Name: scopes scopes_pkey; Type: CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."scopes"
    ADD CONSTRAINT "scopes_pkey" PRIMARY KEY ("id");


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_email_key" UNIQUE ("email");


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_username_key" UNIQUE ("username");


--
-- Name: app_contexts app_contexts_application_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."app_contexts"
    ADD CONSTRAINT "app_contexts_application_id_fkey" FOREIGN KEY ("application_id") REFERENCES "public"."applications"("id");


--
-- Name: user_scope_mappings user_scope_mappings_scope_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."user_scope_mappings"
    ADD CONSTRAINT "user_scope_mappings_scope_id_fkey" FOREIGN KEY ("scope_id") REFERENCES "public"."scopes"("id");


--
-- Name: scopes scopes_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."scopes"
    ADD CONSTRAINT "scopes_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "public"."categories"("id");


--
-- Name: scopes scopes_parent_scope_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."scopes"
    ADD CONSTRAINT "scopes_parent_scope_id_fkey" FOREIGN KEY ("parent_scope_id") REFERENCES "public"."scopes"("id");


--
-- Name: users_user_scope_mappings users_user_scope_mappings_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."users_user_scope_mappings"
    ADD CONSTRAINT "users_user_scope_mappings_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."user_scope_mappings"("id");


--
-- Name: users_user_scope_mappings users_user_scope_mappings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: wfiivtismscrpe
--

ALTER TABLE ONLY "public"."users_user_scope_mappings"
    ADD CONSTRAINT "users_user_scope_mappings_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id");


--
-- PostgreSQL database dump complete
--

