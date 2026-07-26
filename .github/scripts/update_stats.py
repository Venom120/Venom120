import os
import requests

USERNAME = "Venom120"

LANGUAGES_API = str(f"https://hackatime.hackclub.com/api/v1/users/{USERNAME}/stats")
PROJECTS_API = str(
    f"https://hackatime.hackclub.com/api/v1/users/{USERNAME}/projects/details"
)


def fetch_languages():
    """Fetch language statistics from Hackatime."""
    response = requests.get(LANGUAGES_API, timeout=30)
    response.raise_for_status()
    return response.json()["data"]


def fetch_projects():
    """Fetch project statistics from Hackatime."""
    response = requests.get(PROJECTS_API, timeout=30)
    response.raise_for_status()
    return response.json()["projects"]


def make_bar(percent, width=20):
    filled = round(width * percent / 100)
    return "█" * filled + "░" * (width - filled)


def format_duration(seconds):
    """Convert seconds into 'X hrs Y mins'."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours == 0:
        return f"{minutes} mins"

    return f"{hours} hrs {minutes} mins"


def generate_markdown(language_data, projects):
    languages = language_data["languages"]
    total_text = language_data["human_readable_total"]

    # Sort projects by coding time
    projects = sorted(
        projects,
        key=lambda x: x["total_seconds"],
        reverse=True,
    )

    total_project_seconds = sum(p["total_seconds"] for p in projects)

    output = []

    output.append("### 📡 **My Hackatime stats (All Time)**\n")

    # ---------------- Languages ----------------

    output.append("💾 **Languages:**")
    output.append("```text")

    for lang in languages[:5]:
        name = lang["name"]
        time_str = lang["text"]
        percent = lang["percent"]

        output.append(
            f"{name:<15} {time_str:<16} {make_bar(percent)} {percent:6.2f}%"
        )

    output.append("```")
    output.append("")

    # ---------------- Projects ----------------

    output.append("💼 **Projects:**")
    output.append("```text")

    for project in projects[:5]:
        percent = (
            project["total_seconds"] * 100 / total_project_seconds
            if total_project_seconds
            else 0
        )

        output.append(
            f"{project['name']:<15} "
            f"{format_duration(project['total_seconds']):<16} "
            f"{make_bar(percent)} "
            f"{percent:6.2f}%"
        )

    output.append("```")
    output.append("")
    output.append(f"**Total:** {total_text}")

    return "\n".join(output)


def update_readme():
    language_data = fetch_languages()
    projects = fetch_projects()

    new_stats = generate_markdown(language_data, projects)

    readme_path = "README.md"

    if not os.path.exists(readme_path):
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("<!-- HACKATIME:START -->\n<!-- HACKATIME:END -->")

    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()

    start_tag = "<!-- HACKATIME:START -->"
    end_tag = "<!-- HACKATIME:END -->"

    if start_tag in readme and end_tag in readme:
        start_index = readme.index(start_tag) + len(start_tag)
        end_index = readme.index(end_tag)

        updated = (
            readme[:start_index]
            + "\n"
            + new_stats
            + "\n"
            + readme[end_index:]
        )
    else:
        updated = (
            readme
            + f"\n\n{start_tag}\n"
            + new_stats
            + f"\n{end_tag}\n"
        )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(updated)


if __name__ == "__main__":
    update_readme()