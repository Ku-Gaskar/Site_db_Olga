import os
import psycopg2 
from psycopg2 import Error

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur=db.cursor()
        self.__query_all_nure = """select tsh."id_Sciencer",tsh."FIO" ,foo1.dep , tsh."ID_Scopus_Author",tsh."ORCID_ID" ,tsh."Researcher_ID",name_l  from public."Table_Sсience_HNURE" tsh 
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
    def get_nure_list(self,limit=0,offset=0):
        try:
            
            self.__cur.execute(self.__query_all_nure)
            return self.__cur.fetchall()
        except (Exception,Error) as error:
            print("Ошибка при работе чтения БД:", error)

    def get_nure_one_list(self,autor_):
        try:
            one_author_SQL=f"""SELECT * FROM ({self.__query_all_nure}) AS one_author WHERE one_author."FIO" ILIKE '%{autor_}%';"""
            self.__cur.execute(one_author_SQL)
            return self.__cur.fetchall()
        except (Exception,Error) as error:
            print("Ошибка при работе чтения БД:", error)

    def get_nure_total_dep_list(self):
        try:
            dep_list_SQL=f"""SELECT * FROM departments;"""
            self.__cur.execute(dep_list_SQL)
            return self.__cur.fetchall()
        except (Exception,Error) as error:
            print("Ошибка при работе чтения БД:", error)

    def get_nure_one_dep_list(self,deportment):
        try:
            one_dep_SQL=f"{self.__query_one_dep_nure}{deportment};"
            self.__cur.execute(one_dep_SQL)
            return self.__cur.fetchall()
        except (Exception,Error) as error:
            print("Ошибка при работе чтения БД:", error)

    def get_author_by_id(self,id):
        try:
            one_author_SQL=f"""SELECT * FROM ({self.__query_all_nure}) AS one_author WHERE one_author."id_Sciencer" = {id};"""
            self.__cur.execute(one_author_SQL)
            return self.__cur.fetchall()
        except (Exception,Error) as error:
            print("Ошибка при работе чтения БД:", error)


    

    

        
    


