import beam


app = beam.App(
    name="lol_scraper",
    cpu=1,
    memory="16Gi",
    python_packages=["requests"]
)


app.Trigger.Webhook(inputs={"username": beam.Types.String()}, handler="main.py:crawl")
app.Output.File(path="./data.json", name="scraped_data")