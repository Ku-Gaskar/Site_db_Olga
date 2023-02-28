from FDataBase import FDataBase
from datetime import datetime


class SC_Dbase(FDataBase):
    
    def get_data_update_scopus(self):
        res=self._FDataBase__read_execute("select max(s.data_update) from scopus s") 
        return res[0][0].strftime("%Y-%m-%d  %H:%M:%S") if res else ''
    
    def get_doc_sum(self):
        res=self._FDataBase__read_execute("select count(s.eid) doc ,sum (s.note::int) from scopus s;") 
        return res[0] if res else ''

    def get_h_ind(self):
        res=self._FDataBase__read_execute("""select count(*) h_ind from (select  foo.sn, row_number() over() c 
        from (select s.note::int sn  from scopus s order by sn desc ) foo) res where  res.sn > res.c;""") 
        return res[0][0] if res else ''
