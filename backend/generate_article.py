import os
import sys
import datetime
import google.generativeai as genai

# APIキーの設定
# 実行時に環境変数 GEMINI_API_KEY が必要です
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable not set.")
    sys.exit(1)

genai.configure(api_key=api_key)

def generate_article(game_title):
    print(f"Generating article for: {game_title}")
    
    # モデルの初期化 (Gemini 1.5 Proなどを指定)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    prompt = f"""
    あなたはプロのゲーム攻略ライターです。
    トレンドゲーム「{game_title}」に関するSEOに強い攻略記事を1つ作成してください。
    
    【要件】
    * 形式: Markdown形式 (フロントマターを除く、# から始める)
    * 文字数: 1000〜2000文字程度
    * 構成:
      * # {game_title} 攻略ガイド
      * 目次（不要、MkDocsが自動生成するため）
      * 導入（読者の興味を惹く文章）
      * 見出し2 (##) を2〜3つ設定（例: 序盤の効率的な進め方、おすすめ武器・キャラ、ボス攻略のコツなど）
      * まとめ
    * 文体: ゲーマー向けに親しみやすく、かつ有益な情報を提供するトーン
    
    【出力形式】
    Markdownのテキストのみを出力してください（Markdownコードブロック of ```markdown 等で囲まないでください）。
    """
    
    try:
        response = model.generate_content(prompt)
        content = response.text
        
        # 不要なMarkdownコードブロック of バッククォートが含まれている場合は除去
        if content.startswith("```markdown"):
            content = content[11:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        return content.strip()
    except Exception as e:
        print(f"Failed to generate content: {e}")
        sys.exit(1)

def save_article(game_title, content):
    try:
        # 保存先のディレクトリ
        docs_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "docs")
        os.makedirs(docs_dir, exist_ok=True)
        
        # ファイル名の生成 (URLセーフにするため簡易的に処理)
        safe_title = game_title.replace(" ", "-").replace("/", "-").lower()
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}-{safe_title}.md"
        filepath = os.path.join(docs_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            # MkDocs/Material用のフロントマター（メタデータ）を付与
            frontmatter = f"---\ntitle: {game_title} 攻略ガイド\ndescription: {game_title} の最新攻略情報まとめ\n---\n\n"
            f.write(frontmatter + content)
            
        print(f"Article saved to: {filepath}")
        
        # MkDocsのナビゲーションに自動追加されるように index.md も更新（簡易版）
        index_path = os.path.join(docs_dir, "index.md")
        with open(index_path, "a", encoding="utf-8") as f:
            f.write(f"\n* [{game_title} 攻略ガイド]({filename})")
    except Exception as e:
        print(f"Failed to save article: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # コマンドライン引数からゲームタイトルを取得、なければデフォルト
    target_game = sys.argv[1] if len(sys.argv) > 1 else "モンスターハンターワイルズ"
    
    article_content = generate_article(target_game)
    if article_content:
        save_article(target_game, article_content)
