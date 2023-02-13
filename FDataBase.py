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
                                    ORDER BY tsh."id_Sciencer";"""

    def get_nure_list(self):
        try:
            self.__cur.execute(self.__query_all_nure)
            return self.__cur.fetchall()
        except (Exception,Error) as error:
            print("Ошибка при работе чтения БД:", error)
    

        
    


