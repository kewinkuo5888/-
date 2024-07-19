from click import prompt
from flask import Flask, request, render_template, jsonify, session
import os
import fitz
import openai
import dotenv
import time
from flask_cors import CORS

# Define the client variable
client = openai

# Rest of the code...


dotenv.load_dotenv()
# 設定 OpenAI API 金鑰
openai.api_key = os.getenv("OPENAI_API_KEY")
app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# 组合的故事数据
stories_data = {
    "Andersen": [
        {
            "title": "小美人鱼",
            "characters": [
                {"name": "小美人鱼", "description": "海底王國的公主，對人類世界充滿嚮往"},
                {"name": "王子", "description": "被小美人鱼救下的英俊王子"},
                {"name": "海巫婆", "description": "強大的巫婆，能夠實現小美人鱼的願望但代價高昂"}
            ],
            "settings": [
                {"name": "海底王國", "description": "美麗的海底世界，充滿奇異的生物和植物"},
                {"name": "人類王國", "description": "地上的華麗宮殿和城市"}
            ],
            "situations": [
                {"name": "救王子", "description": "小美人鱼救下溺水的王子並將他帶到岸上"},
                {"name": "換取雙腿", "description": "小美人鱼向海巫婆換取雙腿，希望能與王子在一起"}
            ],
            "styles": [
                {"name": "浪漫", "description": "充滿愛情和犧牲的故事"},
                {"name": "悲劇", "description": "最終小美人鱼未能和王子在一起"}
            ]
        },
        # ... 其他安徒生故事 ...
    ],
    "Grimm": [
        {
            "title": "白雪公主",
            "characters": [
                {"name": "白雪公主", "description": "美麗的公主，皮膚如雪白，唇紅如血"},
                {"name": "邪惡皇后", "description": "嫉妒白雪公主美貌的邪惡繼母"},
                {"name": "七個小矮人", "description": "住在森林裡的七個善良的矮人"},
                {"name": "王子", "description": "愛上白雪公主並最終拯救她的王子"}
            ],
            "settings": [
                {"name": "城堡", "description": "白雪公主和邪惡皇后居住的地方"},
                {"name": "森林", "description": "白雪公主逃離後藏身的地方"},
                {"name": "矮人小屋", "description": "七個小矮人的居所"}
            ],
            "situations": [
                {"name": "魔鏡告知真相", "description": "魔鏡告訴皇后白雪公主比她更美麗"},
                {"name": "逃離森林", "description": "白雪公主逃離皇后的追殺，藏身於七個小矮人的家中"},
                {"name": "毒蘋果", "description": "皇后假扮老婦人用毒蘋果陷害白雪公主"},
                {"name": "王子拯救", "description": "王子發現並拯救陷入昏迷的白雪公主"}
            ],
            "styles": [
                {"name": "經典童話", "description": "善良與邪惡的對立，最終善良戰勝邪惡"},
                {"name": "黑暗奇幻", "description": "故事中充滿驚悚和黑暗元素"}
            ]
        },
        # ... 其他格林童话 ...
    ]
}

# PDF处理函数


def read_pdf(file_path):
    try:
        document = fitz.open(file_path)
        content = ""
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            content += page.get_text()
        return content
    except Exception as e:
        print(f"Error reading PDF file at {file_path}: {e}")
        raise


def extract_elements(content, keyword):
    elements = []
    is_collecting = False
    for line in content.split('\n'):
        if keyword in line:
            is_collecting = True
        elif is_collecting:
            if line.strip() == "":
                break
            elements.append(line.strip())
    return elements


def extract_fairy_tale_elements(content):
    characters = extract_elements(content, "人物:")
    settings = extract_elements(content, "場景:")
    plot = extract_elements(content, "情境:")
    style = extract_elements(content, "風格:")
    return {
        "characters": characters,
        "settings": settings,
        "plot": plot,
        "style": style
    }


def extract_marketing_strategy_elements(content):
    strategies = extract_elements(content, "策略:")
    plans = extract_elements(content, "方案:")
    scenarios = extract_elements(content, "情境:")
    return {
        "strategies": strategies,
        "plans": plans,
        "scenarios": scenarios
    }


def process_pdfs(fairy_tale_path, marketing_strategy_path):
    fairy_tale_content = read_pdf(fairy_tale_path)
    marketing_strategy_content = read_pdf(marketing_strategy_path)

    fairy_tale_elements = extract_fairy_tale_elements(fairy_tale_content)
    marketing_strategy_elements = extract_marketing_strategy_elements(
        marketing_strategy_content)

    fused_elements = {
        "characters": fairy_tale_elements["characters"],
        "settings": fairy_tale_elements["settings"],
        "plot": fairy_tale_elements["plot"],
        "style": fairy_tale_elements["style"],
        "strategies": marketing_strategy_elements["strategies"],
        "plans": marketing_strategy_elements["plans"],
        "scenarios": marketing_strategy_elements["scenarios"]
    }

    return fused_elements

# 路由


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_stories', methods=['GET'])
def get_stories():
    return jsonify(stories_data)


@app.route('/generate_story', methods=['POST'])
def generate_story():
    data = request.json
    story_script = generate_story_script(data)
    return jsonify({"story": story_script})

def generate_story_script(data):
    # Your story generation logic here
    return "This is a generated story based on the input data."

# @app.route('/generate_image', methods=['POST'])
# def generate_image():
#     data = request.json
#     selected_elements = data['selectedElements']
#     image_prompts_and_scripts = generate_image_prompts_and_scripts(
#         selected_elements)
#     return jsonify(image_prompts_and_scripts)


@app.route('/process', methods=['POST'])
def process():
    fairy_tale_pdf = request.files['fairy_tale_pdf']
    marketing_strategy_pdf = request.files['marketing_strategy_pdf']

    fairy_tale_path = os.path.join('uploads', fairy_tale_pdf.filename)
    marketing_strategy_path = os.path.join(
        'uploads', marketing_strategy_pdf.filename)

    fairy_tale_pdf.save(fairy_tale_path)
    marketing_strategy_pdf.save(marketing_strategy_path)

    elements = process_pdfs(fairy_tale_path, marketing_strategy_path)

    session['elements'] = elements

    return render_template('select_elements.html', elements=elements)

# 生成函数

def generate_story_and_dalle_prompts(form_data):
    # 構建故事創作的提示
    story_prompt = (
        f"創作一個融合以下元素的童話故事：\n"
        f"行銷主題: {form_data['marketingTopic']}\n"
        f"童話故事: {form_data['fairyTale']}\n"
        f"行銷策略: {form_data['marketingStrategy']}\n"
        f"人物: {form_data['character']}\n"
        f"場景: {form_data['scene']}\n"
        f"情境: {form_data['situation']}\n"
        f"風格: {form_data['style']}\n"
        f"策略方案: {form_data['strategy']}\n"
        f"執行方法: {form_data['execution']}\n"
        f"請根據上述元素創作一個吸引人的童話故事，將行銷主題巧妙融入其中。"
    )
    # def generate_story_script(form_data):
    # prompt = (
    #     f"創作一個融合以下元素的童話故事：\n"
    #     f"行銷主題: {form_data['marketingTopic']}\n"
    #     f"童話故事: {form_data['fairyTale']}\n"
    #     f"行銷策略: {form_data['marketingStrategy']}\n"
    #     f"人物: {form_data['character']}\n"
    #     f"場景: {form_data['scene']}\n"
    #     f"情境: {form_data['situation']}\n"
    #     f"風格: {form_data['style']}\n"
    #     f"策略方案: {form_data['strategy']}\n"
    #     f"執行方法: {form_data['execution']}\n"
    #     f"請根據上述元素創作一個吸引人的童話故事，將行銷主題巧妙融入其中。"
    # )
    # response = client.completions.create(
    #     model="gpt-3.5-turbo-instruct",
    #     prompt=prompt,
    #     max_tokens=1000
    # )
    # result = response.choices[0].text
    # print('-'*50)
    # print(result)
    # print('-'*50)
    # return result
        # 使用OpenAI API生成故事
 
    try:
        # 使用OpenAI API生成故事
        story_response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=story_prompt,
            max_tokens=1200,
            n=1,
            stop=None,
            temperature=0.7
        )
        story = story_response.choices[0].text.strip()
        
        # 將生成的故事保存到檔案中
        with open('story.txt', 'w', encoding='utf-8') as story_file:
            story_file.write(story)
        
        # 構建DALL-E提示的生成請求
        dalle_prompt = (
            "你是一個AI，幫助將故事轉換為DALL-E的提示。"
            "請將以下故事轉換為四個DALL-E的提示，每個提示描述一個場景：\n"
            f"{story}"
        )
        
        # 使用OpenAI API生成DALL-E提示
        dalle_response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=dalle_prompt,
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.7
        )
        dalle_prompts = dalle_response.choices[0].text.strip().split('\n')
        
        # 將生成的DALL-E提示保存到檔案中
        with open('dalle_prompts.txt', 'w', encoding='utf-8') as file:
            for prompt in dalle_prompts:
                file.write(prompt + '\n')
        
        return "Story and DALL-E prompts generated successfully."
    
    except Exception as e:
        print("Error while generating the story or DALL-E prompts:", str(e))
        return None

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    print(generate_story_and_dalle_prompts({
        'marketingTopic': 'Environmental Awareness',
        'fairyTale': 'A magical forest',
        'marketingStrategy': 'Social Media Campaign',
        'character': 'A talking tree',
        'scene': 'A lush green forest',
        'situation': 'Saving the forest from pollution',
        'style': 'Whimsical and enchanting',
        'strategy': 'Highlight the importance of nature',
        'execution': 'Engage the audience with interactive content'
    }))
