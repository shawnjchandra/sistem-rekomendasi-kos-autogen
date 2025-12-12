dataset_schema = {
    "name": "filter_data",
    "description" : "Mencari program studi dari database berdasarkan IPK, bidang, negara, dan tujuan karier.",
    "parameters" : {
        "type": "object",
        "properties": {
            "min_ipk" : {
                "type": "number",
                "description": "Persyaratan minimum ipk yang diterima oleh universitas, seperti 3.5"
            },
            "bidang" : {
                "type": "string",
                "description": "Bidang peminatan dalam Bahasa Inggris, dipisahkan oleh koma, seperti 'Computer Science,Engineering'"
            },
            "negara" : {
                "type": "string",
                "description": "Negara dalam Bahasa Inggris, dipisahkan dengan koma, seperti 'Indonesia,Netherlands'"
            },
            "tujuan_karier" : {
                "type": "string",
                "description": "Tujuan karir dalam Bahasa Inggris, dipisahkan oleh koma, seperti 'Researche,Data Scientist,Game Developer'"
            }
            
        },
        "required": ["min_ipk", "bidang", "negara"]
    }
    
}