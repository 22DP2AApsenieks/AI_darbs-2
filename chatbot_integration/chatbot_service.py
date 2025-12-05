import os
from openai import OpenAI
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        # ===== 1. SOLIS - API atslēgas ielāde =====
        load_dotenv()  # ielādē mainīgos no .env
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY nav atrasts .env failā!")

        # ===== 2. SOLIS - OpenAI klienta inicializācija =====
        self.client = OpenAI(api_key=self.api_key)

        # ===== 3. SOLIS - Sistēmas instrukcijas =====
        # Tiek papildināta ar iespēju pievienot produktu sarakstu dinamisku
        self.system_instruction_template = (
            "Tu esi gudrs un laipns e-veikala asistents. "
            "Atbildi uz jautājumiem tikai par veikala produktiem, cenām, pasūtījumiem un piegādi. "
            "Ja lietotājs jautā par kaut ko ārpus veikala, atbildi: "
            "'Atvainojiet, es varu atbildēt tikai par mūsu veikala produktiem.' "
            "Atbildes veido īsas un saprotamas, maksimāli 3–4 teikumus.\n\n"
            "Veikala produkti:\n{product_list}"
        )

    def get_chatbot_response(self, user_message, chat_history=None, product_list=""):
        if chat_history is None:
            chat_history = []

        # ===== 4. SOLIS - Ziņojumu saraksta izveide =====
        messages = []
        # Sistēmas instrukcija ar dinamisko produktu sarakstu
        system_instruction = self.system_instruction_template.format(product_list=product_list)
        messages.append({"role": "system", "content": system_instruction})

        # Pievieno iepriekšējo sarunas vēsturi, ja tāda ir
        messages.extend(chat_history)

        # Pievieno pēdējo lietotāja ziņu
        messages.append({"role": "user", "content": user_message})

        # ===== 5. SOLIS - HF API izsaukums ar OpenAI bibliotēku =====
        try:
            response = self.client.chat.completions.create(
                model="katanemo/Arch-Router-1.5B",
                messages=messages,
                max_tokens=300,
                temperature=0.6
            )
        except Exception as e:
            print("❌ Kļūda izsaucot API:", e)
            return {"response": "Atvainojiet, šobrīd nav iespējams sazināties ar čatbotu."}

        # ===== 6. SOLIS - Atbildes apstrāde =====
        reply_text = ""
        try:
            if response.choices and len(response.choices) > 0:
                reply_text = response.choices[0].message.get("content", "")
            else:
                reply_text = "Atvainojiet, modelis neatgrieza atbildi."
        except Exception as e:
            print("❌ Kļūda apstrādājot atbildi:", e)
            reply_text = "Atvainojiet, radās kļūda apstrādājot API atbildi."

        return {"response": reply_text.strip()}
