import json
from typing import List, Optional
import pandas as pd
import csv
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path =  os.path.join(current_dir, '..', 'dataset', 'dataset_studi.csv')
splitter = [' ', ';', ',']

class DatasetAgent:
    def __init__(self, csv_path: str = file_path) -> None:
        self.csv_path = csv_path
        self.df = None
        
    def load_data(self):
        if self.df is None:
            self.df = pd.read_csv(self.csv_path)
        return self.df
    
    def filter_data(self, 
                    min_ipk: Optional[float] = None,
                    bidang: Optional[str] = None,
                    negara: Optional[str] = None,
                    tujuan_karier: Optional[str] = None,
                    )  :
        try:
            df = self.load_data().copy()
       
            if min_ipk is not None:
                df = df[df['min_ipk'] <= min_ipk]
                
            if bidang is not None:
                bidang_list = [b.strip() for b in bidang.split(',') if b.strip()]
                
                if bidang_list:
                    mask = pd.Series([False] * len(df), index=df.index)
                    for b in bidang_list:
                        # ✅ Search in BOTH bidang AND fokus_riset columns!
                        mask_bidang = df['bidang'].str.contains(b, case=False, na=False)
                        mask_fokus = df['fokus_riset'].str.contains(b, case=False, na=False)
                        combined = mask_bidang | mask_fokus
                        mask |= combined
                    
                    df = df[mask]
            
            if negara is not None:
                negara_list = [n.strip() for n in negara.split(',') if n.strip()]
                if negara_list:
                    mask = pd.Series([False] * len(df), index=df.index)
                    for n in negara_list:
                        mask |= df['negara'].str.contains(n, case=False, na=False)
                    df = df[mask]
              
            if df.empty:
                return "Tidak ada program yang cocok dengan kriteria yang diberikan."
     
            return df.to_dict('records') # type: ignore
        
            
        except FileNotFoundError:
            print("Tidak ada")
            
    def search_program_wrapper(self, min_ipk, bidang, negara, tujuan_karier):
        """
        Fungsi wrapper untuk memanggil dataset Anda.
        """
        try:
            raw_result = self.filter_data(
                min_ipk=float(min_ipk), 
                bidang=bidang, 
                negara=negara, 
                tujuan_karier=tujuan_karier
            )

            if isinstance(raw_result, (list, dict)):
                return json.dumps(raw_result, indent=2)
            return str(raw_result)
        except Exception as e:
            return f"Error accessing dataset: {str(e)}"
                
            