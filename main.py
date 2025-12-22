import sys
import os
import requests
from bs4 import BeautifulSoup
import asyncio
from telegram import Bot
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# 윈도우 환경에서 종료 시 RuntimeError 방지
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TOKEN = os.getenv('TOKEN')
CHAT_IDS = os.getenv('CHAT_IDS', '').split(',')

def get_quantum_news():
    rss_url = "https://news.google.com/rss/search?q=양자컴퓨터+OR+Quantum+Computing+when:1d&hl=ko&gl=KR&ceid=KR:ko"
    # headers = {"User-Agent": "Mozilla/5.0"}
    # headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        response = requests.get(rss_url, headers=headers)
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all('item')
        if not items: return None

        items.sort(key=lambda x: datetime.strptime(x.pubDate.text, '%a, %d %b %Y %H:%M:%S %Z'), reverse=True)
        
        news_results = []
        for i, item in enumerate(items[:10], 1):
            # news_results.append(f"{i}. <a href='{item.link.text}'>{item.title.text}</a>")
            
            short_link = shorten_url(item.link.text)
            # [수정] 제목(굵게)과 짧은 링크를 줄바꿈(\n)으로 구분하여 추가
            news_results.append(f"<b>{i}. {item.title.text}</b>\n🔗 {short_link}")
            
        return "🚀 <b>오늘의 양자컴퓨터 최신 뉴스</b>\n\n" + "\n\n".join(news_results)
    except Exception as e:
        return f"스크래핑 중 오류 발생: {e}"

async def main():
    if not TOKEN or not CHAT_IDS:
        print("설정값이 비어있습니다.")
        return

    bot = Bot(token=TOKEN)
    message_content = get_quantum_news()
    
    if message_content:
        for chat_id in CHAT_IDS:
            try:
                await bot.send_message(chat_id=chat_id.strip(), text=message_content, parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                print(f"{chat_id} 전송 실패: {e}")
        print("모든 전송 완료!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (RuntimeError, KeyboardInterrupt):
        pass
