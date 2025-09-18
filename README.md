# smart-album-splitter

> Work In Progress (WIP): This tool is under development. Currently only the core pipeline functions are implemented and working.

## Quick Start

### Requirements
- Python 3.10+
- ffmpeg installed and on your PATH
- Dependencies installed: `pip install -r requirements.txt`

### Running
From the project root:

```bash
python -m smart_splitter.cli run projects/<your-project>/project.yml
```

Other available commands that work:

```bash
python -m smart_splitter.cli detect projects/<your-project>/project.yml --emit json
python -m smart_splitter.cli split projects/<your-project>/project.yml
python -m smart_splitter.cli tag projects/<your-project>/project.yml
```

These will download audio, detect/split tracks, and tag metadata based on your `project.yml`. Output files are written to the project’s `output/` directory.

---