from google import genai
from rich.console import Console
from rich.markdown import Markdown

def analyze_role(role_name):
    client = genai.Client(api_key="Enter your API KEY")
    prompt = (
        f"Tell me everything about the role of a {role_name} in IT – "
        "include required skills (technical & soft), tools used, experience level, "
        "certifications (if any), career progression, and typical responsibilities."
    )
    console = Console()
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        console.print("\n[bold green]--- Role Analysis ---[/bold green]")
        console.print(Markdown(response.text))
    except Exception as e:
        console.print(f"[bold red]An error occurred while generating the role analysis:[/bold red] {e}")

def main():
    role_name = input("Enter the IT role you want to analyze: ").strip()
    if not role_name:
        print("Role name cannot be empty.")
        return
    analyze_role(role_name)

if __name__ == "__main__":
    main()
