import os
import requests

def fetch_hackatime_stats():
    # Updated API endpoint for Hackatime using user ID 15520
    api_url = os.environ.get("HACKATIME_API_URL", "https://hackatime.hackclub.com/api/v1/users/15520/stats")
    
    # Hackatime API for public stats typically doesn't require a Bearer token, 
    # but we can leave the header optional or include it if needed.
    headers = {}
    api_key = os.environ.get("HACKATIME_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    return response.json().get("data", {})

def make_bar(percent, width=15):
    filled = int(round(width * percent / 100))
    return "█" * filled + "░" * (width - filled)

def generate_markdown(data):
    languages = data.get("languages", [])
    projects = data.get("projects", [])
    total_text = data.get("human_readable_total", "0 hrs 0 mins")

    output = []
    output.append("📡 **my hackatime stats from the last week**\n")

    output.append("💾 Languages:")
    for lang in languages[:5]:
        name = lang.get("name")
        time_str = lang.get("text")
        percent = lang.get("percent")
        bar = make_bar(percent)
        output.append(f"`{name:<12} {time_str:<12} {bar} {percent:6.2f}%`")
    
    output.append("")
    output.append("💼 Projects:")
    for proj in projects[:5]:
        name = proj.get("name")
        time_str = proj.get("text")
        percent = proj.get("percent")
        bar = make_bar(percent)
        output.append(f"`{name:<15} {time_str:<12} {bar} {percent:6.2f}%`")

    output.append("")
    output.append(f"**Total:** {total_text}")
    return "\n".join(output)

def update_readme():
    data = fetch_hackatime_stats()
    new_stats_content = generate_markdown(data)

    readme_path = "README.md"
    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()

    start_tag = "<!-- HACKATIME:START -->"
    end_tag = "<!-- HACKATIME:END -->"

    if start_tag in readme and end_tag in readme:
        start_idx = readme.index(start_tag) + len(start_tag)
        end_idx = readme.index(end_tag)
        updated_readme = readme[:start_idx] + "\n" + new_stats_content + "\n" + readme[end_idx:]
    else:
        updated_readme = readme + f"\n\n{start_tag}\n{new_stats_content}\n{end_tag}\n"

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(updated_readme)

if __name__ == "__main__":
    update_readme()