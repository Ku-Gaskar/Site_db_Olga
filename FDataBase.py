import os
import psycopg2 
from psycopg2 import Error

class Author():
    def __init__(self):
        name_author:str = None
        scopus_id=None
        


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur=db.cursor()
        self.__query_all_nure = """select tsh."id_Sciencer",tsh."FIO" ,foo1.dep , tsh."ID_Scopus_Author",tsh."ORCID_ID" ,tsh."Researcher_ID",name_l from     public."Table_Sсience_HNURE" tsh 
                                    full join (select aid.id_autors, array_to_string(array_agg(aid.name_department),'\n') dep from  public.autors_in_departments aid 
                                    GROUP by aid.id_autors) as foo1
                                    on (tsh."id_Sciencer" = foo1.id_autors )
                                    full join (select lnh.id_autor , array_to_string(array_agg(lnh.name_lat),'; ') name_l  FROM public.lat_name_hnure lnh
                                    GROUP by lnh.id_autor) as foo 
                                    on  (tsh."id_Sciencer" = foo.id_autor)
                                    ORDER BY tsh."id_Sciencer" """

        self.__query_one_dep_nure = """select * from (select tsh."id_Sciencer" id,tsh."FIO" ,aid.name_department , tsh."ID_Scopus_Author",tsh."ORCID_ID" ,tsh."Researcher_ID",name_l, aid.id_depatment
                                from  public.autors_in_departments aid
                                inner join public."Table_Sсience_HNURE" tsh 
                                on (tsh."id_Sciencer"=aid.id_autors)
                                full join (select lnh.id_autor , array_to_string(array_agg(lnh.name_lat),'; ') name_l  FROM public.lat_name_hnure lnh
                                GROUP by lnh.id_autor) as foo 
                                on  ((tsh."id_Sciencer" = foo.id_autor))
                                ORDER BY tsh."FIO") as res
                                where res.id_depatment ="""
    
    def __read_execute(self,_SQL_query:str):
            try:            
                self.__cur.execute(_SQL_query)
                return self.__cur.fetchall()
            except (Exception,Error) as error:
                print("Ошибка при чтении БД:", error)
        
    def __update_execute(self,_sql_query:str):
            try:
                self.__cur.execute(_sql_query)
                self.__db.commit()
                return self.__cur.fetchall()
            except (Exception,Error) as error:
                print("Ошибка при обновлении БД:", error)    
        
    def get_nure_list(self):
        return self.__read_execute(self.__query_all_nure)

    def get_nure_one_list(self,autor_):
        one_author_SQL=f"""SELECT * FROM ({self.__query_all_nure}) AS one_author WHERE one_author."FIO" ILIKE '%{autor_}%';"""
        return self.__read_execute(one_author_SQL)

    def get_nure_total_dep_list(self):
        return self.__read_execute("""SELECT * FROM departments;""")

    def get_nure_one_dep_list(self,deportment):
        one_dep_SQL=f"{self.__query_one_dep_nure}{deportment};"
        return self.__read_execute(one_dep_SQL)

    def get_author_by_id(self,id):
        one_author_SQL=f"""SELECT * FROM ({self.__query_all_nure}) AS one_author WHERE one_author."id_Sciencer" = {id};"""
        return self.__read_execute(one_author_SQL)

    def get_dep_by_author(self,id_author):
        one_author_SQL=f"""SELECT * FROM public.autors_in_departments aid
                            WHERE aid .id_autors = {id_author};"""
        return self.__read_execute(one_author_SQL)

    def update_dep_by_id(self,id_author,dep_id,dep_id_old):
        up_dep_SQL=f"""update public.autors_in_departments aid  set id_depatment = {dep_id} ,
            name_department = (select d.name_depat from departments d where d.id_depat = {dep_id})
            where aid.id_autors = {id_author} and aid.id_depatment = {dep_id_old} 
            returning name_department ; """ 
        return self.__update_execute(up_dep_SQL)
    
    def update_name_scopus_orcid_reasearcher_id_by_author_id(self,new_id,old_id):
        up_scopus_SQL=f"""update public."Table_Sсience_HNURE" tsh 
            set                            "FIO" = '{new_id.name_author}',
                              "ID_Scopus_Author" = '{new_id.scopus_id}',
                                      "ORCID_ID" = '{new_id.orcid_id}',
                                 "Researcher_ID" = '{new_id.researcher_id}'
        
            where                      tsh."FIO" = '{old_id['author'][0][1]}' and
                               tsh."id_Sciencer" =  {old_id['author'][0][0]}  and 
                          tsh."ID_Scopus_Author" = '{old_id['author'][0][3]}' and 
                                  tsh."ORCID_ID" = '{old_id['author'][0][4]}' """
        if old_id['author'][0][5] != None:
            up_scopus_SQL+=f""" and  tsh."Researcher_ID" = '{old_id['author'][0][5]}' """
        up_scopus_SQL+="""returning tsh ."FIO"; """
        return self.__update_execute(up_scopus_SQL)

    


