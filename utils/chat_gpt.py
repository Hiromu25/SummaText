import openai


# GPT-3.5を使用してテキストを要約し、それがどのような人におすすめかを述べる関数
def summarize_and_recommend_with_gpt3(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "system",
                "content": "You are a talented writer with a knack for captivating summaries. Imagine you are crafting a compelling headline to entice readers to dive into the article. Summarize the content in three sentences, making it engaging and intriguing. After the summary, also provide a recommendation on who would find this article most beneficial. Write in Japanese.",
            },
            {
                "role": "user",
                "content": f"Summarize this and recommend who would benefit: {text}",
            },
        ],
        max_tokens=1024,
    )
    return response.choices[0].message["content"]

def extract_keywords_with_gpt3(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a highly intelligent model capable of understanding and interpreting text, even when it contains inaccuracies due to OCR errors. Your task is to identify and extract the most relevant keywords from the following text, while intelligently completing any missing or erroneous characters."},
            {"role": "user", "content": f"Here is the text: {text}"},
        ],
        max_tokens=60,
    )
    return response.choices[0].message['content']
