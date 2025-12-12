import inspect
import json
import os 
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import config.schema as schema
from dotenv import load_dotenv
import utils.dataset as ds

# Load semua variable .env
load_dotenv()


# #Inisialisasi Objek dan Variabel
dataset = ds.DatasetAgent()

config_list = [{
    "model" : os.environ.get("LOCAL_LLAMA_MODEL"),
    "base_url": os.environ.get("LOCAL_LLAMA_URL"),
    "api_base": os.environ.get("LOCAL_LLAMA_URL"),
    "api_key" : os.environ.get("LOCAL_LLAMA_API_KEY"),
}]
llm_config= {
    "config_list" : config_list,
    "temperature":0,
    "cache_seed":42,
    "functions" : [schema.dataset_schema],
}



config_list = [{
    "model": os.environ.get("LOCAL_LLAMA_MODEL"), 
    "api_key": os.environ.get("LOCAL_LLAMA_API_KEY"),
    "api_base": os.environ.get("LOCAL_LLAMA_URL"),
    "request_timeout": 600,
}]

llm_config = {
    "config_list": config_list,
    "temperature": 0,
    "seed": 42,
}

llm_config_interpreter = {
    "config_list": config_list,
    "temperature": 0,
    "seed": 42,
    "functions": [schema.dataset_schema] 
}


# 1. User Proxy 
user_proxy = UserProxyAgent(
    name="user",
    human_input_mode="TERMINATE", 
    code_execution_config={"work_dir": "coding"},
    function_map={"filter_data": dataset.search_program_wrapper}
)

# 2. Profile Interpreter
profile_interpreter = AssistantAgent(
    name="profile_interpreter",
    system_message="""Kamu adalah penafsir profil. 
    Tugas: Analisis input user. Ekstrak IPK, Bidang, Negara, dan Tujuan Karier.
    
    LALU, panggil fungsi 'filter_data' dengan parameter tersebut.
    Ini adalah cara kamu memerintahkan agen data untuk bekerja.
    
    Setelah kamu melihat hasil datanya kembali, katakan: "Data sudah ada, silakan fit_evaluator menganalisis." """,
    llm_config=llm_config,
)

# 3. Program Data Specialist 
program_data_agent = UserProxyAgent(
    name="program_data_agent",
    human_input_mode="NEVER", # otomatis jalan
    max_consecutive_auto_reply=0, # Diam setelah eksekusi
    code_execution_config={"work_dir": "coding"},
    function_map={
        "filter_data": dataset.search_program_wrapper
    }
)
# 4. Fit Evaluator
fit_evaluator = AssistantAgent(
    name="fit_evaluator",
    system_message="""Kamu adalah penilai kecocokan.
    Tugas: 
    1. Baca data JSON program studi yang diberikan.
    2. Bandingkan dengan profil user.
    3. Kategorikan setiap program menjadi 'Realistic Match' atau 'Ambitious Target'.
    4. Setelah selesai analisis, minta 'recommendation_writer' membuat laporan.""",
    llm_config=llm_config,
)

# 5. Recommendation Writer
study_recommendation_writer_agent = AssistantAgent(
    name="recommendation_writer",
    system_message="""Kamu adalah konsultan pendidikan.
    Tugas: Susun rekomendasi 3 "Realistic Match" dan 2 "Ambitious Target". Jelaskan kecocokan user dengan rekomendasi tersebut, dan berikan arahan singkat jika ingin mengejar "Ambitious Target" 
    Jika sudah selesai, akhiri percakapan dengan mengatakan: TERMINATE""",
    llm_config=llm_config,
)

# --- 4. GROUP CHAT ---
groupchat = GroupChat(
    agents=[user_proxy, profile_interpreter, program_data_agent, fit_evaluator, study_recommendation_writer_agent],
    messages=[],
    max_round=20
)

manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

if __name__ == "__main__":
    user_story = """
    Halo, saya Rina. Saya lulusan Informatika IPK 3.6, memiliki pengalaman riset tentang AI dan 1 tahun kerja di perusahaan data. Saya ingin studi S2 di bidang machine learning.
    """

    print("Running system with pyautogen 0.1.14...")
    user_proxy.initiate_chat(
        manager,
        message=user_story
    )