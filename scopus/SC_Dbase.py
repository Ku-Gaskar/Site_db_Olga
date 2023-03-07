from scopus.FDataBase import FDataBase
from datetime import datetime
from psycopg2 import Error
from scopus.sc_forms import DataScForm, SC_Form


class SC_Dbase(FDataBase):

    __SQL_sc_All_aurhors="""select tsh ."id_Sciencer" ,tsh ."FIO",dep, ais.id_scopus,ais.doc ,ais.note,ais.h_ind  from  "Table_Sсience_HNURE" tsh 
                                full join author_in_scopus ais on (tsh."id_Sciencer" = ais.id_author)
                                left join (select aid.id_autors, array_to_string(array_agg(aid.name_department),'; ') dep from  public.autors_in_departments aid 
                                GROUP by aid.id_autors) as foo1
                                on (tsh."id_Sciencer" = foo1.id_autors )
                                where tsh.works 
                                order by tsh ."id_Sciencer" """ 

    __SQL_sc_authors_by_dep="""select DISTINCT * from (select tsh."id_Sciencer" id,tsh."FIO" ,aid.name_department , ais.id_scopus ,ais.doc ,ais.note,ais.h_ind , aid.id_depatment,tsh.works
                                from  public.autors_in_departments aid
                                inner join public."Table_Sсience_HNURE" tsh 
                                on (tsh."id_Sciencer"=aid.id_autors)
                                left join public.author_in_scopus ais 
                                on (tsh."id_Sciencer" = ais.id_author )
                                ORDER BY tsh."FIO") as res
                                where res.works and res.id_depatment = """       
    
    def __read_db(self,SQL_String): 
        return self._FDataBase__read_execute(SQL_String)
    
    def __read_one_db(self,SQL_String):
        try:            
            self._FDataBase__cur.execute(SQL_String)
            return self._FDataBase__cur.fetchone()
        except (Exception,Error) as error:
            print("Ошибка при чтении БД:", error)


    def get_data_update_scopus(self):
        res=self.__read_db("select max(s.data_update) from scopus s") 
        return res[0][0].strftime("%Y-%m-%d  %H:%M:%S") if res else ''
    
    def get_doc_sum(self):
        return self.__read_one_db("select count(s.eid) doc ,sum (s.note::int) from scopus s;")

    def get_h_ind(self):
        res=self.__read_db("""select count(*) h_ind from (select  foo.sn, row_number() over() c 
        from (select s.note::int sn  from scopus s order by sn desc ) foo) res where  res.sn > res.c;""") 
        return res[0][0] if res else ''

    def get_all_authors(self):
        return self.__read_db(self.__SQL_sc_All_aurhors)

    def select_authors_by_form(self, form):
        if form.sc_select_dep.data == '9999':
             return self.get_all_authors()
        else:
            return self.__read_db(self.__SQL_sc_authors_by_dep + str(form.sc_select_dep.data)+" order by res.id")
                
    def get_stamp_table(self,id):
        return self.__read_one_db(f"""select * from stamp_tables st 
                                  where st.id_table = '{id}';""")
         
    def get_count_all_article(self,my_form:SC_Form.data):
        return self.__read_one_db(f"""select count(*)  from public.scopus s
                                    {self.__set_where_sc_SQL_string(my_form)};""")[0]
    
    def __set_where_sc_SQL_string(self,my_form:DataScForm)->str:
        strSQLwhere = {'where':' where '}  
        if not my_form['sc_article'] and not my_form['sc_book'] and not my_form['sc_conf']:
            strSQLwhere['where']+="not document_type in ('Article','Conference Paper','Book Chapter') "
        else:
            dic_type = {'Article':my_form['sc_article'],'Conference Paper':my_form['sc_conf'],'Book Chapter':my_form['sc_book']}              
            strSQLwhere['where']+=f"""document_type in ({','.join(f"'{key}'"  for key,vol in dic_type.items() if vol)} ) """

        if not 'Все' in  my_form['sc_select_year']:
            strSQLwhere['where'] += f""" and s."year" in ({','.join(f"'{y}'" for y in my_form['sc_select_year'])}) """

        return strSQLwhere['where']
    
    def get_limit_all_article(self,offset,limit,my_form:DataScForm):

        return self.__read_db(f""" select eid ,title ,author ,"year" ,document_type ,journal from scopus s 
                                {self.__set_where_sc_SQL_string(my_form)}
                                offset {offset} limit {limit};""")

    def get_sc__search(self,myform:DataScForm ):
        if myform.sc_radio_auth_atcl == 'author':
            return self.__read_db(f"""select * from ({self.__SQL_sc_All_aurhors}) as too 
                                        where too."FIO" ILIKE '%{myform.sc_search}%' """)
        else:
            return self.__read_db(f"""select eid ,title ,author ,"year" ,document_type ,journal from scopus s  
                                        where s.title ILIKE '%{myform.sc_search}%'   or
                                              s.author ILIKE '%{myform.sc_search}%'; """)


