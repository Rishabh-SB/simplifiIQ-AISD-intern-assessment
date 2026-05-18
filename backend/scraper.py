import os
import httpx
from bs4 import BeautifulSoup
from google import genai

async def enrich_company_data(company_name: str, company_url: str) -> dict:
    """
    Scrapes the target homepage and leverages Gemini to output a structured
    analysis containing business focus areas and automation ideas.
    """
    # Ensure URL formatting is correct
    url = company_url if company_url.startswith(("http://", "https://")) else f"https://{company_url}"
    web_context = "[No Live Content Recovered due to Scraping Barriers]"

    # Attempt to fetch content safely
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CoreScraper/1.0"}
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                for script in soup(["script", "style"]):
                    script.decompose()
                web_context = " ".join(soup.get_text().split())[:4000]
    except Exception as err:
        print(f"⚠️ Scraping barrier encountered for {url}: {err}. Transitioning to fallback inferences.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY inside environment configuration.")
    
    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert corporate analyst and automation consultant. Analyze this company.
    
    Company Name: {company_name}
    Provided URL: {url}
    Cleaned Home Page Content:
    ---
    {web_context}
    ---

    Generate an actionable, highly professional business profile report using exactly the following uppercase keys, splitting sections with double newlines:
    
    INDUSTRY: (Specify clear industry domain)
    SUMMARY: (Provide a sharp 2-3 sentence overview of their core business offering)
    AUDIENCE: (Identify who their primary customers or buyers are)
    VALUE_PROP: (Detail their main competitive advantage)
    STRATEGY_1: (A detailed, customized AI or workflow automation recommendation to upgrade their business)
    STRATEGY_2: (A second distinct technical/operational process optimization strategy)
    STRATEGY_3: (A third unique domain-specific technical growth strategy)
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return parse_gemini_response(response.text)
    except Exception as e:
        print(f"❌ Gemini enrichment failure: {e}")
        return {
            "industry": "General Corporate Domain",
            "summary": f"Active operational enterprise tracing to {company_name}.",
            "audience": "Commercial B2B/B2C client ecosystems.",
            "value_prop": "Providing solutions tailored around client needs.",
            "strategy_1": "Deploy internal LLM knowledge alignment frameworks to enhance response times.",
            "strategy_2": "Integrate structured programmatic capture pipelines to streamline operations.",
            "strategy_3": "Audit structural digital funnels to mitigate dropping customer metrics."
        }

def parse_gemini_response(text: str) -> dict:
    lines = text.split("\n")
    data = {"industry": "", "summary": "", "audience": "", "value_prop": "", "strategy_1": "", "strategy_2": "", "strategy_3": ""}
    current_key = None
    for line in lines:
        line_str = line.strip()
        if not line_str: continue
        for key in data.keys():
            upper_key = f"{key.upper()}:"
            if line_str.startswith(upper_key):
                current_key = key
                line_str = line_str[len(upper_key):].strip()
                break
        if current_key and line_str:
            clean_val = line_str.lstrip("- *•").strip()
            if data[current_key]: data[current_key] += " " + clean_val
            else: data[current_key] = clean_val
    return data