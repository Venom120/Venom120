import os
import requests

def fetch_hackatime_stats():
    api_key = os.environ.get("HACKATIME_API_KEY")
    if not api_key:
        raise ValueError("HACKATIME_API_KEY environment variable is not set. Please add it to your repository secrets.")
        
    # Updated API endpoint appending the API key as a query parameter
    api_url = f"https://hackatime.hackclub.com/api/hackatime/v1/users/current/stats/last_7_days?api_key={api_key}"
    
    # Passing the API key in the Authorization header as well
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
        
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    
    # Based on the JSON schema, the data we need is inside the top-level "data" object
    return response.json().get("data", {})

def make_bar(percent, width=20):
    filled = int(round(width * percent / 100))
    return "█" * filled + "░" * (width - filled)

def generate_markdown(data):
    languages = data.get("languages", [])
    projects = data.get("projects", [])
    total_text = data.get("human_readable_total", "0 hrs 0 mins")

    output = []
    output.append("📡 **my hackatime stats from the last week**\n")

    # Using fenced code blocks (```text) forces proper line breaks and monospaced alignment
    output.append("💾 **Languages:**")
    output.append("```text")
    for lang in languages[:5]:
        name = lang.get("name", "Unknown")
        time_str = lang.get("text", "0 hrs 0 mins")
        percent = lang.get("percent", 0.0)
        bar = make_bar(percent)
        # Formatted spacing: 15 chars for name, 16 for time, then the bar and percentage
        output.append(f"{name:<15} {time_str:<16} {bar} {percent:6.2f}%")
    output.append("```\n")
    
    output.append("💼 **Projects:**")
    output.append("```text")
    for proj in projects[:5]:
        name = proj.get("name", "Unknown")
        time_str = proj.get("text", "0 hrs 0 mins")
        percent = proj.get("percent", 0.0)
        bar = make_bar(percent)
        output.append(f"{name:<15} {time_str:<16} {bar} {percent:6.2f}%")
    output.append("```\n")

    output.append(f"**Total:** {total_text}")
    return "\n".join(output)

def update_readme():
    data = fetch_hackatime_stats()
    new_stats_content = generate_markdown(data)

    readme_path = "README.md"
    
    # Check if README.md exists, if not, create it (helpful for initial setup)
    if not os.path.exists(readme_path):
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("<!-- HACKATIME:START -->\n<!-- HACKATIME:END -->\n")

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