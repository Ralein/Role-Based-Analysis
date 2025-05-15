import os
import sys
import argparse
import requests
from rich.console import Console
from rich.markdown import Markdown

def get_api_url():
    # Default to local Ollama instance; adjust as needed
    return os.getenv("OLLAMA_API_URL", "http://10.10.99.24:11434/api/generate")

def validate_role_name(role_name):
    if not role_name or len(role_name) < 2 or len(role_name) > 100:
        return False
    forbidden = set('!@#$%^&*()[]{};:\'",<>/?\\|`~')
    return not any(c in forbidden for c in role_name)

def analyze_role(role_name, api_url, console):
    prompt = (
        f"Tell me everything about the role of a {role_name} in IT – "
        "include required skills (technical & soft), tools used, experience level, "
        "certifications (if any), career progression, and typical responsibilities."
    )
    try:
        payload = {
            "model": "mistral:latest",  # Change to your preferred Ollama model
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json()
        text = result.get("response", "")
        console.print(f"\n[bold green]--- Role Analysis: {role_name} ---[/bold green]")
        console.print(Markdown(text))
        return text
    except Exception as e:
        console.print(f"[bold red]An error occurred while generating the role analysis for {role_name}:[/bold red] {e}")
        with open("role-analysis-error.log", "a") as log_file:
            log_file.write(f"Error for role '{role_name}': {e}\n")
        return None

def suggest_roles(skills, api_url, console):
    prompt = (
        f"Given the following IT skills: {skills}, suggest 5 suitable IT roles. "
        "List only the role names, separated by commas. Do not explain."
    )
    try:
        payload = {
            "model": "mistral:latest",  # Change to your preferred Ollama model
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json()
        roles_line = result.get("response", "").strip()
        roles = [role.strip() for role in roles_line.split(",") if role.strip()]
        return roles
    except Exception as e:
        console.print(f"[bold red]An error occurred while suggesting roles:[/bold red] {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description="Analyze IT roles using Ollama API.")
    parser.add_argument("-s", "--skills", help="Comma-separated list of your IT skills")
    parser.add_argument("-o", "--output", help="Output Markdown file to save the analysis")
    args = parser.parse_args()

    console = Console()
    api_url = get_api_url()

    # Step 1: Get user skills
    if args.skills:
        skills = args.skills
    else:
        console.print("[bold yellow]Enter your IT skills, separated by commas (e.g., Python, SQL, Cloud):[/bold yellow]")
        skills = input("Your skills: ").strip()

    # Step 2: Suggest roles based on skills
    suggested_roles = suggest_roles(skills, api_url, console)
    if not suggested_roles:
        console.print("[bold red]No roles could be suggested based on the provided skills.[/bold red]")
        sys.exit(1)

    console.print("\n[bold green]Suggested IT Roles based on your skills:[/bold green]")
    for idx, role in enumerate(suggested_roles, 1):
        console.print(f"{idx}. {role}")

    # Step 3: Let user select a role
    while True:
        try:
            choice = int(input(f"Select a role to analyze (1-{len(suggested_roles)}): "))
            if 1 <= choice <= len(suggested_roles):
                selected_role = suggested_roles[choice - 1]
                break
            else:
                console.print("[bold red]Invalid selection. Try again.[/bold red]")
        except ValueError:
            console.print("[bold red]Please enter a valid number.[/bold red]")

    # Step 4: Analyze the selected role
    all_results = []
    if validate_role_name(selected_role):
        result = analyze_role(selected_role, api_url, console)
        if result:
            all_results.append((selected_role, result))

    if args.output and all_results:
        with open(args.output, "w", encoding="utf-8") as f:
            for role_name, analysis in all_results:
                f.write(f"# Role Analysis: {role_name}\n\n{analysis}\n\n")
        console.print(f"[bold blue]Analysis saved to {args.output}[/bold blue]")

if __name__ == "__main__":
    main()