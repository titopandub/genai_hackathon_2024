create user metabase with encrypted password 'postgres';
create database metabase owner metabase;

create user streamlit with encrypted password 'postgres';
create database streamlit owner streamlit;