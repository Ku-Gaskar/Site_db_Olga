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
        self.__query_all_nure = """select tsh."id_Sciencer",tsh."FIO" ,foo1.dep ,foo2.id_sc,tsh."ORCID_ID" ,tsh."Researcher_ID",foo.name_l from   public."Table_Sсience_HNURE" tsh 
                                    left join (select aid.id_autors, array_to_string(array_agg(aid.name_department),'; ') dep from  public.autors_in_departments aid 
                                    GROUP by aid.id_autors) as foo1
                                    on (tsh."id_Sciencer" = foo1.id_autors )
                                    left join (select lnh.id_autor , array_to_string(array_agg(lnh.name_lat),'; ') name_l  FROM public.lat_name_hnure lnh
                                    GROUP by lnh.id_autor) as foo 
                                    on  (tsh."id_Sciencer" = foo.id_autor)
                                    left join (select ais.id_author, array_to_string(array_agg(ais.id_scopus),';') id_sc from  public.author_in_scopus ais 
                                    GROUP by ais.id_author) as foo2 
                                    on (tsh."id_Sciencer" = foo2.id_author )
                                    where tsh.works = True    
                                    ORDER BY tsh."id_Sciencer" """

        self.__query_one_dep_nure = """select DISTINCT * from (select tsh."id_Sciencer" id,tsh."FIO" ,aid.name_department , foo2.id_sc,tsh."ORCID_ID" ,tsh."Researcher_ID",name_l, aid.id_depatment,tsh.works
                                from  public.autors_in_departments aid
                                inner join public."Table_Sсience_HNURE" tsh 
                                on (tsh."id_Sciencer"=aid.id_autors)
                                left join (select lnh.id_autor , array_to_string(array_agg(lnh.name_lat),'; ') name_l  FROM public.lat_name_hnure lnh
                                GROUP by lnh.id_autor) as foo 
                                on  (tsh."id_Sciencer" = foo.id_autor)
                                left join (select ais.id_author, array_to_string(array_agg(ais.id_scopus),';') id_sc from  public.author_in_scopus ais 
                                GROUP by ais.id_author) as foo2 
                                on (tsh."id_Sciencer" = foo2.id_author )
                                ORDER BY tsh."FIO") as res
                                where res.works = true and res.id_depatment ="""
        
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

# админка------------------------------------------------

    def getUser(self,user_id:int):
        user_SQL_query =f"""select * from public.users where id={user_id}"""
        res=self.__read_execute(user_SQL_query)
        if not res:
            print("User not found")
            return False
        return dict(zip(('id','name','email','psw','time_up'),res[0])) 
    
    def getUserByName(self,user_name:str):
        user_name_SQL_query =f"""select * from public.users where name='{user_name}'"""
        res=self.__read_execute(user_name_SQL_query)
        if not res:
            print("User not found")
            return False
        return dict(zip(('id','name','email','psw','time_up'),res[0])) 

#----------------------------------------------------------
    
    def get_nure_list(self):
        return self.__read_execute(self.__query_all_nure)

    def get_nure_one_list(self,autor_):
        one_author_SQL=f"""SELECT * FROM ({self.__query_all_nure}) AS one_author WHERE 
                                                                one_author."FIO" ILIKE '%{autor_}%' or 
                                                                one_author.name_l ILIKE '%{autor_}%';"""
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
    
    def update_name_orcid_reasearcher_id_by_author_id(self,new_id,old_id):
        up_scopus_SQL=f"""update public."Table_Sсience_HNURE" tsh 
            set                            "FIO" = '{new_id.name_author}',
                             
                                      "ORCID_ID" = '{new_id.orcid_id}',
                                 "Researcher_ID" = '{new_id.researcher_id}'
        
            where                      tsh."FIO" = '{old_id['author'][0][1]}' and
                               tsh."id_Sciencer" =  {old_id['author'][0][0]}  and 
                          
                                  tsh."ORCID_ID" = '{old_id['author'][0][4]}' """
        

        if old_id['author'][0][5] != None:
            up_scopus_SQL+=f""" and  tsh."Researcher_ID" = '{old_id['author'][0][5]}' """
        up_scopus_SQL+="""returning tsh ."FIO"; """
        return self.__update_execute(up_scopus_SQL)
    
    def delete_lat_name_by_id_author(self,id):
        up_dep_SQL=f"""delete from public.lat_name_hnure AS t 
                        where t.id_autor = {id} """
        return self.__update_execute(up_dep_SQL)
    
    def insert_lat_name_by_author_id(self,lat_name,id):    
        up_dep_SQL=f"""INSERT INTO public.lat_name_hnure AS t (id_autor,name_lat) 
                values ({id},'{lat_name}') 
                RETURNING name_lat; """      
        return self.__update_execute(up_dep_SQL)    

    def insert_dep_by_id_author(self,id_author,name_author,id_dep):
        insert_dep_SQL=f"""INSERT INTO public.autors_in_departments AS t(id_autors,name_autor,id_depatment,name_department) 
                SELECT * FROM (values ({id_author},'{name_author}',{id_dep},(select dep.name_depat from departments dep where dep.id_depat = {id_dep}))) v(id_autors,name_autor,id_depatment,name_department) 
                WHERE NOT EXISTS  (SELECT FROM public.autors_in_departments AS d where d.id_autors = v.id_autors AND d.id_depatment = v.id_depatment) 
                on conflict do nothing returning id_autors;"""      
        return self.__update_execute(insert_dep_SQL)
    
    def delete_dep_by_id_author(self,id):
        del_dep_SQL=f"""DELETE FROM public.autors_in_departments WHERE id_autors = {id} RETURNING * ;"""
        return self.__update_execute(del_dep_SQL)
    
    def insert_new_author(self,d):
        tsh_SQL=f"""INSERT INTO public."Table_Sсience_HNURE" AS t("FIO","ID_Scopus_Author","ORCID_ID") 
            SELECT * FROM (values ('{d.name_author}','{d.scopus_id}','{d.orcid_id}')) v("FIO","ID_Scopus_Author","ORCID_ID") 
            WHERE NOT EXISTS  (SELECT FROM public."Table_Sсience_HNURE" AS d where d."FIO" = v."FIO") 
            on conflict do nothing returning "id_Sciencer";"""
        id_author=self.__update_execute(tsh_SQL)
        
        if not id_author: 
            tsh_SQL=f"""SELECT t."id_Sciencer" FROM public."Table_Sсience_HNURE"  AS t
                              WHERE  t."FIO" = '{d.name_author}' ;"""
            id_author=self.__read_execute(tsh_SQL)       
        id_author=id_author[0][0]

            
        aid_SQL=f"""INSERT INTO public.autors_in_departments AS t(id_autors,name_autor,id_depatment,name_department) 
                SELECT * FROM (values ({id_author},'{d.name_author}',{d.depat},(select dep.name_depat from departments dep where dep.id_depat = {d.depat}))) v(id_autors,name_autor,id_depatment,name_department) 
                WHERE NOT EXISTS  (SELECT FROM public.autors_in_departments AS d where d.id_autors = v.id_autors AND d.id_depatment = v.id_depatment) 
                on conflict do nothing returning id_autors;"""      
        b=self.__update_execute(aid_SQL)

        if d.list_lat_name: 
            for f_name in d.list_lat_name.split(';'):
                f_name=f_name.strip()
                if f_name:
                    lnh_SQL=f"""INSERT INTO public.lat_name_hnure AS t(id_autor,name_lat) 
                        SELECT * FROM (values ({id_author},'{f_name}')) v(id_autor,name_lat) 
                        WHERE NOT EXISTS  (SELECT FROM public.lat_name_hnure AS d where d.id_autor = v.id_autor AND d.name_lat = v.name_lat) 
                        on conflict do nothing returning id_autor;"""                          
                    a=self.__update_execute(lnh_SQL)
        return id_author
    
    def hiden_author_by_id(self,id_author): 
        hi_aut_SQL=f"""update public."Table_Sсience_HNURE"  tsh set works = false 
            where tsh."id_Sciencer" = {id_author}
            returning "id_Sciencer" ; """ 
        return self.__update_execute(hi_aut_SQL)

    def delete_scopus_id_by_author_id(self,id_author):
        del_dep_SQL=f"""DELETE FROM public.author_in_scopus WHERE id_author = {id_author} RETURNING * ;"""
        return self.__update_execute(del_dep_SQL)


    def insert_scopus_id_by_author_id(self,id_author,d):
        list_scopus_id=(d.scopus_id,d.scopus_id_1,d.scopus_id_2)
        id_au=True
        for scopus_id in list_scopus_id:
            if scopus_id:
                sc_id_SQL=f"""INSERT INTO public.author_in_scopus AS t(id_author,id_scopus) 
                SELECT * FROM (values ({id_author},'{scopus_id}')) v(id_author,id_scopus) 
                WHERE NOT EXISTS  (SELECT FROM public.author_in_scopus AS d where d.id_author = v.id_author AND d.id_scopus = v.id_scopus) 
                on conflict do nothing returning id_author;"""
                id_au=self.__update_execute(sc_id_SQL)
        return id_au