from scopus.FDataBase import FDataBase
from datetime import datetime
from psycopg2 import Error
from scopus.sc_forms import DataScForm, SC_Form

ALL_DEP='9999'


class SC_Dbase(FDataBase):

    # __SQL_sc_All_aurhors="""select tsh ."id_Sciencer" ,tsh ."FIO",dep, ais.id_scopus,ais.doc ,ais.note,ais.h_ind  from  "Table_Sсience_HNURE" tsh 
    #                              full join author_in_scopus ais on (tsh."id_Sciencer" = ais.id_author)
    #                              left join (select aid.id_autors, array_to_string(array_agg(aid.name_department),'; ') dep from  public.autors_in_departments aid 
    #                              GROUP by aid.id_autors) as foo1
    #                              on (tsh."id_Sciencer" = foo1.id_autors )
    #                              where tsh.works 
    #                              order by tsh ."id_Sciencer" """ 

# редакция Изменено!!!!!
    # __SQL_sc_article_select = """SELECT DISTINCT /*on (title)*/  title, s.author, aid.name_autor, aid.name_department, "year", aid.id_depatment ,tsh.works, s.eid, document_type,journal
    #                     FROM public.scopus  s
    #                     full join public.scopus_autors sa on (sa.eid = s.eid  )
    #                     left join public."Table_Sсience_HNURE" tsh on (sa.id_sc_autor = tsh."ID_Scopus_Author")
    #                     left join public.autors_in_departments aid on (aid.id_autors = tsh."id_Sciencer"  )
    #                     order by "eid" """
    
# Изменено на это:
    __SQL_sc_article_select = """SELECT DISTINCT /*on (title)*/  title, s.author, aid.name_autor, aid.name_department, "year", aid.id_depatment ,tsh.works, s.eid, document_type,journal,s.note
                        FROM public.scopus  s
                        full join public.scopus_autors sa on (sa.eid = s.eid  )                        
                        left join public.author_in_scopus ais on (sa.id_sc_autor = ais.id_scopus )                        
                        left join public."Table_Sсience_HNURE" tsh on (ais.id_author = tsh."id_Sciencer")                                                
                        left join public.autors_in_departments aid on (aid.id_autors = tsh."id_Sciencer"  )
                        order by "eid" """
                                

    __SQL_sc_authors_by_dep = """select DISTINCT * from (select tsh."id_Sciencer" id,tsh."FIO" ,aid.name_department , ais.id_scopus ,ais.doc ,ais.note,ais.h_ind , aid.id_depatment,tsh.works
                                from  public.autors_in_departments aid
                                inner join public."Table_Sсience_HNURE" tsh 
                                on (tsh."id_Sciencer"=aid.id_autors)
                                left join public.author_in_scopus ais 
                                on (tsh."id_Sciencer" = ais.id_author )
                                ORDER BY tsh."FIO") as res
                                where res.works """  
    __SQL_sc_author_with_article ="""select distinct  tsh ."id_Sciencer" id ,tsh ."FIO",s.title ,s."year" , aid.name_department , aid.id_depatment , s.author , s.journal , s.volume, s.number, s.pages , s.doi , ais.id_scopus, wa.id_autor from  "Table_Sсience_HNURE" tsh 
                                left join author_in_scopus ais on (tsh."id_Sciencer"  = ais.id_author)
                                inner join  scopus_autors sa  on (ais.id_scopus  = sa.id_sc_autor) 
                                inner join  scopus s on (s.eid = sa.eid)
                                inner join  autors_in_departments aid on (tsh."id_Sciencer"  = aid.id_autors)	 
                        where id_scopus = id_sc_autor and works  
                        order by "id_Sciencer" """
    
    __SQL_full_data_green_table = """select tsh."id_Sciencer" id,tsh."FIO" ,tsh."ORCID_ID" ,ais.id_scopus, ais.doc ,ais.note ,ais.h_ind ,wos_sum.doc,wos_sum.sum_note,wos_sum.h_ind, foo1.dep ,works, tsh.googlescholar,name_l  from public."Table_Sсience_HNURE" tsh 
                                full join (select aid.id_autors, array_to_string(array_agg(aid.name_department),'; ') dep from  public.autors_in_departments aid 
                                GROUP by aid.id_autors) as foo1
                                on (tsh."id_Sciencer"=foo1.id_autors)
                                full join (select lnh.id_autor , array_to_string(array_agg(lnh.name_lat),'; ') name_l  FROM public.lat_name_hnure lnh
                                GROUP by lnh.id_autor) as foo 
                                on  (tsh."id_Sciencer" = foo.id_autor)
                                left join  public.author_in_scopus ais   
                                on  (tsh."id_Sciencer" = ais.id_author)
                                inner join (select  "id_Sciencer",doc,sum_note,h_ind from 
                                            (select  tsh."id_Sciencer",count(*) filter (where tsh."id_Sciencer" = sa.id_autor ) as doc ,sum(w.note::int) sum_note , hidex_wos(tsh."id_Sciencer"::int) h_ind 
                                            from public."Table_Sсience_HNURE" tsh  
                                            left  join wos_autors sa on (tsh."id_Sciencer"  = sa.id_autor)
                                            left  join wos w on (w.unique_id  = sa.unique_id)
                                            group by tsh."id_Sciencer") as wos_sum1) wos_sum
                                on (wos_sum."id_Sciencer"=tsh."id_Sciencer"  )
                                order by tsh."id_Sciencer" """  #tsh."Researcher_ID",

    
    def __read_db(self,SQL_String): 
        return self._FDataBase__read_execute(SQL_String)
    
    def __read_one_db(self,SQL_String,data=None):
        try:            
            self._FDataBase__cur.execute(SQL_String,data)
            return self._FDataBase__cur.fetchone()
        except (Exception,Error) as error:
            print("Ошибка при чтении БД:", error)

    
#----------------------------------------------------------------
    def get_data_update_scopus(self):
        res=self.__read_db("select max(s.data_update) from scopus s") 
        
        return res[0][0].strftime("%Y-%m-%d  %H:%M:%S") if res[0][0] else ''
    
    def get_doc_sum(self):
        return self.__read_one_db("select count(s.eid) doc ,sum (s.note::int) from scopus s;")

    def get_h_ind(self):
        res=self.__read_db("""select count(*) h_ind from (select  foo.sn, row_number() over() c 
        from (select s.note::int sn  from scopus s order by sn desc ) foo) res where  res.sn >= res.c;""") 
        return res[0][0]  #if res[0][0] else ''

    def select_authors_by_form(self, form:SC_Form):
        where_=lambda x:f""" where  r.doc::int >= {form.sc_input_limit.data} order by r.doc::int desc """ if x else ' order by r.id'               

        return self.__read_db(f"""select * from ({self.__SQL_sc_authors_by_dep}
                            {f' and res.id_depatment = {form.sc_select_dep.data} ' if form.sc_select_dep.data != ALL_DEP else '' }) as r 
                            {where_(form.sc_bool_limit.data and (form.sc_input_limit.data > 0))} ;""")
            
                
    def get_stamp_table(self,id):
        return self.__read_one_db(f"""select * from stamp_tables st 
                                  where st.id_table = '{id}';""")
         
    def get_count_all_article(self,my_form:SC_Form.data):
        w_ty=self.__set_where_sc_SQL_type_year(my_form)
        return self.__read_one_db(f""" select count (DISTINCT eid) from ({self.__SQL_sc_article_select}) art                                                                               
                                        {w_ty} {f"{self.and_str(w_ty)} works" if my_form['sc_select_dep']!=ALL_DEP else ""} """)[0]



    
    def __set_where_sc_SQL_type_year(self,my_form:DataScForm)->str:
        strSQLwhere = {'where':'where '}  
        if not my_form['sc_other'] and not my_form['sc_book'] and not my_form['sc_conf'] and not my_form['sc_article']:
            strSQLwhere['where']+=" document_type = 'NONE TYPE' "            
        elif my_form['sc_other'] and my_form['sc_book'] and my_form['sc_conf'] and my_form['sc_article']:
            pass
        else:
            if my_form['sc_other']:
                strSQLwhere['where']+=f"{'(' if my_form['sc_article'] + my_form['sc_book'] + my_form['sc_conf'] else ''} not document_type in ('Article','Conference Paper','Book Chapter','Book')  "    
            if my_form['sc_article'] or my_form['sc_book'] or my_form['sc_conf']:    
                dic_type = {'Article':my_form['sc_article'],'Conference Paper':my_form['sc_conf'],'Book Chapter':my_form['sc_book'],'Book':my_form['sc_book']}              
                strSQLwhere['where']+=f""" {self.or_str(strSQLwhere['where'])} document_type in ({','.join(f"'{key}'"  for key,vol in dic_type.items() if vol)} 
                                            {')' if my_form['sc_other']  else ''})  """
        if not (('Все' in  my_form['sc_select_year']) or (not my_form['sc_select_year'])):
            strSQLwhere['where'] += f""" {self.and_str(strSQLwhere['where'])} "year" in ({','.join(f"'{y}'" for y in my_form['sc_select_year'])}) """
        if my_form['sc_select_dep'] !=ALL_DEP: 
            strSQLwhere['where'] += f""" {self.and_str(strSQLwhere['where'])} id_depatment = {my_form['sc_select_dep']} """
        return strSQLwhere['where'] if len(strSQLwhere['where'])>10 else ''


    def get_limit_all_article(self,offset,limit,my_form:DataScForm):
        w_ty=self.__set_where_sc_SQL_type_year(my_form)    
        return self.__read_db(f""" select DISTINCT eid , title , author , "year" , document_type , journal , works from ({self.__SQL_sc_article_select}) art
                                    {w_ty} {f"{self.and_str(w_ty)} works" if my_form['sc_select_dep']!=ALL_DEP else ""}
                                      offset {offset} limit {limit}""")    

    def get_articles_export(self,my_form:DataScForm):
        w_ty=self.__set_where_sc_SQL_type_year(my_form)
        strSQLquery=f"""select * from ({self.__SQL_sc_article_select}) res
                        {w_ty} {f"{self.and_str(w_ty)} works" if my_form['sc_select_dep']!=ALL_DEP else ""} """
        return self.__read_db(strSQLquery)


    def get_sc__search(self,myform:DataScForm ):
        if myform.sc_radio_auth_atcl == 'author':
            return self.__read_db(f"""select * from ({self.__SQL_sc_authors_by_dep}) as too 
                                        where too."FIO" ILIKE '%{myform.sc_search}%' """)
        else:
            return self.__read_db(f"""select eid ,title ,author ,"year" ,document_type ,journal from scopus s  
                                        where s.title ILIKE '%{myform.sc_search}%'   or
                                              s.author ILIKE '%{myform.sc_search}%'; """)


    def get_sum_export(self):        
        return self.__read_db("""select  name_autor,name_department,note from
	            (select * from autors_in_departments aid 
	            left join author_in_scopus on( aid.id_autors  = id_author)) too
            where  NULLIF(too.note, 'None')::int > 0
            order  by name_department""")
    
    def get_sc_author_with_article(self,myform:DataScForm):
        sql = f"""select {f'DISTINCT ON (id,"FIO",title) ' if myform['sc_select_dep'] == ALL_DEP else ""} id ,"FIO",title ,"year" ,name_department , id_depatment , author , journal , volume, number, pages , doi , id_autor from ({self.__SQL_sc_author_with_article}) 
                    as a  {f'where id_depatment = {myform["sc_select_dep"]}' if myform['sc_select_dep'] != ALL_DEP else ""}  order by a.id """
        return self.__read_db(sql)
    
    def get_list_scopusID(self):
        return self.__read_db("select * from author_in_scopus order by id_author;")

    def update_cit_doc_hIndex(self,author:dict,id):
        sql = f""" update author_in_scopus set doc = '{author['doc']}', note = '{author['note']}', h_ind = '{author['h_index']}' where id_author = {id[0]} and id_scopus = '{id[1]}'  RETURNING id_author"""
        return self._FDataBase__update_execute(sql)
        
    def get_full_data_export(self):
        return self.__read_db(self.__SQL_full_data_green_table)
    
    def update_article(self,article:tuple):
        sql = """INSERT INTO public.scopus AS t(eid,title,journal,year,volume,number,pages,doi,note,publisher,document_type,author) 
            SELECT * FROM (values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)) v(eid,title,journal,year,volume,number,pages,doi,note,publisher,document_type,author) 
            WHERE NOT EXISTS  (SELECT FROM public.scopus AS d where d.eid = v.eid) 
            on conflict do nothing returning "eid";""" 
        res=self._FDataBase__update_execute(sql,article)
        if res: 
            return res[0]
        else:
            sql="""UPDATE public.scopus AS s SET note = %s, data_update = now()
                            WHERE  s.eid = %s 
                            RETURNING  s.eid;""" 
            return self.__read_one_db(sql,(article[8],article[0]))

    def update_sc_in_autors(self,id_autor,eid):
        sql = """INSERT INTO public.scopus_autors AS t(id_sc_autor,eid) 
                SELECT * FROM (values (%s,%s)) v(id_sc_autor,eid) 
                WHERE NOT EXISTS  (SELECT FROM public.scopus_autors AS d where d.eid = v.eid and d.id_sc_autor = v.id_sc_autor) 
                on conflict do nothing returning "eid";""" 
        res=self._FDataBase__update_execute(sql,(id_autor,eid))
        if res: return res[0][0]
        else: return '0'

    def deleteArticle(self):
        self._FDataBase__update_execute('delete from public.scopus_autors')
        self._FDataBase__update_execute('delete from public.scopus')
