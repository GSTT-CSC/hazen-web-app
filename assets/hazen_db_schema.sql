--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4 (Homebrew)

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
-- Name: device; Type: TABLE; Schema: public; Owner: sophieratkai
--

CREATE TABLE public.device (
    id uuid NOT NULL,
    created_at timestamp without time zone NOT NULL,
    institution character varying(100),
    manufacturer character varying(100),
    device_model character varying(100),
    station_name character varying(100)
);


ALTER TABLE public.device OWNER TO sophieratkai;

--
-- Name: image; Type: TABLE; Schema: public; Owner: sophieratkai
--

CREATE TABLE public.image (
    id uuid NOT NULL,
    created_at timestamp without time zone NOT NULL,
    uid character varying(100),
    filename character varying(200),
    accession_number character varying(100),
    series_id uuid
);


ALTER TABLE public.image OWNER TO sophieratkai;

--
-- Name: report; Type: TABLE; Schema: public; Owner: sophieratkai
--

CREATE TABLE public.report (
    id uuid NOT NULL,
    created_at timestamp without time zone NOT NULL,
    hazen_version character varying(10),
    data jsonb,
    user_id uuid,
    series_id uuid,
    task_name character varying(100)
);


ALTER TABLE public.report OWNER TO sophieratkai;

--
-- Name: series; Type: TABLE; Schema: public; Owner: sophieratkai
--

CREATE TABLE public.series (
    id uuid NOT NULL,
    created_at timestamp without time zone NOT NULL,
    uid character varying(64),
    description character varying(100),
    series_datetime timestamp without time zone,
    has_report boolean,
    archived boolean,
    user_id uuid,
    device_id uuid,
    study_id uuid
);


ALTER TABLE public.series OWNER TO sophieratkai;

--
-- Name: study; Type: TABLE; Schema: public; Owner: sophieratkai
--

CREATE TABLE public.study (
    id uuid NOT NULL,
    created_at timestamp without time zone NOT NULL,
    uid character varying(64),
    description character varying(100),
    study_date character varying(64)
);


ALTER TABLE public.study OWNER TO sophieratkai;

--
-- Name: task; Type: TABLE; Schema: public; Owner: sophieratkai
--

CREATE TABLE public.task (
    id uuid NOT NULL,
    created_at timestamp without time zone NOT NULL,
    name character varying(100)
);


ALTER TABLE public.task OWNER TO sophieratkai;

--
-- Name: user; Type: TABLE; Schema: public; Owner: sophieratkai
--

CREATE TABLE public."user" (
    id uuid NOT NULL,
    created_at timestamp without time zone NOT NULL,
    firstname character varying(64),
    lastname character varying(64),
    institution character varying(64),
    username character varying(64),
    email character varying(320),
    password_hash character varying(128),
    last_seen timestamp without time zone
);


ALTER TABLE public."user" OWNER TO sophieratkai;

--
-- Name: device device_pkey; Type: CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public.device
    ADD CONSTRAINT device_pkey PRIMARY KEY (id);


--
-- Name: image image_pkey; Type: CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public.image
    ADD CONSTRAINT image_pkey PRIMARY KEY (id);


--
-- Name: report report_pkey; Type: CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public.report
    ADD CONSTRAINT report_pkey PRIMARY KEY (id);


--
-- Name: series series_pkey; Type: CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public.series
    ADD CONSTRAINT series_pkey PRIMARY KEY (id);


--
-- Name: study study_pkey; Type: CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public.study
    ADD CONSTRAINT study_pkey PRIMARY KEY (id);


--
-- Name: task task_name_key; Type: CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_name_key UNIQUE (name);


--
-- Name: task task_pkey; Type: CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_pkey PRIMARY KEY (id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: ix_user_email; Type: INDEX; Schema: public; Owner: sophieratkai
--

CREATE UNIQUE INDEX ix_user_email ON public."user" USING btree (email);


--
-- Name: ix_user_username; Type: INDEX; Schema: public; Owner: sophieratkai
--

CREATE UNIQUE INDEX ix_user_username ON public."user" USING btree (username);


--
-- Name: image image_series_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public.image
    ADD CONSTRAINT image_series_id_fkey FOREIGN KEY (series_id) REFERENCES public.series(id);


--
-- Name: report report_series_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public.report
    ADD CONSTRAINT report_series_id_fkey FOREIGN KEY (series_id) REFERENCES public.series(id);


--
-- Name: report report_task_name_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public.report
    ADD CONSTRAINT report_task_name_fkey FOREIGN KEY (task_name) REFERENCES public.task(name);


--
-- Name: report report_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public.report
    ADD CONSTRAINT report_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: series series_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public.series
    ADD CONSTRAINT series_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.device(id);


--
-- Name: series series_study_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public.series
    ADD CONSTRAINT series_study_id_fkey FOREIGN KEY (study_id) REFERENCES public.study(id);


--
-- Name: series series_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sophieratkai
--

ALTER TABLE ONLY public.series
    ADD CONSTRAINT series_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- PostgreSQL database dump complete
--

