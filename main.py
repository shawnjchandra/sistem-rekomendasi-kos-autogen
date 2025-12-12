import inspect
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
    
}]
# model= 'gpt-4o-mini'
# llm_config= {
#     "model": model,
#     "api_key" : os.environ.get("OPENAI_API_KEY"),
#     "temperature":0,
#     "functions" : [schema.dataset_schema],
#     "function_call" : "auto"
# }

config_list = [{
    "model" : os.environ.get("LOCAL_LLAMA_MODEL"),
    "base_url": os.environ.get("LOCAL_LLAMA_URL"),
    "api_base": os.environ.get("LOCAL_LLAMA_URL"),
    "api_key" : "ollama",
}]
llm_config= {
    "config_list" : config_list,
    # "mode;"
    "temperature":0,
    "cache_seed":42,
    "functions" : [schema.dataset_schema],
    # "function_call" : "auto"
}

# # UserProxyAgent
user = UserProxyAgent(
    name='executor',
    human_input_mode='TERMINATE',
    max_consecutive_auto_reply=2,
    code_execution_config={
        "work_dir": "user_representation",
        "use_docker": False
    },
)

# user

# ProfileInterpreterAgent (LLM)
profile_interpreter = AssistantAgent(
    name="profile_interpreter",
    system_message="""Kamu adalah asisten pencari program studi pascasarjana.

    PENTING: Kamu HARUS menggunakan fungsi filter_data untuk mencari program. JANGAN jawab langsung tanpa memanggil fungsi.

    Langkah-langkah:
    1. Ekstrak informasi dari input user: IPK, bidang, negara, tujuan karier
    2. WAJIB panggil fungsi filter_data dengan parameter yang sesuai
    3. Setelah dapat hasil, analisis dan berikan rekomendasi

    Parameter filter_data:
    - min_ipk: IPK minimum (number)
    - bidang: Bidang studi, pisahkan dengan koma (string)
    - negara: Negara tujuan, pisahkan dengan koma (string)
    - tujuan_karier: Tujuan karier, pisahkan dengan koma (string)

    Contoh pemanggilan:
    filter_data(min_ipk=3.5, bidang="Computer Science,AI", negara="Indonesia,Netherlands", tujuan_karier="Researcher,Data Scientist")


    """,
    max_consecutive_auto_reply=2,
    llm_config=llm_config
)

# ProgramData Agent (Python)
program_data = UserProxyAgent(
    name="program_data",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=2,
    code_execution_config=False,
    function_map={
        "filter_data": dataset.filter_data
    }
    
)

#ProgramFitEvaluatorAgent (LLM)
program_fit_evaluator = AssistantAgent(
    name="program_fit_evaluator",
    system_message="""Kamu bertugas untuk menilai kecocokan antara program studi dengan profil mahasiswa.
    
    Tugas kamu:
    1. Analisis setiap program yang ditemukan.
    2. Cari nilai kecocokan berdasarkan: bidang, minimal persyaratan IPK, fokus riset, dan tujuan karier
    3. Kelompokkan program menjadi:
        - "Realistic Match": Program yang sesuai dengan profil
        - "Ambitious Target": Program yang bagus tapi perlu peningkatan atau penyesuaian lebih lanjut dari profil
        
        Berikan skor dan penjelasan alasan untuk setiap program""",
        max_consecutive_auto_reply=2,
    llm_config=llm_config
)

#StudyRecommendationWriterAgent (LLM)
study_recommendation = AssistantAgent(
    name="study_recommendation",
    system_message="""
        Kamu bertugas untuk membuat rekomendasi program studi yang final.
        
        Tugas kamu:
        1. Membuat rekomendasi sebanyak 2-3 program "Realistic Match".
        2. Membuat rekomendasi sebanyak 1-2 "Ambitious Target".
        3. Untuk setiap program jelaskan:
            - Kenapa program ini cocok untuk pengguna
            - Kelebihan program
            - Persyaratan yang perlu diperhatikan
        4. Berikan saran untuk penguatan profil jika pengguna ingin mengejar pilihan yang lebih ambisius
    """,
    max_consecutive_auto_reply=2,
    llm_config=llm_config
)

profile_interpreter.register_function(
    function_map={
        "filter_data": dataset.filter_data
    }
)
# profile_interpreter.register_function(
#     function_map={
#         "filter_data": dataset.filter_data
#     }
# )

# records = dataset.filter_data(minat_bidang="engineering")
# if records is not None:
#     print(len(records))
#     for r in records:
#         print(r)
if __name__ == "__main__":
    # print("Test")
    # records = dataset.filter_data(bidang="Computer Science")
    # if records:
    #     print(f"Jumlah program: {len(records)}")
    #     for r in records[:3]:
    #         print(r)
            
    groupchat = GroupChat(
        agents=[user,profile_interpreter,program_data,program_fit_evaluator,study_recommendation],
        messages=[],
        max_round=5
        )
    groupchat_mgr = GroupChatManager(
        groupchat, 
        llm_config=llm_config,
        max_consecutive_auto_reply=10,
        human_input_mode="ALWAYS")
    
    user.initiate_chat(
        groupchat_mgr,
        message="""
        Saya lulusan S1 Informatika dengan IPK 3.5.
        Saya tertarik kuliah S2 di bidang Computer Science dan AI.
        Saya ingin kuliah di Indonesia atau Netherlands.
        Tujuan karier saya menjadi Researcher atau Data Scientist.
        Tolong carikan program yang cocok.
        """
    )

# sig = inspect.signature(ds.DatasetAgent.filter_data)
# func_params = list(sig.parameters.keys())[1:]  # Skip 'self'
# print("Function params:", func_params)

# schema_params = list(schema.dataset_schema['parameters']['properties'].keys())
# print("Schema params:", schema_params)

# # Should be identical!
# assert func_params == schema_params, "Parameter mismatch!"
# print("✅ Parameters match!")

# # Di main script, setelah create user agent
# print("=== Debug Info ===")
# print("Executor function_map:", user.function_map)
# print("Dataset object:", dataset)
# print("Filter function:", dataset.filter_data)
# print("Callable?", callable(dataset.filter_data))