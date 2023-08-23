from wos.FDataBase import FDataBase
from datetime import datetime
from psycopg2 import Error
from scopus.sc_forms import DataScForm, SC_Form

ALL_DEP='9999'


class WOS_Dbase(FDataBase):

    __SQL_wos_authors_by_dep="""select * from ( select  id,"FIO",name_department,aut."ORCID_ID",aut."Researcher_ID",doc,sum_note,h_ind,id_depatment, works  from public.autors_in_departments aid 
            inner join (
            select  tsh."id_Sciencer" as id , tsh."FIO",tsh."ORCID_ID",tsh."Researcher_ID" ,count(*) filter (where tsh."id_Sciencer" = sa.id_autor ) doc ,sum(w.note::int) sum_note , hidex_wos(tsh."id_Sciencer"::int) h_ind, tsh.works 
            from public."Table_Sсience_HNURE"  tsh  
            left  join wos_autors sa on (tsh."id_Sciencer"  = sa.id_autor)
            left  join wos w on (w.unique_id  = sa.unique_id)
            group by id) aut
            on (aut.id = aid.id_autors )
            order by aut.id ) r
            where r.works  """
    
    __SQL_wos_all_article="""SELECT  w.unique_id ,w.title, w.author , "year", w.document_type, w.journal ,/*aid.name_autor, aid.name_department,*/ aid.id_depatment ,tsh.works
            FROM public.wos w 
            inner join public.wos_autors wa on (wa.unique_id  = w.unique_id )
            left join public."Table_Sсience_HNURE" tsh on (wa.id_autor  = tsh."id_Sciencer")
            left join public.autors_in_departments aid on (aid.id_autors = tsh."id_Sciencer"  )
            order by w.unique_id  """


    __SQL_wos_export_article="""  SELECT  distinct w.unique_id ,w.title,aid.name_autor, w.author , "year", w.document_type, w.journal , aid.name_department, aid.id_depatment ,tsh.works, w.note
            FROM public.wos w 
            left join public.wos_autors wa on (wa.unique_id  = w.unique_id )
            left join public."Table_Sсience_HNURE" tsh on (wa.id_autor  = tsh."id_Sciencer")
            left join public.autors_in_departments aid on (aid.id_autors = tsh."id_Sciencer"  )
            order by w.unique_id  """

    __SQL_wos_export_author_with_article="""select distinct  tsh ."id_Sciencer" id ,tsh ."FIO",w.title ,w."year" , aid.name_department , aid.id_depatment from  "Table_Sсience_HNURE" tsh 
                                left join wos_autors wa  on (tsh."id_Sciencer"  = wa.id_autor)
                                inner join  wos w  on (w.unique_id  = wa.unique_id)
                                inner join  autors_in_departments aid on (tsh."id_Sciencer"  = aid.id_autors)	 
                                where  works  
                                order by "id_Sciencer" """

    def __read_db(self,SQL_String,data:tuple=None): 
        return self._FDataBase__read_execute(SQL_String,data)
    
    def __read_one_db(self,SQL_String):
        try:            
            self._FDataBase__cur.execute(SQL_String)
            return self._FDataBase__cur.fetchone()
        except (Exception,Error) as error:
            print("Ошибка при чтении БД:", error)
#----------------------------------------------------------------
    def get_data_update_wos(self):
        res=self.__read_one_db("select max(w.data_update) from wos w;") 
        return res[0].strftime("%Y-%m-%d  %H:%M:%S") if res[0] else ''
    
    def get_doc_sum(self):
        return self.__read_one_db("select count(w.unique_id) doc ,sum (w.note::int) from wos w;")

    def get_h_ind(self):
        res=self.__read_one_db("""select count(*) h_ind from (select  foo.sn, row_number() over() c 
        from (select w.note::int sn  from wos w order by sn desc ) foo) res where  res.sn >= res.c ;""") 
        return res[0]
    
    def select_authors_by_form(self,form:SC_Form):
        where_=lambda x:f""" and r.doc::int >= {form.sc_input_limit.data} order by r.doc::int desc """ if x else ' order by r.id'               

        return self.__read_db(f"""{self.__SQL_wos_authors_by_dep}
                            {f' and id_depatment = {form.sc_select_dep.data} ' if form.sc_select_dep.data != ALL_DEP else '' } 
                            {where_(form.sc_bool_limit.data and (form.sc_input_limit.data > 0))} ;""")
    
    def get_stamp_table_wos(self,id):
        return self.__read_one_db(f"""select * from stamp_tables st 
                            where st.id_table = '{id}';""")
    
    def __set_where_sc_SQL_type_year(self,my_form:DataScForm)->str:
        strSQLwhere = {'where':'where '}  
        if not my_form['sc_other'] and not my_form['sc_book'] and not my_form['sc_conf'] and not my_form['sc_article']:
            strSQLwhere['where']+=" document_type = 'NONE TYPE' "            
        elif my_form['sc_other'] and my_form['sc_book'] and my_form['sc_conf'] and my_form['sc_article']:
            pass
        else:
            if my_form['sc_other']:
                strSQLwhere['where']+=f"""{'(' if my_form['sc_article'] + my_form['sc_book'] + my_form['sc_conf'] else ''} 
                                        not (document_type LIKE '%Article%' or document_type LIKE '%Proceedings Paper%' or document_type LIKE '%Book%')  """    
            if my_form['sc_article'] or my_form['sc_book'] or my_form['sc_conf']:    
                dic_type = {'Article':my_form['sc_article'],'Proceedings Paper':my_form['sc_conf'],'Book':my_form['sc_book']}              
                strSQLwhere['where']+=f""" {self.or_str(strSQLwhere['where'])}  ({' or '.join(f"document_type LIKE '%{key}%'"  for key,vol in dic_type.items() if vol)} 
                                            {')' if my_form['sc_other']  else ''})  """
        if not (('Все' in  my_form['sc_select_year']) or (not my_form['sc_select_year'])):
            strSQLwhere['where'] += f""" {self.and_str(strSQLwhere['where'])} "year" in ({','.join(f"'{y}'" for y in my_form['sc_select_year'])}) """
        if my_form['sc_select_dep'] !=ALL_DEP: 
            strSQLwhere['where'] += f""" {self.and_str(strSQLwhere['where'])} id_depatment = {my_form['sc_select_dep']} """
        return strSQLwhere['where'] if len(strSQLwhere['where'])>10 else ''

        
    def get_limit_all_article(self,offset,limit,my_form:SC_Form):
        w_ty=self.__set_where_sc_SQL_type_year(my_form)    
        return self.__read_db(f""" select  DISTINCT on (unique_id) unique_id , title , author , "year" , document_type , journal , works from ({self.__SQL_wos_all_article}) art
                                    {w_ty} {f"{self.and_str(w_ty)} works" if my_form['sc_select_dep']!=ALL_DEP else ""}
                                        offset {offset} limit {limit}""")    

    def get_count_all_article(self,my_form:SC_Form):
        w_ty=self.__set_where_sc_SQL_type_year(my_form)    
        return self.__read_one_db(f""" select  count (DISTINCT unique_id)  from ({self.__SQL_wos_all_article}) art
                                    {w_ty} {f"{self.and_str(w_ty)} works" if my_form['sc_select_dep']!=ALL_DEP else ""}  """)[0]    
                
    def get_wos_search(self,myform:SC_Form):
        if myform.sc_radio_auth_atcl == 'author':
            return self.__read_db(f"""select * from ({self.__SQL_wos_authors_by_dep}) as too 
                                        where too."FIO" ILIKE '%{myform.sc_search}%' """)
        else:
            return self.__read_db(f"""select unique_id ,title , author ,"year" ,document_type ,journal from wos w  
                                        where w.title ILIKE '%{myform.sc_search}%'   or
                                              w.author ILIKE '%{myform.sc_search}%'; """)
    
    def get_articles_export(self,my_form:SC_Form):
        w_ty=self.__set_where_sc_SQL_type_year(my_form)
        strSQLquery=f"""select title,author,name_autor,name_department,"year", id_depatment, works, unique_id, document_type, journal, note from ({self.__SQL_wos_export_article}) res
                        {w_ty} {f"{self.and_str(w_ty)} works" if my_form['sc_select_dep']!=ALL_DEP else ""} """
        return self.__read_db(strSQLquery)

        
    def get_sc_author_with_article(self,myform:SC_Form):
        sql = f"""select {f'DISTINCT ON (id,"FIO",title) ' if myform['sc_select_dep'] == ALL_DEP else ""} id ,"FIO",title ,"year" ,name_department , id_depatment from ({self.__SQL_wos_export_author_with_article}) 
                    as a  {f'where id_depatment = {myform["sc_select_dep"]}' if myform['sc_select_dep'] != ALL_DEP else ""}  order by a.id """
        return self.__read_db(sql)        

    def get_sum_export(self):
        return self.__read_db(f"""select  "FIO",name_department,sum_note  from
	            ({self.__SQL_wos_authors_by_dep}) too
            where  too.sum_note::int > 0
            order  by name_department""")
    
    def select_idAuthor_by_orcid(self,id_orcid):
        return self.__read_db("""SELECT "id_Sciencer" FROM public."Table_Sсience_HNURE" AS tsh WHERE tsh."ORCID_ID" = %s ;""",(id_orcid,))
    
    def select_idAuthor_by_latName(self,author:str):
        return self.__read_db("""SELECT * FROM public.lat_name_hnure AS lnh WHERE lnh.name_lat = %s;""",(author,))

    def insert_article(self,data):
        sql ="""INSERT INTO public.wos AS t(unique_id,title,journal,year,author,volume,number,pages,doi,note,publisher,document_type) 
            SELECT * FROM (values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)) v(unique_id,title,journal,year,author,volume,number,pages,doi,note,publisher,document_type) 
            WHERE NOT EXISTS  (SELECT FROM public.wos AS d where d.unique_id = v.unique_id) 
            on conflict do nothing returning "unique_id";"""        
        res=self._FDataBase__update_execute(sql,data)
        return res[0][0] if res else ''
    
    def insert_author_in_table_wosAutors(self,data):
        sql="""INSERT INTO public.wos_autors AS t(unique_id,orcid,researcher_id,author,id_autor) 
            SELECT unique_id,orcid,researcher_id,author,id_autor::int FROM (values (%s,%s,%s,%s,%s)) v(unique_id,orcid,researcher_id,author,id_autor) 
            WHERE NOT EXISTS  (SELECT FROM public.wos_autors AS d where (d.unique_id = v.unique_id) and (d.author = v.author)) 
            on conflict do nothing returning "id_autor";"""
        return self._FDataBase__update_execute(sql,data)

    def update_note(self,data):
        sql="""UPDATE public.wos AS s SET note = %s, data_update = now()
                            WHERE  s.unique_id = %s 
                            RETURNING  s.unique_id;"""
        return self._FDataBase__update_execute(sql,data)

    def deleteArticle(self):
        self._FDataBase__update_execute('delete from public.wos_autors')
        self._FDataBase__update_execute('delete from public.wos')
