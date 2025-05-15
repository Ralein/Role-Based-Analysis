import os
import sys
import argparse
from google import genai
from rich.console import Console
from rich.markdown import Markdown

def get_api_key():
    api_key = os.getenv("GENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set the GENAI_API_KEY environment variable.")
    return api_key

def analyze_role(role_name, client, console):
    prompt = (
        f"Tell me everything about the role of a {role_name} in IT – "
        "include required skills (technical & soft), tools used, experience level, "
        "certifications (if any), career progression, and typical responsibilities."
    )
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        console.print(f"\n[bold green]--- Role Analysis: {role_name} ---[/bold green]")
        console.print(Markdown(response.text))
        return response.text
    except Exception as e:
        console.print(f"[bold red]An error occurred while generating the role analysis for {role_name}:[/bold red] {e}")
        with open("role-analysis-error.log", "a") as log_file:
            log_file.write(f"Error for role '{role_name}': {e}\n")
        return None

def validate_role_name(role_name):
    if not role_name or len(role_name) < 2 or len(role_name) > 100:
        return False
    forbidden = set('!@#$%^&*()[]{};:\'",<>/?\\|`~')
    return not any(c in forbidden for c in role_name)

def main():
    parser = argparse.ArgumentParser(description="Analyze IT roles using Gemini AI.")
    parser.add_argument("roles", nargs="*", help="IT role(s) to analyze (e.g., 'Data Analyst' 'DevOps Engineer')")
    parser.add_argument("-o", "--output", help="Output Markdown file to save the analysis")
    args = parser.parse_args()

    console = Console()
    try:
        api_key = get_api_key()
    except ValueError as e:
        console.print(f"[bold red]{e}[/bold red]")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    if not args.roles:
        console.print("[bold yellow]No roles provided as arguments. Enter roles one by one (empty input to finish):[/bold yellow]")
        roles = []
        while True:
            role_name = input("Enter IT role: ").strip()
            if not role_name:
                break
            roles.append(role_name)
    else:
        roles = args.roles

    all_results = []
    for role_name in roles:
        if not validate_role_name(role_name):
            console.print(f"[bold red]Invalid role name: {role_name}[/bold red]")
            continue
        result = analyze_role(role_name, client, console)
        if result:
            all_results.append((role_name, result))

    if args.output and all_results:
        with open(args.output, "w", encoding="utf-8") as f:
            for role_name, analysis in all_results:
                f.write(f"# Role Analysis: {role_name}\n\n{analysis}\n\n")
        console.print(f"[bold blue]Analysis saved to {args.output}[/bold blue]")

if __name__ == "__main__":
    main()