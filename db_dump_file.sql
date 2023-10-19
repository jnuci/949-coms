--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: comments_cleaned; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comments_cleaned (
    video_id character varying NOT NULL,
    comment_id character varying NOT NULL,
    content character varying NOT NULL,
    published timestamp with time zone NOT NULL,
    username character varying NOT NULL,
    profile_image character varying NOT NULL,
    likes integer NOT NULL
);


ALTER TABLE public.comments_cleaned OWNER TO postgres;

--
-- Name: comments_raw; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comments_raw (
    video_id character varying NOT NULL,
    comment_id character varying NOT NULL,
    content character varying NOT NULL,
    published timestamp with time zone NOT NULL,
    username character varying NOT NULL,
    profile_image character varying NOT NULL,
    likes integer NOT NULL
);


ALTER TABLE public.comments_raw OWNER TO postgres;

--
-- Name: comments_cleaned comments_cleaned_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments_cleaned
    ADD CONSTRAINT comments_cleaned_pkey PRIMARY KEY (comment_id);


--
-- Name: comments_raw comments_raw_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments_raw
    ADD CONSTRAINT comments_raw_pkey PRIMARY KEY (comment_id);


--
-- PostgreSQL database dump complete
--

