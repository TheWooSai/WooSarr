"""WooSarr CLI entry points."""
import typer
from rich.console import Console

from app.core.config import settings

app = typer.Typer()
console = Console()


@app.command()
def start():
    """Start the WooSarr backend API server."""
    import uvicorn

    console.print(f"Starting WooSarr backend on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


@app.command()
def bot():
    """Start the WooSarr Discord bot."""
    from app.bot import run_bot

    console.print("Starting WooSarr Discord bot...")
    run_bot()


@app.command()
def migrate():
    """Run database migrations."""
    import subprocess

    console.print("Running database migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
        cwd=".",
    )
    if result.returncode == 0:
        console.print("Migrations completed successfully")
    else:
        console.print(result.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()